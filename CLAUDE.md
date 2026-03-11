# CLAUDE.md — Greenmark Docs

Consolidated Architecture Decision Records (ADRs) and Standard Operating Procedures (SOPs) for Greenmark Waste Solutions.

## What This Repo Is

The single source of truth for all technical decisions and operating procedures across the Greenmark organization. Previously ADRs were scattered across `infra`, `greenmark-cockpit`, and `greenmark-competitive-intelligence` — now they live here.

## Structure

```
greenmark-docs/
├── adrs/                    ← Architecture Decision Records (ADR-2026-01 through ADR-2026-35)
│   └── _generators/         ← ReportLab scripts that produce branded PDFs
├── sops/                    ← Standard Operating Procedures (SOP-001+)
│   └── _generators/         ← ReportLab scripts that produce branded PDFs
├── lib/greenmark_pdf.py     ← Shared brand library (colors, flowables, table builders)
├── brand/                   ← Logo assets for PDF generation
└── CLAUDE.md                ← You are here
```

## Numbering

ADRs use `ADR-YYYY-NN` format. The unified sequence:

| Range | Origin | Topics |
|-------|--------|--------|
| 01-24 | infra | Medallion architecture, gold security, RLS, PostgREST, auth, vault |
| 25-31 | greenmark-cockpit | Engagement decisions, vendor strategy, document formats |
| 32-35 | greenmark-competitive-intelligence | CI architecture, job queue, claude-p constraint |

SOPs use `SOP-NNN` (sequential, no year).

## Creating Documents

Read **SOP-001** (`sops/SOP-001-creating-adrs-and-sops.md`) — it covers:
- When to write an ADR vs SOP
- Required sections and BLUF format
- Branded PDF generation workflow
- Brand constants and shared library usage

## Generating PDFs

```bash
# Single ADR
python3 adrs/_generators/adr_028.py

# All ADRs
python3 adrs/_generators/build_all.py

# Single SOP
python3 sops/_generators/sop_001.py

# All SOPs
python3 sops/_generators/build_all.py
```

Requires: `pip install reportlab`

## Rules

- Every ADR and SOP **must** have a BLUF (Bottom Line Up Front)
- Every ADR and SOP **must** ship with a branded PDF
- ADRs are **immutable** — superseded by new ADRs, never edited
- SOPs are **living documents** — updated in place
- All generators import from `lib/greenmark_pdf.py` — never duplicate brand constants or flowables

## cerebro-mcp Integration

`cerebro_adrs()` and `cerebro_sops()` tools in cerebro-mcp read from this repo's filesystem. Set `GREENMARK_DOCS_ROOT` env var if the repo isn't cloned at the default path.
