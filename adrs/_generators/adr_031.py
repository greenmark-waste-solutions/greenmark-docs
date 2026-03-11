#!/usr/bin/env python3
"""ADR-2026-31 — Establish SOP Document Type"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-31-establish-sop-document-type.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-31", "Establish SOP Document Type"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "We're creating SOPs (Standard Operating Procedures) to capture institutional knowledge for "
        "the technology role at Greenmark. SOPs record who to contact for what, how recurring tasks "
        "are performed, and what not to do. Same BLUF + branded PDF format as ADRs."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Create a sops/ directory for Standard Operating Procedures. "
                           "Same standards as ADRs (BLUF + branded PDF). "
                           "SOPs are living documents updated in place."))
    story.append(Spacer(1, 6))

    story.append(p("ADR vs SOP", H2))
    story.append(tbl(["", "ADR", "SOP"], [
        [p("<b>Purpose</b>", CELL), p("Record a decision", CELL), p("Record a procedure", CELL)],
        [p("<b>Audience</b>", CELL), p("Future architects", CELL), p("Current operator", CELL)],
        [p("<b>Tone</b>", CELL), p("'We decided X because Y'", CELL), p("'Do X. Don't do Y.'", CELL)],
        [p("<b>Changes</b>", CELL), p("Superseded by new ADR", CELL), p("Updated in place", CELL)],
        [p("<b>Location</b>", CELL), p("decisions/", MONO), p("sops/", MONO)],
    ], [USABLE * 0.18, USABLE * 0.41, USABLE * 0.41]))
    story.append(hr())

    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Bus factor</b>", CELL),
         p("Critical knowledge is in one person's head. SOPs make it transferable.", CELL)],
        [p("<b>Onboarding</b>", CELL),
         p("New hire reads sops/ and knows how to operate within a day.", CELL)],
        [p("<b>AI agents</b>", CELL),
         p("Claude sessions reference SOPs for procedural guidance.", CELL)],
        [p("<b>Accountability</b>", CELL),
         p("'It's in the SOP' is defensible. Unwritten procedures are unenforceable.", CELL)],
    ], [USABLE * 0.2, USABLE * 0.8]))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-31: Establish SOP Document Type", content)
