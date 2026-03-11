#!/usr/bin/env python3
"""ADR-2026-27 — HubSpot Entity Resolution"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-27-hubspot-entity-resolution.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-27", "HubSpot Entity Resolution"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-04  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        'Default all HubSpot records to the ntx entity. There is no reliable entity-distinguishing field '
        'in HubSpot today — the "Brands" field is 84% blank with no enum options, and no custom entity '
        'property exists. This is a config change away from being correct once Michael configures entity tagging.'))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Default all HubSpot records to entity='ntx'. "
                           "No inference from geography or owner. "
                           "Correct entity tagging is a YAML config change once HubSpot is configured."))
    story.append(Spacer(1, 6))

    story.append(p("Context", H2))
    story.append(p(
        "Greenmark operates 3 business entities — NTX, Hometown, and Memphis. The warehouse tags every "
        "record with an entity column. HubSpot is a single shared account — all entities share the same "
        "contacts, companies, deals, and pipeline."))
    story.append(hr())

    story.append(p("Investigation Results (2026-03-04)", H2))
    story.append(tbl(["Field", "Exists?", "Data"], [
        [p("hs_all_assigned_business_unit_ids", CELL), p("Yes", CELL),
         p("84% blank, 16% = '0'. No enum options. Not usable.", CELL)],
        [p("Custom entity property", CELL), p("<b>No</b>", CELL),
         p("Does not exist on companies, contacts, or deals", CELL)],
        [p("Owner teams", CELL), p("Partial", CELL),
         p("Michael = 'NTX'. 14 others = no team.", CELL)],
        [p("Deal pipelines", CELL), p("1 only", CELL),
         p("'Sales Pipeline' — no per-entity split", CELL)],
        [p("State/geography", CELL), p("Unreliable", CELL),
         p("Inconsistent (TX, Texas, Tx, tx). No Indiana records.", CELL)],
    ], [USABLE * 0.35, USABLE * 0.12, USABLE * 0.53]))
    story.append(Spacer(1, 6))

    story.append(p("Multi-Tenant Strategy", H2))
    story.append(tbl(["Vendor", "Account Structure", "Entity Strategy"], [
        [p("<b>HubSpot</b>", CELL), p("1 shared account", CELL),
         p("Field-based tagging (future)", CELL)],
        [p("<b>Sage Intacct</b>", CELL), p("Unknown", CELL),
         p("Likely LOCATIONID or entity dimension", CELL)],
        [p("<b>Navusoft</b>", CELL), p("Unknown", CELL),
         p("May have separate databases per entity", CELL)],
    ], [USABLE * 0.2, USABLE * 0.35, USABLE * 0.45]))
    story.append(hr())

    story.append(p("Action Items", H2))
    for i, item in enumerate([
        "Daniel → Michael: Use 'Brands' field or create custom property?",
        "After decision: Update hubspot.yaml with entity_column",
        "Before Sage: Investigate entity structure in Sage tenant",
    ], 1):
        story.append(p(f"<b>{i}.</b> {item}"))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 4))

    story.append(p("Consequences", H2))
    story.append(p("<b>Positive:</b> Clean pipeline ships now. Entity resolution is a config change."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "RISK: Low. Hometown's CRM activity appears minimal — no Indiana companies "
                           "in first 100 records. The mis-tagging window is small.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER, bold=False))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-27: HubSpot Entity Resolution", content)
