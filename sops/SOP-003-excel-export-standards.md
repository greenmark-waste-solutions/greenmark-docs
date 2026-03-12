# SOP-003: Excel Export Standards

- **Effective**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Applies to**: Any tool or script that generates Excel workbooks for Greenmark

## BLUF

Every Excel workbook produced by Cerebro or any Greenmark data tool must have a branded cover sheet, be pre-formatted for letter landscape printing, use real numeric values (not formatted strings), and include CONFIDENTIAL markings. These standards ensure workbooks are print-ready, AI-transparent, and professionally branded.

## Cover Sheet (Required)

Every workbook starts with a branded cover page.

| Element | Requirement |
|---------|------------|
| Product name | Large, bold, brand primary (#2D4A3E) |
| Report title | What this workbook contains |
| Entity | Who this data belongs to (RLS-filtered) |
| Date | `=NOW()` or datetime cell with Excel format — never hardcoded string |
| Row count | Total rows across all data tabs |
| CONFIDENTIAL | Red, bold, prominently placed |
| Prepared by | "Project Cerebro — AIC Holdings" or equivalent |
| RLS note | "Data filtered by Row-Level Security" |
| Gridlines | Hidden |
| Print | Fit to 1 page width AND 1 page height (cover = exactly 1 printed page) |

The cover page has NO header/footer — it IS the cover.

## Print Setup (Every Sheet)

Assume every sheet will be printed, stapled, and handed to someone in a meeting.

```
Orientation:  Landscape
Paper:        Letter (8.5 x 11)
Fit to:       1 page wide, unlimited pages tall
Margins:      0.5" left/right, 0.6" top, 0.75" bottom
```

### Header (top of every printed page)
| Left | Center | Right |
|------|--------|-------|
| `&F` (filename) | Tab name | *(empty)* |

### Footer (bottom of every printed page)
| Left | Center | Right |
|------|--------|-------|
| `CONFIDENTIAL — {entity}` | `Printed &D &T` | `Page &P of &N` |

`&F`, `&D`, `&T`, `&P`, `&N` are Excel print codes — resolved at print time. The printed date is always when someone actually printed it.

### Print title rows
Always freeze row 1 (or the header row) as a print title so column headers repeat on every printed page.

## Transparency to AI

**Every number must be a real number, not a formatted string.**

| Wrong | Right |
|-------|-------|
| `"87.3%"` (string) | `0.873` with format `0.0%` |
| `"$12,500.00"` (string) | `12500` with format `$#,##0.00` |
| `"2026-03-11 14:30"` (string) | `datetime(2026,3,11,14,30)` with format `YYYY-MM-DD HH:MM` |

Where formulas are possible, use them. Where they're not (Python-computed values), write raw numeric values with Excel number formats.

## Brand Colors

Source: `greenmark-assets/brand/palette.json`

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#2D4A3E` | Titles, headers, "good" status |
| Accent | `#C9A84C` | Gold layer, planning tabs, "needs work" |
| Surface | `#F5F0E8` | Input row fills, cream background |
| Text Gray | `#6B7280` | Body text, secondary info |
| Error Red | `#A4262C` | Critical, failed, below standard |

### Conditional formatting
| Condition | Font | Fill |
|-----------|------|------|
| Positive / On Target | `#006100` | `#E2EFDA` |
| Negative / Below Standard | `#9C0006` | `#FCE4EC` |

## Typography Hierarchy

| Level | Size | Bold | Italic | Color |
|-------|------|------|--------|-------|
| Page title | 16pt | Yes | No | Primary |
| Section header | 13pt | Yes | No | Primary |
| Subtitle | 9pt | No | Yes | `#666666` |
| Table header | 11pt | Yes | No | White on fill |
| Body | 11pt | No | No | Default |

## Layout Rules

- **Section spacing**: Exactly 1 blank row between sections
- **Zebra striping**: `#F2F2F2` on raw data tabs only (not analysis tabs)
- **Callout boxes**: Yellow `#FFF2CC` background on planning/input tabs
- **No merged cells on data tabs** — breaks filtering and sorting
- **No color-only meaning** — every colored cell also has text

## Tab Structure

Reading flow left to right:

1. Cover — branded, CONFIDENTIAL
2. Summary — overview, how-to-read
3. Tab Index — every tab with descriptions
4. Diagnostics — connection health
5. Planning tabs — stakeholder input sheets
6. Data Quality — metrics with goals and benchmarks
7. Data tabs — grouped by layer (Bronze, Silver, Gold)
8. Verification — automated checks, scorecard

## Reference Implementation

`cerebro-excel/scripts/` implements all of the above. Key files:
- `lib/styles.py` — brand colors, fills, fonts, helpers
- `lib/sheets.py` — tab writers, `_setup_print()`
- `lib/benchmarks.py` — DQ benchmarks as constants
- `lib/quality.py` — pure analysis functions

## Why This Exists

Luke's beartraps backtest report demonstrated professional Excel patterns (green/red conditional formatting, zebra striping, scorecard widgets, no merged cells on data tabs). We studied it, compared against our approach, and adopted the best practices while keeping our brand identity and print requirements. This SOP ensures consistency across all future Excel exports.

## Exceptions

None. Every Excel workbook follows these standards. If a workbook is internal-only and will never be printed, the print setup still applies — the cost is one function call, the risk of skipping it is a bad impression when someone inevitably prints it anyway.
