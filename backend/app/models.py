from pydantic import BaseModel, Field


class GenerateDeckRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=180)
    slide_count: int = Field(default=8, ge=3, le=15)
    audience: str = Field(default="general audience", max_length=120)
    tone: str = Field(default="clear and professional", max_length=120)
    theme: str = Field(default="modern", max_length=80)


class SlidePlan(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)
    speaker_notes: str = ""


class DeckPlan(BaseModel):
    title: str
    subtitle: str
    slides: list[SlidePlan]
