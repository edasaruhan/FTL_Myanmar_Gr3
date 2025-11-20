# Lecture Companion

## How to Run This Project
1. Clone:
   ```bash
   git clone <repo-url>
   cd FTL_Myanmar_Gr3
   ```
2. Start services (first build may download models):
   ```bash
   docker compose up --build
   ```
3. Open:
   - Frontend: http://localhost:3000
   - Backend docs (Swagger): http://localhost:8000/docs
4. Stop:
   ```bash
   docker compose down
   ```
5. Update deps (backend or frontend):
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
    requirements.txt
    Dockerfile
  frontend/
    app/
    package.json
    Dockerfile
docker-compose.yml
```

## Backend Overview
- Tech: FastAPI, Python 3.10.
- Flow (YouTube): try captions → else download audio → Whisper.
- Endpoints:
  - POST /api/transcribe/youtube
  - POST /api/transcribe/upload
- Key libs: faster-whisper, yt-dlp, ffmpeg-python, youtube-transcript-api, PyPDF2, srt, webvtt-py.

## Frontend Overview
- Tech: Next.js 14 App Router + TypeScript + Tailwind.
- Two tabs: YouTube URL | File Upload.
- Uses `NEXT_PUBLIC_API_BASE_URL` to call backend.

## Dev Loop
1. Run stack.
2. Test a YouTube URL with/without native captions.
3. Test uploads (.pdf/.txt/.srt/.vtt).
4. Adjust logic → rebuild affected service.

## Common Issues
| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: srt` | Rebuild backend image after ensuring dependency in requirements.txt |
| `sh: next: not found` | Remove/adjust frontend volume; rebuild to restore node_modules |
| 404 at `/` backend | Use `/docs` or API endpoints; no root HTML |
| Slow transcription | Switch model_size to `small` |

## Future Work Checklist
- Translation (multi-language output)
- Summarization (section + overall summary)
- RAG Q&A over transcript
- Speaker diarization (if multi-speaker)
- Persistence + user sessions
- Model size auto-selection based on length

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
