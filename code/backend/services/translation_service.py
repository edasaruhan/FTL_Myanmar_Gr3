from typing import List
from .gemini_helper import chunk_text, call_gemini

TRANSLATION_PROMPT = """You are a professional translator. Translate the following English text to Burmese (Myanmar language).
Preserve technical terms where possible. Maintain the original structure and tone.
Provide only the translated text without any additional commentary."""

def translate_to_burmese(text: str, model: str = "gemini-1.5-flash") -> str:
    """Translate English text to Burmese using Gemini."""
    if not text or len(text.strip()) < 10:
        raise ValueError("Text is too short to translate.")
    
    chunks = chunk_text(text, max_chars=4000)
    translated = call_gemini(model, TRANSLATION_PROMPT, chunks)
    return translated
