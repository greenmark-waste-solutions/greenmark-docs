#!/usr/bin/env python3
"""MEMO-002 — Why Foundation-First Wins at the Speed of AI"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "memos" / "MEMO-002-foundation-first-at-speed-of-ai.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "MEMO-002", "Internal Tech Memo — Thesis"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Date:</b> 2026-03-11  |  <b>Author:</b> Daniel Shanklin / Director of AI &amp; Technology  |  "
                   "<b>Classification:</b> Internal", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Review Date:</b> 2027-03-11 — evaluate this thesis against 12 months of execution", META))
    story.append(Spacer(1, 8))

    # ── What This Document Is ──
    story.append(AccentBox(USABLE,
                           "This memo captures a thesis about how AI-assisted engineering changes the "
                           "calculus on infrastructure investment. Unlike MEMO-001 (a numerical prediction), "
                           "this is a strategic argument: that building the foundation right — security, "
                           "architecture, documentation — is not overhead when AI makes execution fast. "
                           "It's the compounding asset that makes everything after it faster.",
                           bold=False, size=8))
    story.append(Spacer(1, 10))

    # ── The Thesis ──
    story.append(p("The Thesis", H1))
    story.append(AccentBox(USABLE,
                           "When engineering velocity is limited by human typing speed and context switching, "
                           "infrastructure investment feels expensive — every hour on architecture is an hour "
                           "not shipping features. When engineering velocity is limited by AI context and "
                           "decision quality, infrastructure investment compounds — every ADR, every SOP, "
                           "every security decision becomes reusable context that makes every future session faster."))
    story.append(Spacer(1, 8))

    # ── The Traditional Risk ──
    story.append(p("The Traditional Risk Model (and Why It's Wrong Here)", H2))
    story.append(p(
        "Standard startup advice says: ship value fast, get stakeholder buy-in with visible results, "
        "worry about architecture later. The fear is that if you spend too long building infrastructure "
        "before showing value, leadership loses patience and pulls funding."))
    story.append(Spacer(1, 4))
    story.append(p(
        "This risk model assumes two things:"))
    story.append(Spacer(1, 4))
    story.append(tbl(["Assumption", "Traditional", "Our Situation"], [
        [p("<b>Stakeholder patience</b>", CELL),
         p("Limited. Must prove value quarterly.", CELL),
         p("Leadership has granted buy-in. They understand the investment.", CELL)],
        [p("<b>Engineering speed</b>", CELL),
         p("Fixed. Every hour on infra = one fewer hour on features.", CELL),
         p("AI-assisted. Infrastructure hours produce reusable context "
           "that accelerates all future feature hours.", CELL)],
    ], [USABLE * 0.22, USABLE * 0.39, USABLE * 0.39]))
    story.append(Spacer(1, 4))
    story.append(p(
        "When both assumptions are wrong — when you have buy-in and AI velocity — the traditional "
        "risk model inverts. The real risk becomes shipping fast on a weak foundation, then paying "
        "the compounding cost of fixing it across 10 data sources instead of 1."))
    story.append(hr())

    # ── The Compounding Effect ──
    story.append(p("How Foundation Decisions Compound", H1))
    story.append(p(
        "Every decision documented in an ADR is a decision the AI never has to re-derive. "
        "Every SOP is a procedure the AI follows without negotiation. Every security constraint "
        "baked into the architecture is a vulnerability that can never be introduced by a future "
        "session that doesn't know the history."))
    story.append(Spacer(1, 6))

    story.append(p("Concrete examples from the first 39 ADRs:", BODY))
    story.append(Spacer(1, 4))
    story.append(tbl(["Decision", "One-Time Cost", "Compounding Benefit"], [
        [p("<b>ADR-2026-09:</b> Service role revoked from gold", CELL),
         p("2 hours to implement", CELL),
         p("Every future connector inherits gold-layer security automatically. "
           "No connector can accidentally write to gold. Ever.", CELL)],
        [p("<b>ADR-2026-11:</b> Default-deny RLS", CELL),
         p("3 hours to design + implement", CELL),
         p("Every new gold table gets entity isolation by default. "
           "NTX can never see Memphis data. No per-table security review needed.", CELL)],
        [p("<b>ADR-2026-38:</b> Unified migration authority", CELL),
         p("1 hour to consolidate", CELL),
         p("Every new vendor integration is one PR in one repo. "
           "Cross-repo ordering failures structurally eliminated.", CELL)],
        [p("<b>ADR-2026-33:</b> SKIP LOCKED job queue", CELL),
         p("4 hours to build", CELL),
         p("Every new data source plugs into the same queue. "
           "No new infrastructure per vendor. YAML file + connector = done.", CELL)],
        [p("<b>ADR-2026-39:</b> No DAG scheduler", CELL),
         p("0 hours (said no)", CELL),
         p("No unnecessary abstraction to maintain. Priority + _depends_on "
           "handles the flat topology. Revisit trigger documented.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.18, USABLE * 0.57]))
    story.append(Spacer(1, 6))

    story.append(p(
        "Total investment in these 5 decisions: approximately 10 hours. "
        "But every future data source — Sage, Navusoft, QuickBooks, ServiceTitan, fleet telematics — "
        "inherits all of them for free. The 10 hours are amortized across every table, every connector, "
        "every dashboard built from now on."))
    story.append(hr())

    # ── The AI Multiplier ──
    story.append(p("The AI Multiplier", H1))
    story.append(p(
        "In traditional engineering, documentation is a tax. You write it because someone told you to, "
        "and it's stale by next quarter. With AI-assisted engineering, documentation is the multiplier. "
        "Every ADR is a prompt. Every SOP is a constraint. The AI reads them at the start of every "
        "session and internalizes 39 decisions in 30 seconds."))
    story.append(Spacer(1, 6))

    story.append(mermaid("""
        flowchart TD
            subgraph "Traditional Engineering"
                T_DOC["Write docs<br/>(tax — time spent not coding)"] --> T_STALE["Docs go stale<br/>(no one reads them)"]
                T_STALE --> T_REDO["New dev re-derives decisions<br/>(wastes weeks)"]
                T_REDO --> T_DRIFT["Architecture drifts<br/>(entropy wins)"]
            end
            subgraph "AI-Assisted Engineering"
                A_DOC["Write ADR/SOP<br/>(investment — context for AI)"] --> A_READ["AI reads at session start<br/>(39 decisions in 30 seconds)"]
                A_READ --> A_INHERIT["Every session inherits<br/>full architectural context"]
                A_INHERIT --> A_COMPOUND["Decisions compound<br/>(consistency across 10+ sources)"]
            end
            style T_DRIFT fill:#FDECEC,stroke:#E74C3C
            style A_COMPOUND fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 6))

    story.append(p(
        "A human developer joining the team would need weeks to internalize the security model, "
        "the medallion architecture, the migration authority pattern, and the entity isolation design. "
        "An AI agent reads the CLAUDE.md and 39 ADRs in the first 30 seconds of every session. "
        "The documentation isn't overhead — it's the programming language for AI judgment."))
    story.append(hr())

    # ── The Real Risk ──
    story.append(p("The Real Risk: Getting It Wrong on Source #1", H1))
    story.append(p(
        "Consider the alternative timeline: skip the ADRs, skip the security design, ship HubSpot fast, "
        "then add Sage, Navusoft, QuickBooks, and ServiceTitan. What happens?"))
    story.append(Spacer(1, 4))

    story.append(tbl(["Source #", "Without Foundation", "With Foundation"], [
        [p("<b>#1 HubSpot</b>", CELL),
         p("Ships 2 weeks faster. No RLS. No entity isolation. "
           "Works fine — only 1 entity using it.", CELL),
         p("Ships 2 weeks slower. RLS baked in. Entity isolation from day one. "
           "Feels over-engineered for 1 source.", CELL)],
        [p("<b>#2 Sage</b>", CELL),
         p("New patterns emerge. Some conflict with HubSpot's. "
           "Quick fixes. Technical debt accumulates.", CELL),
         p("Follows established patterns. YAML + connector. "
           "Inherits all security automatically.", CELL)],
        [p("<b>#5 ServiceTitan</b>", CELL),
         p("5 different security models. 5 different migration patterns. "
           "Retrofitting RLS across 200+ tables. 2-3 week project.", CELL),
         p("Same YAML. Same patterns. Same security. "
           "Indistinguishable from source #1 in architecture.", CELL)],
        [p("<b>#10</b>", CELL),
         p("Team refuses to touch the codebase. 'It's too fragile.' "
           "Rewrite discussions begin.", CELL),
         p("New AI session reads CLAUDE.md, inherits 39 decisions, "
           "adds source #10 like source #1.", CELL)],
    ], [USABLE * 0.10, USABLE * 0.45, USABLE * 0.45]))
    story.append(Spacer(1, 6))

    story.append(p(
        "The cost of fixing RLS, entity isolation, and migration authority at source #5 across 200+ tables "
        "dwarfs the cost of building it right at source #1 across 33 tables. The foundation investment "
        "is cheapest when the surface area is smallest."))
    story.append(hr())

    # ── The Scoreboard ──
    story.append(p("Current Scoreboard", H1))
    story.append(p(
        "Where the platform stands today — not to celebrate, but to anchor the thesis against "
        "concrete output."))
    story.append(Spacer(1, 4))

    story.append(StatCard(USABLE, [
        ("39", "ADRs"),
        ("33", "Tables Extracting"),
        ("16", "Gold Tables Live"),
        ("100%", "RLS Coverage"),
    ]))
    story.append(Spacer(1, 6))

    story.append(tbl(["Layer", "Status", "What's Done"], [
        [p("<b>Bronze</b>", CELL),
         p("100%", CELL),
         p("17 object tables + 16 association tables extracting from HubSpot. "
           "Post-sync smoke tests on every table.", CELL)],
        [p("<b>Silver</b>", CELL),
         p("100%", CELL),
         p("All materialized views deployed. Engagement associations migration ready. "
           "Backward-compat wrappers in place.", CELL)],
        [p("<b>Gold</b>", CELL),
         p("100%", CELL),
         p("16 gold tables with MERGE refresh. SECURITY DEFINER functions. "
           "RLS on every table. Service role revoked.", CELL)],
        [p("<b>Frontend</b>", CELL),
         p("~10%", CELL),
         p("Sales dashboard live. 15 gold tables awaiting UI. "
           "This is the next focus area.", CELL)],
        [p("<b>Infrastructure</b>", CELL),
         p("100%", CELL),
         p("YAML-driven ETL. SKIP LOCKED queue. Dependency enforcement. "
           "Unified migration authority. Post-sync tests.", CELL)],
    ], [USABLE * 0.15, USABLE * 0.10, USABLE * 0.75]))
    story.append(hr())

    # ── The Sequence ──
    story.append(p("The Sequence Going Forward", H2))
    story.append(mermaid("""
        flowchart LR
            FOUND["Foundation<br/>(DONE)"] --> HUBSPOT["HubSpot<br/>full pipeline<br/>(DONE)"]
            HUBSPOT --> DASH["Dashboards<br/>surface gold data<br/>(NEXT)"]
            DASH --> SRC2["Source #2<br/>Sage / Navusoft<br/>(AFTER)"]
            SRC2 --> SRC3["Sources #3-10<br/>repeat pattern"]
            style FOUND fill:#E8F0EC,stroke:#2D6B4A
            style HUBSPOT fill:#E8F0EC,stroke:#2D6B4A
            style DASH fill:#FDF8EC,stroke:#D4A843
    """))
    story.append(Spacer(1, 4))
    story.append(p(
        "The foundation is done. HubSpot is fully piped. The next step is surfacing value in dashboards — "
        "making the gold layer visible to the managers who need it. Then source #2 plugs into the same "
        "foundation with zero architectural changes."))
    story.append(hr())

    # ── The Bottom Line ──
    story.append(p("The Bottom Line", H1))
    story.append(AccentBox(USABLE,
                           "Foundation first, velocity second. Velocity is a consequence of foundation, "
                           "not a replacement for it. At the speed of AI, every decision we document today "
                           "is a decision that never needs to be re-derived — not by a human, not by an agent, "
                           "not at source #1, not at source #10. The efforts compound insanely. That's the thesis. "
                           "Check it in 12 months.",
                           bg=BRAND_LIGHT, border=ACCENT_GREEN, text_color=BRAND_GREEN))
    story.append(Spacer(1, 10))

    # ── How to Check This ──
    story.append(p("How to Validate This Thesis", H2))
    story.append(tbl(
        [p("<b>Check</b>", CELL), p("<b>Question</b>", CELL), p("<b>Success Looks Like</b>", CELL)],
        [
            [p("Source velocity", CELL_BOLD),
             p("How long did source #2 take vs source #1?", CELL),
             p("Meaningfully faster. Same patterns, no new architecture.", CELL)],
            [p("Security incidents", CELL_BOLD),
             p("Any entity isolation or RLS failures?", CELL),
             p("Zero. The foundation held.", CELL)],
            [p("AI session ramp", CELL_BOLD),
             p("Does a fresh AI session produce correct, secure code on first attempt?", CELL),
             p("Yes. ADRs and SOPs provide sufficient context.", CELL)],
            [p("Architecture drift", CELL_BOLD),
             p("Do sources #5-10 look architecturally identical to #1?", CELL),
             p("Yes. YAML + connector + same security model.", CELL)],
            [p("Rewrite discussions", CELL_BOLD),
             p("Has anyone suggested starting over?", CELL),
             p("No. The foundation accommodated growth.", CELL)],
        ],
        [USABLE * 0.17, USABLE * 0.38, USABLE * 0.45],
    ))
    story.append(Spacer(1, 8))

    story.append(p("Why We're Writing This Down", H2))
    story.append(p(
        "Because 'build it right the first time' is easy to say and hard to defend when someone asks "
        "'why isn't there a dashboard yet?' This memo is the defense — written before the outcome is known, "
        "so it can't be rationalized after the fact. In 12 months, either the compounding thesis held and "
        "the foundation paid for itself many times over, or it didn't and we learn something important "
        "about when to invest and when to ship."))


if __name__ == "__main__":
    build_doc(OUTPUT, "MEMO-002: Foundation-First at the Speed of AI", content)
