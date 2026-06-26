import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .ai_service import generate_deck_plan
from .models import GenerateDeckRequest
from .pptx_service import THEMES, build_pptx

load_dotenv()

app = FastAPI(
    title="AI PPT Slide Generator API",
    description="Generate structured presentation plans and editable PowerPoint files.",
    version="0.2.0",
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


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-ppt-slide-generator"}


@app.get("/api/themes")
def list_themes() -> dict[str, list[str]]:
    return {"themes": sorted(THEMES.keys())}


@app.post("/api/preview-plan")
def preview_plan(request: GenerateDeckRequest):
    return generate_deck_plan(request)


@app.post("/api/generate-ppt")
def generate_ppt(request: GenerateDeckRequest) -> StreamingResponse:
    deck = generate_deck_plan(request)
    pptx = build_pptx(deck, request.theme)

    return StreamingResponse(
        pptx,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(request.topic)}.pptx"'},
    )
