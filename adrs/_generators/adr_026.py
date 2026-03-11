#!/usr/bin/env python3
"""ADR-2026-26 — No Separate Post-Ingestion Worker"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-26.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-26", "No Separate Post-Ingestion Worker"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-04  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "Do not create a separate post-ingestion worker service. data-daemon handles extraction and "
        "transforms in one process, with Postgres materialized views doing the SQL-based Bronze-to-Silver-to-Gold "
        "work. At Greenmark's scale (15 systems, thousands of records), a separate worker is overhead with no "
        "performance justification — it costs $5/mo on Railway and adds monitoring surface for zero benefit."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Do not create a separate post-ingestion worker. "
                           "data-daemon + Postgres materialized views handle everything. "
                           "Identity resolution (fuzzy matching) stays in data-daemon as a transform job type."))
    story.append(Spacer(1, 6))

    story.append(p("Context", H2))
    story.append(p(
        "With the medallion architecture (Bronze/Silver/Gold) taking shape, the question arose: should there "
        "be a separate cerebro-worker service for post-ingestion transforms, or should that work stay within "
        "data-daemon and Postgres?"))
    story.append(hr())

    story.append(p("Transform Architecture", H2))
    story.append(tbl(["Layer", "How", "Notes"], [
        [p("<b>Bronze → Silver</b>", CELL), p("Postgres materialized views", CELL),
         p("No application code needed", CELL)],
        [p("<b>Identity resolution</b>", CELL), p("data-daemon transform job", CELL),
         p("Needs Python (fuzzywuzzy)", CELL)],
        [p("<b>Silver → Gold</b>", CELL), p("Postgres materialized views", CELL),
         p("Cross-source joins in SQL", CELL)],
        [p("<b>Gold aggregates</b>", CELL), p("pg_cron or data-daemon trigger", CELL),
         p("After extraction runs", CELL)],
    ], [USABLE * 0.22, USABLE * 0.42, USABLE * 0.36]))
    story.append(Spacer(1, 6))

    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Scale</b>", CELL),
         p("15 systems, 3 entities, thousands of records. Postgres handles transforms in milliseconds.", CELL)],
        [p("<b>Job queue exists</b>", CELL),
         p("data-daemon already uses Postgres SKIP LOCKED. Adding transform jobs is trivial.", CELL)],
        [p("<b>Most transforms are SQL</b>", CELL),
         p("CREATE MATERIALIZED VIEW doesn't need Python, a container, or a deployment pipeline.", CELL)],
        [p("<b>Operational cost</b>", CELL),
         p("Each Railway service costs ~$5/mo minimum. Don't pay for what you don't need.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(hr())

    story.append(p("When to Revisit", H2))
    for i, item in enumerate([
        "Transform contention — transforms block the job queue",
        "ML-based identity resolution needing GPU",
        "Real-time streaming — vendor webhooks requiring instant updates",
        "Fault isolation — transform failures blocking extraction",
    ], 1):
        story.append(p(f"<b>{i}.</b> {item}"))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 4))
    story.append(p("<i>None of these conditions exist at Greenmark's current scale.</i>", META))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-26: No Separate Worker", content)
