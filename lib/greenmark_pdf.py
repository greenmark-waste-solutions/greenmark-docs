"""
Greenmark Branded PDF Library

Shared brand system for all ADR, SOP, and report PDFs.
Import from here instead of duplicating flowables in every generator.

Usage:
    from lib.greenmark_pdf import *
    # or: import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from lib.greenmark_pdf import *
"""

from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.flowables import Flowable

# ── Brand Colors ─────────────────────────────────────────────────────
BRAND_GREEN = HexColor("#193B2D")
BRAND_LIGHT = HexColor("#E8F0EC")
ACCENT_GREEN = HexColor("#2D6B4A")
MUTED = HexColor("#6B7B73")
DARK = HexColor("#1A1A1A")
WHITE = white

RED = HexColor("#C0392B")
RED_BG = HexColor("#FDECEC")
RED_BORDER = HexColor("#E74C3C")
AMBER = HexColor("#92700A")
AMBER_BG = HexColor("#FDF8EC")
AMBER_BORDER = HexColor("#D4A843")
BLUE = HexColor("#2E86C1")

CHART_COLORS = [
    HexColor("#2D6B4A"), HexColor("#3A9D72"), HexColor("#7BC8A4"),
    HexColor("#D4A843"), HexColor("#2E86C1"), HexColor("#E67E22"),
    HexColor("#C0392B"), HexColor("#8E44AD"),
]

# ── Paths ────────────────────────────────────────────────────────────
DOCS_ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = DOCS_ROOT / "brand"
LOGO_PATH = str(BRAND_DIR / "greenmark-full-white.png")
COCKPIT_ROOT = DOCS_ROOT  # backward compat alias

# ── Page Layout ──────────────────────────────────────────────────────
W, H = letter
MARGIN = 0.5 * inch
USABLE = W - 2 * MARGIN
CONTENT_W = USABLE * 0.78
SCORE_W = USABLE * 0.22

# ── Styles ───────────────────────────────────────────────────────────
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12, textColor=DARK)
BODY_BOLD = ParagraphStyle("body_bold", parent=BODY, fontName="Helvetica-Bold")
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14, leading=18,
                     textColor=BRAND_GREEN, spaceAfter=4)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=14,
                     textColor=ACCENT_GREEN, spaceBefore=10, spaceAfter=4)
H3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                     textColor=BRAND_GREEN, spaceBefore=6, spaceAfter=2)
META = ParagraphStyle("meta", fontName="Helvetica", fontSize=8, leading=10, textColor=MUTED)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8, leading=10, textColor=DARK)
CELL_BOLD = ParagraphStyle("cell_bold", parent=CELL, fontName="Helvetica-Bold")
CELL_CENTER = ParagraphStyle("cell_center", parent=CELL, alignment=TA_CENTER)
MONO = ParagraphStyle("mono", fontName="Courier", fontSize=7.5, leading=10, textColor=ACCENT_GREEN)
RED_TEXT = ParagraphStyle("red_text", parent=CELL, textColor=RED, fontName="Helvetica-Bold")
GREEN_TEXT = ParagraphStyle("green_text", parent=CELL, textColor=ACCENT_GREEN, fontName="Helvetica-Bold")


# ── Flowables ────────────────────────────────────────────────────────

class BrandHeader(Flowable):
    """Dark green rounded rect with Greenmark logo, title, and subtitle."""

    def __init__(self, width, title, subtitle):
        super().__init__()
        self.width = width
        self.height = 0.95 * inch
        self.title = title
        self.subtitle = subtitle

    def draw(self):
        c = self.canv
        c.setFillColor(BRAND_GREEN)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        try:
            c.drawImage(LOGO_PATH, 12, self.height - 32, width=1.35 * inch,
                        height=0.28 * inch, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(12, 14, self.title)
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#A8C4B4"))
        c.drawRightString(self.width - 12, 14, self.subtitle)


class AccentBox(Flowable):
    """Alert/callout box with left accent stripe. Auto word-wraps."""

    def __init__(self, width, text, bg=None, border=None, text_color=None,
                 bold=True, size=9):
        super().__init__()
        self.width = width
        _bg = bg or BRAND_LIGHT
        _border = border or ACCENT_GREEN
        _tc = text_color or BRAND_GREEN
        sty = ParagraphStyle("ab", fontName="Helvetica-Bold" if bold else "Helvetica",
                             fontSize=size, leading=size + 3, textColor=_tc)
        self._para = Paragraph(text, sty)
        pw = width - 20
        _, self._ph = self._para.wrap(pw, 999)
        self.height = self._ph + 14
        self.bg = _bg
        self.border = _border

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        c.setFillColor(self.border)
        c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        self._para.drawOn(c, 14, (self.height - self._ph) / 2)


class StatCard(Flowable):
    """Row of stat cards — light green boxes with accent bar on top."""

    def __init__(self, width, stats):
        super().__init__()
        self.width = width
        self.height = 0.7 * inch
        self.stats = stats

    def draw(self):
        c = self.canv
        n = len(self.stats)
        gap = 6
        cw = (self.width - gap * (n - 1)) / n
        for i, (value, label) in enumerate(self.stats):
            x = i * (cw + gap)
            c.setFillColor(BRAND_LIGHT)
            c.roundRect(x, 0, cw, self.height, 4, fill=1, stroke=0)
            c.setFillColor(ACCENT_GREEN)
            c.rect(x, self.height - 4, cw, 4, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(BRAND_GREEN)
            c.drawCentredString(x + cw / 2, 18, str(value))
            c.setFont("Helvetica", 7)
            c.setFillColor(MUTED)
            c.drawCentredString(x + cw / 2, 6, label)


# ── Table Builders ───────────────────────────────────────────────────

def tbl(header, rows, widths):
    """Standard branded table — dark green header, alternating rows."""
    data = [header] + rows
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D0D0D0")),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), BRAND_LIGHT))
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle(style))
    return t


def severity_tbl(header, rows, widths):
    """Branded table with color-coded severity column (index 1)."""
    data = [header] + rows
    sev_colors = {
        "CRITICAL": RED,
        "HIGH": HexColor("#E67E22"),
        "MEDIUM": AMBER,
        "LOW": MUTED,
    }
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D0D0D0")),
    ]
    for i, row in enumerate(rows, 1):
        sev = str(row[1]).upper() if len(row) > 1 else ""
        if sev in sev_colors:
            style.append(("TEXTCOLOR", (1, i), (1, i), sev_colors[sev]))
            style.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), BRAND_LIGHT))
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle(style))
    return t


# ── Helpers ──────────────────────────────────────────────────────────

def hr():
    """Thin gray horizontal rule."""
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#D0D0D0"),
                      spaceBefore=6, spaceAfter=6)


def make_footer(doc_title):
    """Return a footer function for the given document title."""
    def footer_func(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, 0.35 * inch,
                          f"Greenmark Waste Solutions  |  {doc_title}  |  "
                          f"{datetime.now().strftime('%Y-%m-%d')}")
        canvas.drawRightString(W - MARGIN, 0.35 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return footer_func


def build_doc(output_path, doc_title, build_fn):
    """Create a branded PDF. build_fn(story, p) adds content to the story list."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=0.6 * inch)
    story = []
    p = lambda t, s=BODY: Paragraph(t, s)
    build_fn(story, p)
    footer = make_footer(doc_title)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {output_path}")
