"""Miolo 5,5 x 8,5 com índice paginado; capa impressa continua decisão gráfica."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents

from .markdown import blocks, inline
from .project import Project


PAGE_SIZE = (5.5 * inch, 8.5 * inch)


def _font_family() -> tuple[str, str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/georgia.ttf"), Path("C:/Windows/Fonts/georgiab.ttf"), Path("C:/Windows/Fonts/georgiai.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf")),
    ]
    for files in candidates:
        if all(file.is_file() for file in files):
            for name, path in zip(("Editoria", "Editoria-Bold", "Editoria-Italic"), files):
                if name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(name, str(path)))
            pdfmetrics.registerFontFamily("Editoria", normal="Editoria", bold="Editoria-Bold", italic="Editoria-Italic", boldItalic="Editoria-Bold")
            return "Editoria", "Editoria-Bold", "Editoria-Italic"
    return "Times-Roman", "Times-Bold", "Times-Italic"


class _BookDocument(BaseDocTemplate):
    def __init__(self, filename: str, *, title: str, author: str):
        super().__init__(filename, pagesize=PAGE_SIZE, leftMargin=.7 * inch, rightMargin=.65 * inch, topMargin=.65 * inch, bottomMargin=.7 * inch, title=title, author=author)
        self.book_title = title
        self.book_author = author
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="text", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="book", frames=[frame], onPage=self._page_marks))

    def _page_marks(self, canvas, doc) -> None:
        if doc.page <= 1:
            return
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d1cbc0"))
        canvas.setLineWidth(.35)
        canvas.line(.7 * inch, PAGE_SIZE[1] - .44 * inch, PAGE_SIZE[0] - .65 * inch, PAGE_SIZE[1] - .44 * inch)
        canvas.setFont("Times-Roman", 7.5)
        canvas.setFillColor(colors.HexColor("#77736d"))
        canvas.drawCentredString(PAGE_SIZE[0] / 2, PAGE_SIZE[1] - .36 * inch, self.book_author if doc.page % 2 else self.book_title[:42])
        canvas.drawCentredString(PAGE_SIZE[0] / 2, .4 * inch, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph) and flowable.style.name == "ChapterTitle":
            label = flowable.getPlainText()
            self.notify("TOCEntry", (0, label, self.page))


def _styles() -> dict[str, ParagraphStyle]:
    normal, bold, italic = _font_family()
    ink = colors.HexColor("#26231e")
    return {
        "body": ParagraphStyle("Body", fontName=normal, fontSize=10.5, leading=15.3, textColor=ink, alignment=TA_JUSTIFY, firstLineIndent=12, spaceAfter=5),
        "back_body": ParagraphStyle("BackBody", fontName=normal, fontSize=10.5, leading=15.3, textColor=ink, alignment=TA_LEFT, firstLineIndent=0, spaceAfter=10),
        "dialogue": ParagraphStyle("Dialogue", fontName=normal, fontSize=10.5, leading=15.3, textColor=ink, alignment=TA_LEFT, spaceAfter=5),
        "title": ParagraphStyle("Title", fontName=bold, fontSize=24, leading=29, alignment=TA_CENTER, textColor=colors.HexColor("#20332c"), spaceAfter=18),
        "subtitle": ParagraphStyle("Subtitle", fontName=italic, fontSize=12, leading=17, alignment=TA_CENTER, textColor=ink, spaceAfter=20),
        "author": ParagraphStyle("Author", fontName=normal, fontSize=12, leading=17, alignment=TA_CENTER, textColor=ink),
        "chapter_label": ParagraphStyle("ChapterLabel", fontName=bold, fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#a44d39"), spaceAfter=8),
        "chapter_title": ParagraphStyle("ChapterTitle", fontName=bold, fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#20332c"), spaceAfter=18),
        "section": ParagraphStyle("SectionTitle", fontName=bold, fontSize=14, leading=18, textColor=colors.HexColor("#20332c"), spaceBefore=12, spaceAfter=8),
        "quote": ParagraphStyle("Quote", fontName=italic, fontSize=10.3, leading=15, leftIndent=20, rightIndent=18, spaceAfter=9),
        "scene": ParagraphStyle("Scene", fontName=normal, fontSize=10, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#a44d39"), spaceBefore=12, spaceAfter=12),
        "toc": ParagraphStyle("TOCEntry", fontName=normal, fontSize=9.8, leading=14, leftIndent=0, firstLineIndent=0, spaceAfter=5),
    }


def _paragraph_markup(text: str) -> str:
    return inline(text).replace("<strong>", "<b>").replace("</strong>", "</b>").replace("<em>", "<i>").replace("</em>", "</i>")


def _flowables(source: str, styles: dict[str, ParagraphStyle]) -> list:
    result = []
    for block in blocks(source):
        if block.kind == "scene":
            result.append(Paragraph("• • •", styles["scene"]))
        elif block.kind in {"h1", "h2", "h3"}:
            result.append(Paragraph(_paragraph_markup(block.text), styles["section"]))
        elif block.kind == "quote":
            result.append(Paragraph(_paragraph_markup(block.text), styles["quote"]))
        elif block.kind in {"bullet", "number"}:
            result.append(Paragraph("• " + _paragraph_markup(block.text), styles["dialogue"]))
        else:
            style = styles["dialogue"] if block.text.startswith("—") or block.text.startswith('*"') else styles["body"]
            result.append(Paragraph(_paragraph_markup(block.text), style))
    return result


def _art_flowable(path: Path, available_width: float) -> RLImage:
    with Image.open(path) as image:
        width, height = image.size
    scale = min(available_width / width, (3.25 * inch) / height)
    illustration = RLImage(str(path), width=width * scale, height=height * scale)
    illustration.hAlign = "CENTER"
    return illustration


def build_pdf(project: Project, destination: Path) -> tuple[Path, int]:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "miolo-5.5x8.5.pdf"
    doc = _BookDocument(str(target), title=project.title, author=project.author)
    styles = _styles()
    story: list = [Spacer(1, 1.8 * inch), Paragraph(_paragraph_markup(project.title), styles["title"])]
    subtitle = str(project.config.get("subtitulo", "")).strip()
    if subtitle:
        story.append(Paragraph(_paragraph_markup(subtitle), styles["subtitle"]))
    story.extend([Spacer(1, .6 * inch), Paragraph(_paragraph_markup(project.author), styles["author"]), PageBreak()])

    story.append(Paragraph("Direitos autorais", styles["section"]))
    story.append(Paragraph(f"© {project.config['ano_publicacao']} {_paragraph_markup(project.author)}. Todos os direitos reservados.", styles["dialogue"]))
    story.append(Paragraph("Esta é uma obra de ficção. Personagens e acontecimentos foram criados para esta narrativa.", styles["dialogue"]))
    story.append(PageBreak())

    opening = project.source("ABERTURA.md")
    if opening.strip():
        story.extend(_flowables(opening, styles))
        story.append(PageBreak())

    story.append(Paragraph("Índice", styles["title"]))
    toc = TableOfContents()
    toc.levelStyles = [styles["toc"]]
    story.extend([toc, PageBreak()])

    for chapter in project.chapters:
        story.extend([Paragraph(f"CAPÍTULO {chapter.number}", styles["chapter_label"]), Paragraph(_paragraph_markup(chapter.title), styles["chapter_title"])])
        art = project.art_for(chapter.number)
        if art:
            source, _ = art
            story.extend([_art_flowable(source, doc.width), Spacer(1, 12)])
        story.extend(_flowables(chapter.body, styles))
        story.append(PageBreak())

    back_styles = {**styles, "body": styles["back_body"]}
    back_present = False
    for name in ("AGRADECIMENTOS.md", "SOBRE_AUTORIA.md"):
        source = project.source(name)
        if source.strip():
            story.extend(_flowables(source, back_styles))
            back_present = True
            if name == "AGRADECIMENTOS.md" and project.source("SOBRE_AUTORIA.md").strip():
                story.append(Spacer(1, 12))
    last_word = project.source("ULTIMA_PALAVRA.md")
    if last_word.strip():
        if back_present:
            story.append(PageBreak())
        story.extend(_flowables(last_word, back_styles))
    if isinstance(story[-1], PageBreak):
        story.pop()
    doc.multiBuild(story)
    pages = len(PdfReader(str(target)).pages)
    return target, pages
