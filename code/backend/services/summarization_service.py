from typing import Tuple
from .gemini_helper import chunk_text, call_gemini

ENGLISH_SUMMARY_PROMPT = """You are an educational assistant. Summarize the following English text for B1-B2 level students.
Keep the summary clear, concise, and suitable for learners. Focus on main points and key takeaways.
Use simple academic language. Provide only the summary without additional commentary."""

BURMESE_SUMMARY_PROMPT = """You are an educational assistant. Summarize the following English text in Burmese (Myanmar language) for B1-B2 level students.
Keep the summary clear, concise, and suitable for learners. Focus on main points and key takeaways.
Preserve important technical terms. Provide only the summary without additional commentary."""

def summarize_text(text: str, model: str = "gemini-2.5-flash") -> Tuple[str, str]:
    """Generate English and Burmese summaries using Gemini.
    
    Returns:
        Tuple of (english_summary, burmese_summary)
    """
    if not text or len(text.strip()) < 20:
        raise ValueError("Text is too short to summarize.")
    
    chunks = chunk_text(text, max_chars=4000)
    
    # Generate English summary
    english_summary = call_gemini(model, ENGLISH_SUMMARY_PROMPT, chunks)
    
    # Generate Burmese summary
    burmese_summary = call_gemini(model, BURMESE_SUMMARY_PROMPT, chunks)
    
    return english_summary, burmese_summary
