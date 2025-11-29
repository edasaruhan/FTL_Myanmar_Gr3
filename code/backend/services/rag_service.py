import os
import re
import time
from typing import List, Dict, Any, Tuple, Optional
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from .cache_service import get_cached_result, set_cached_result

# Initialize ChromaDB
CHROMA_PATH = "./data/chroma"
os.makedirs(CHROMA_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Collection for transcript chunks
collection_name = "transcript_chunks"

RAG_SYSTEM_PROMPT = """You are a helpful assistant answering questions based ONLY on the provided transcript snippets.

IMPORTANT RULES:
1. ONLY use information from the provided snippets
2. DO NOT add any outside knowledge or assumptions
3. If the answer is not in the snippets, say "I don't have enough information in this transcript to answer that question."
4. Be concise and clear in B1-B2 level English"""

def chunk_transcript_by_segments(segments: List[dict]) -> List[Dict[str, Any]]:
    """Convert ASR segments to chunks."""
    chunks = []
    for i, seg in enumerate(segments):
        chunks.append({
            "chunk_id": f"seg_{i}",
            "text": seg.get("text", ""),
            "start_time": seg.get("start"),
            "end_time": seg.get("end"),
            "source_type": "asr_segment"
        })
    return chunks

def chunk_transcript_by_text(text: str) -> List[Dict[str, Any]]:
    """Chunk plain text into overlapping windows."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    window_size = 5
    overlap = 2
    
    for i in range(0, len(sentences), window_size - overlap):
        window = sentences[i:i + window_size]
        chunk_text = " ".join(window)
        if chunk_text.strip():
            chunks.append({
                "chunk_id": f"text_{i}",
                "text": chunk_text,
                "start_time": None,
                "end_time": None,
                "source_type": "text_chunk"
            })
    return chunks

def compute_embeddings(texts: List[str]) -> List[List[float]]:
    """Compute embeddings using Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")
    
    genai.configure(api_key=api_key)
    embeddings = []
    
    for text in texts:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(result['embedding'])
    
    return embeddings

def keyword_score(question: str, text: str) -> float:
    """Simple keyword overlap score (BM25-like)."""
    q_words = set(question.lower().split())
    t_words = set(text.lower().split())
    
    if not q_words:
        return 0.0
    
    overlap = len(q_words & t_words)
    return overlap / len(q_words)

def build_rag_index(transcript_text: str, segments: Optional[List[dict]] = None) -> Dict[str, Any]:
    """Build or update RAG index."""
    # Determine chunking strategy
    if segments:
        chunks = chunk_transcript_by_segments(segments)
    else:
        chunks = chunk_transcript_by_text(transcript_text)
    
    if not chunks:
        raise ValueError("No chunks generated from transcript")
    
    # Compute embeddings
    texts = [c["text"] for c in chunks]
    embeddings = compute_embeddings(texts)
    
    # Store in ChromaDB
    try:
        collection = chroma_client.get_collection(collection_name)
        chroma_client.delete_collection(collection_name)
    except:
        pass
    
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "start_time": c.get("start_time"),
            "end_time": c.get("end_time"),
            "source_type": c.get("source_type", "unknown")
        } for c in chunks]
    )
    
    return {"indexed_chunks": len(chunks), "status": "success"}

def query_rag(question: str, top_k: int = 5, keyword_threshold: float = 0.2) -> Tuple[str, List[Dict[str, Any]], float, bool]:
    """Query RAG system with two-stage ranking.
    
    Returns:
        Tuple of (answer, top_chunks, elapsed_ms, from_cache)
    \"\"\""""
    
    # Check cache
    cache_key = f"rag:{question}"
    cached = get_cached_result(cache_key, "rag_answer")
    if cached:
        return cached["answer"], cached["top_chunks"], 0, True
    
    start = time.perf_counter()
    
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        return "Please index a transcript first before asking questions.", [], (time.perf_counter() - start) * 1000, False
    
    # Get all chunks for keyword scoring
    all_data = collection.get()
    all_chunks = [
        {
            "chunk_id": all_data["ids"][i],
            "text": all_data["documents"][i],
            "metadata": all_data["metadatas"][i]
        }
        for i in range(len(all_data["ids"]))
    ]
    
    # Compute keyword scores
    keyword_scores = {c["chunk_id"]: keyword_score(question, c["text"]) for c in all_chunks}
    max_keyword = max(keyword_scores.values()) if keyword_scores else 0
    
    # Semantic search
    q_embedding = genai.embed_content(
        model="models/embedding-001",
        content=question,
        task_type="retrieval_query"
    )
    
    results = collection.query(
        query_embeddings=[q_embedding['embedding']],
        n_results=min(top_k, len(all_chunks))
    )
    
    # Combine scores: 0.4 * keyword + 0.6 * semantic
    ranked_chunks = []
    for i, chunk_id in enumerate(results["ids"][0]):
        semantic_score = 1.0 - results["distances"][0][i]  # Convert distance to similarity
        kw_score = keyword_scores.get(chunk_id, 0)
        combined_score = 0.4 * kw_score + 0.6 * semantic_score
        
        ranked_chunks.append({
            "chunk_id": chunk_id,
            "score": combined_score,
            "text": results["documents"][0][i],
            "text_preview": results["documents"][0][i][:200] + "..." if len(results["documents"][0][i]) > 200 else results["documents"][0][i],
            "start_time": results["metadatas"][0][i].get("start_time"),
            "end_time": results["metadatas"][0][i].get("end_time")
        })
    
    ranked_chunks.sort(key=lambda x: x["score"], reverse=True)
    top_chunks = ranked_chunks[:3]
    
    # Check if we have relevant content
    if max_keyword < keyword_threshold and (not top_chunks or top_chunks[0]["score"] < 0.3):
        answer = "I can only answer questions based on this transcript. I couldn't find relevant information to answer your question."
        elapsed_ms = (time.perf_counter() - start) * 1000
        result = {"answer": answer, "top_chunks": top_chunks}
        set_cached_result(cache_key, "rag_answer", result)
        return answer, top_chunks, elapsed_ms, False
    
    # Generate answer with Gemini
    context = "\n\n".join([f"Snippet {i+1}:\n{c['text']}" for i, c in enumerate(top_chunks)])
    prompt = f"""{RAG_SYSTEM_PROMPT}

Question: {question}

Transcript snippets:
{context}

Answer:"""
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    answer = response.text
    
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    # Cache result
    result = {"answer": answer, "top_chunks": top_chunks}
    set_cached_result(cache_key, "rag_answer", result)
    
    return answer, top_chunks, elapsed_ms, False
