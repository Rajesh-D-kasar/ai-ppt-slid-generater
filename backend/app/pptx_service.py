from io import BytesIO

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from .models import DeckPlan


THEMES = {
    "modern": {
        "background": RGBColor(247, 250, 252),
        "primary": RGBColor(20, 83, 136),
        "accent": RGBColor(17, 145, 110),
        "text": RGBColor(24, 32, 43),
    },
    "dark": {
        "background": RGBColor(17, 24, 39),
        "primary": RGBColor(96, 165, 250),
        "accent": RGBColor(45, 212, 191),
        "text": RGBColor(248, 250, 252),
    },
    "warm": {
        "background": RGBColor(255, 251, 235),
        "primary": RGBColor(154, 52, 18),
        "accent": RGBColor(5, 150, 105),
        "text": RGBColor(41, 37, 36),
    },
}


def _set_background(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_footer(slide, theme: dict, slide_number: int) -> None:
    box = slide.shapes.add_textbox(Inches(0.6), Inches(6.85), Inches(12.1), Inches(0.25))
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text = f"AI PPT Slide Generator  |  {slide_number}"
    paragraph.alignment = PP_ALIGN.RIGHT
    run = paragraph.runs[0]
    run.font.size = Pt(9)
    run.font.color.rgb = theme["primary"]


def build_pptx(deck: DeckPlan, theme_name: str = "modern") -> BytesIO:
    theme = THEMES.get(theme_name.lower(), THEMES["modern"])
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    title_slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _set_background(title_slide, theme["background"])

    title_box = title_slide.shapes.add_textbox(Inches(0.75), Inches(1.55), Inches(11.8), Inches(1.3))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_run = title_frame.paragraphs[0].add_run()
    title_run.text = deck.title
    title_run.font.size = Pt(44)
    title_run.font.bold = True
    title_run.font.color.rgb = theme["primary"]

    subtitle_box = title_slide.shapes.add_textbox(Inches(0.8), Inches(3.05), Inches(10.8), Inches(0.8))
    subtitle_run = subtitle_box.text_frame.paragraphs[0].add_run()
    subtitle_run.text = deck.subtitle
    subtitle_run.font.size = Pt(20)
    subtitle_run.font.color.rgb = theme["text"]

    accent = title_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.25), Inches(2.6), Inches(0.08))
    accent.fill.solid()
    accent.fill.fore_color.rgb = theme["accent"]
    accent.line.color.rgb = theme["accent"]

    for index, slide_plan in enumerate(deck.slides, start=2):
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        _set_background(slide, theme["background"])

        title = slide.shapes.add_textbox(Inches(0.65), Inches(0.55), Inches(12), Inches(0.75))
        title_run = title.text_frame.paragraphs[0].add_run()
        title_run.text = slide_plan.title
        title_run.font.size = Pt(30)
        title_run.font.bold = True
        title_run.font.color.rgb = theme["primary"]

        content = slide.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.25), Inches(4.75))
        frame = content.text_frame
        frame.clear()
        frame.word_wrap = True

        for bullet_index, bullet in enumerate(slide_plan.bullets[:6]):
            paragraph = frame.paragraphs[0] if bullet_index == 0 else frame.add_paragraph()
            paragraph.text = bullet
            paragraph.level = 0
            paragraph.space_after = Pt(12)
            paragraph.font.size = Pt(22)
            paragraph.font.color.rgb = theme["text"]

        notes = slide.notes_slide.notes_text_frame
        notes.text = slide_plan.speaker_notes
        _add_footer(slide, theme, index - 1)

    output = BytesIO()
    presentation.save(output)
    output.seek(0)
    return output
