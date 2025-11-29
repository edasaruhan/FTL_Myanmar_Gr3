from pydantic import BaseModel

class TranscriptRequest(BaseModel):
    transcript_text: str

class TranslationResponse(BaseModel):
    source_language: str = "en"
    target_language: str = "my"
    translated_text: str

class SummaryResponse(BaseModel):
    english_summary: str
    burmese_summary: str
