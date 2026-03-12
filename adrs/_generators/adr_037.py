#!/usr/bin/env python3
"""ADR-2026-37 — pg_depend + Context Reasoning for Migration Validation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-37-dag-aware-deploy-planning.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-37", "Migration Validation via pg_depend"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Related:</b> ADR-2026-38 (Unified Migration Authority), "
                   "elt-forge Feature Spec", META))
    story.append(Spacer(1, 8))

    # BLUF
    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "When validating migrations, use PostgreSQL's pg_depend for existing object dependencies "
        "and AI context reasoning for pending migrations. No SQL parsing. This is how the CI gate "
        "in cerebro-migrations knows whether a migration stack is safe to merge."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Use pg_depend (ground truth for existing objects) + AI context "
                           "reasoning (for pending migrations) to validate migration stacks in CI. "
                           "No SQL parsing. No manifest files."))
    story.append(Spacer(1, 8))

    # The Problem
    story.append(p("The Problem", H2))
    story.append(p(
        "Before a migration merges, we need to answer: 'will this migration succeed against "
        "the real database?' That means knowing what depends on what."))
    story.append(Spacer(1, 4))
    story.append(tbl(["What we need to know", "Where the answer lives"], [
        [p("What objects exist today and how they relate", CELL),
         p("PostgreSQL's <b>pg_depend</b> catalog — ground truth", CELL)],
        [p("What a pending migration will create and reference", CELL),
         p("The <b>raw SQL text</b> of the migration file", CELL)],
    ], [USABLE * 0.45, USABLE * 0.55]))
    story.append(Spacer(1, 6))

    # Two-Source Merge — the core diagram
    story.append(p("The Decision: Two-Source Dependency Resolution", H2))
    story.append(mermaid("""
        flowchart TB
            subgraph "Source 1: Known World"
                PG["pg_depend catalog<br/>(one SQL query)"] --> EXACT["Exact dependency graph<br/>for every existing object"]
            end
            subgraph "Source 2: Pending Changes"
                SQL["Raw migration SQL"] --> AI["AI reads the text<br/>identifies creates + references"]
            end
            EXACT --> MERGE["Merged dependency graph"]
            AI --> MERGE
            MERGE --> CHECK{"Missing<br/>dependency?"}
            CHECK -->|Yes| BLOCK["Block PR merge"]
            CHECK -->|No| PASS["Safe to merge"]
            style BLOCK fill:#FDECEC,stroke:#E74C3C
            style PASS fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "pg_depend handles the known world with zero ambiguity. AI context reasoning handles "
        "pending migrations that don't exist in the catalog yet. The merge of both gives a "
        "complete picture with zero parsing code to maintain."))
    story.append(Spacer(1, 6))

    # Why Not Parse SQL?
    story.append(p("Why Not Parse SQL?", H2))
    story.append(mermaid("""
        flowchart TD
            Q{"How to find<br/>dependencies?"}
            Q -->|Parse SQL| BAD["Regex: brittle<br/>AST: fails on PL/pgSQL<br/>Manifests: drift from reality"]
            Q -->|Don't parse| GOOD["pg_depend: ground truth<br/>+ AI reads raw SQL<br/>= zero parsing code"]
            style BAD fill:#FDECEC,stroke:#E74C3C
            style GOOD fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 4))
    story.append(tbl(["Rejected Approach", "Why"], [
        [p("<b>Regex parsing</b>", CELL),
         p("Brittle. Breaks on dynamic DDL, PL/pgSQL, conditional creates.", CELL)],
        [p("<b>Full AST parser</b>", CELL),
         p("Fails on Supabase extensions. Heavy dependency for marginal gain.", CELL)],
        [p("<b>Manifest/header files</b>", CELL),
         p("Developer burden. Drifts from reality. Another thing to sync.", CELL)],
        [p("<b>pg_depend alone</b>", CELL),
         p("Can't see pending migrations. Only knows current state.", CELL)],
        [p("<b>Context reasoning alone</b>", CELL),
         p("Works but no ground-truth anchor. May miss subtle dependencies.", CELL)],
    ], [USABLE * 0.28, USABLE * 0.72]))
    story.append(Spacer(1, 6))

    # How It Fits
    story.append(p("How It Fits Together", H2))
    story.append(mermaid("""
        flowchart LR
            A["All migrations in<br/>cerebro-migrations<br/>(ADR-2026-38)"] --> B["CI spins up<br/>ephemeral Postgres"]
            B --> C["Apply full<br/>migration stack"]
            C --> D["elt-forge validates<br/>dependency graph<br/>(this ADR)"]
            D --> E{"Pass?"}
            E -->|Yes| F["PR can merge"]
            E -->|No| G["PR blocked"]
            style F fill:#E8F0EC,stroke:#2D6B4A
            style G fill:#FDECEC,stroke:#E74C3C
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>ADR-2026-38</b> answers where migrations live and who owns them. "
        "<b>This ADR</b> answers how we validate them. Together they form the "
        "complete migration safety system."))
    story.append(Spacer(1, 6))

    # When to Revisit
    story.append(p("When to Revisit", H2))
    story.append(p("• If schema count exceeds ~50 and context window pressure becomes real"))
    story.append(p("• If a production failure traces back to AI misreading a pending migration"))
    story.append(p("• If PostgreSQL changes pg_depend semantics (unlikely — stable since 8.0)"))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-37: Migration Validation via pg_depend", content)
