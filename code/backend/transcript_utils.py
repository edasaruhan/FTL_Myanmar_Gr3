import os
import tempfile
import yt_dlp
import ffmpeg
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from faster_whisper import WhisperModel
from PyPDF2 import PdfReader
from typing import List, Optional
import srt, webvtt

# --- YouTube transcript/caption extraction ---
def extract_youtube_id(url: str) -> Optional[str]:
    import re
    match = re.search(r"(?:v=|youtu.be/)([\w-]{11})", url)
    return match.group(1) if match else None

def get_youtube_captions(youtube_url: str):
    video_id = extract_youtube_id(youtube_url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        segments = [
            {"start": seg["start"], "end": seg["start"] + seg["duration"], "text": seg["text"]}
            for seg in transcript
        ]
        text = " ".join(seg["text"] for seg in segments)
        return {"source": "youtube_captions", "transcript_text": text, "segments": segments}
    except Exception:
        # Fallback to yt-dlp subtitles
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'subtitleslangs': ['en'],
            'outtmpl': '%(id)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            subs = info.get('subtitles', {})
            if 'en' in subs:
                # Download and parse the subtitle file as needed
                pass
        return None

# --- Audio download and ASR ---
def download_youtube_audio(youtube_url: str, out_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_path,
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def convert_audio_to_wav(src_path: str, dst_path: str):
    (
        ffmpeg.input(src_path)
        .output(dst_path, ac=1, ar=16000, format='wav')
        .overwrite_output()
        .run(quiet=True)
    )

def transcribe_with_whisper(audio_path: str, model_size: str):
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language="en")
    segs = []
    texts = []
    for seg in segments:
        segs.append({"start": seg.start, "end": seg.end, "text": seg.text})
        texts.append(seg.text)
    return {"source": "asr", "transcript_text": " ".join(texts), "segments": segs}

# --- File upload handling ---
def parse_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return {"source": "uploaded_file", "file_type": "pdf", "transcript_text": text, "segments": [{"start": None, "end": None, "text": text}]}

def parse_txt(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return {"source": "uploaded_file", "file_type": "txt", "transcript_text": text, "segments": [{"start": None, "end": None, "text": text}]}

def parse_srt(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))
    segments = [{"start": sub.start.total_seconds(), "end": sub.end.total_seconds(), "text": sub.content} for sub in subs]
    text = " ".join(sub.content for sub in subs)
    return {"source": "uploaded_file", "file_type": "srt", "transcript_text": text, "segments": segments}

def parse_vtt(file_path: str):
    vtt = webvtt.read(file_path)
    segments = [{"start": float(caption.start_in_seconds), "end": float(caption.end_in_seconds), "text": caption.text} for caption in vtt]
    text = " ".join(caption.text for caption in vtt)
    return {"source": "uploaded_file", "file_type": "vtt", "transcript_text": text, "segments": segments}
