import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os

from .ai_service import generate_deck_plan
from .models import GenerateDeckRequest
from .pptx_service import build_pptx

load_dotenv()

app = FastAPI(title="AI PPT Slide Generator API")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate-ppt")
def generate_ppt(request: GenerateDeckRequest) -> StreamingResponse:
    deck = generate_deck_plan(request)
    pptx = build_pptx(deck, request.theme)
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", request.topic).strip("-").lower() or "presentation"

    return StreamingResponse(
        pptx,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.pptx"'},
    )
