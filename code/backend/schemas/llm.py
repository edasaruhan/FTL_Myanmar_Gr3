from pydantic import BaseModel
from typing import List, Optional

class TranscriptRequest(BaseModel):
    transcript_text: str

class TranslationResponse(BaseModel):
    source_language: str = "en"
    target_language: str = "my"
    translated_text: str
    elapsed_ms: float
    from_cache: bool

class SummaryResponse(BaseModel):
    english_summary: str
    burmese_summary: str
    elapsed_ms: float
    from_cache: bool

class TransformResponse(BaseModel):
    translation_mm: str
    summary_en: str
    summary_mm: str
    elapsed_ms: float

class ChunkInfo(BaseModel):
    chunk_id: str
    score: float
    text_preview: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class RAGQueryRequest(BaseModel):
    question: str

class RAGQueryResponse(BaseModel):
    answer: str
    elapsed_ms: float
    top_chunks: List[ChunkInfo]
    from_cache: bool

class RAGIndexRequest(BaseModel):
    transcript_text: str
    segments: Optional[List[dict]] = None
