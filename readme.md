# Lecture Companion

AI-powered transcript generation, translation, and summarization for lectures.

## Features
- **Transcript Generation**: YouTube URL or file upload (.pdf, .txt, .srt, .vtt)
- **Translation**: English → Burmese using Google Gemini
- **Summarization**: English & Burmese summaries (B1-B2 level)

## How to Run This Project
1. Clone:
   ```bash
   git clone <repo-url>
   cd FTL_Myanmar_Gr3
   ```
2. Add your Gemini API key to `.env` in project root:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```
3. Start services (first build may download models):
   ```bash
   docker compose up --build
   ```
4. Open:
   - Frontend: http://localhost:3000
   - Backend docs (Swagger): http://localhost:8000/docs
5. Stop:
   ```bash
   docker compose down
   ```
6. Update deps (backend or frontend):
   ```bash
   docker compose build backend   # or frontend
   ```

### Optional Local Dev (no Docker)
Backend:
```bash
cd code/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Frontend:
```bash
cd code/frontend
npm install
npm run dev
```

## Project Layout
```
code/
  backend/
    main.py
    transcript_utils.py
    services/
      gemini_helper.py
      translation_service.py
      summarization_service.py
    schemas/
      llm.py
    routes/
      llm.py
    requirements.txt
    Dockerfile
  frontend/
    app/
    components/
      TranslationSummary.tsx
    package.json
    Dockerfile
docker-compose.yml
.env
```

## Backend Overview
- Tech: FastAPI, Python 3.10, Google Gemini.
- Transcription flow: YouTube captions → else audio download + Whisper.
- LLM flow: chunk text → call Gemini per chunk → stitch results.
- Endpoints:
  - POST /api/transcribe/youtube
  - POST /api/transcribe/upload
  - POST /api/llm/translate
  - POST /api/llm/summarize
- Key libs: faster-whisper, yt-dlp, ffmpeg-python, youtube-transcript-api, PyPDF2, srt, webvtt-py, google-generativeai.

## Frontend Overview
- Tech: Next.js 14 App Router + TypeScript + Tailwind.
- Two tabs: YouTube URL | File Upload.
- Translation & Summary section appears after transcript generation.
- Uses `NEXT_PUBLIC_API_BASE_URL` to call backend.

## Dev Loop
1. Run stack.
2. Generate transcript from YouTube URL or upload.
3. Click "Translate to Burmese" or "Generate Summaries".
4. View results in panels.
5. Adjust code → rebuild affected service.

## Common Issues
| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: srt` or `google.generativeai` | Rebuild backend: `docker compose build backend` |
| `sh: next: not found` | Remove/adjust frontend volume; rebuild to restore node_modules |
| 404 at `/` backend | Use `/docs` or API endpoints; no root HTML |
| Slow transcription | Switch model_size to `small` |
| Gemini API error | Check `.env` has valid `GEMINI_API_KEY` |

## Future Work Checklist
- ✅ Translation (English → Burmese)
- ✅ Summarization (English + Burmese summaries)
- RAG Q&A over transcript
- Multi-language translation support
- Speaker diarization (if multi-speaker)
- Persistence + user sessions
- Model size auto-selection based on length
- Batch processing for multiple videos

## Contribution Guidelines
- Branch naming: `feat/<topic>`, `fix/<topic>`
- Keep changes minimal & modular.
- Update README if setup changes.
- Avoid committing large model weights or `node_modules/`.

## Git Hygiene
Ensure `.gitignore` excludes: `node_modules/`, `.next/`, `__pycache__/`, `.env*`.
If already tracked:
```bash
git rm -r --cached node_modules .next __pycache__
git commit -m "chore: remove tracked build artifacts"
```

## License
MIT
