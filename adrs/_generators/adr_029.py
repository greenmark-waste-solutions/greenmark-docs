#!/usr/bin/env python3
"""ADR-2026-29 — BLUF Requirement (Superseded by SOP-001)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-29-adr-format-requires-bluf.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-29", "All ADRs Require a BLUF"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Superseded by SOP-001  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin", META))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "SUPERSEDED: This ADR has been absorbed into SOP-001 (Creating ADRs and SOPs). "
                           "The BLUF requirement is now part of the unified document creation procedure.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "Every ADR must open with a BLUF section — a 2-3 sentence summary that gives the reader "
        "the decision, the reason, and the consequence. This requirement is now consolidated into "
        "SOP-001 alongside the branded PDF requirement (ADR-2026-06)."))
    story.append(Spacer(1, 6))

    story.append(p("Original Decision", H2))
    story.append(p(
        "Every ADR must include a BLUF section immediately after the metadata block and before Context. "
        "The BLUF states the decision, the primary reason, and the consequence in 2-3 sentences."))
    story.append(hr())
    story.append(p("See SOP-001 for the current, consolidated procedure.", META))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-29: BLUF Requirement (Superseded)", content)
