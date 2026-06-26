# Deployment Guide

This project can run locally, with Docker, or on common hosting providers.

## Required Secrets

Never commit real secrets. Configure these in your hosting provider dashboard:

```text
OPENAI_API_KEY=your_real_key
OPENAI_MODEL=gpt-4.1-mini
AI_FALLBACK_ON_ERROR=true
ALLOWED_ORIGINS=https://your-frontend-domain.example
```

Frontend environment:

```text
VITE_API_URL=https://your-backend-domain.example
```

## Local Production Docker

Create `backend/.env` from `backend/.env.example`, then run:

```powershell
docker compose -f docker-compose.prod.yml up --build
```

Open:

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`

## Render Blueprint

The root `render.yaml` contains a backend web service and a static frontend service.

Before deploying:

1. Replace `https://your-frontend-domain.example` in `render.yaml` with your real frontend URL.
2. Replace `https://your-backend-domain.example` with your real backend URL.
3. Add `OPENAI_API_KEY` as a secret in Render.

## Vercel Frontend + Render Backend

Backend on Render:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL=https://your-backend-domain.example`

Set backend `ALLOWED_ORIGINS` to the final Vercel frontend URL.

## Health Checks

Backend health:

```powershell
curl http://localhost:8000/api/health
```

AI provider status:

```powershell
curl http://localhost:8000/api/ai-status
```

`/api/ai-status` never returns the API key.

## Production Notes

- Keep `AI_FALLBACK_ON_ERROR=true` if you want the app to keep working with demo fallback content when OpenAI has a temporary issue.
- Set `AI_FALLBACK_ON_ERROR=false` if you want API errors to fail fast during production debugging.
- Use HTTPS domains in `ALLOWED_ORIGINS` for deployed frontends.