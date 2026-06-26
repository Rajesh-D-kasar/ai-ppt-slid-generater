# AI PPT Slide Generator

AI PPT Slide Generator is a full-stack web app that turns a simple topic or prompt into an editable PowerPoint presentation. It creates a structured deck outline, supports multiple themes and speaker notes, previews the plan before download, and exports a real `.pptx` file.

[![CI](https://github.com/Rajesh-D-kasar/ai-ppt-slid-generater/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajesh-D-kasar/ai-ppt-slid-generater/actions/workflows/ci.yml)

## Highlights

- Generate editable PowerPoint decks from a topic or prompt
- Preview the AI-created slide outline before downloading
- Choose slide count, audience, tone, language, and visual theme
- Add speaker notes automatically
- Export clean `.pptx` files with title, agenda, and content slides
- Works without an API key using demo-mode fallback content
- FastAPI backend with a React/Vite frontend
- Automated backend tests and GitHub Actions CI

## Demo Flow

1. Enter a topic, for example `AI tools for small businesses`.
2. Choose slide count, audience, tone, language, and theme.
3. Click `Preview Outline` to inspect the generated deck plan.
4. Click `Generate PPT` to download the editable PowerPoint file.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | React, Vite, lucide-react |
| Backend | FastAPI, Pydantic, OpenAI SDK |
| PPT export | python-pptx |
| Testing | Python unittest, FastAPI TestClient, Vite build |
| CI | GitHub Actions |
| Runtime | Local PowerShell script or Docker Compose |

## Architecture

```text
User Prompt
   |
   v
React Frontend
   |
   | POST /api/preview-plan
   | POST /api/generate-ppt
   v
FastAPI Backend
   |
   +--> AI service
   |      - Uses OpenAI when OPENAI_API_KEY is available
   |      - Uses demo fallback when no key is configured
   |
   +--> PPTX service
          - Builds title slide
          - Builds agenda slide
          - Builds designed content slides
          - Adds speaker notes
          - Returns .pptx download
```

## Project Structure

```text
.github/
  workflows/
    ci.yml                 GitHub Actions workflow
backend/
  app/
    main.py                API routes and app metadata
    models.py              request and deck schemas
    ai_service.py          AI prompt, demo fallback, normalization
    pptx_service.py        PowerPoint generation and themes
  tests/
    test_api.py            backend API and PPT export tests
  requirements.txt         backend dependencies
frontend/
  src/
    App.jsx                generator UI and download flow
    styles.css             responsive product styling
  package.json             frontend scripts and dependencies
  package-lock.json        locked npm dependency tree
run-dev.ps1                one-command local startup script
docker-compose.yml         optional Docker runtime
```

## Quick Start

Run everything with one command:

```powershell
.\run-dev.ps1
```

Then open:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Backend Setup

Use Python 3.10, 3.11, or 3.12 for the backend virtual environment. Python 3.14 may try to build native packages locally.

```powershell
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Set `OPENAI_API_KEY` in `backend/.env` for real AI generation. If no key is set, the app still works in demo mode.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`. Override it with `VITE_API_URL` if needed.

## Environment Variables

Create `backend/.env` from `backend/.env.example`:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGINS=http://localhost:5173
```

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | No | Enables real AI generation. Demo mode is used when empty. |
| `OPENAI_MODEL` | No | OpenAI model used for deck planning. Defaults to `gpt-4.1-mini`. |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins for the frontend. |

## API Reference

### `GET /api/health`

Returns service health.

```json
{
  "status": "ok",
  "service": "ai-ppt-slide-generator"
}
```

### `GET /api/themes`

Returns available presentation themes.

```json
{
  "themes": ["dark", "minimal", "modern", "startup", "warm"]
}
```

### `POST /api/preview-plan`

Returns the generated deck outline as JSON.

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

### `POST /api/generate-ppt`

Returns a downloadable PowerPoint file.

Response content type:

```text
application/vnd.openxmlformats-officedocument.presentationml.presentation
```

## Themes

Available themes:

- `modern`
- `minimal`
- `startup`
- `dark`
- `warm`

## Testing

Backend API tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## CI

GitHub Actions runs on every push and pull request to `main`:

- Installs backend dependencies on Python 3.10
- Runs backend API tests
- Installs frontend dependencies with `npm ci`
- Builds the React frontend

Workflow file: `.github/workflows/ci.yml`

## Docker

Optional Docker workflow:

```powershell
docker compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Troubleshooting

### Python dependency install fails on Windows

Use Python 3.10, 3.11, or 3.12. Python 3.14 may try to compile native packages locally.

```powershell
Remove-Item backend\.venv -Recurse -Force
py -3.10 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### Frontend cannot reach backend

Check that the backend is running:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

If the backend is on another URL, set `VITE_API_URL` before starting Vite.

### AI output is demo content

Set `OPENAI_API_KEY` in `backend/.env` and restart the backend.

## Roadmap

- Add slide image generation or stock-image suggestions
- Add branded company templates
- Add template upload support
- Add user accounts and saved deck history
- Add PDF export
- Add presentation sharing links
- Add deployment configs for production hosting

## Repository

GitHub: https://github.com/Rajesh-D-kasar/ai-ppt-slid-generater
