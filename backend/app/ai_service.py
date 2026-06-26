import json
import os
import re
from json import JSONDecodeError

from openai import OpenAI

from .models import DeckPlan, GenerateDeckRequest, SlidePlan

ALLOWED_LAYOUTS = {"bullets", "two_column", "timeline", "metrics", "quote", "closing"}

DECK_BLUEPRINTS = {
    "business": [
        ("Executive Overview", "Frame the decision, opportunity, and expected outcome", "quote"),
        ("Market Context", "Explain the external situation and why timing matters", "bullets"),
        ("Strategic Priorities", "Compare the most important priorities and trade-offs", "two_column"),
        ("Expected Impact", "Show business, operational, or financial impact", "metrics"),
        ("Implementation Roadmap", "Break the plan into practical phases", "timeline"),
        ("Risks and Mitigation", "Pair major risks with practical controls", "two_column"),
        ("Success Metrics", "Define how progress and quality will be measured", "metrics"),
        ("Next Steps", "Close with decisions, owners, and immediate actions", "closing"),
    ],
    "startup_pitch": [
        ("Problem", "Make the pain clear, specific, and urgent", "quote"),
        ("Solution", "Explain the product and the core value proposition", "bullets"),
        ("Market Opportunity", "Show audience, market size, and timing", "metrics"),
        ("Product Experience", "Describe the workflow and key differentiators", "two_column"),
        ("Business Model", "Explain revenue model and pricing logic", "metrics"),
        ("Go-to-Market", "Show acquisition channels and launch motion", "timeline"),
        ("Traction", "Summarize proof, adoption, pilots, or signals", "metrics"),
        ("The Ask", "Close with funding, partnership, or next-step request", "closing"),
    ],
    "education": [
        ("Learning Goals", "State what learners should understand by the end", "bullets"),
        ("Concept Overview", "Define the topic in simple language", "quote"),
        ("Why It Matters", "Connect the concept to practical life or work", "bullets"),
        ("Key Ideas", "Split the topic into memorable parts", "two_column"),
        ("Worked Example", "Walk through an example step by step", "timeline"),
        ("Common Mistakes", "Compare misunderstandings with correct ideas", "two_column"),
        ("Quick Check", "Prompt reflection, activity, or discussion", "bullets"),
        ("Takeaways", "Summarize the lesson and next practice step", "closing"),
    ],
    "sales": [
        ("Customer Problem", "Show the buyer pain and business cost", "quote"),
        ("Recommended Solution", "Connect the solution to buyer needs", "bullets"),
        ("Value Drivers", "Highlight measurable benefits", "metrics"),
        ("Proof Points", "Show evidence, case studies, or credibility", "two_column"),
        ("Rollout Plan", "Explain how adoption will happen", "timeline"),
        ("Commercial Fit", "Frame package, pricing, or ROI logic", "metrics"),
        ("Objection Handling", "Answer likely concerns directly", "two_column"),
        ("Next Step", "Close with a clear call to action", "closing"),
    ],
    "research": [
        ("Research Question", "Define the central question and scope", "quote"),
        ("Background", "Summarize context and prior knowledge", "bullets"),
        ("Methodology", "Describe the method or process", "timeline"),
        ("Key Findings", "Present the most important results", "metrics"),
        ("Analysis", "Explain what the findings mean", "two_column"),
        ("Limitations", "Clarify uncertainty and boundaries", "bullets"),
        ("Recommendations", "Turn findings into practical actions", "two_column"),
        ("Conclusion", "Close with the strongest implication", "closing"),
    ],
    "general": [
        ("Overview", "Set the context and define the topic", "quote"),
        ("Why It Matters", "Explain urgency, value, and relevance", "bullets"),
        ("Current Landscape", "Show the present state or market reality", "two_column"),
        ("Key Opportunities", "Highlight practical benefits", "metrics"),
        ("Challenges", "Explain risks, blockers, and trade-offs", "two_column"),
        ("Action Plan", "Recommend practical steps", "timeline"),
        ("Success Metrics", "Show how progress should be measured", "metrics"),
        ("Conclusion", "Close with a memorable takeaway", "closing"),
    ],
}


def _blueprint_for(deck_type: str):
    return DECK_BLUEPRINTS.get(deck_type, DECK_BLUEPRINTS["general"])


def _clean_bullets(bullets: list[str]) -> list[str]:
    cleaned = []
    for bullet in bullets:
        text = re.sub(r"\s+", " ", str(bullet)).strip(" -•\t")
        if text:
            cleaned.append(text[:180])
    return cleaned[:6]


def _clean_layout(layout: str, fallback: str) -> str:
    layout = str(layout or "").strip().lower()
    return layout if layout in ALLOWED_LAYOUTS else fallback


def _fallback_slide(request: GenerateDeckRequest, index: int) -> SlidePlan:
    blueprint = _blueprint_for(request.deck_type)
    section, purpose, layout = blueprint[index % len(blueprint)]
    if index == request.slide_count - 1:
        section, purpose, layout = blueprint[-1]
    return SlidePlan(
        title=section,
        bullets=[
            f"{purpose} for {request.topic}",
            f"Make it relevant for {request.audience}",
            "Keep the message clear, specific, and actionable",
        ],
        speaker_notes=f"Present this in a {request.tone} tone. Add one short example before moving on.",
        visual_hint="Use a clean supporting visual, diagram, metric, or comparison",
        layout=layout,
    )


def normalize_deck(deck: DeckPlan, request: GenerateDeckRequest) -> DeckPlan:
    blueprint = _blueprint_for(request.deck_type)
    slides = []
    for index, slide in enumerate(deck.slides[: request.slide_count]):
        _, _, fallback_layout = blueprint[index % len(blueprint)]
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
                layout=_clean_layout(slide.layout, fallback_layout),
            )
        )

    while len(slides) < request.slide_count:
        slides.append(_fallback_slide(request, len(slides)))

    if slides:
        slides[-1].layout = "closing"

    return DeckPlan(
        title=(deck.title.strip() or request.topic)[:120],
        subtitle=(deck.subtitle.strip() or f"A {request.deck_type.replace('_', ' ')} deck for {request.audience}")[:180],
        slides=slides[: request.slide_count],
    )


def build_demo_deck(request: GenerateDeckRequest) -> DeckPlan:
    slides = [_fallback_slide(request, index) for index in range(request.slide_count)]
    return DeckPlan(
        title=request.topic,
        subtitle=f"A {request.deck_type.replace('_', ' ')} presentation for {request.audience}",
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
        "deck_type": request.deck_type,
        "language": request.language,
        "include_speaker_notes": request.include_speaker_notes,
        "extra_instructions": request.extra_instructions,
        "allowed_layouts": sorted(ALLOWED_LAYOUTS),
        "recommended_structure": _blueprint_for(request.deck_type),
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
                    "speaker_notes, visual_hint, and layout. layout must be one of: "
                    "bullets, two_column, timeline, metrics, quote, closing. Avoid generic filler. "
                    "Follow the deck type and make the deck ready for PowerPoint."
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