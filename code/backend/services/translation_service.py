from typing import List, Tuple
import time
from .gemini_helper import chunk_text, call_gemini
from .cache_service import get_cached_result, set_cached_result

TRANSLATION_PROMPT = """You are a professional translator. Translate the following English text to Burmese (Myanmar language).
Preserve technical terms where possible. Maintain the original structure and tone.
Provide only the translated text without any additional commentary."""

def translate_to_burmese(text: str, model: str = "gemini-2.5-flash") -> Tuple[str, float, bool]:
    """Translate English text to Burmese using Gemini.
    
    Returns:
        Tuple of (translated_text, elapsed_ms, from_cache)
    """
    if not text or len(text.strip()) < 10:
        raise ValueError("Text is too short to translate.")
    
    # Check cache
    cached = get_cached_result(text, "translation")
    if cached:
        return cached, 0, True
    
    start = time.perf_counter()
    chunks = chunk_text(text, max_chars=4000)
    translated = call_gemini(model, TRANSLATION_PROMPT, chunks)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    # Store in cache
    set_cached_result(text, "translation", translated)
    
    return translated, elapsed_ms, False
