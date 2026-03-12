#!/usr/bin/env python3
"""SOP-003 — Excel Export Standards"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "sops" / "SOP-003-excel-export-standards.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "SOP-003", "Excel Export Standards"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Effective:</b> 2026-03-11  |  <b>Owner:</b> Daniel Shanklin  |  "
                   "<b>Applies to:</b> Any tool or script that generates Excel workbooks for Greenmark",
                   META))
    story.append(Spacer(1, 6))

    # BLUF
    story.append(p("BLUF", H2))
    story.append(p(
        "Every Excel workbook produced by Cerebro or any Greenmark data tool must have a branded "
        "cover sheet, be pre-formatted for letter landscape printing, use real numeric values (not "
        "formatted strings), and include CONFIDENTIAL markings. These standards ensure workbooks are "
        "print-ready, AI-transparent, and professionally branded."))
    story.append(Spacer(1, 8))

    # Cover sheet
    story.append(p("Cover Sheet (Required)", H2))
    story.append(tbl(["Element", "Requirement"], [
        [p("<b>Product name</b>", CELL), p("Large, bold, brand primary (#2D4A3E)", CELL)],
        [p("<b>Report title</b>", CELL), p("What this workbook contains", CELL)],
        [p("<b>Entity</b>", CELL), p("Who this data belongs to (RLS-filtered)", CELL)],
        [p("<b>Date</b>", CELL), p("=NOW() or datetime cell with Excel format — never hardcoded string", CELL)],
        [p("<b>CONFIDENTIAL</b>", CELL), p("Red, bold, prominently placed", CELL)],
        [p("<b>Gridlines</b>", CELL), p("Hidden", CELL)],
        [p("<b>Print</b>", CELL), p("Fit to 1 page width AND height (exactly 1 printed page)", CELL)],
    ], [USABLE * 0.22, USABLE * 0.78]))
    story.append(Spacer(1, 8))

    # Print setup
    story.append(p("Print Setup (Every Sheet)", H2))
    story.append(AccentBox(USABLE,
                           "Assume every sheet will be printed, stapled, and handed to someone in a meeting."))
    story.append(Spacer(1, 4))
    story.append(tbl(["Setting", "Value"], [
        [p("<b>Orientation</b>", CELL), p("Landscape", CELL)],
        [p("<b>Paper</b>", CELL), p("Letter (8.5 x 11)", CELL)],
        [p("<b>Fit to</b>", CELL), p("1 page wide, unlimited pages tall", CELL)],
        [p("<b>Margins</b>", CELL), p('0.5" left/right, 0.6" top, 0.75" bottom', CELL)],
    ], [USABLE * 0.22, USABLE * 0.78]))
    story.append(Spacer(1, 4))

    story.append(p("Header / Footer", H3))
    story.append(tbl(["Position", "Header (top)", "Footer (bottom)"], [
        [p("<b>Left</b>", CELL), p("&amp;F (filename)", MONO), p("CONFIDENTIAL — {entity}", CELL)],
        [p("<b>Center</b>", CELL), p("Tab name", CELL), p("Printed &amp;D &amp;T", MONO)],
        [p("<b>Right</b>", CELL), p("(empty)", CELL), p("Page &amp;P of &amp;N", MONO)],
    ], [USABLE * 0.15, USABLE * 0.42, USABLE * 0.43]))
    story.append(Spacer(1, 4))
    story.append(p("&amp;F, &amp;D, &amp;T, &amp;P, &amp;N are Excel print codes — resolved at print time, "
                   "not export time. The printed date is always when someone actually printed it.", CELL))
    story.append(hr())

    # AI transparency
    story.append(p("Transparency to AI", H2))
    story.append(p("<b>Every number must be a real number, not a formatted string.</b>", CELL_BOLD))
    story.append(Spacer(1, 4))
    story.append(tbl(["Wrong", "Right"], [
        [p('"87.3%" (string)', RED_TEXT), p("0.873 with format 0.0%", GREEN_TEXT)],
        [p('"$12,500.00" (string)', RED_TEXT), p("12500 with format $#,##0.00", GREEN_TEXT)],
        [p('"2026-03-11 14:30" (string)', RED_TEXT), p("datetime object with YYYY-MM-DD HH:MM", GREEN_TEXT)],
    ], [USABLE * 0.5, USABLE * 0.5]))
    story.append(Spacer(1, 4))
    story.append(p("Where formulas are possible, use them. The formula is the audit trail.", CELL))
    story.append(Spacer(1, 8))

    # Brand colors
    story.append(p("Brand Colors", H2))
    story.append(tbl(["Token", "Hex", "Usage"], [
        [p("Primary", CELL), p("#2D4A3E", MONO), p("Titles, headers, good status", CELL)],
        [p("Accent", CELL), p("#C9A84C", MONO), p("Gold layer, planning tabs, needs work", CELL)],
        [p("Surface", CELL), p("#F5F0E8", MONO), p("Input fills, cream background", CELL)],
        [p("Error Red", CELL), p("#A4262C", MONO), p("Critical, failed, below standard", CELL)],
    ], [USABLE * 0.15, USABLE * 0.15, USABLE * 0.70]))
    story.append(Spacer(1, 4))

    story.append(p("Conditional Formatting (Luke's Pattern)", H3))
    story.append(tbl(["Condition", "Font Color", "Fill Color"], [
        [p("Positive / On Target", GREEN_TEXT), p("#006100", MONO), p("#E2EFDA", MONO)],
        [p("Negative / Below Standard", RED_TEXT), p("#9C0006", MONO), p("#FCE4EC", MONO)],
    ], [USABLE * 0.35, USABLE * 0.32, USABLE * 0.33]))
    story.append(Spacer(1, 8))

    # Typography
    story.append(p("Typography Hierarchy", H2))
    story.append(tbl(["Level", "Size", "Bold", "Italic", "Color"], [
        [p("Page title", CELL), p("16pt", CELL), p("Yes", CELL), p("No", CELL), p("Primary", CELL)],
        [p("Section header", CELL), p("13pt", CELL), p("Yes", CELL), p("No", CELL), p("Primary", CELL)],
        [p("Subtitle", CELL), p("9pt", CELL), p("No", CELL), p("Yes", CELL), p("#666666", MONO)],
        [p("Table header", CELL), p("11pt", CELL), p("Yes", CELL), p("No", CELL), p("White on fill", CELL)],
        [p("Body", CELL), p("11pt", CELL), p("No", CELL), p("No", CELL), p("Default", CELL)],
    ], [USABLE * 0.2, USABLE * 0.12, USABLE * 0.12, USABLE * 0.12, USABLE * 0.44]))
    story.append(Spacer(1, 8))

    # Layout rules
    story.append(p("Layout Rules", H2))
    story.append(tbl(["Rule", "Detail"], [
        [p("<b>Section spacing</b>", CELL), p("Exactly 1 blank row between sections", CELL)],
        [p("<b>Zebra striping</b>", CELL), p("#F2F2F2 on raw data tabs only (not analysis tabs)", CELL)],
        [p("<b>Callout boxes</b>", CELL), p("Yellow #FFF2CC on planning/input tabs", CELL)],
        [p("<b>No merged cells</b>", CELL), p("On data tabs — breaks filtering. Cover merges OK.", CELL)],
        [p("<b>No color-only meaning</b>", CELL), p("Every colored cell also has text (accessibility)", CELL)],
    ], [USABLE * 0.22, USABLE * 0.78]))
    story.append(Spacer(1, 8))

    # Tab structure
    story.append(p("Tab Structure", H2))
    story.append(tbl(["#", "Tab", "Purpose"], [
        [p("1", CELL), p("<b>Cover</b>", CELL), p("Branded, CONFIDENTIAL, 1-page print", CELL)],
        [p("2", CELL), p("<b>Summary</b>", CELL), p("Overview, how-to-read guide", CELL)],
        [p("3", CELL), p("<b>Tab Index</b>", CELL), p("Every tab with descriptions", CELL)],
        [p("4", CELL), p("<b>Diagnostics</b>", CELL), p("Connection health, table status", CELL)],
        [p("5", CELL), p("<b>Planning tabs</b>", CELL), p("Stakeholder input (callouts, examples, cream fills)", CELL)],
        [p("6", CELL), p("<b>Data Quality</b>", CELL), p("Metrics with goals and benchmarks", CELL)],
        [p("7", CELL), p("<b>Data tabs</b>", CELL), p("Bronze, Silver, Gold (layer-colored headers)", CELL)],
        [p("8", CELL), p("<b>Verification</b>", CELL), p("Automated checks, scorecard, verdict", CELL)],
    ], [0.3 * inch, USABLE * 0.2, USABLE - 0.3 * inch - USABLE * 0.2]))
    story.append(hr())

    # Why
    story.append(p("Why This Exists", H2))
    story.append(p(
        "Luke's beartraps backtest report demonstrated professional Excel patterns. We studied it, "
        "compared against our approach, and adopted the best practices while keeping our brand identity "
        "and print requirements. This SOP ensures consistency across all future Excel exports."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "No exceptions. Every Excel workbook follows these standards. "
                           "The cost of print setup is one function call. "
                           "The risk of skipping it is a bad impression when someone inevitably prints it."))


if __name__ == "__main__":
    build_doc(OUTPUT, "SOP-003: Excel Export Standards", content)
