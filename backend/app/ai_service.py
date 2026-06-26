import json
import os

from openai import OpenAI

from .models import DeckPlan, GenerateDeckRequest, SlidePlan


def build_demo_deck(request: GenerateDeckRequest) -> DeckPlan:
    slides = [
        SlidePlan(
            title="Overview",
            bullets=[
                f"What {request.topic} means",
                "Why it matters now",
                f"How it affects {request.audience}",
            ],
            speaker_notes="Start with a simple definition and a practical example.",
        ),
        SlidePlan(
            title="Key Benefits",
            bullets=[
                "Improves speed and consistency",
                "Helps people make better decisions",
                "Creates new opportunities for innovation",
            ],
            speaker_notes="Connect each benefit to a real-world use case.",
        ),
        SlidePlan(
            title="Challenges",
            bullets=[
                "Quality depends on good inputs",
                "Privacy and trust need careful handling",
                "Teams need training and clear processes",
            ],
            speaker_notes="Keep this balanced and avoid making the topic sound risk-free.",
        ),
    ]

    extra_needed = max(0, request.slide_count - len(slides) - 1)
    for index in range(extra_needed):
        slides.append(
            SlidePlan(
                title=f"Important Point {index + 1}",
                bullets=[
                    f"Core idea related to {request.topic}",
                    "Example or supporting evidence",
                    "Practical takeaway for the audience",
                ],
                speaker_notes="Add detail here when presenting this section.",
            )
        )

    slides.append(
        SlidePlan(
            title="Conclusion",
            bullets=[
                f"{request.topic} is most useful when applied with a clear goal",
                "Start small, measure results, and improve",
                "Focus on outcomes, not only tools",
            ],
            speaker_notes="End with a crisp recommendation or next step.",
        )
    )

    return DeckPlan(
        title=request.topic,
        subtitle=f"A {request.tone} presentation for {request.audience}",
        slides=slides[: request.slide_count],
    )


def generate_deck_plan(request: GenerateDeckRequest) -> DeckPlan:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return build_demo_deck(request)

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = {
        "topic": request.topic,
        "slide_count": request.slide_count,
        "audience": request.audience,
        "tone": request.tone,
        "theme": request.theme,
    }

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Create a PowerPoint deck plan as JSON with keys title, subtitle, "
                    "and slides. slides must be an array of objects with title, bullets, "
                    "and speaker_notes. Keep bullets concise and presentation-ready."
                ),
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )

    content = response.choices[0].message.content or "{}"
    return DeckPlan.model_validate_json(content)
