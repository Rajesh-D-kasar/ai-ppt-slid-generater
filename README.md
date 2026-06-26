# AI PPT Slide Generator

Generate editable PowerPoint decks from a simple topic or prompt.

## What It Does

- Creates a structured slide outline with AI
- Generates editable `.pptx` files
- Supports themes, tone, audience, language, and speaker notes
- Includes an outline preview endpoint before downloading
- Works in demo mode without an API key

## Tech Stack

- Backend: FastAPI, Pydantic, python-pptx, OpenAI SDK
- Frontend: React, Vite, lucide-react
- Runtime: local PowerShell script or Docker Compose

## Project Structure

```text
backend/
  app/
    main.py          API routes
    models.py        request and deck schemas
    ai_service.py    AI prompt, fallback, and normalization
    pptx_service.py  PowerPoint generation and themes
frontend/
  src/
    App.jsx          generator UI
    styles.css       responsive product styling
```

## Quick Start

```powershell
.\run-dev.ps1
```

Then open `http://localhost:5173`.

## Backend Setup

Use Python 3.10, 3.11, or 3.12 for the backend virtual environment. Python 3.14 may try to build native packages locally.

```powershell
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `OPENAI_API_KEY` in `backend/.env` for real AI generation. Without a key, the backend uses a local demo outline so the app still works.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`. You can override this with `VITE_API_URL`.

## API

### `GET /api/health`

Returns service health.

### `GET /api/themes`

Returns available PPT themes.

### `POST /api/preview-plan`

Returns the generated deck outline as JSON.

### `POST /api/generate-ppt`

Returns a downloadable PowerPoint file.

Request example:

```json
{
  "topic": "Artificial Intelligence in Education",
  "slide_count": 8,
  "audience": "college students",
  "tone": "educational",
  "theme": "modern",
  "language": "English",
  "include_speaker_notes": true,
  "extra_instructions": "Use simple examples and practical takeaways."
}
```

## Environment Variables

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGINS=http://localhost:5173
```

## Next Roadmap

- Add image generation or stock-image selection per slide
- Add template upload support
- Add user accounts and saved deck history
- Add PDF export
- Add branded company themes

