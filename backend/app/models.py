from typing import Literal

from pydantic import BaseModel, Field, field_validator


Tone = Literal["professional", "friendly", "persuasive", "educational", "executive"]
Theme = Literal["modern", "dark", "warm", "minimal", "startup"]
DeckType = Literal["business", "startup_pitch", "education", "sales", "research", "general"]
SlideLayout = Literal["bullets", "two_column", "timeline", "metrics", "quote", "closing"]


class GenerateDeckRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=220)
    slide_count: int = Field(default=8, ge=3, le=15)
    audience: str = Field(default="general audience", min_length=2, max_length=140)
    tone: Tone = "professional"
    theme: Theme = "modern"
    deck_type: DeckType = "business"
    language: str = Field(default="English", min_length=2, max_length=40)
    include_speaker_notes: bool = True
    extra_instructions: str = Field(default="", max_length=500)

    @field_validator("topic", "audience", "language", "extra_instructions")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()


class SlidePlan(BaseModel):
    title: str = Field(..., min_length=1, max_length=90)
    bullets: list[str] = Field(default_factory=list, max_length=6)
    speaker_notes: str = Field(default="", max_length=900)
    visual_hint: str = Field(default="", max_length=160)
    layout: SlideLayout = "bullets"


class DeckPlan(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    subtitle: str = Field(default="", max_length=180)
    slides: list[SlidePlan] = Field(default_factory=list)