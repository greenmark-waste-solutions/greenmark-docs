# SOP-001: Creating ADRs and SOPs

- **Effective**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Applies to**: Anyone creating project documentation in the cockpit repo
- **Supersedes**: ADR-2026-29 (BLUF requirement), ADR-2026-30 (branded PDF requirement)

## BLUF

ADRs record decisions. SOPs record procedures. Every ADR and SOP must have a BLUF and a branded PDF. This document tells you how to decide which one you're writing and exactly how to produce it.

## Definitions

| Term | What It Is |
|------|-----------|
| **ADR** | **Architecture Decision Record** — a document that captures a significant technical decision, the options considered, and the reasoning behind the choice. ADRs are immutable: once accepted or rejected, they don't change. If a decision is reversed, a new ADR supersedes the old one. ADRs answer: *"What did we decide, and why?"* |
| **SOP** | **Standard Operating Procedure** — a document that captures how to perform a recurring task, a standing rule, or institutional knowledge that the technology team needs to operate. SOPs are living documents: they're updated in place when procedures change. SOPs answer: *"How do we do this?"* or *"What should I know?"* |
| **BLUF** | **Bottom Line Up Front** — a 2-3 sentence summary at the top of every ADR and SOP. Borrowed from military communications. States the decision/procedure, the reason, and the consequence. If the reader stops after the BLUF, they still know what happened and why. |

## Decision Tree

```
You have something to document. What is it?

  "We decided to do X because Y"
  → You decided something about architecture, tooling, or strategy
  → Write an ADR

  "When X happens, do Y"
  → You're documenting how to perform a task or follow a rule
  → Write an SOP

  "We explored X and rejected it"
  → That's a decision (to reject)
  → Write an ADR

  "Don't ask Michael about Sage credentials"
  → That's a standing procedure / institutional knowledge
  → Write an SOP

  Still unsure?
  → If it has a "because" → ADR
  → If it has a "how to" → SOP
```

## ADR vs SOP at a Glance

| | ADR | SOP |
|---|-----|-----|
| **Purpose** | Record a decision and its reasoning | Record a procedure, rule, or institutional knowledge |
| **Question it answers** | "What did we decide and why?" | "How do we do this?" or "What should I know?" |
| **Tone** | "We decided X because Y" | "Do X. Don't do Y. Here's how." |
| **Numbering** | `ADR-YYYY-NN` (year-scoped) | `SOP-NNN` (sequential, no year) |
| **Location** | `decisions/` | `sops/` |
| **Updates** | Immutable — superseded by new ADR | Updated in place — living document |
| **BLUF** | Required | Required |
| **Branded PDF** | Required | Required |

## How to Write an ADR

### File naming
```
decisions/ADR-YYYY-NN-slug.md           ← markdown (source of truth)
decisions/ADR-YYYY-NN-slug.pdf          ← branded PDF (stakeholder artifact)
decisions/_generators/adr_NNN.py        ← generator script (imports from lib/greenmark_pdf.py)
```

### Required sections

```markdown
# ADR-YYYY-NN: Title

- **Status**: Accepted | Rejected | Superseded by [ADR-YYYY-NN]
- **Date**: YYYY-MM-DD
- **Owner**: Name / Role
- **Related**: links to related files, ADRs, or SOPs

## BLUF (Bottom Line Up Front)

[2-3 sentences. The decision + the reason + the consequence.
No hedging. No "on the other hand." Military-style.]

## Context

[What situation prompted this decision? What problem were we solving?]

## Decision

[What we decided. Clear, direct statement.]

## Rationale

[Why we decided this. Table format preferred:
| Factor | Assessment |]

## Options Considered

[Table of options with pros/cons. Mark the chosen option bold.]

## Consequences

- **Positive**: what we gain
- **Negative**: what we lose or accept
- **Mitigation**: how we handle the negatives

## When to Revisit

[Under what conditions should this decision be reconsidered?]
```

### BLUF rules for ADRs
- State the decision (what are we doing or not doing)
- State the primary reason (the one thing that tipped the scale)
- State the consequence (what this means in practice)
- 2-3 sentences maximum
- No hedging, no passive voice

