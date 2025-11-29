from typing import Tuple
import time
from .gemini_helper import chunk_text, call_gemini
from .cache_service import get_cached_result, set_cached_result

ENGLISH_SUMMARY_PROMPT = """You are an educational assistant. Summarize the following English text for B1-B2 level students.
Keep the summary clear, concise, and suitable for learners. Focus on main points and key takeaways.
Use simple academic language. Provide only the summary without additional commentary."""

BURMESE_SUMMARY_PROMPT = """You are an educational assistant. Summarize the following English text in Burmese (Myanmar language) for B1-B2 level students.
Keep the summary clear, concise, and suitable for learners. Focus on main points and key takeaways.
Preserve important technical terms. Provide only the summary without additional commentary."""

def summarize_text(text: str, model: str = "gemini-2.5-flash") -> Tuple[str, str, float, bool, float, bool]:
    """Generate English and Burmese summaries using Gemini.
    
    Returns:
        Tuple of (english_summary, burmese_summary, en_elapsed_ms, en_from_cache, mm_elapsed_ms, mm_from_cache)
    """
    if not text or len(text.strip()) < 20:
        raise ValueError("Text is too short to summarize.")
    
    chunks = chunk_text(text, max_chars=4000)
    
    # Generate English summary
    cached_en = get_cached_result(text, "summary_en")
    if cached_en:
        english_summary, en_elapsed_ms, en_from_cache = cached_en, 0, True
    else:
        start = time.perf_counter()
        english_summary = call_gemini(model, ENGLISH_SUMMARY_PROMPT, chunks)
        en_elapsed_ms = (time.perf_counter() - start) * 1000
        en_from_cache = False
        set_cached_result(text, "summary_en", english_summary)
    
    # Generate Burmese summary
    cached_mm = get_cached_result(text, "summary_mm")
    if cached_mm:
        burmese_summary, mm_elapsed_ms, mm_from_cache = cached_mm, 0, True
    else:
        start = time.perf_counter()
        burmese_summary = call_gemini(model, BURMESE_SUMMARY_PROMPT, chunks)
        mm_elapsed_ms = (time.perf_counter() - start) * 1000
        mm_from_cache = False
        set_cached_result(text, "summary_mm", burmese_summary)
    
    return english_summary, burmese_summary, en_elapsed_ms, en_from_cache, mm_elapsed_ms, mm_from_cache
