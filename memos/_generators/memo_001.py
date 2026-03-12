#!/usr/bin/env python3
"""MEMO-001 — Unified Migration Authority: A 12-Month Prediction"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "memos" / "MEMO-001-unified-migration-prediction.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "MEMO-001", "Internal Tech Memo — Prediction"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Date:</b> 2026-03-11  |  <b>Author:</b> Daniel Shanklin / Director of AI &amp; Technology  |  "
                   "<b>Classification:</b> Internal", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Review Date:</b> 2027-03-11 — evaluate this prediction against reality", META))
    story.append(Spacer(1, 8))

    # ── What This Document Is ──
    story.append(AccentBox(USABLE,
                           "This is a tech memo — a new document type. Unlike ADRs (decisions) or SOPs "
                           "(procedures), a memo captures a moment and makes a prediction. Its purpose is "
                           "to be checked against reality later. If we were right, we learn to trust our "
                           "instincts. If we were wrong, we learn why.",
                           bold=False, size=8))
    story.append(Spacer(1, 10))

    # ── The Moment ──
    story.append(p("The Moment", H1))
    story.append(p(
        "On March 11, 2026, we executed ADR-2026-38 — consolidating all database schema management "
        "into a single <font face='Courier'>cerebro-migrations</font> repository. Before this, DDL was "
        "split between <font face='Courier'>cerebro</font> (21 migrations for silver/gold/RLS) and "
        "<font face='Courier'>data-daemon</font> (8 migrations for bronze tables). Both repos thought "
        "they owned the database. Neither did."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The cutover took approximately 1 hour. We created the repository, consolidated 29 migration "
        "files, synced them to Supabase, froze data-daemon's migration system with a runtime guard, "
        "removed cerebro's migration files entirely, and updated the deployment SOP."))
    story.append(Spacer(1, 4))
    story.append(p(
        "This is the first time we've restructured infrastructure proactively — before a crisis forced "
        "our hand. The question is: <b>was it worth it?</b>"))
    story.append(hr())

    # ── What We Did ──
    story.append(p("What Changed", H2))
    story.append(tbl(
        ["Before", "After"],
        [
            [p("Bronze DDL in data-daemon<br/>Silver/gold DDL in cerebro<br/>No single owner", CELL),
             p("All DDL in cerebro-migrations<br/>data-daemon = pure ETL runner<br/>cerebro = pure frontend", CELL)],
            [p("Deploy order was implicit<br/>Relied on developer memory<br/>Cross-repo dependency failures", CELL),
             p("Deploy order is explicit<br/>Single <font face='Courier'>npm run migrate</font> command<br/>Dependencies resolved in one sequence", CELL)],
            [p("New vendor = touch 2 repos<br/>Hope migration order is right<br/>Debug failures across repos", CELL),
             p("New vendor = one PR in one repo<br/>Bronze + silver + gold in sequence<br/>One place to debug", CELL)],
        ],
        [USABLE * 0.5, USABLE * 0.5],
    ))
    story.append(Spacer(1, 10))

    # ── The Prediction ──
    story.append(p("The Prediction", H1))
    story.append(AccentBox(USABLE,
                           "We predict this 1-hour investment will save approximately 61 hours of "
                           "engineering time over the next 12 months and prevent at least 2 production "
                           "incidents that would have been caused by cross-repo migration failures."))
    story.append(Spacer(1, 8))

    # ── Month by Month ──
    story.append(p("Projected Time Savings — Month by Month", H2))
    story.append(tbl(
        [p("<b>Month</b>", CELL), p("<b>Activity</b>", CELL),
         p("<b>Old Cost</b>", CELL_CENTER), p("<b>New Cost</b>", CELL_CENTER),
         p("<b>Saved</b>", CELL_CENTER)],
        [
            [p("Apr 2026", CELL_BOLD), p("Navusoft bronze+silver build-out", CELL),
             p("6h", CELL_CENTER), p("3h", CELL_CENTER), p("3h", GREEN_TEXT)],
            [p("May 2026", CELL_BOLD), p("Fleet bronze+silver build-out", CELL),
             p("6h", CELL_CENTER), p("3h", CELL_CENTER), p("3h", GREEN_TEXT)],
            [p("Jun 2026", CELL_BOLD), p("Sage expanded bronze tables + first gold refresh cycles", CELL),
             p("8h", CELL_CENTER), p("3h", CELL_CENTER), p("5h", GREEN_TEXT)],
            [p("Jul 2026", CELL_BOLD), p("HubSpot silver expansion (tickets, products, line items)", CELL),
             p("6h", CELL_CENTER), p("2h", CELL_CENTER), p("4h", GREEN_TEXT)],
            [p("Aug 2026", CELL_BOLD), p("Gold layer v2 — cross-vendor joins, RLS expansion", CELL),
             p("10h", CELL_CENTER), p("4h", CELL_CENTER), p("6h", GREEN_TEXT)],
            [p("Sep 2026", CELL_BOLD), p("Production incident avoided — migration ordering bug", CELL),
             p("4h", CELL_CENTER), p("0h", CELL_CENTER), p("4h", GREEN_TEXT)],
            [p("Oct 2026", CELL_BOLD), p("New vendor integration (QuickBooks or similar)", CELL),
             p("8h", CELL_CENTER), p("3h", CELL_CENTER), p("5h", GREEN_TEXT)],
            [p("Nov 2026", CELL_BOLD), p("Staging environment spin-up (test Supabase project)", CELL),
             p("6h", CELL_CENTER), p("2h", CELL_CENTER), p("4h", GREEN_TEXT)],
            [p("Dec 2026", CELL_BOLD), p("Year-end schema freeze + audit", CELL),
             p("4h", CELL_CENTER), p("1h", CELL_CENTER), p("3h", GREEN_TEXT)],
            [p("Jan 2027", CELL_BOLD), p("Production incident avoided — breaking change coordination", CELL),
             p("6h", CELL_CENTER), p("0h", CELL_CENTER), p("6h", GREEN_TEXT)],
            [p("Feb 2027", CELL_BOLD), p("Silver/gold refactoring — materialized view refresh tuning", CELL),
             p("8h", CELL_CENTER), p("2h", CELL_CENTER), p("6h", GREEN_TEXT)],
            [p("Mar 2027", CELL_BOLD), p("Annual review + onboarding second developer", CELL),
             p("14h", CELL_CENTER), p("2h", CELL_CENTER), p("12h", GREEN_TEXT)],
        ],
        [0.7 * inch, USABLE * 0.42, 0.65 * inch, 0.65 * inch, 0.55 * inch],
    ))
    story.append(Spacer(1, 6))

    story.append(StatCard(USABLE, [
        ("1h", "Investment"),
        ("61h", "Projected Savings"),
        ("61x", "ROI"),
        ("2", "Incidents Prevented"),
    ]))
    story.append(Spacer(1, 10))

    # ── Key Assumptions ──
    story.append(p("Key Assumptions Behind This Prediction", H2))
    story.append(p("These are the bets we're making. If any turn out wrong, the savings change:"))
    story.append(Spacer(1, 4))
    rows = [
        ("We add 2-3 new vendor integrations in 12 months",
         "If we only add 1, cut savings by ~8h. If we add 4+, add ~10h."),
        ("At least 1 developer joins who needs to understand the migration system",
         "The 12h onboarding savings in March 2027 assumes this. If it's still solo, cut that to 2h."),
        ("We hit at least 2 cross-schema dependency situations",
         "The old system would have caused ordering failures. If our schemas stay simple, these don't manifest."),
        ("data-daemon connectors continue expanding",
         "Each new connector means new bronze tables. Single-repo DDL saves ~2h per connector."),
    ]
    for assumption, impact in rows:
        story.append(p(f"<b>{assumption}.</b> {impact}", BODY))
        story.append(Spacer(1, 3))
    story.append(hr())

    # ── How to Check This ──
    story.append(p("How to Validate This Prediction", H1))
    story.append(p(
        "On or after March 11, 2027, review this memo. Score each month's prediction against reality. "
        "The honest answer might be 'we saved more' or 'we saved less' or 'the whole roadmap changed.' "
        "All outcomes are useful — the point is calibrating our ability to predict engineering ROI."))
    story.append(Spacer(1, 6))

    story.append(tbl(
        [p("<b>Check</b>", CELL), p("<b>Question</b>", CELL), p("<b>Where to Look</b>", CELL)],
        [
            [p("Vendor count", CELL_BOLD), p("How many new vendors were integrated?", CELL),
             p("cerebro-migrations git log", CELL)],
            [p("Incident count", CELL_BOLD), p("How many migration-related incidents occurred?", CELL),
             p("Devlogs, incident channel, deploy logs", CELL)],
            [p("Time per integration", CELL_BOLD), p("How long did each new vendor take end-to-end?", CELL),
             p("Git timestamps on PRs, devlog entries", CELL)],
            [p("Onboarding", CELL_BOLD), p("Did a new developer touch the migration system? How long to ramp?", CELL),
             p("Ask them directly", CELL)],
            [p("Complexity growth", CELL_BOLD), p("How many total migrations exist? Any cross-schema issues?", CELL),
             p("<font face='Courier'>npm run migrate:status</font>", CELL)],
        ],
        [1.0 * inch, USABLE * 0.42, USABLE - 1.0 * inch - USABLE * 0.42],
    ))
    story.append(Spacer(1, 10))

    # ── Why This Matters ──
    story.append(p("Why We're Writing This Down", H2))
    story.append(p(
        "Most infrastructure improvements are invisible. Nobody counts the incidents that didn't happen "
        "or the hours that weren't wasted. By writing the prediction down now — before we know the answer — "
        "we create an honest benchmark. In 12 months, we'll know if we're good at predicting the value of "
        "structural work, or if we're fooling ourselves."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "The goal isn't to be right. It's to get better at knowing what's worth doing.",
                           bg=BRAND_LIGHT, border=ACCENT_GREEN, text_color=BRAND_GREEN))


if __name__ == "__main__":
    build_doc(OUTPUT, "MEMO-001: Unified Migration Prediction", content)
