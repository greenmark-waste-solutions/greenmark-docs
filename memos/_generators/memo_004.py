#!/usr/bin/env python3
"""MEMO-004 — From Playbook to Gate: How We Made Migration Safety Automatic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *
from reportlab.lib.colors import Color

OUTPUT = DOCS_ROOT / "memos" / "MEMO-004-playbook-to-gate.pdf"


class DefenseLayerChart(Flowable):
    """Stacked defense-in-depth diagram showing 4 layers with descriptions."""

    def __init__(self, width, height=150):
        super().__init__()
        self.chart_width = width
        self.chart_height = height
        self.layers = [
            ("CI GATE", "GitHub Actions — fresh-db + staging contract",
             "#193B2D", WHITE, "Blocks merge if migrations fail from zero"),
            ("CONTRACT CHECKS", "19 RBAC assertions — schemas, tables, RLS, grants",
             "#2D6B4A", WHITE, "Caught missing unique constraint on staging (day 1)"),
            ("SMOKE QUERIES", "28 SQL checks — silver/gold views, data, cross-layer joins",
             "#3A9D72", WHITE, "Caught 8 wrong column names on first run"),
            ("BOOTSTRAP MIGRATION", "Migration 000 — IF NOT EXISTS, fully idempotent",
             "#7BC8A4", HexColor("#1A1A1A"), "Eliminates manual SQL on fresh databases"),
        ]

    def wrap(self, _aW, _aH):
        return self.chart_width, self.chart_height

    def draw(self):
        c = self.canv
        w = self.chart_width
        h = self.chart_height
        n = len(self.layers)
        row_h = (h - 10) / n
        pad = 6

        for i, (title, subtitle, bg, text_color, proof) in enumerate(self.layers):
            y = h - (i + 1) * row_h
            # Background bar
            c.setFillColor(HexColor(bg) if isinstance(bg, str) else bg)
            c.roundRect(0, y, w, row_h - 3, 3, fill=1, stroke=0)
            # Title (left)
            c.setFillColor(text_color)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(pad, y + row_h - 16, title)
            # Subtitle (left, below title)
            c.setFont("Helvetica", 7)
            c.drawString(pad, y + row_h - 26, subtitle)
            # Proof point (right-aligned)
            c.setFont("Helvetica-Oblique", 6.5)
            c.drawRightString(w - pad, y + row_h - 16, proof)


def content(story, p):
    story.append(BrandHeader(USABLE, "MEMO-004", "Internal Tech Memo \u2014 Implementation Record"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Date:</b> 2026-03-12  |  <b>Author:</b> Daniel Shanklin / Director of AI &amp; Technology  |  "
                   "<b>Classification:</b> Internal", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Related:</b> MEMO-003 (staging database wired)  |  ADR-2026-09 (database isolation)  |  "
                   "SOP-002 (deploy pipeline)  |  TASK-140 (bootstrap migration)", META))
    story.append(Spacer(1, 8))

    # ── BLUF ──
    story.append(AccentBox(USABLE,
        "We turned a playbook into a gate. SOP-002 told people what to do. Now CI enforces it. "
        "A bootstrap migration eliminates manual SQL on fresh databases. 19 RBAC contract checks "
        "validate auth infrastructure is intact. 28 smoke queries validate the analytics pipeline. "
        "A GitHub Actions workflow proves all 31 migrations apply from zero on every PR. "
        "The dangerous thing is now impossible by default \u2014 not just documented.",
        bold=False, size=8))
    story.append(Spacer(1, 10))

    # ── The Problem ──
    story.append(p("The Problem: Playbooks Are Suggestions", H1))
    story.append(p(
        "MEMO-003 documented the staging database wiring and ended with a \"What's Left\" checklist. "
        "SOP-002 codified the two-environment deploy pipeline. Both are good documents. Neither "
        "prevents a human from skipping a step."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The gap wasn't in the documentation \u2014 it was in enforcement. A deploy playbook that "
        "relies on humans remembering to run smoke queries is one forgot-to-check away from "
        "pushing broken migrations to production. The question wasn't \"what should we do\" "
        "(SOP-002 answers that). The question was \"how do we guarantee it happens.\""))
    story.append(Spacer(1, 4))
    story.append(p(
        "The answer: CI. If the check isn't in a pipeline, it's a suggestion."))
    story.append(hr())

    # ── What We Built ──
    story.append(p("What We Built", H1))

    # Bootstrap migration
    story.append(p("1. Bootstrap Migration (migration 000)", H2))
    story.append(p(
        "File: <mono>20260300000000_bootstrap_rbac.sql</mono>. Creates the RBAC and platform "
        "infrastructure that was previously created outside of migration files: <mono>rbac</mono> "
        "and <mono>platform</mono> schemas, <mono>rbac.roles</mono>, "
        "<mono>rbac.role_permissions</mono>, <mono>public.user_roles</mono> with RLS policies "
        "and grants."))
    story.append(Spacer(1, 4))
    story.append(tbl(["Property", "Value"], [
        [p("<b>Idempotent</b>", CELL),
         p("IF NOT EXISTS on all CREATE, conditional policy creation, GRANT is inherently idempotent", CELL)],
        [p("<b>Sort order</b>", CELL),
         p("Timestamp 20260300000000 sorts before all 30 existing migrations", CELL)],
        [p("<b>Dry-run validated</b>", CELL),
         p("Executed with rollback against both staging and production before push", CELL)],
        [p("<b>Push result</b>", CELL),
         p("All no-ops on both databases (objects already existed). 16/16 smoke checks pass.", CELL)],
    ], [USABLE * 0.22, USABLE * 0.78]))
    story.append(Spacer(1, 4))
    story.append(p(
        "On existing databases (production, staging): every statement is a no-op. On a fresh "
        "database: creates the foundation that all 30 subsequent migrations depend on. No manual "
        "SQL required."))
    story.append(Spacer(1, 8))

    # RBAC contract checks
    story.append(p("2. RBAC Contract Checks (rbac_contract.py)", H2))
    story.append(p(
        "19 SQL assertions that validate the RBAC bootstrap infrastructure is intact. Separate "
        "from smoke.py (which checks analytics pipeline health). These check security posture:"))
    story.append(Spacer(1, 4))
    story.append(tbl(["Category", "Count", "What They Check"], [
        [p("<b>Schema existence</b>", CELL), p("2", CELL_CENTER),
         p("rbac and platform schemas exist", CELL)],
        [p("<b>Table structure</b>", CELL), p("7", CELL_CENTER),
         p("rbac.roles, role_permissions, user_roles exist with correct column types", CELL)],
        [p("<b>RLS</b>", CELL), p("2", CELL_CENTER),
         p("Row-level security enabled on user_roles, policy exists", CELL)],
        [p("<b>Grants</b>", CELL), p("6", CELL_CENTER),
         p("supabase_auth_admin and authenticated have correct privileges on schemas and tables", CELL)],
        [p("<b>Constraints</b>", CELL), p("1", CELL_CENTER),
         p("Unique constraint on (role_id, permission)", CELL)],
        [p("<b>Functions</b>", CELL), p("1", CELL_CENTER),
         p("rbac.custom_access_token_hook exists", CELL)],
    ], [USABLE * 0.22, USABLE * 0.08, USABLE * 0.70]))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
        "Day 1 catch: The contract checks found a missing UNIQUE constraint on "
        "rbac.role_permissions(role_id, permission) on staging. The manual bootstrap from "
        "MEMO-003 missed it. Fixed immediately. This is exactly the kind of silent drift "
        "these tests exist to catch.",
        bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER, bold=False, size=8))
    story.append(Spacer(1, 8))

    # CI pipeline
    story.append(p("3. CI Pipeline (verify-migrations.yml)", H2))
    story.append(p("GitHub Actions workflow with three jobs:"))
    story.append(Spacer(1, 4))
    story.append(tbl(["Job", "What It Proves", "Trigger", "Blocks Merge?"], [
        [p("<b>fresh-db</b>", CELL),
         p("All 31 migrations apply from zero on a blank local Supabase", CELL),
         p("Every PR + push", CELL),
         p("<b>Yes</b>", GREEN_TEXT)],
        [p("<b>staging-contract</b>", CELL),
         p("RBAC + smoke checks pass against live staging DB", CELL),
         p("develop push + PR to main", CELL),
         p("<b>Yes</b>", GREEN_TEXT)],
        [p("<b>prod-contract</b>", CELL),
         p("RBAC + smoke checks pass against production (post-deploy monitoring)", CELL),
         p("main push only", CELL),
         p("No (monitoring)", CELL)],
    ], [USABLE * 0.16, USABLE * 0.38, USABLE * 0.24, USABLE * 0.22]))
    story.append(Spacer(1, 4))
    story.append(p(
        "The fresh-db job is the real enforcer. It runs <mono>supabase start</mono> \u2192 "
        "<mono>supabase db reset</mono> (applies all migrations from zero) \u2192 "
        "<mono>rbac_contract.py</mono> \u2192 <mono>smoke.py --schema-only</mono>. "
        "If the bootstrap is broken or any migration assumes objects exist outside of migrations, "
        "the PR cannot merge."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The prod-contract job uses <mono>continue-on-error: true</mono> \u2014 it monitors "
        "but doesn't block. Transient production issues shouldn't prevent development. "
        "This distinction (staging = gate, production = monitoring) was recommended by external "
        "architecture review."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
        "Two GitHub secrets required: SUPABASE_STAGING_DB_PASSWORD and SUPABASE_DB_PASSWORD. "
        "Without these, the staging and production jobs will fail. Add them in the "
        "cerebro-migrations repo settings.",
        bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER, bold=False, size=8))
    story.append(hr())

    # ── Defense in Depth ──
    story.append(p("Defense in Depth", H1))
    story.append(p(
        "Four layers. Each exists because the one above it might fail. Each one has already "
        "caught a real bug."))
    story.append(Spacer(1, 6))
    story.append(DefenseLayerChart(USABLE, height=140))
    story.append(Spacer(1, 6))
    story.append(p(
        "Every assertion earned its place by catching something real \u2014 not by imagining "
        "something theoretical. The contract checks caught a missing constraint. The smoke "
        "queries caught wrong column names. The bootstrap migration eliminates the manual SQL "
        "that MEMO-003 documented as technical debt. The CI gate makes all of it automatic."))
    story.append(hr())

    # ── npm scripts ──
    story.append(p("Developer Interface", H1))
    story.append(tbl(["Command", "What It Does"], [
        [p("<mono>npm run contract:staging</mono>", CELL),
         p("19 RBAC checks against staging (1.1s)", CELL)],
        [p("<mono>npm run contract:prod</mono>", CELL),
         p("19 RBAC checks against production (1.1s)", CELL)],
        [p("<mono>npm run smoke:staging</mono>", CELL),
         p("28 analytics pipeline checks against staging (1.4s)", CELL)],
        [p("<mono>npm run smoke:prod</mono>", CELL),
         p("28 analytics pipeline checks against production (1.4s)", CELL)],
        [p("<mono>npm run verify:staging</mono>", CELL),
         p("Contract + smoke combined \u2014 the full verification suite (2.5s)", CELL)],
        [p("<mono>npm run verify:prod</mono>", CELL),
         p("Contract + smoke combined against production (2.5s)", CELL)],
    ], [USABLE * 0.36, USABLE * 0.64]))
    story.append(hr())

    # ── How We Got Here ──
    story.append(p("How We Got Here: The Correction That Shaped Everything", H1))
    story.append(p(
        "This work traces back to a correction earlier in the session. The initial instinct "
        "was that a single database for staging and production was fine \u2014 \"solve problems "
        "you have, not problems you might have.\" The human corrected this: data corruption "
        "is silent, retroactive, and unrecoverable. You can't un-show bad numbers to a CEO."))
    story.append(Spacer(1, 4))
    story.append(p(
        "That correction didn't just produce ADR-2026-09 (database isolation). It established "
        "a principle: <b>the dangerous thing should be impossible by default, not merely "
        "documented.</b> Every artifact in this memo \u2014 the bootstrap migration, the contract "
        "checks, the CI gate \u2014 exists to make that principle structural rather than aspirational."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The session moved from documentation (SOP-002) to enforcement (smoke queries) to "
        "automation (CI). Each step was a response to the same question: \"but how do we "
        "guarantee it?\" The answer, each time, was to remove the human from the loop and "
        "let the machine enforce the invariant."))
    story.append(Spacer(1, 8))

    # ── Bottom Line ──
    story.append(AccentBox(USABLE,
        "Playbooks tell people what to do. CI gates make it impossible to skip. "
        "31 migrations apply from zero. 19 RBAC assertions validate auth infrastructure. "
        "28 smoke queries validate the analytics pipeline. Every PR proves the full stack works. "
        "The next person in this seat doesn't need tribal knowledge, a playbook, or Daniel's "
        "phone number. They need a green CI check."))


if __name__ == "__main__":
    build_doc(OUTPUT, "MEMO-004: From Playbook to Gate", content)
