# AI PPT Generator

AI PPT Generator is a full-stack app that creates editable PowerPoint presentations from a topic, audience, tone, and deck type.

## Overview

This project combines a React/Vite frontend with a FastAPI backend. The backend can use the OpenAI API to generate a structured deck outline, then converts that outline into a real `.pptx` file using `python-pptx`.

If no API key is configured, or if the AI request fails, the app can still generate a demo deck from built-in templates.

## Features

- Generate editable `.pptx` presentations
- Preview the slide outline before downloading
- Choose slide count, audience, tone, language, theme, and deck type
- Supports speaker notes
- Supports deck types: business, startup pitch, education, sales, research, and general
- Supports layouts: bullets, two-column, timeline, metrics, quote, and closing
- Shows whether the backend is running in OpenAI mode or demo mode
- Includes backend tests and GitHub Actions CI

## Tech Stack

| Area | Technology |
| --- | --- |
| Frontend | React, Vite, lucide-react |
| Backend | FastAPI, Pydantic, Uvicorn |
| AI | OpenAI Python SDK |
| PPT export | python-pptx |
| Config | python-dotenv |
| Tests | Python unittest, FastAPI TestClient |

## How It Works

1. The user fills the generator form in the React frontend.
2. The frontend sends the request to the FastAPI backend.
3. The backend validates the request with Pydantic.
4. `ai_service.py` creates a deck plan using OpenAI or demo templates.
5. `pptx_service.py` renders the deck into an editable PowerPoint file.
6. The backend returns the `.pptx` file as a download.

Main backend entrypoint:

```text
backend/app/main.py
FastAPI app: app.main:app
```

Important API routes:

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| GET | `/api/ai-status` | Shows demo/OpenAI mode |
| GET | `/api/themes` | Lists available themes |
| GET | `/api/deck-types` | Lists deck templates |
| POST | `/api/preview-plan` | Returns slide outline JSON |
| POST | `/api/generate-ppt` | Downloads the generated `.pptx` |

## Project Structure

```text
backend/
  app/
    main.py          FastAPI routes and app setup
    models.py        Request and response schemas
    ai_service.py    OpenAI integration, demo templates, normalization
    pptx_service.py  PowerPoint generation and slide layouts
  tests/
    test_api.py      Backend API and PPT export tests
  requirements.txt

frontend/
  src/
    App.jsx          Generator UI and download flow
    styles.css       Responsive styling
  package.json

run-dev.ps1          One-command local startup script
docker-compose.yml   Optional Docker Compose setup
DEPLOYMENT.md        Deployment notes
```

## Setup Instructions

### Required Software

Install these first:

1. Python 3.10, 3.11, or 3.12
2. Node.js LTS
3. Git
4. PowerShell, already available on Windows

Check installation:

```powershell
python --version
node --version
npm --version
git --version
```

If these commands show version numbers, the system is ready.

### Clone the Project

Open PowerShell and run:

```powershell
git clone https://github.com/Rajesh-D-kasar/ai-ppt-slid-generater.git
cd ai-ppt-slid-generater
```

If you downloaded ZIP from GitHub instead, unzip it, open that folder, then right-click inside the folder and choose `Open in Terminal`.

### Add API Key

Go to this file:

```text
backend/.env
```

If `.env` does not exist, create it by copying `.env.example`:

```powershell
cd backend
copy .env.example .env
```

