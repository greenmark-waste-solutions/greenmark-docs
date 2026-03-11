#!/usr/bin/env python3
"""SOP-001 — Creating ADRs and SOPs"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "sops" / "SOP-001-creating-adrs-and-sops.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "SOP-001", "Creating ADRs and SOPs"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Effective:</b> 2026-03-11  |  <b>Owner:</b> Daniel Shanklin  |  "
                   "<b>Applies to:</b> Anyone creating project documentation  |  "
                   "<b>Supersedes:</b> ADR-2026-29, ADR-2026-30", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF", H2))
    story.append(p(
        "ADRs record decisions. SOPs record procedures. Every ADR and SOP must have a BLUF and a "
        "branded PDF. This document tells you how to decide which one you're writing and exactly "
        "how to produce it."))
    story.append(Spacer(1, 6))

    # Definitions
    story.append(p("Definitions", H2))
    story.append(tbl(["Term", "Definition"], [
        [p("<b>ADR</b>", CELL),
         p("<b>Architecture Decision Record</b> — captures a technical decision, options considered, "
           "and reasoning. Immutable: superseded by new ADR, never edited. "
           "Answers: <i>'What did we decide, and why?'</i>", CELL)],
        [p("<b>SOP</b>", CELL),
         p("<b>Standard Operating Procedure</b> — captures how to perform a task, a standing rule, "
           "or institutional knowledge. Living document: updated in place. "
           "Answers: <i>'How do we do this?'</i> or <i>'What should I know?'</i>", CELL)],
        [p("<b>BLUF</b>", CELL),
         p("<b>Bottom Line Up Front</b> — 2-3 sentence summary at the top of every ADR and SOP. "
           "States decision/procedure, reason, and consequence. Military-style.", CELL)],
    ], [USABLE * 0.12, USABLE * 0.88]))
    story.append(Spacer(1, 6))

    # Decision tree
    story.append(p("Decision Tree: ADR or SOP?", H2))
    story.append(tbl(["You want to write...", "What that means", "Type"], [
        [p('"We decided to do X because Y"', CELL),
         p("Architecture, tooling, or strategy decision", CELL), p("<b>ADR</b>", CELL)],
        [p('"When X happens, do Y"', CELL),
         p("Task procedure or standing rule", CELL), p("<b>SOP</b>", CELL)],
        [p('"We explored X and rejected it"', CELL),
         p("Decision (to reject)", CELL), p("<b>ADR</b>", CELL)],
        [p('"Don\'t ask Michael about Sage"', CELL),
         p("Institutional knowledge", CELL), p("<b>SOP</b>", CELL)],
    ], [USABLE * 0.35, USABLE * 0.42, USABLE * 0.23]))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           'Still unsure? If it has a "because" → ADR. If it has a "how to" → SOP.'))
    story.append(Spacer(1, 6))

    # Comparison
    story.append(p("ADR vs SOP at a Glance", H2))
    story.append(tbl(["", "ADR", "SOP"], [
        [p("<b>Numbering</b>", CELL), p("ADR-YYYY-NN", CELL), p("SOP-NNN", CELL)],
        [p("<b>Location</b>", CELL), p("decisions/", MONO), p("sops/", MONO)],
        [p("<b>Generators</b>", CELL), p("decisions/_generators/", MONO), p("sops/_generators/", MONO)],
        [p("<b>Updates</b>", CELL), p("Superseded by new ADR", CELL), p("Updated in place", CELL)],
        [p("<b>BLUF</b>", CELL), p("Required", CELL), p("Required", CELL)],
        [p("<b>Branded PDF</b>", CELL), p("Required", CELL), p("Required", CELL)],
    ], [USABLE * 0.18, USABLE * 0.41, USABLE * 0.41]))
    story.append(hr())

    # ADR sections
    story.append(p("ADR Required Sections", H2))
    story.append(tbl(["#", "Section", "Content"], [
        [p("1", CELL), p("<b>Title + metadata</b>", CELL), p("Status, Date, Owner, Related", CELL)],
        [p("2", CELL), p("<b>BLUF</b>", CELL), p("Decision + reason + consequence, 2-3 sentences", CELL)],
        [p("3", CELL), p("<b>Context</b>", CELL), p("What prompted this decision", CELL)],
        [p("4", CELL), p("<b>Decision</b>", CELL), p("Clear, direct statement", CELL)],
        [p("5", CELL), p("<b>Rationale</b>", CELL), p("Why — table format (Factor | Assessment)", CELL)],
        [p("6", CELL), p("<b>Options Considered</b>", CELL), p("Table: Option | Description | Pros | Cons", CELL)],
        [p("7", CELL), p("<b>Consequences</b>", CELL), p("Positive, Negative, Mitigation", CELL)],
        [p("8", CELL), p("<b>When to Revisit</b>", CELL), p("Conditions for reconsideration", CELL)],
    ], [0.3 * inch, USABLE * 0.25, USABLE - 0.3 * inch - USABLE * 0.25]))
    story.append(Spacer(1, 4))

    # BLUF examples
    story.append(AccentBox(USABLE,
                           "GOOD BLUF: We will not build a secrets management UI in Cerebro. Any web-tier "
                           "access to vault secrets creates a permanent privilege escalation path. The "
                           "inconvenience of SQL Editor access is the security control."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "BAD BLUF: After careful consideration of several options and their trade-offs, "
                           "we have decided that it would be best to avoid building a vault UI at this "
                           "time, pending further security review.",
                           bg=RED_BG, border=RED_BORDER, text_color=RED))
    story.append(Spacer(1, 6))
    story.append(PageBreak())

    # SOP sections
    story.append(p("SOP Required Sections", H2))
    story.append(tbl(["#", "Section", "Content"], [
        [p("1", CELL), p("<b>Title + metadata</b>", CELL), p("Effective, Owner, Applies to", CELL)],
        [p("2", CELL), p("<b>BLUF</b>", CELL), p("What, when, why — 2-3 sentences", CELL)],
        [p("3", CELL), p("<b>Procedure</b>", CELL), p("Steps, rules, or reference tables", CELL)],
        [p("4", CELL), p("<b>Why This Exists</b>", CELL), p("Brief backstory", CELL)],
        [p("5", CELL), p("<b>Exceptions</b>", CELL), p("When it doesn't apply, or 'None'", CELL)],
    ], [0.3 * inch, USABLE * 0.25, USABLE - 0.3 * inch - USABLE * 0.25]))
    story.append(hr())

    # Brand spec
    story.append(p("Brand Constants", H2))
    story.append(tbl(["Name", "Hex", "Usage"], [
        [p("BRAND_GREEN", CELL), p("#193B2D", MONO), p("Headers, titles, table headers", CELL)],
        [p("BRAND_LIGHT", CELL), p("#E8F0EC", MONO), p("Alternating rows, accent backgrounds", CELL)],
        [p("ACCENT_GREEN", CELL), p("#2D6B4A", MONO), p("Section headings, positive borders", CELL)],
        [p("MUTED", CELL), p("#6B7B73", MONO), p("Metadata, footers", CELL)],
        [p("DARK", CELL), p("#1A1A1A", MONO), p("Body text", CELL)],
        [p("RED", CELL), p("#C0392B", MONO), p("Rejection / critical", CELL)],
        [p("AMBER", CELL), p("#92700A", MONO), p("Warning / caution", CELL)],
    ], [USABLE * 0.2, USABLE * 0.15, USABLE * 0.65]))
    story.append(Spacer(1, 4))
    story.append(p("<b>Shared library:</b> <i>lib/greenmark_pdf.py</i> — import all brand constants, "
                   "flowables, and table builders from here. Never duplicate.", CELL_BOLD))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "No exceptions. Every ADR and SOP follows this format. "
                           "If it's worth writing down, it's worth writing correctly.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))


if __name__ == "__main__":
    build_doc(OUTPUT, "SOP-001: Creating ADRs and SOPs", content)
