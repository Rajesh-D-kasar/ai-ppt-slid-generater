# AI PPT Slide Generator

Generate editable PowerPoint decks from a simple topic or prompt.

## Features

- AI-generated slide outline from a topic
- Downloadable `.pptx` presentation
- Theme, audience, tone, and slide count controls
- FastAPI backend and React frontend
- Clean API boundary so the AI provider can be swapped later

## Project Structure

```text
backend/
  app/
    main.py
    models.py
    pptx_service.py
    ai_service.py
frontend/
  src/
    App.jsx
    styles.css
```

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `OPENAI_API_KEY` in `backend/.env` when you want real AI generation. Without a key, the backend uses a local demo outline so development still works.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`.

## API

`POST /api/generate-ppt`

Request:

```json
{
  "topic": "Artificial Intelligence in Education",
  "slide_count": 8,
  "audience": "college students",
  "tone": "clear and practical",
  "theme": "modern"
}
```

Response: downloadable PowerPoint file.