Open `backend/.env` and add your key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
AI_FALLBACK_ON_ERROR=true
ALLOWED_ORIGINS=http://localhost:5173
```

Do not upload `.env` to GitHub.

## Beginner Friendly Run Guide

This is the easiest way to run the project on Windows.

### Step 1: Open the Project Folder

Open PowerShell in the main project folder. The folder should contain these files:

```text
backend
frontend
run-dev.ps1
README.md
```

If you are not inside the project folder, go there with:

```powershell
cd path\to\ai-ppt-slid-generater
```

Example:

```powershell
cd C:\Users\ASUS\Documents\Codex\2026-06-24\github-plugin-github-openai-curated-remote-2
```

### Step 2: Run One Command

Run:

```powershell
.\run-dev.ps1
```

The first run can take a few minutes because it installs backend and frontend dependencies.

### Step 3: Open the App

After the command finishes, open this in your browser:

```text
http://localhost:5173
```

Backend API docs are available here:

```text
http://localhost:8000/docs
```

### Step 4: Use the App

1. Enter a topic.
2. Select deck type, audience, tone, theme, and slide count.
3. Click `Preview Outline`.
4. Click `Generate PPT`.
5. The PowerPoint file will download.

### If PowerShell Blocks the Script

Run this command once in the same PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run again:

```powershell
.\run-dev.ps1
```

## Manual Run Commands

Use this method if you want to run backend and frontend separately.

### Backend

Open PowerShell in the project folder:

```powershell
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Keep this terminal open.

### Frontend

Open a second PowerShell window in the project folder:

```powershell
cd frontend
npm install
npm run dev
```

Keep this terminal open too.

Now open:

```text
http://localhost:5173
```

## Environment Variables

Backend variables:

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | No | Enables OpenAI deck generation. Without it, demo mode is used. |
| `OPENAI_MODEL` | No | OpenAI model name. Default: `gpt-4.1-mini`. |
| `AI_FALLBACK_ON_ERROR` | No | Uses demo fallback when AI fails. Default: `true`. |
| `ALLOWED_ORIGINS` | No | CORS origins. Default: `http://localhost:5173`. |

Frontend variable:

| Variable | Required | Description |
| --- | --- | --- |
| `VITE_API_URL` | No | Backend URL. Default: `http://localhost:8000`. |

## Running the Project

Recommended command:

```powershell
.\run-dev.ps1
```

Manual backend command:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

Manual frontend command:

```powershell
cd frontend
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`

## Usage Guide

1. Enter a presentation topic.
2. Select deck type, slide count, audience, tone, language, and theme.
3. Click `Preview Outline` to review the slide plan.
4. Click `Generate PPT` to download the editable PowerPoint file.

## Example Workflow

Example input:

```text
Topic: AI tools for small businesses
Deck type: Business Brief
Audience: Small business owners
Tone: Professional
Slides: 8
Theme: Modern
```

Expected output:

- Title slide
- Agenda slide
- Structured content slides
- Speaker notes, if enabled
- Downloadable `.pptx` file

## Screenshots

Screenshots are not included in the repository yet. Recommended screenshots to add later:

- Generator form
- Outline preview
- Downloaded PowerPoint deck

## Common Problems

### `python` or `py` is not recognized

Install Python 3.10, 3.11, or 3.12, then reopen PowerShell.

### `npm` is not recognized

Install Node.js LTS, then reopen PowerShell.

### PowerShell script is blocked

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\run-dev.ps1
```

### Frontend does not open

Make sure this URL is used:

```text
http://localhost:5173
```

### Backend docs do not open

Make sure backend is running, then open:

```text
http://localhost:8000/docs
```

### App shows demo mode

This means the API key is missing, invalid, or OpenAI quota/billing is not active. The app can still generate demo PPT files.

## Limitations

- OpenAI generation requires a valid API key with active quota/billing.
- Demo mode uses predefined templates, so content is less customized than AI output.
- The PowerPoint uses generated text, shapes, layouts, and speaker notes; it does not insert AI-generated images.
- No user authentication is included.
- No database is currently used.

## Future Improvements

- Add saved presentation history
- Add user accounts
- Add more PowerPoint themes
- Add image generation or image upload support
- Add export options such as PDF
- Add more tests for layout rendering

## What I Learned

- Building a full-stack AI workflow with React and FastAPI
- Validating API input with Pydantic
- Using OpenAI responses to create structured slide plans
- Generating editable PowerPoint files with `python-pptx`
- Handling fallback behavior when an AI API is unavailable
- Organizing a project for local setup, CI, and deployment documentation

## Author

Rajesh

GitHub: [Rajesh-D-kasar](https://github.com/Rajesh-D-kasar)