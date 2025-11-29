import os
import google.generativeai as genai
from typing import List, Optional

def init_gemini():
    """Initialize Gemini with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)

def chunk_text(text: str, max_chars: int = 4000) -> List[str]:
    """Split text into chunks by paragraphs or fixed size."""
    paragraphs = text.split('\n\n')
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"
    if current:
        chunks.append(current.strip())
    return chunks if chunks else [text]

def call_gemini(model_name: str, prompt: str, text_chunks: List[str]) -> str:
    """Call Gemini API on chunks and combine results."""
    init_gemini()
    model = genai.GenerativeModel(model_name)
    results = []
    for chunk in text_chunks:
        full_prompt = f"{prompt}\n\nText:\n{chunk}"
        response = model.generate_content(full_prompt)
        results.append(response.text)
    return "\n\n".join(results)
