#!/usr/bin/env python3
"""ADR-2026-39 — No DAG Scheduler for ETL Job Queue"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-39-no-dag-scheduler-for-etl.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-39", "No DAG Scheduler for ETL Job Queue"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Related:</b> ADR-2026-33 (SKIP LOCKED Job Queue), "
                   "ADR-2026-26 (No Separate Post-Ingestion Worker)", META))
    story.append(Spacer(1, 8))

    # BLUF
    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "We will not build a DAG scheduler for the ETL job queue. Bronze extraction is "
        "inherently flat — objects then associations, two levels — and cross-source dependencies "
        "live at the silver/gold layer where materialized view refresh order handles them. "
        "Priority-based ordering plus a single _depends_on field is the correct tool at this "
        "scale and topology."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Do not build a DAG scheduler. Keep priority-based ordering "
                           "with single _depends_on dependency enforcement. The extraction topology "
                           "is flat — each source is an independent two-level tree (objects → associations). "
                           "Cross-source dependencies are handled by silver/gold view refresh, not "
                           "the job queue."))
    story.append(Spacer(1, 8))

    # Context
    story.append(p("Context", H2))
    story.append(p(
        "During architecture review of the data-daemon ETL pipeline, we implemented job dependency "
        "enforcement: association tables (priority 0) are blocked until their parent object tables "
        "(priority 10) complete. This uses a _depends_on field in the job payload, checked by the "
        "claim_job SQL query via a NOT EXISTS subquery."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The question arose: should we build a proper DAG scheduler? The pipeline is growing from "
        "1 data source (HubSpot, 33 tables) toward 10+ sources (Sage, Navusoft, fleet telematics, "
        "QuickBooks, ServiceTitan). We challenged the assumption that more sources requires a DAG."))
    story.append(Spacer(1, 6))

    # Current Architecture
    story.append(p("Current Architecture", H2))
    story.append(mermaid("""
        flowchart TD
            SCHED["Scheduler tick"] --> LOAD["Load service YAML"]
            LOAD --> SPLIT["Split tables:<br/>Objects (priority 10)<br/>Associations (priority 0)"]
            SPLIT --> ENQ["Enqueue all jobs<br/>Set _depends_on for assoc tables"]
            ENQ --> CLAIM["Workers claim via SKIP LOCKED"]
            CLAIM --> CHECK{"_depends_on<br/>parent done?"}
            CHECK -->|Yes| RUN["Execute job"]
            CHECK -->|No| SKIP["Skip, try next job"]
            style SCHED fill:#E8F0EC,stroke:#2D6B4A
            style RUN fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "This handles the only dependency pattern that exists in bronze extraction: "
        "objects → associations. Two levels. No diamonds, no chains, no conditionals."))
    story.append(hr())

    # The Key Insight
    story.append(p("The Key Insight: Sources Are Independent", H2))
    story.append(p(
        "10+ sources sounds like it demands a DAG. But each source extracts independently — "
        "HubSpot doesn't wait for Salesforce, QuickBooks doesn't need Google Contacts. "
        "10 independent two-level trees is not a DAG. It's 10 separate lists running in "
        "the same job queue."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "HubSpot (independent)"
                H_OBJ["Objects<br/>17 tables<br/>Priority 10"] --> H_ASSOC["Associations<br/>16 tables<br/>Priority 0"]
            end
            subgraph "Sage (independent)"
                S_OBJ["Objects<br/>~10 tables<br/>Priority 10"] --> S_ASSOC["Associations<br/>~5 tables<br/>Priority 0"]
            end
            subgraph "Navusoft (independent)"
                N_OBJ["Objects<br/>~8 tables<br/>Priority 10"] --> N_ASSOC["Associations<br/>~3 tables<br/>Priority 0"]
            end
            style H_OBJ fill:#E8F0EC,stroke:#2D6B4A
            style S_OBJ fill:#E8F0EC,stroke:#2D6B4A
            style N_OBJ fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 6))

    # Where Cross-Source Dependencies Live
    story.append(p("Where Cross-Source Dependencies Actually Live", H2))
    story.append(mermaid("""
        flowchart TD
            subgraph "Bronze layer (job queue)"
                HS["HubSpot<br/>extracts independently"] ~~~ SG["Sage<br/>extracts independently"]
            end
            subgraph "Silver layer (view refresh)"
                SV["CREATE VIEW silver.unified_deals AS<br/>SELECT ... FROM hubspot_bronze.deals<br/>UNION ALL SELECT ... FROM sage_bronze.deals"]
            end
            subgraph "Gold layer (refresh function)"
                GD["MERGE INTO gold.deals<br/>FROM silver.unified_deals"]
            end
            HS --> SV
            SG --> SV
            SV --> GD
            style SV fill:#FDF8EC,stroke:#D4A843
            style GD fill:#FDF8EC,stroke:#D4A843
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "Cross-source joins happen at silver/gold via SQL view definitions, not at the extraction "
        "layer. The executor already refreshes views after loading their source tables. "
        "View refresh ordering is a simpler problem than DAG scheduling — and it's already solved."))
    story.append(hr())

    # Rationale
    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Extraction is flat</b>", CELL),
         p("Every source follows the same two-level pattern: objects → associations. "
           "No three-level chains, no diamonds, no conditional branches.", CELL)],
        [p("<b>Sources are independent</b>", CELL),
         p("10 sources = 10 independent two-level trees, not one 10-source DAG. "
           "SKIP LOCKED handles concurrency.", CELL)],
        [p("<b>Cross-source = silver/gold</b>", CELL),
         p("A silver view joining HubSpot + Sage is a REFRESH MATERIALIZED VIEW — "
           "view refresh ordering, not job queue ordering.", CELL)],
        [p("<b>_depends_on handles it</b>", CELL),
         p("Single string covers every real case: assoc_deal_contact depends on deals, "
           "assoc_call_deal depends on calls. No multi-parent bronze dependencies exist.", CELL)],
        [p("<b>YAGNI</b>", CELL),
         p("TopologicalSorter, cycle detection, multi-parent arrays solve problems "
           "we don't have. Maintaining unused code is negative value.", CELL)],
        [p("<b>The YAML is the DAG</b>", CELL),
         p("assoc_from_table: hubspot_bronze.deals is a human-readable dependency "
           "declaration. A runtime graph would produce identical ordering.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(hr())

    # Options Considered
    story.append(p("Options Considered", H2))
    story.append(tbl(["Option", "Verdict"], [
        [p("<b>Keep priority + _depends_on (chosen)</b>", CELL),
         p("Correct tool for flat topology. Zero new code. Already working.", CELL)],
        [p("Build DAG with graphlib.TopologicalSorter", CELL),
         p("Solves problems we don't have. ~100 lines with no current consumer.", CELL)],
        [p("Adopt Airflow / Dagster / Prefect", CELL),
         p("Massive infrastructure for 33 tables every 15 minutes. 1000x overkill.", CELL)],
        [p("Extend _depends_on to a list now", CELL),
         p("Pre-optimizing for multi-parent dependencies that don't exist in bronze.", CELL)],
    ], [USABLE * 0.35, USABLE * 0.65]))
    story.append(hr())

    # Consequences
    story.append(p("Consequences", H2))
    story.append(p(
        "<b>Positive:</b> No new code to write, test, or maintain. Architecture stays simple. "
        "Mental model stays simple: 'objects first, associations second.' New data sources plug in "
        "with zero scheduler changes — just add a YAML file."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Negative:</b> If a bronze table ever needs to depend on two different parent tables "
        "within the same service, the single _depends_on string won't handle it. Known limitation."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Mitigation:</b> Extending _depends_on from a string to a list is a 30-minute change. "
        "The SQL subquery changes from checking one table name to checking ANY() on an array. "
        "Trivial upgrade, not a rewrite."))
    story.append(Spacer(1, 6))

    # When to Revisit
    story.append(p("When to Revisit", H2))
    story.append(p("• A bronze table needs two different parent tables within the same extraction service"))
    story.append(p("• The executor needs to orchestrate cross-service extraction order"))
    story.append(p("• Pipeline grows beyond ~500 tables and parallelism optimization matters"))
    story.append(p("• Team grows beyond 3 people and 'just read the YAML' stops being sufficient"))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-39: No DAG Scheduler for ETL Job Queue", content)
