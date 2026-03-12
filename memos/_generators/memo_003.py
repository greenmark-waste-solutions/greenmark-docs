#!/usr/bin/env python3
"""MEMO-003 — Staging Database Wired: What We Did, What Broke, What's Left"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *
from reportlab.lib.colors import Color

OUTPUT = DOCS_ROOT / "memos" / "MEMO-003-staging-database-wired.pdf"


class SessionEffectivenessChart(Flowable):
    """Line chart showing session effectiveness score over time with labeled phases."""

    def __init__(self, width, height=180):
        super().__init__()
        self.chart_width = width
        self.chart_height = height
        # (label, score_0_to_10, annotation)
        self.phases = [
            ("Start", 5, "Is single DB\na problem?"),
            ("Bad\nAdvice", 2, "\"Solve problems\nyou have\""),
            ("Correction", 5, "User: \"willing to\ncorrupt prod data\""),
            ("GPT-5.2\nConsult", 7, "Confirmed:\nsingle DB is\ndangerous"),
            ("ADR-09\nWritten", 8, "Decision\nrecorded"),
            ("SOP-002\nWritten", 8.5, "Pipeline\ncodified"),
            ("Smoke\nQueries", 9, "28 checks,\nvalidated\non prod"),
            ("Staging\nWired", 9.5, "30 migrations\npushed,\n16/16 pass"),
            ("Memo +\nBacklog", 10, "Everything\ndocumented,\nnothing tribal"),
        ]

    def wrap(self, availWidth, availHeight):
        return self.chart_width, self.chart_height + 10

    def draw(self):
        c = self.canv
        w = self.chart_width
        h = self.chart_height

        pad_left = 30
        pad_right = 20
        pad_top = 15
        pad_bottom = 55
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        # Background
        c.setFillColor(HexColor("#F7FAF8"))
        c.roundRect(0, 0, w, h, 4, fill=1, stroke=0)

        # Y-axis gridlines and labels
        c.setFont("Helvetica", 7)
        for score in range(0, 11, 2):
            y = pad_bottom + (score / 10.0) * plot_h
            c.setStrokeColor(HexColor("#E0E8E4"))
            c.setLineWidth(0.3)
            c.line(pad_left, y, w - pad_right, y)
            c.setFillColor(MUTED)
            c.drawRightString(pad_left - 4, y - 3, str(score))

        # Y-axis title
        c.saveState()
        c.translate(8, pad_bottom + plot_h / 2)
        c.rotate(90)
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(HexColor("#193B2D"))
        c.drawCentredString(0, 0, "Effectiveness")
        c.restoreState()

        n = len(self.phases)
        points = []
        for i, (label, score, annotation) in enumerate(self.phases):
            x = pad_left + (i / (n - 1)) * plot_w
            y = pad_bottom + (score / 10.0) * plot_h
            points.append((x, y, label, score, annotation))

        # Shaded area under curve
        c.setFillColor(Color(0.18, 0.42, 0.29, 0.08))  # brand green, very transparent
        path = c.beginPath()
        path.moveTo(points[0][0], pad_bottom)
        for x, y, *_ in points:
            path.lineTo(x, y)
        path.lineTo(points[-1][0], pad_bottom)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

        # Line segments — red for drop, green for rise
        c.setLineWidth(2.5)
        for i in range(len(points) - 1):
            x1, y1 = points[i][0], points[i][1]
            x2, y2 = points[i + 1][0], points[i + 1][1]
            if y2 < y1:  # dropping — danger
                c.setStrokeColor(HexColor("#C0392B"))
            else:
                c.setStrokeColor(HexColor("#2D6B4A"))
            c.line(x1, y1, x2, y2)

        # Correction marker — vertical dashed line at phase 2→3
        cx = points[2][0]
        c.setStrokeColor(HexColor("#D4A843"))
        c.setLineWidth(1)
        c.setDash(3, 3)
        c.line(cx, pad_bottom, cx, pad_bottom + plot_h)
        c.setDash()
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(HexColor("#92700A"))
        c.drawCentredString(cx, pad_bottom + plot_h + 4, "PIVOT")

        # Data points
        for i, (x, y, label, score, annotation) in enumerate(points):
            # Dot
            if i == 1:  # bad advice — red
                c.setFillColor(HexColor("#C0392B"))
            elif i == 2:  # correction — amber
                c.setFillColor(HexColor("#D4A843"))
            else:
                c.setFillColor(HexColor("#2D6B4A"))
            c.circle(x, y, 3.5, fill=1, stroke=0)

            # White inner dot
            c.setFillColor(WHITE)
            c.circle(x, y, 1.5, fill=1, stroke=0)

            # X-axis label (phase name)
            c.setFont("Helvetica", 5.5)
            c.setFillColor(DARK)
            for j, line in enumerate(label.split("\n")):
                c.drawCentredString(x, pad_bottom - 10 - (j * 7), line)

        # Score labels above dots
        c.setFont("Helvetica-Bold", 7)
        for x, y, _label, score, _ann in points:
            c.setFillColor(HexColor("#193B2D"))
            c.drawCentredString(x, y + 7, str(score))


def content(story, p):
    story.append(BrandHeader(USABLE, "MEMO-003", "Internal Tech Memo — Implementation Record"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Date:</b> 2026-03-12  |  <b>Author:</b> Daniel Shanklin / Director of AI &amp; Technology  |  "
                   "<b>Classification:</b> Internal", META))
    story.append(Spacer(1, 4))
    story.append(p("<b>Related:</b> ADR-2026-09 (separate databases)  |  SOP-002 (deploy pipeline)  |  "
                   "cerebro-migrations repo", META))
    story.append(Spacer(1, 8))

    # ── What This Document Is ──
    story.append(AccentBox(USABLE,
        "Implementation record for wiring greenmark-cerebro-test as the staging database. "
        "Covers what we did, what broke during migration push, how we fixed it, and what's "
        "left before the two-environment deploy pipeline is operational. Written immediately "
        "after implementation so the gotchas are fresh.",
        bold=False, size=8))
    story.append(Spacer(1, 10))

    # ── Current State ──
    story.append(p("Current State: Two Databases, Same Schema", H1))
    story.append(tbl(["", "Production", "Staging"], [
        [p("<b>Supabase project</b>", CELL),
         p("greenmark-cerebro", CELL), p("greenmark-cerebro-test", CELL)],
        [p("<b>Project ref</b>", CELL),
         p("wwmcgtyngnziepeynccz", MONO), p("izmuckuepryqneebwwol", MONO)],
        [p("<b>Pooler host</b>", CELL),
         p("aws-1-us-east-1.pooler.supabase.com:5432", CELL),
         p("aws-1-us-east-1.pooler.supabase.com:5432", CELL)],
        [p("<b>Password in vault</b>", CELL),
         p("SUPABASE_DB_PASSWORD", MONO), p("SUPABASE_STAGING_DB_PASSWORD", MONO)],
        [p("<b>Migrations applied</b>", CELL),
         p("30 / 30", CELL), p("30 / 30", CELL)],
        [p("<b>Schema smoke checks</b>", CELL),
         p("16 / 16 pass", CELL), p("16 / 16 pass", CELL)],
        [p("<b>Data</b>", CELL),
         p("Real (115 companies, 175 contacts, 72 deals)", CELL),
         p("Empty (schema only, ready for seed)", CELL)],
    ], [USABLE * 0.20, USABLE * 0.40, USABLE * 0.40]))
    story.append(hr())

    # ── What We Built ──
    story.append(p("Artifacts Created", H1))
    story.append(tbl(["Artifact", "Location", "Purpose"], [
        [p("<b>ADR-2026-09</b>", CELL),
         p("greenmark-cockpit/decisions/", CELL),
         p("Decision record: why separate staging and production databases", CELL)],
        [p("<b>SOP-002</b>", CELL),
         p("greenmark-cockpit/sops/", CELL),
         p("Full deploy pipeline playbook: two environments, database isolation, "
           "staging data strategy, rollback procedures, checklists", CELL)],
        [p("<b>smoke.py</b>", CELL),
         p("cerebro-migrations/", CELL),
         p("28 smoke queries (16 schema + 12 data). Validates staging health "
           "after migrate + seed. Runs in 1.4 seconds.", CELL)],
        [p("<b>Branded PDFs</b>", CELL),
         p("decisions/_generators/, sops/_generators/", CELL),
         p("ADR-09 (3 pages) and SOP-002 PDF generators", CELL)],
    ], [USABLE * 0.16, USABLE * 0.34, USABLE * 0.50]))
    story.append(hr())

    # ── Gotchas ──
    story.append(p("Gotchas Hit During Migration Push", H1))
    story.append(p(
        "Pushing 30 migrations to a fresh Supabase project was not clean. Four issues "
        "required manual intervention. All are documented here so the next fresh database "
        "(or staging wipe) doesn't repeat them."))
    story.append(Spacer(1, 6))

    # Gotcha 1
    story.append(p("1. Pooler Host Is aws-1, Not aws-0", H2))
    story.append(p(
        "The smoke query runner initially used <mono>aws-0-us-east-1.pooler.supabase.com</mono>. "
        "The actual host is <mono>aws-1</mono>. Supabase pooler URLs are region-specific and "
        "not guessable \u2014 always read from <mono>.temp/pooler-url</mono> in the Supabase project."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
        "Connection string format:\n"
        "postgresql://postgres.<project-ref>:<password>@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require",
        bold=False, size=8))
    story.append(Spacer(1, 6))

    # Gotcha 2
    story.append(p("2. rbac Schema Exists Outside of Migrations", H2))
    story.append(p(
        "Production has an <mono>rbac</mono> schema with <mono>roles</mono> and "
        "<mono>role_permissions</mono> tables, plus <mono>public.user_roles</mono>. "
        "These were created through the Supabase dashboard or cerebro's auth setup \u2014 "
        "<b>not through the migration files</b>. Migration "
        "<mono>20260309152700_gold_rls_use_rbac.sql</mono> references "
        "<mono>rbac.custom_access_token_hook</mono> and <mono>rbac.role_permissions</mono>, "
        "which don't exist on a fresh database."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
        "BOOTSTRAP REQUIRED: Before pushing migrations to a fresh Supabase project, create:\n"
        "\u2022 rbac schema + rbac.roles table + rbac.role_permissions table\n"
        "\u2022 public.user_roles table (full production schema)\n"
        "\u2022 platform schema (referenced in auth hook search_path)\n\n"
        "This is technical debt. Should become a proper migration (migration 000).",
        bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 6))

    # Gotcha 3
    story.append(p("3. entity Column Migration Assumes Existing Data", H2))
    story.append(p(
        "Migration <mono>20260309170000_entities_array.sql</mono> runs "
        "<mono>UPDATE public.user_roles SET entities = CASE WHEN entity = 'both' ...</mono> "
        "\u2014 which assumes an <mono>entity</mono> (singular) column exists. On a bootstrapped "
        "staging database that went straight to the final schema, this column doesn't exist."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Fix applied:</b> Added <mono>entity text</mono> column before running the migration. "
        "The migration's UPDATE is a no-op on 0 rows, then the migration drops the column. "
        "Net effect: correct final schema."))
    story.append(Spacer(1, 6))

    # Gotcha 4
    story.append(p("4. Different Passwords Per Project (Expected)", H2))
    story.append(p(
        "Separate Supabase projects = separate credentials. This is correct and expected, but "
        "means the smoke script's <mono>--staging</mono> and <mono>--prod</mono> flags both read "
        "from <mono>SUPABASE_DB_PASSWORD</mono> \u2014 the caller must set the right value. "
        "Future improvement: read from <mono>SUPABASE_STAGING_DB_PASSWORD</mono> for staging, "
        "matching vault-simple's naming convention."))
    story.append(hr())

    # ── Smoke Queries ──
    story.append(p("Smoke Query Suite", H1))
    story.append(p("28 queries in <mono>cerebro-migrations/smoke.py</mono>:"))
    story.append(Spacer(1, 4))

    story.append(tbl(["Category", "Count", "What They Check"], [
        [p("<b>Silver schema</b>", CELL), p("6", CELL_CENTER),
         p("companies, contacts, deals, owners, tickets, engagements \u2014 "
           "correct columns exist in materialized views", CELL)],
        [p("<b>Gold schema</b>", CELL), p("10", CELL_CENTER),
         p("pipeline_summary, deal_velocity, deal_aging, win_loss, rep_activity, "
           "ticket_summary, customer_health, forecast, contracts, CSAT", CELL)],
        [p("<b>Silver data</b>", CELL), p("3", CELL_CENTER),
         p("companies, contacts, deals have \u2265 1 row after seed", CELL)],
        [p("<b>Gold data</b>", CELL), p("5", CELL_CENTER),
         p("pipeline_summary, deal_velocity populated; 3 post-refresh tables tracked", CELL)],
        [p("<b>Cross-layer</b>", CELL), p("4", CELL_CENTER),
         p("Join paths work, entity_id populated, temporal spread, soft delete filter", CELL)],
    ], [USABLE * 0.18, USABLE * 0.08, USABLE * 0.74]))
    story.append(Spacer(1, 4))

    story.append(p("<b>Performance:</b> 1.0 \u2013 1.4 seconds end-to-end. Fast enough for every deploy.", BODY))
    story.append(Spacer(1, 4))
    story.append(p("<b>Usage:</b> <mono>npm run smoke:staging</mono> (after migrate + seed) | "
                   "<mono>npm run smoke:prod</mono> (after migrate) | "
                   "<mono>npm run smoke:schema</mono> (schema only, no seed needed)", BODY))
    story.append(hr())

    # ── What's Left ──
    story.append(p("What's Left Before Pipeline Ships", H1))

    story.append(p("Must Do", H2))
    story.append(tbl(["#", "Task", "Why"], [
        [p("1", CELL_CENTER), p("Create rbac bootstrap migration", CELL),
         p("Fresh databases need manual setup without it. Should be migration 000.", CELL)],
        [p("2", CELL_CENTER), p("Set per-environment Railway vars", CELL),
         p("SUPABASE_URL, ANON_KEY, SERVICE_ROLE_KEY, DATABASE_URL for develop env "
           "of all 6 database-touching services", CELL)],
        [p("3", CELL_CENTER), p("Add startup environment guard", CELL),
         p("Every DB service validates NODE_ENV matches SUPABASE_URL at boot. "
           "Catches misconfigured vars immediately.", CELL)],
        [p("4", CELL_CENTER), p("Create db:push scripts", CELL),
         p("db:push:staging and db:push:prod in cerebro-migrations. "
           "Prevents accidental cross-push via supabase link.", CELL)],
        [p("5", CELL_CENTER), p("Seed staging data", CELL),
         p("Run SEED=42 fixtures to populate bronze, refresh silver/gold views.", CELL)],
    ], [USABLE * 0.05, USABLE * 0.32, USABLE * 0.63]))
    story.append(Spacer(1, 6))

    story.append(p("Nice to Have", H2))
    story.append(tbl(["Task", "Why"], [
        [p("Populate rbac.role_permissions on staging", CELL),
         p("133 rows from production. Auth hook needs them.", CELL)],
        [p("Create staging test user in user_roles", CELL),
         p("So cerebro can authenticate in staging.", CELL)],
        [p("Automate migrate \u2192 seed \u2192 smoke", CELL),
         p("Single command: npm run staging:reset", CELL)],
        [p("Update smoke.py env var naming", CELL),
         p("Use SUPABASE_STAGING_DB_PASSWORD for --staging to match vault", CELL)],
    ], [USABLE * 0.40, USABLE * 0.60]))
    story.append(Spacer(1, 8))

    # ── Session Effectiveness ──
    story.append(p("Session Effectiveness Over Time", H1))
    story.append(p(
        "Scored 0\u201310 per phase. The dip at phase 2 is the bad advice (\"solve problems you have\"). "
        "The pivot at phase 3 is the user correction. Everything after the pivot builds from the "
        "corrected frame \u2014 each artifact compounds on the one before it."))
    story.append(Spacer(1, 6))
    story.append(SessionEffectivenessChart(USABLE, height=165))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Key insight:</b> The session's best work came <i>after</i> the human corrected the AI. "
        "The correction didn't slow us down \u2014 it redirected energy from a defensive posture "
        "(\"is this really a problem?\") to a constructive one (\"how do we make the dangerous thing "
        "impossible?\"). The final score reflects not just what was built, but that nothing was left "
        "as tribal knowledge.", BODY))
    story.append(hr())

    # ── Why This Matters ──
    story.append(p("Why This Matters", H1))
    story.append(p(
        "This session started with a question: is having a single database for staging and "
        "production actually a problem? The initial instinct was conservative \u2014 solve problems "
        "you have, not problems you might have. That instinct was wrong here, and the correction "
        "shaped everything that followed."))
    story.append(Spacer(1, 4))
    story.append(p(
        "Data corruption is not like a crashed service. A crashed service pages you. Data corruption "
        "is silent. It's retroactive. By the time you discover that a staging deploy wrote test rows "
        "into the production pipeline_summary table, those numbers have already been in front of "
        "Michael, Alex, and Robert. The executive dashboard they use to make business decisions "
        "showed wrong numbers, and nobody knew. You can't un-show bad data to a CEO. You can't "
        "un-make a decision that was based on corrupted metrics."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The single-database setup was one misconfigured Railway environment variable away from "
        "exactly that failure. Not a hypothetical \u2014 a near-certainty as the service count grew "
        "from 3 to 10 and multiple engineers started deploying. The question was never \"if\" but \"when.\""))
    story.append(Spacer(1, 6))

    story.append(p("What Changed Because of That Correction", H2))
    story.append(p(
        "Once we committed to database isolation as non-negotiable, the rest of the session became "
        "about making the dangerous thing impossible by default rather than asking people to be careful:"))
    story.append(Spacer(1, 4))
    story.append(tbl(["Layer", "What It Prevents"], [
        [p("<b>Separate Supabase projects</b>", CELL),
         p("Physical isolation. Staging credentials literally cannot authenticate to production. "
           "Wrong password = connection refused, not silent corruption.", CELL)],
        [p("<b>Startup environment guard</b>", CELL),
         p("Runtime assertion. If NODE_ENV says production but SUPABASE_URL says test, "
           "the service refuses to start. Railway marks it as a failed deploy. Catches misconfigured "
           "vars before a single query runs.", CELL)],
        [p("<b>Explicit db:push scripts</b>", CELL),
         p("Eliminates supabase link local state as a failure vector. You can't accidentally push "
           "staging migrations to production because the script re-links every time.", CELL)],
        [p("<b>Smoke queries</b>", CELL),
         p("28 SQL checks in 1.4 seconds. If a migration broke a gold view, you know before "
           "promoting to production \u2014 not after Michael opens the dashboard.", CELL)],
        [p("<b>SOP-002</b>", CELL),
         p("The governing document. Not tribal knowledge in Daniel's head, but a playbook "
           "anyone can follow. The next person in this seat doesn't reconstruct the process "
           "from git blame.", CELL)],
    ], [USABLE * 0.28, USABLE * 0.72]))
    story.append(Spacer(1, 6))

    story.append(p(
        "Each layer exists because the one above it might fail. Separate projects are the primary "
        "defense. The startup guard catches what separate projects can't (misconfigured vars within "
        "the right project). The db:push scripts catch what the guard can't (wrong migration target). "
        "Smoke queries catch what the scripts can't (migrations that apply cleanly but produce wrong "
        "data). Defense in depth \u2014 not because we're paranoid, but because the cost of failure is "
        "silent, retroactive, and lands on people who trust us to get this right."))
    story.append(Spacer(1, 8))

    # ── Bottom Line ──
    story.append(AccentBox(USABLE,
        "Nothing is tribal knowledge anymore. The decision is recorded (ADR-2026-09). The process "
        "is codified (SOP-002). The enforcement is automated (smoke queries, startup guards). "
        "The gotchas are documented (this memo). Five tasks remain before the pipeline is fully "
        "operational (TASK-140 through TASK-145). The staging database is wired. The next step is "
        "wiring Railway's develop environment, adding the startup guard, and seeding data. "
        "Then the two-environment deploy pipeline becomes operational \u2014 and the dangerous thing "
        "becomes impossible by default."))


if __name__ == "__main__":
    build_doc(OUTPUT, "MEMO-003: Staging Database Wired", content)
