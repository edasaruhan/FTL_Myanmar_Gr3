from fastapi import APIRouter, HTTPException
from schemas.llm import TranscriptRequest, TranslationResponse, SummaryResponse
from services.translation_service import translate_to_burmese
from services.summarization_service import summarize_text

router = APIRouter(prefix="/api/llm", tags=["LLM"])

@router.post("/translate", response_model=TranslationResponse)
def translate_transcript(req: TranscriptRequest):
    """Translate English transcript to Burmese."""
    try:
        translated = translate_to_burmese(req.transcript_text)
        return TranslationResponse(
            source_language="en",
            target_language="my",
            translated_text=translated
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@router.post("/summarize", response_model=SummaryResponse)
def summarize_transcript(req: TranscriptRequest):
    """Generate English and Burmese summaries of transcript."""
    try:
        english_summary, burmese_summary = summarize_text(req.transcript_text)
        return SummaryResponse(
            english_summary=english_summary,
            burmese_summary=burmese_summary
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
