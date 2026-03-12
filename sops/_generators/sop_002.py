#!/usr/bin/env python3
"""SOP-002 — Database Migrations"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "sops" / "SOP-002-database-migrations.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "SOP-002", "Database Migrations"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Effective:</b> 2026-03-11  |  <b>Owner:</b> Daniel Shanklin  |  "
                   "<b>Applies to:</b> Anyone writing SQL migrations for Greenmark Supabase databases",
                   META))
    story.append(Spacer(1, 6))

    # BLUF
    story.append(p("BLUF", H2))
    story.append(p(
        "Two migration systems write to the same Postgres database. Data-daemon owns bronze schemas "
        "(raw vendor data). Cerebro owns everything else (silver, gold, auth, RBAC). Follow this SOP "
        "to know which system to use, how to apply migrations, and how to verify they ran."))
    story.append(Spacer(1, 8))

    # Schema Ownership
    story.append(p("Schema Ownership", H2))
    story.append(tbl(["Schema", "Owner", "Why", "Migration System"], [
        [p("daemon", MONO), p("<b>data-daemon</b>", CELL), p("Job queue, migration history", CELL), p("Numbered SQL", CELL)],
        [p("hubspot_bronze", MONO), p("<b>data-daemon</b>", CELL), p("Raw HubSpot extraction", CELL), p("Numbered SQL", CELL)],
        [p("sage_bronze", MONO), p("<b>data-daemon</b>", CELL), p("Raw Sage extraction", CELL), p("Numbered SQL", CELL)],
        [p("navusoft_bronze", MONO), p("<b>data-daemon</b>", CELL), p("Raw Navusoft extraction", CELL), p("Numbered SQL", CELL)],
        [p("fleet_bronze", MONO), p("<b>data-daemon</b>", CELL), p("Raw Fleetio extraction", CELL), p("Numbered SQL", CELL)],
        [p("vault", MONO), p("<b>data-daemon</b>", CELL), p("Vendor API credentials", CELL), p("Numbered SQL", CELL)],
        [p("gold", MONO), p("<b>cerebro</b>", CELL), p("Business metrics, RLS", CELL), p("Supabase CLI", CELL)],
        [p("silver", MONO), p("<b>cerebro</b>", CELL), p("Normalized views", CELL), p("Supabase CLI", CELL)],
        [p("public", MONO), p("<b>cerebro</b>", CELL), p("User auth, roles", CELL), p("Supabase CLI", CELL)],
        [p("rbac", MONO), p("<b>cerebro</b>", CELL), p("Role/permission lookups", CELL), p("Supabase CLI", CELL)],
        [p("audit", MONO), p("<b>cerebro</b>", CELL), p("Drift detection, security", CELL), p("Supabase CLI", CELL)],
        [p("platform", MONO), p("<b>cerebro</b>", CELL), p("Config, feature flags", CELL), p("Supabase CLI", CELL)],
        [p("forge / secure", MONO), p("<b>cerebro</b>", CELL), p("SECURITY DEFINER refresh", CELL), p("Supabase CLI", CELL)],
    ], [USABLE * 0.22, USABLE * 0.16, USABLE * 0.34, USABLE * 0.28]))
    story.append(Spacer(1, 4))

    story.append(AccentBox(USABLE,
                           "The clean rule: If you're creating tables where data-daemon extracts raw vendor "
                           "data into, it goes in data-daemon. Everything else goes in cerebro."))
    story.append(Spacer(1, 8))

    # System A
    story.append(p("System A: Data-Daemon", H2))
    story.append(p("<b>Location:</b> <i>data-daemon/migrations/NNN_description.sql</i>", CELL_BOLD))
    story.append(p("<b>Tracker:</b> <i>daemon.migration_history</i> table", CELL_BOLD))
    story.append(Spacer(1, 4))
    story.append(p("How to Apply", H3))
    story.append(tbl(["Method", "Steps"], [
        [p("<b>Production</b>", CELL),
         p("Push to main branch. Railway redeploys. Startup auto-applies pending migrations.", CELL)],
        [p("<b>Manual</b>", CELL),
         p("Set DATABASE_URL and run: <i>python -c 'from src.db.migrate import run_migrations; ...'</i>", CELL)],
    ], [USABLE * 0.18, USABLE * 0.82]))
    story.append(Spacer(1, 4))
    story.append(p("How to Verify", H3))
    story.append(p("<i>SELECT filename, applied_at FROM daemon.migration_history ORDER BY applied_at;</i>", MONO))
    story.append(Spacer(1, 8))

    # System B
    story.append(p("System B: Cerebro (Supabase CLI)", H2))
    story.append(p("<b>Location:</b> <i>cerebro/supabase/migrations/YYYYMMDDHHMMSS_description.sql</i>", CELL_BOLD))
    story.append(p("<b>Tracker:</b> <i>supabase_migrations.schema_migrations</i> table", CELL_BOLD))
    story.append(Spacer(1, 4))
    story.append(p("How to Apply", H3))
    story.append(tbl(["Method", "Command"], [
        [p("<b>New migration</b>", CELL),
         p("npx supabase migration new description_here", MONO)],
        [p("<b>Apply to prod</b>", CELL),
         p("npx supabase db push --linked", MONO)],
        [p("<b>Apply to test</b>", CELL),
         p("npx supabase db push --db-url postgresql://postgres:&lt;pw&gt;@db.izmuckuepryqneebwwol...", MONO)],
    ], [USABLE * 0.2, USABLE * 0.8]))
    story.append(Spacer(1, 4))
    story.append(p("How to Verify", H3))
    story.append(p("<i>SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version;</i>", MONO))
    story.append(Spacer(1, 4))
    story.append(p("Or: Supabase Dashboard > Database > Migrations", CELL))
    story.append(hr())

    # PostgREST
    story.append(p("PostgREST Exposed Schemas", H2))
    story.append(p("PostgREST only serves schemas explicitly listed in config. Tables in unexposed schemas "
                   "return HTTP 406.", CELL))
    story.append(Spacer(1, 4))
    story.append(tbl(["Status", "Schemas"], [
        [p("<b>Currently exposed</b>", CELL),
         p("public, graphql_public, audit, platform, rbac, gold", MONO)],
        [p("<b>Needs adding</b>", CELL),
         p("hubspot_bronze, silver (per-vendor)", MONO)],
    ], [USABLE * 0.22, USABLE * 0.78]))
    story.append(Spacer(1, 4))
    story.append(p("Fix via: Supabase Dashboard > Settings > API > Exposed schemas", CELL))
    story.append(Spacer(1, 8))

    # Pre-flight
    story.append(p("Pre-Flight Checklist", H2))
    story.append(tbl(["#", "Check"], [
        [p("1", CELL), p("Confirm which system owns the schema (see ownership table)", CELL)],
        [p("2", CELL), p("Check what's already applied (migration_history or schema_migrations)", CELL)],
        [p("3", CELL), p("Test against Cerebro Test project (izmuckuepryqneebwwol) first", CELL)],
        [p("4", CELL), p("Use IF NOT EXISTS / IF EXISTS for idempotency", CELL)],
        [p("5", CELL), p("Include GRANT statements for new tables", CELL)],
        [p("6", CELL), p("Gold tables: add RLS policy for entity isolation", CELL)],
        [p("7", CELL), p("Refresh functions: SECURITY DEFINER owned by svc_etl_runner", CELL)],
    ], [0.3 * inch, USABLE - 0.3 * inch]))
    story.append(Spacer(1, 8))

    # Known issues
    story.append(p("Known Issues", H2))
    story.append(AccentBox(USABLE,
                           "14 of 19 planned gold tables don't exist in production. They're defined in "
                           "data-daemon migrations 018-019 but belong in cerebro. A new cerebro migration "
                           "is needed to create them.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "Data-daemon migrations 009, 010, 012, 017 create silver/gold objects that are "
                           "superseded by cerebro migrations. Harmless (IF NOT EXISTS) but signals ownership "
                           "confusion. Tracked for cleanup.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 8))

    # Why
    story.append(p("Why This Exists", H2))
    story.append(p(
        "We discovered that 14 of 19 gold tables were returning 404 from PostgREST because the "
        "migrations that create them hadn't been deployed. Both migration systems were creating "
        "objects in the same schemas with no documented ownership. This SOP prevents future "
        "confusion about which system owns what and how to apply pending migrations."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "No exceptions. All schema changes go through one of these two migration systems. "
                           "No ad-hoc SQL in Supabase SQL Editor for schema changes (data queries are fine)."))


if __name__ == "__main__":
    build_doc(OUTPUT, "SOP-002: Database Migrations", content)
