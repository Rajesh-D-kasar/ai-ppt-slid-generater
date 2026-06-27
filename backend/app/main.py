import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .ai_service import generate_deck_plan, get_ai_provider_status
from .models import DeckPlan, GenerateDeckRequest
from .pptx_service import DECK_TYPE_LABELS, THEMES, build_pptx

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env", override=True, encoding="utf-8-sig")

app = FastAPI(
    title="AI PPT Slide Generator API",
    description=(
        "Generate structured presentation outlines and editable PowerPoint files from a prompt. "
        "The API supports outline preview, deck types, themed PPTX export, speaker notes, "
        "demo-mode fallback, and OpenAI-powered deck planning when an API key is configured."
    ),
    version="0.5.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _safe_filename(topic: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower() or "presentation"


def _build_deck_or_502(request: GenerateDeckRequest) -> DeckPlan:
    try:
        return generate_deck_plan(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-ppt-slide-generator"}


@app.get("/api/ai-status")
def ai_status() -> dict[str, str | bool]:
    return get_ai_provider_status()


@app.get("/api/themes")
def list_themes() -> dict[str, list[str]]:
    return {"themes": sorted(THEMES.keys())}


@app.get("/api/deck-types")
def list_deck_types() -> dict[str, dict[str, str]]:
    return {"deck_types": DECK_TYPE_LABELS}


@app.post("/api/preview-plan")
def preview_plan(request: GenerateDeckRequest):
    return _build_deck_or_502(request)


@app.post("/api/generate-ppt")
def generate_ppt(request: GenerateDeckRequest) -> StreamingResponse:
    deck = _build_deck_or_502(request)
    pptx = build_pptx(deck, request.theme, request.deck_type)

    return StreamingResponse(
        pptx,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(request.topic)}.pptx"'},
    )