# RAG & Caching Implementation Guide

## What Was Added

### 1. Caching Layer (`services/cache_service.py`)
- **In-memory cache** using SHA256 keys
- Keys format: `{operation}:{text}` hashed
- Operations: `translation`, `summary_en`, `summary_mm`, `rag_answer`
- Simple API: `get_cached_result()`, `set_cached_result()`, `clear_cache()`

### 2. Enhanced Translation & Summarization
- Added **timing** with `time.perf_counter()`
- Returns: `(result, elapsed_ms, from_cache)`
- Automatic cache check before Gemini calls
- Automatic cache storage after new results

### 3. RAG Service (`services/rag_service.py`)
**Features:**
- ChromaDB for vector storage (persisted to `./data/chroma`)
- Gemini embeddings (`models/embedding-001`)
- Two chunking strategies:
  - ASR segments (if available)
  - Text-based overlapping windows (5 sentences, 2 overlap)
- Two-stage ranking:
  - **Keyword score** (BM25-like term overlap)
  - **Semantic similarity** (vector search)
  - Combined: `0.4 * keyword + 0.6 * semantic`
- Context-only answers with threshold checks
- System prompt enforces "no outside knowledge"

**Endpoints:**
- `POST /api/llm/rag/index` - Build index
- `POST /api/llm/rag/query` - Ask questions

### 4. Combined Transform Endpoint
- `POST /api/transform/translate-and-summarise`
- Returns all 3 results in one call:
  - Burmese translation
  - English summary
  - Burmese summary
  - Total elapsed time

### 5. Updated Schemas (`schemas/llm.py`)
- All responses now include `elapsed_ms` and `from_cache`
- New models: `TransformResponse`, `RAGQueryResponse`, `RAGIndexRequest`, `ChunkInfo`

### 6. Frontend Enhancements

**TranslationSummary Component:**
- Shows timing: "Took X.XXs"
- Cache indicator: "(cached)" label
- Progress states maintained

**RAGComponent (`components/RAGComponent.tsx`):**
- "Index Transcript" button (one-time setup)
- Question input with Enter key support
- Answer display with timing
- Info icon (ℹ️) to toggle source chunks
- Top 3 chunks shown with:
  - Score
  - Text preview
  - Timestamps (if from ASR segments)

### 7. Dependencies Added
- `chromadb` - Vector database
- `sentence-transformers` - Alternative embedding option

## How It Works

### Caching Flow
```
1. User requests translation
2. Check cache with SHA256(text + "translation")
3. If found → return immediately (elapsed_ms=0, from_cache=true)
4. If not → call Gemini → store result → return
```

### RAG Flow
```
1. Index phase:
   - Chunk transcript (segments or text windows)
   - Compute embeddings via Gemini
   - Store in ChromaDB with metadata

2. Query phase:
   - Check cache first
   - Compute keyword scores for all chunks
   - Run semantic search (top K)
   - Combine scores
   - If best score < threshold → "not found" message
   - Else → pass top 3 chunks to Gemini → generate answer
   - Cache result
```

### Two-Stage Ranking
- **Keyword**: Fast, catches exact matches
- **Semantic**: Understands meaning, handles paraphrasing
- **Weighted**: Keyword (40%) + Semantic (60%)
- **Fallback**: If no keyword overlap, pure semantic

## Testing Checklist

### Backend
- [ ] Cache hit/miss works for translation
- [ ] Cache hit/miss works for summaries
- [ ] Timing is accurate and visible
- [ ] RAG indexing succeeds with ASR segments
- [ ] RAG indexing succeeds with plain text
- [ ] RAG returns relevant chunks
- [ ] RAG refuses off-topic questions
- [ ] Combined transform endpoint works

### Frontend
- [ ] Timing displays correctly
- [ ] Cache indicator shows when appropriate
- [ ] RAG index button works
- [ ] RAG question input and query works
- [ ] Info icon toggles chunk display
- [ ] Chunks show timestamps (if available)
- [ ] Progress indicators during requests

## Performance Notes

- **Caching**: ~0ms for cache hits vs ~2-5s for Gemini calls
- **RAG indexing**: ~1-3s per transcript (one-time)
- **RAG queries**: ~1-2s (embedding + search + generation)
- **Combined transform**: Runs translation + 2 summaries in parallel batches

## Next Steps (Future)

1. **Persistent cache**: Use Redis or disk storage
2. **Cache expiry**: Add TTL for stale results
3. **Streaming**: Use Gemini streaming for real-time output
4. **Better chunking**: Smart sentence boundary detection
5. **Multi-index**: Support multiple transcripts in one session
6. **Citation**: Link answer text to specific chunks
7. **Follow-up**: Maintain conversation context
