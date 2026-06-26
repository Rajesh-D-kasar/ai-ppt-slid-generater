from io import BytesIO

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

from .models import DeckPlan


THEMES = {
    "modern": {
        "background": RGBColor(247, 250, 252),
        "surface": RGBColor(255, 255, 255),
        "primary": RGBColor(20, 83, 136),
        "accent": RGBColor(17, 145, 110),
        "muted": RGBColor(91, 111, 132),
        "text": RGBColor(24, 32, 43),
    },
    "dark": {
        "background": RGBColor(17, 24, 39),
        "surface": RGBColor(31, 41, 55),
        "primary": RGBColor(96, 165, 250),
        "accent": RGBColor(45, 212, 191),
        "muted": RGBColor(203, 213, 225),
        "text": RGBColor(248, 250, 252),
    },
    "warm": {
        "background": RGBColor(255, 251, 235),
        "surface": RGBColor(255, 255, 255),
        "primary": RGBColor(154, 52, 18),
        "accent": RGBColor(5, 150, 105),
        "muted": RGBColor(120, 113, 108),
        "text": RGBColor(41, 37, 36),
    },
    "minimal": {
        "background": RGBColor(255, 255, 255),
        "surface": RGBColor(248, 250, 252),
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(37, 99, 235),
        "muted": RGBColor(100, 116, 139),
        "text": RGBColor(30, 41, 59),
    },
    "startup": {
        "background": RGBColor(250, 245, 255),
        "surface": RGBColor(255, 255, 255),
        "primary": RGBColor(88, 28, 135),
        "accent": RGBColor(234, 88, 12),
        "muted": RGBColor(87, 83, 78),
        "text": RGBColor(28, 25, 23),
    },
}

SLIDE_W = 13.333
SLIDE_H = 7.5


def _set_background(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _text_box(slide, left, top, width, height, text=""):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    if text:
        frame.text = text
    return shape


def _shape(slide, kind, left, top, width, height, fill, line=None):
    shape = slide.shapes.add_shape(kind, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def _add_run(paragraph, text, size, color, bold=False):
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return run


def _add_footer(slide, theme: dict, slide_number: int, total: int) -> None:
    box = _text_box(slide, 0.65, 6.94, 12.05, 0.25)
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text = f"AI PPT Slide Generator  |  {slide_number}/{total}"
    paragraph.alignment = PP_ALIGN.RIGHT
    paragraph.runs[0].font.size = Pt(8)
    paragraph.runs[0].font.color.rgb = theme["muted"]


def _add_title_slide(presentation, deck: DeckPlan, theme: dict) -> None:
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _set_background(slide, theme["background"])
    _shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, 0.18, SLIDE_H, theme["accent"])
    _shape(slide, MSO_SHAPE.RECTANGLE, 0.72, 4.52, 2.95, 0.08, theme["accent"])

    title = _text_box(slide, 0.75, 1.35, 11.7, 1.55)
    _add_run(title.text_frame.paragraphs[0], deck.title, 44, theme["primary"], True)

    subtitle = _text_box(slide, 0.78, 3.12, 10.9, 0.76)
    _add_run(subtitle.text_frame.paragraphs[0], deck.subtitle, 19, theme["text"])

    label = _text_box(slide, 0.8, 5.72, 4.8, 0.35, "Generated editable PowerPoint deck")
    label.text_frame.paragraphs[0].runs[0].font.size = Pt(10)
    label.text_frame.paragraphs[0].runs[0].font.color.rgb = theme["muted"]


def _add_agenda_slide(presentation, deck: DeckPlan, theme: dict) -> None:
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _set_background(slide, theme["background"])
    _add_header(slide, "Agenda", theme)

    for index, item in enumerate(deck.slides[:8], start=1):
        row = 1.55 + ((index - 1) * 0.58)
        _shape(slide, MSO_SHAPE.OVAL, 0.82, row + 0.03, 0.3, 0.3, theme["accent"])
        num = _text_box(slide, 0.82, row + 0.055, 0.3, 0.16, str(index))
        p = num.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.runs[0].font.size = Pt(7)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = theme["surface"]
        text = _text_box(slide, 1.28, row - 0.01, 10.7, 0.42, item.title)
        text.text_frame.paragraphs[0].runs[0].font.size = Pt(18)
        text.text_frame.paragraphs[0].runs[0].font.color.rgb = theme["text"]


def _add_header(slide, title: str, theme: dict) -> None:
    _shape(slide, MSO_SHAPE.RECTANGLE, 0.65, 1.2, 1.25, 0.06, theme["accent"])
    title_box = _text_box(slide, 0.65, 0.48, 12, 0.62)
    _add_run(title_box.text_frame.paragraphs[0], title, 29, theme["primary"], True)


def _add_content_slide(presentation, title: str, bullets: list[str], notes: str, visual_hint: str, theme: dict, number: int, total: int) -> None:
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _set_background(slide, theme["background"])
    _add_header(slide, title, theme)

    panel = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.72, 1.55, 7.45, 4.88, theme["surface"], theme["surface"])
    panel.shadow.inherit = False

    content = _text_box(slide, 1.05, 1.88, 6.8, 4.25)
    for index, bullet in enumerate(bullets[:5]):
        paragraph = content.text_frame.paragraphs[0] if index == 0 else content.text_frame.add_paragraph()
        paragraph.text = bullet
        paragraph.level = 0
        paragraph.space_after = Pt(10)
        paragraph.font.size = Pt(18 if len(bullet) < 115 else 15)
        paragraph.font.color.rgb = theme["text"]

    visual = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 8.55, 1.55, 3.95, 4.88, theme["primary"], theme["primary"])
    visual.shadow.inherit = False
    hint = _text_box(slide, 8.92, 2.05, 3.2, 1.95, visual_hint or "Supporting visual")
    hint_p = hint.text_frame.paragraphs[0]
    hint_p.alignment = PP_ALIGN.CENTER
    hint_p.runs[0].font.size = Pt(18)
    hint_p.runs[0].font.bold = True
    hint_p.runs[0].font.color.rgb = theme["surface"]
    _shape(slide, MSO_SHAPE.RECTANGLE, 9.62, 4.52, 1.9, 0.08, theme["accent"])

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    _add_footer(slide, theme, number, total)


def build_pptx(deck: DeckPlan, theme_name: str = "modern") -> BytesIO:
    theme = THEMES.get(theme_name.lower(), THEMES["modern"])
    presentation = Presentation()
    presentation.slide_width = Inches(SLIDE_W)
    presentation.slide_height = Inches(SLIDE_H)
    total = len(deck.slides) + 2

    _add_title_slide(presentation, deck, theme)
    _add_agenda_slide(presentation, deck, theme)

    for index, slide_plan in enumerate(deck.slides, start=3):
        _add_content_slide(
            presentation,
            slide_plan.title,
            slide_plan.bullets,
            slide_plan.speaker_notes,
            slide_plan.visual_hint,
            theme,
            index - 1,
            total - 1,
        )

    output = BytesIO()
    presentation.save(output)
    output.seek(0)
    return output

