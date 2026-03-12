#!/usr/bin/env python3
"""ADR-2026-38 — Unified Migration Authority for Shared Database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-38-unified-migration-authority.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-38", "Unified Migration Authority"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Related:</b> ADR-2026-37 (DAG Validation), ADR-2026-04 (Medallion), "
                   "SOP-005 (Release &amp; Deployment)", META))
    story.append(Spacer(1, 8))

    # BLUF
    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "All medallion schema DDL — bronze, silver, gold, RLS, forge — moves to a dedicated "
        "cerebro-migrations repo with Supabase CLI as the single migration tool. data-daemon and "
        "cerebro become pure consumers: one writes data, the other reads it. Neither owns the "
        "database. This eliminates cross-repo migration ordering failures by removing the "
        "cross-repo migration pattern entirely."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Create a cerebro-migrations repo as the single migration authority "
                           "for the shared Greenmark PostgreSQL database. All medallion DDL consolidates there. "
                           "data-daemon and cerebro become pure consumers of the schema contract."))
    story.append(Spacer(1, 8))

    # The Incident
    story.append(p("Context: The Incident", H2))
    story.append(p(
        "On 2026-03-11, a cerebro silver expansion migration failed in production because it "
        "referenced hubspot_bronze.tickets — a bronze table created by data-daemon migration 016, "
        "which hadn't been deployed. Root cause: two repos independently mutating the same database "
        "with no coordination mechanism."))
    story.append(Spacer(1, 4))

    # Incident sequence diagram
    story.append(mermaid("""
        sequenceDiagram
            participant Dev as Developer
            participant Cerebro as Cerebro<br/>(Supabase CLI)
            participant DB as Production DB
            participant Daemon as data-daemon<br/>(Railway)
            Dev->>Cerebro: npx supabase db push
            Cerebro->>DB: CREATE silver.tickets
            DB-->>Cerebro: ERROR: hubspot_bronze.tickets<br/>does not exist
            Note over DB: Transaction ROLLBACK
            Note over Daemon: Migration 016 not deployed yet
            Note over Dev: Bronze dependency was invisible
    """))
    story.append(Spacer(1, 6))

    # The Problem with Split Ownership
    story.append(p("The Problem: Split Migration Ownership", H2))
    story.append(mermaid("""
        flowchart TB
            subgraph "BEFORE: Two migration owners"
                DD[data-daemon<br/>19 numbered migrations<br/>Auto-apply on startup] -->|Creates| BRONZE[Bronze tables]
                CE[cerebro<br/>21 timestamp migrations<br/>Manual supabase db push] -->|Creates| SILVER[Silver views]
                CE -->|Creates| GOLD[Gold views]
                CE -->|Creates| RLS[RLS policies]
                CE -->|Creates| FORGE[Forge functions]
                SILVER -.->|Depends on| BRONZE
                GOLD -.->|Depends on| SILVER
            end
            style DD fill:#FDF8EC,stroke:#D4A843
            style CE fill:#FDF8EC,stroke:#D4A843
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "Two repos, two migration systems, two history tables, one database. The dependency "
        "between them was invisible and unenforceable."))
    story.append(Spacer(1, 6))

    # The Solution
    story.append(p("The Solution: Dedicated Migrations Repo", H2))
    story.append(mermaid("""
        flowchart TB
            subgraph "AFTER: One migration owner"
                CM[cerebro-migrations<br/>All medallion DDL<br/>Supabase CLI] -->|Creates| BRONZE[Bronze tables]
                CM -->|Creates| SILVER[Silver views]
                CM -->|Creates| GOLD[Gold views]
                CM -->|Creates| RLS[RLS policies]
                CM -->|Creates| FORGE[Forge functions]
            end
            subgraph "Pure consumers"
                DD2[data-daemon<br/>Writes data to bronze<br/>Zero new DDL] -->|INSERT INTO| BRONZE
                CE2[cerebro<br/>Reads gold tables<br/>Zero migrations] -->|SELECT FROM| GOLD
            end
            style CM fill:#E8F0EC,stroke:#2D6B4A
            style DD2 fill:#E8F0EC,stroke:#193B2D
            style CE2 fill:#E8F0EC,stroke:#193B2D
    """))
    story.append(Spacer(1, 6))

    # Service Roles After Migration
    story.append(p("Service Roles After Migration", H2))
    story.append(tbl(["Service", "Role", "Owns"], [
        [p("<b>cerebro-migrations</b>", CELL),
         p("Single migration authority", CELL),
         p("All medallion DDL (bronze, silver, gold, RLS, forge). "
           "Supabase CLI. CI validation.", CELL)],
        [p("<b>data-daemon</b>", CELL),
         p("Pure ETL runner", CELL),
         p("ETL connectors, sync logic. Daemon-internal tables only "
           "(daemon.migration_history, daemon.sync_state, daemon.job_queue). "
           "Frozen at migration 019.", CELL)],
        [p("<b>cerebro</b>", CELL),
         p("Pure frontend consumer", CELL),
         p("Next.js app, API routes, UI. Zero migrations. "
           "Reads gold tables via Supabase client.", CELL)],
    ], [USABLE * 0.20, USABLE * 0.22, USABLE * 0.58]))
    story.append(Spacer(1, 6))

    # What Moves
    story.append(p("What Moves to cerebro-migrations", H2))
    story.append(tbl(["Artifact", "Current Owner", "Source"], [
        [p("Bronze table DDL", CELL), p("data-daemon", CELL), p("Migrations 001-019", CELL)],
        [p("Bronze indexes/constraints", CELL), p("data-daemon", CELL), p("Migrations 001-019", CELL)],
        [p("Silver materialized views", CELL), p("cerebro", CELL), p("supabase/migrations/", CELL)],
        [p("Gold materialized views", CELL), p("cerebro", CELL), p("supabase/migrations/", CELL)],
        [p("RLS policies and grants", CELL), p("cerebro", CELL), p("supabase/migrations/", CELL)],
        [p("Forge refresh functions", CELL), p("cerebro", CELL), p("supabase/migrations/", CELL)],
        [p("Schema/role setup", CELL), p("cerebro", CELL), p("supabase/migrations/", CELL)],
    ], [USABLE * 0.35, USABLE * 0.25, USABLE * 0.40]))
    story.append(hr())

    # CI Validation
    story.append(p("CI Validation: Ephemeral Database", H2))
    story.append(mermaid("""
        flowchart LR
            PR["PR opened to<br/>cerebro-migrations"] --> CI["CI pipeline"]
            CI --> SPIN["Spin up ephemeral<br/>PostgreSQL"]
            SPIN --> APPLY["Apply ALL migrations<br/>in timestamp order"]
            APPLY --> DAG["elt-forge build-dag<br/>validates dependencies"]
            DAG --> TEST["Run schema tests<br/>tables, views, RLS, indexes"]
            TEST --> PASS{"All pass?"}
            PASS -->|Yes| MERGE["Allow merge"]
            PASS -->|No| BLOCK["Block merge"]
            style MERGE fill:#E8F0EC,stroke:#2D6B4A
            style BLOCK fill:#FDECEC,stroke:#E74C3C
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "CI validates the full migration stack in isolation — no production queries, "
        "no point-in-time checks, no race conditions. Powered by elt-forge DAG validation "
        "(ADR-2026-37)."))
    story.append(hr())

    # Cutover Plan
    story.append(p("One-Time Cutover Plan", H2))
    story.append(mermaid("""
        flowchart TD
            A["1. Create cerebro-migrations repo<br/>with Supabase CLI toolchain"] --> B["2. Copy cerebro's existing<br/>supabase/migrations/ as baseline"]
            B --> C["3. Translate data-daemon bronze DDL<br/>(001-019) to timestamp format"]
            C --> D["4. Insert history records so<br/>existing migrations marked applied"]
            D --> E["5. Freeze data-daemon migrate.py<br/>daemon-internal tables only"]
            E --> F["6. Remove supabase/migrations/<br/>from cerebro"]
            F --> G["7. Update SOP-005<br/>deploy procedures"]
    """))
    story.append(Spacer(1, 6))

    # The Debate: 16 Options
    story.append(p("Options Considered (16 Evaluated)", H2))
    story.append(p("We evaluated 16 architectural options across five criteria: incident prevention, "
                   "simplicity for a 2-person team, scalability, AI agent compatibility, and clean ownership."))
    story.append(Spacer(1, 4))
    story.append(tbl(["Tier", "Options", "Verdict"], [
        [p("<b>S Tier</b>", CELL),
         p("Dedicated migrations repo + ephemeral DB CI", CELL),
         p("Accepted. Eliminates the problem structurally. Clean ownership.", CELL)],
        [p("<b>A Tier</b>", CELL),
         p("Consolidate into cerebro; Monorepo", CELL),
         p("Viable but semantic mismatch (frontend owns DB) or disproportionate blast radius.", CELL)],
        [p("<b>B Tier</b>", CELL),
         p("Reverse CI; Git submodule; Versioned artifacts; Deploy manifest", CELL),
         p("Overbuilt for a 2-person team.", CELL)],
        [p("<b>C Tier</b>", CELL),
         p("Header comments; Lock file; Contract tests; elt-forge registry", CELL),
         p("Brittle or indirect. Not worth the effort.", CELL)],
        [p("<b>F Tier</b>", CELL),
         p("Do nothing (SOP only); CREATE IF NOT EXISTS; CI queries production", CELL),
         p("Actively dangerous. False sense of security.", CELL)],
    ], [USABLE * 0.12, USABLE * 0.43, USABLE * 0.45]))
    story.append(hr())

    # Deploy Coordination
    story.append(p("Deploy Coordination: Schema-First, Apps Tolerant", H2))
    story.append(p(
        "Schema repo and app repos have independent CI/CD. No cross-repo triggers. No orchestrator. "
        "No release branches. Schema deploys first, apps lag slightly behind."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "Independent pipelines"
                M["cerebro-migrations<br/>npm run migrate<br/>DB at version N"] --> DB[(Production DB)]
                DD["data-daemon<br/>deploys whenever"] -->|writes| DB
                CE["cerebro<br/>deploys whenever"] -->|reads| DB
            end
            style M fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "Both apps are already forward-compatible: data-daemon ETL jobs fail gracefully if a "
        "table doesn't exist yet; cerebro pages show no data if a gold view is missing."))
    story.append(Spacer(1, 4))
    story.append(p("<b>Breaking changes use expand/contract:</b>"))
    story.append(tbl(["Step", "What Happens", "Risk"], [
        [p("<b>1. Expand</b>", CELL),
         p("Migration adds the new thing alongside the old", CELL),
         p("Zero — additive only", CELL)],
        [p("<b>2. Update</b>", CELL),
         p("Apps update to use the new thing (separate deploys)", CELL),
         p("Zero — old thing still exists", CELL)],
        [p("<b>3. Contract</b>", CELL),
         p("Migration removes the old thing", CELL),
         p("Zero — no consumers remain", CELL)],
    ], [USABLE * 0.15, USABLE * 0.55, USABLE * 0.30]))
    story.append(Spacer(1, 4))
    story.append(p("Three separate commits, three separate deploys, zero coordination needed. "
                   "Each step is independently safe."))
    story.append(hr())

    # Rationale
    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Industry consensus</b>", CELL),
         p("Every source converges: one migration owner per shared database", CELL)],
        [p("<b>Incident prevention</b>", CELL),
         p("Cross-repo ordering failures structurally impossible — one repo", CELL)],
        [p("<b>Clean ownership</b>", CELL),
         p("Neither service 'owns' the database. The database has its own repo. "
           "Both services are consumers", CELL)],
        [p("<b>AI agent workflow</b>", CELL),
         p("Agent writes DDL in one place, runs one command. No cross-repo "
           "dependency reasoning", CELL)],
        [p("<b>RLS safety</b>", CELL),
         p("Policy changes go through PR review, not auto-applied on ETL startup", CELL)],
        [p("<b>Scale</b>", CELL),
         p("New vendor integrations need one PR — bronze + silver + gold in one sequence", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(hr())

    # Why We Had to Change
    story.append(p("Why We Had to Change", H2))
    story.append(p(
        "The split migration pattern creates compounding pain as the system grows. "
        "Every new vendor integration multiplies the coordination cost."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart TD
            subgraph "BEFORE: Every vendor integration"
                V1["1. Write bronze DDL<br/>in data-daemon"] --> V2["2. Write connector code<br/>in data-daemon"]
                V2 --> V3["3. Deploy data-daemon<br/>to Railway"]
                V3 --> V4["4. Wait for auto-apply<br/>to finish"]
                V4 --> V5["5. Write silver views<br/>in cerebro"]
                V5 --> V6["6. Write gold views<br/>in cerebro"]
                V6 --> V7["7. Write RLS policies<br/>in cerebro"]
                V7 --> V8["8. Push cerebro migrations<br/>hope bronze exists"]
                V8 --> V9{"Did it work?"}
                V9 -->|No| V10["Debug cross-repo<br/>dependency failure"]
                V10 --> V3
            end
            style V10 fill:#FDECEC,stroke:#E74C3C
            style V9 fill:#FDF8EC,stroke:#D4A843
    """))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart TD
            subgraph "AFTER: Every vendor integration"
                A1["1. Write ALL DDL in<br/>cerebro-migrations<br/>(bronze + silver + gold + RLS)"] --> A2["2. CI validates full stack<br/>in ephemeral Postgres"]
                A2 --> A3["3. Merge PR"]
                A3 --> A4["4. npm run migrate"]
                A4 --> A5["5. Write connector code<br/>in data-daemon"]
                A5 --> A6["6. Deploy data-daemon"]
                A6 --> A7["Done"]
            end
            style A7 fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 6))

    # Time Savings Projection
    story.append(p("Projected Time &amp; Hassle Savings (Next 12 Months)", H2))
    story.append(p(
        "Based on current trajectory: 5 new vendor integrations planned (Sage expansion, "
        "Navusoft expansion, fleet telematics, QuickBooks, ServiceTitan), plus ongoing HubSpot "
        "object additions. Each integration touches bronze + silver + gold + RLS."))
    story.append(Spacer(1, 4))
    story.append(tbl(["Activity", "Before (per integration)", "After (per integration)", "Annual Savings (5+ integrations)"], [
        [p("Migration authoring", CELL),
         p("2 PRs, 2 repos, manual ordering", CELL),
         p("1 PR, 1 repo, natural ordering", CELL),
         p("~5 hours saved", CELL)],
        [p("Deploy coordination", CELL),
         p("Deploy daemon, wait, deploy cerebro, hope", CELL),
         p("npm run migrate, done", CELL),
         p("~5 hours saved", CELL)],
        [p("Cross-repo debugging", CELL),
         p("1-2 hours per ordering failure", CELL),
         p("CI catches before merge", CELL),
         p("~10 hours saved", CELL)],
        [p("Rollback complexity", CELL),
         p("Coordinate 2 repos, 2 systems", CELL),
         p("Revert 1 migration", CELL),
         p("~3 hours saved", CELL)],
        [p("Agent reasoning overhead", CELL),
         p("Cross-repo dependency analysis per deploy", CELL),
         p("Zero — one repo, one sequence", CELL),
         p("~8 hours saved", CELL)],
        [p("<b>TOTAL</b>", CELL),
         p("", CELL),
         p("", CELL),
         p("<b>~31 hours/year + eliminated incident class</b>", CELL)],
    ], [USABLE * 0.22, USABLE * 0.26, USABLE * 0.26, USABLE * 0.26]))
    story.append(Spacer(1, 4))
    story.append(p(
        "The time savings are real but secondary. The primary value is eliminating an entire "
        "class of production failures. The 2026-03-11 incident cost 3 hours of debugging plus "
        "delayed the HubSpot expansion launch. One prevented incident per quarter pays for "
        "the cutover effort in the first month."))
    story.append(hr())

    # Consequences
    story.append(p("Consequences", H2))
    story.append(p(
        "<b>Positive:</b> Cross-repo migration ordering failures eliminated. One source of truth "
        "for database schema. Clean separation: migrations repo owns schema, data-daemon owns ETL, "
        "cerebro owns UI. RLS changes get proper review. AI agents have simple workflow."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Negative:</b> Third repo to maintain. One-time cutover effort to translate and merge "
        "existing migrations. Bronze DDL committed separately from connector code."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Mitigation:</b> AI agents handle multi-repo workflows trivially — repo count is not "
        "a friction factor. One-time cutover is scriptable. CODEOWNERS on cerebro-migrations "
        "ensures review discipline."))
    story.append(Spacer(1, 6))

    # When to Revisit
    story.append(p("When to Revisit", H2))
    story.append(p("• If team grows beyond 5 engineers and migration review becomes a bottleneck"))
    story.append(p("• If a third service needs to write DDL — validates this pattern"))
    story.append(p("• If Supabase CLI gains native multi-repo migration support"))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-38: Unified Migration Authority", content)
