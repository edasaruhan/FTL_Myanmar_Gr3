from fastapi import APIRouter, HTTPException
import time
from schemas.llm import (
    TranscriptRequest, TranslationResponse, SummaryResponse, 
    TransformResponse, RAGQueryRequest, RAGQueryResponse, RAGIndexRequest, ChunkInfo
)
from services.translation_service import translate_to_burmese
from services.summarization_service import summarize_text
from services.rag_service import build_rag_index, query_rag

router = APIRouter(prefix="/api/llm", tags=["LLM"])

@router.post("/translate", response_model=TranslationResponse)
def translate_transcript(req: TranscriptRequest):
    """Translate English transcript to Burmese."""
    try:
        translated, elapsed_ms, from_cache = translate_to_burmese(req.transcript_text)
        return TranslationResponse(
            source_language="en",
            target_language="my",
            translated_text=translated,
            elapsed_ms=elapsed_ms,
            from_cache=from_cache
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@router.post("/summarize", response_model=SummaryResponse)
def summarize_transcript(req: TranscriptRequest):
    """Generate English and Burmese summaries of transcript."""
    try:
        en_summary, mm_summary, en_ms, en_cache, mm_ms, mm_cache = summarize_text(req.transcript_text)
        total_ms = en_ms + mm_ms
        from_cache = en_cache and mm_cache
        return SummaryResponse(
            english_summary=en_summary,
            burmese_summary=mm_summary,
            elapsed_ms=total_ms,
            from_cache=from_cache
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@router.post("/transform/translate-and-summarise", response_model=TransformResponse)
def translate_and_summarise(req: TranscriptRequest):
    """Combined translation and summarization."""
    try:
        start = time.perf_counter()
        
        # Translation
        translation_mm, trans_ms, _ = translate_to_burmese(req.transcript_text)
        
        # Summaries
        summary_en, summary_mm, en_ms, _, mm_ms, _ = summarize_text(req.transcript_text)
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        return TransformResponse(
            translation_mm=translation_mm,
            summary_en=summary_en,
            summary_mm=summary_mm,
            elapsed_ms=elapsed_ms
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transform error: {str(e)}")

@router.post("/rag/index")
def index_transcript(req: RAGIndexRequest):
    """Build RAG index for transcript."""
    try:
        result = build_rag_index(req.transcript_text, req.segments)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index error: {str(e)}")

@router.post("/rag/query", response_model=RAGQueryResponse)
def query_transcript(req: RAGQueryRequest):
    """Query transcript with RAG."""
    try:
        answer, top_chunks, elapsed_ms, from_cache = query_rag(req.question)
        
        chunk_infos = [
            ChunkInfo(
                chunk_id=c["chunk_id"],
                score=c["score"],
                text_preview=c["text_preview"],
                start_time=c.get("start_time"),
                end_time=c.get("end_time")
            )
            for c in top_chunks
        ]
        
        return RAGQueryResponse(
            answer=answer,
            elapsed_ms=elapsed_ms,
            top_chunks=chunk_infos,
            from_cache=from_cache
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query error: {str(e)}")