**Good:** "We will not build a secrets management UI in Cerebro. Any web-tier access to vault secrets creates a permanent privilege escalation path. The inconvenience of SQL Editor access is the security control."

**Bad:** "After careful consideration of several options and their trade-offs, we have decided that it would be best to avoid building a vault UI at this time, pending further security review."

## How to Write an SOP

### File naming
```
sops/SOP-NNN-slug.md                    ← markdown (source of truth)
sops/SOP-NNN-slug.pdf                   ← branded PDF (stakeholder artifact)
sops/_generators/sop_NNN.py             ← generator script (imports from lib/greenmark_pdf.py)
```

### Required sections

```markdown
# SOP-NNN: Title

- **Effective**: YYYY-MM-DD
- **Owner**: Name / Role
- **Applies to**: Who needs to follow this

## BLUF

[2-3 sentences. What to do, when, and why it matters.]

## Procedure

[Step-by-step instructions, rules, or reference tables.
Be specific. Use numbered steps for sequential procedures.
Use bullet points for rules and policies.]

## Why This Exists

[Brief backstory — what went wrong, what prompted this,
or why this knowledge matters. Keep it short.]

## Exceptions

[When this SOP doesn't apply, or who can override it.
If no exceptions, say "None."]
```

### BLUF rules for SOPs
- State what to do
- State when it applies
- State why it matters
- 2-3 sentences maximum
- Imperative mood ("Do X" not "One should do X")

## Branded PDF Requirements

Every ADR and SOP ships with a branded PDF. The PDF is generated by a co-located Python script using ReportLab.

### Brand constants
```python
from reportlab.lib.colors import HexColor, white

BRAND_GREEN  = HexColor("#193B2D")   # Headers, titles, table headers
BRAND_LIGHT  = HexColor("#E8F0EC")   # Alternating rows, accent box backgrounds
ACCENT_GREEN = HexColor("#2D6B4A")   # Section headings, positive accent borders
MUTED        = HexColor("#6B7B73")   # Metadata text, footers
DARK         = HexColor("#1A1A1A")   # Body text
WHITE        = white                  # Text on dark backgrounds

RED          = HexColor("#C0392B")   # Rejection/critical severity
RED_BG       = HexColor("#FDECEC")   # Red accent box background
RED_BORDER   = HexColor("#E74C3C")   # Red accent box border
AMBER        = HexColor("#92700A")   # Warning/medium severity
AMBER_BG     = HexColor("#FDF8EC")   # Amber accent box background
AMBER_BORDER = HexColor("#D4A843")   # Amber accent box border
```

### Required PDF elements
1. **BrandHeader** — dark green rounded rect, Greenmark logo top-left, document number bottom-left, title bottom-right
2. **BLUF section** — first content after metadata
3. **Decision/procedure accent box** — green border for accepted/positive, red border for rejected/warning
4. **Branded tables** — dark green header row, alternating white/light green body rows, thin gray grid
5. **Footer** — "Greenmark Waste Solutions | Document title | Date" left, "Page N" right
6. **Logo path**: `infra/brand/greenmark-full-white.png` (white text on transparent, drawn at 1.35" × 0.28")
7. **Fonts**: Helvetica family only (built into ReportLab)

### Generator script pattern
- File: `decisions/_generators/adr_NNN.py` or `sops/_generators/sop_NNN.py`
- Import everything from `lib/greenmark_pdf.py` — never duplicate flowables
- Content-only: define a `content(story, p)` function, call `build_doc(OUTPUT, title, content)`
- Output PDF to parent directory (next to the markdown)
- Run one: `python3 decisions/_generators/adr_001.py`
- Build all: `python3 decisions/_generators/build_all.py`
- Dependency: `pip install reportlab`

## Why This Exists

ADR-05 and ADR-06 established the BLUF and branded PDF requirements as separate ADRs, but they were really procedures — "how to write documents" not "what we decided about the system." This SOP consolidates both into a single reference that covers the full document creation workflow.

Having one place that answers "how do I create an ADR?" and "how do I create an SOP?" eliminates the need to read three separate documents before writing one.

## Exceptions

None. Every ADR and SOP follows this format. No exceptions for "quick" or "informal" documents — if it's worth writing down, it's worth writing correctly.
