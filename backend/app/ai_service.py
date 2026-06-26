import json
import os
import re
from json import JSONDecodeError

from openai import OpenAI

from .models import DeckPlan, GenerateDeckRequest, SlidePlan

DEFAULT_SECTIONS = [
    ("Overview", "Set the context and define the topic"),
    ("Why It Matters", "Explain urgency, value, and relevance"),
    ("Current Landscape", "Show the present state or market reality"),
    ("Key Opportunities", "Highlight practical benefits"),
    ("Challenges", "Explain risks, blockers, and trade-offs"),
    ("Action Plan", "Recommend practical steps"),
    ("Success Metrics", "Show how progress should be measured"),
    ("Conclusion", "Close with a memorable takeaway"),
]


def _clean_bullets(bullets: list[str]) -> list[str]:
    cleaned = []
    for bullet in bullets:
        text = re.sub(r"\s+", " ", str(bullet)).strip(" -•\t")
        if text:
            cleaned.append(text[:180])
    return cleaned[:6]


def normalize_deck(deck: DeckPlan, request: GenerateDeckRequest) -> DeckPlan:
    slides = []
    for slide in deck.slides[: request.slide_count]:
        title = re.sub(r"\s+", " ", slide.title).strip()[:90] or "Untitled Slide"
        bullets = _clean_bullets(slide.bullets)
        if not bullets:
            bullets = [f"Key point about {request.topic}", "Practical example", "Audience takeaway"]
        notes = slide.speaker_notes.strip() if request.include_speaker_notes else ""
        slides.append(
            SlidePlan(
                title=title,
                bullets=bullets,
                speaker_notes=notes,
                visual_hint=slide.visual_hint.strip()[:160],
            )
        )

    while len(slides) < request.slide_count:
        section, purpose = DEFAULT_SECTIONS[len(slides) % len(DEFAULT_SECTIONS)]
        slides.append(
            SlidePlan(
                title=section,
                bullets=[
                    purpose,
                    f"Apply this idea to {request.audience}",
                    "End with a clear takeaway",
                ],
                speaker_notes=f"Use this slide to {purpose.lower()}.",
                visual_hint="Simple icon, timeline, or comparison layout",
            )
        )

    return DeckPlan(
        title=(deck.title.strip() or request.topic)[:120],
        subtitle=(deck.subtitle.strip() or f"A {request.tone} deck for {request.audience}")[:180],
        slides=slides[: request.slide_count],
    )


def build_demo_deck(request: GenerateDeckRequest) -> DeckPlan:
    slides = []
    for index in range(request.slide_count):
        section, purpose = DEFAULT_SECTIONS[index % len(DEFAULT_SECTIONS)]
        if index == request.slide_count - 1:
            section = "Conclusion"
            purpose = "Summarize the strongest insight and next step"
        slides.append(
            SlidePlan(
                title=section,
                bullets=[
                    f"{purpose} for {request.topic}",
                    f"Make it relevant for {request.audience}",
                    "Keep the message clear, specific, and actionable",
                ],
                speaker_notes=f"Present this in a {request.tone} tone. Add one short example before moving on.",
                visual_hint="Use a clean supporting visual or simple diagram",
            )
        )

    return DeckPlan(
        title=request.topic,
        subtitle=f"A {request.tone} presentation for {request.audience}",
        slides=slides,
    )


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("AI response did not contain a JSON object")
    return text[start : end + 1]


def generate_deck_plan(request: GenerateDeckRequest) -> DeckPlan:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return normalize_deck(build_demo_deck(request), request)

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = {
        "topic": request.topic,
        "slide_count": request.slide_count,
        "audience": request.audience,
        "tone": request.tone,
        "theme": request.theme,
        "language": request.language,
        "include_speaker_notes": request.include_speaker_notes,
        "extra_instructions": request.extra_instructions,
    }

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You create excellent presentation outlines. Return only JSON with keys "
                    "title, subtitle, and slides. slides must be an array with exactly the "
                    "requested count. Each slide must include title, 3-5 concise bullets, "
                    "speaker_notes, and visual_hint. Avoid generic filler. Make the deck useful, "
                    "structured, and ready for PowerPoint."
                ),
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )

    content = response.choices[0].message.content or "{}"
    try:
        deck = DeckPlan.model_validate_json(content)
    except (ValueError, JSONDecodeError):
        deck = DeckPlan.model_validate_json(_extract_json_object(content))
    return normalize_deck(deck, request)
