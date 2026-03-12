#!/usr/bin/env python3
"""SOP-005 — Release and Deployment"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "sops" / "SOP-005-release-and-deployment.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "SOP-005", "Release and Deployment"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Effective:</b> 2026-03-11  |  <b>Owner:</b> Daniel Shanklin  |  "
                   "<b>Applies to:</b> All Greenmark services deployed via Railway, Supabase, and GitHub Actions",
                   META))
    story.append(Spacer(1, 6))

    # ── BLUF ──────────────────────────────────────────────────────────
    story.append(p("BLUF", H2))
    story.append(p(
        "Every production change follows the same pipeline: <b>branch &rarr; test &rarr; review &rarr; "
        "merge &rarr; auto-deploy &rarr; verify &rarr; monitor.</b> Database migrations always deploy "
        "to the test project first. Rollbacks are service-specific &mdash; know your service's rollback "
        "path before you deploy. This SOP is the single source of truth for how code moves from a "
        "developer's machine to production."))
    story.append(Spacer(1, 8))

    # ── 1. Pipeline Overview ──────────────────────────────────────────
    story.append(p("1. Release Pipeline Overview", H2))
    story.append(p(
        "All Greenmark services follow a trunk-based deployment model. Code merges to a target branch "
        "(main or develop) trigger GitHub Actions, which deploy to Railway via the Railway CLI. Database "
        "migrations follow a separate, more cautious path through the Supabase test project before "
        "touching production."))
    story.append(Spacer(1, 4))

    # Pipeline diagram
    story.append(mermaid("""
        flowchart TB
            subgraph Dev["Developer Workstation"]
                A["Write Code / Migration"] --> B["Local Testing"]
                B --> C["git push feature branch"]
            end

            subgraph GH["GitHub"]
                C --> D["Pull Request"]
                D --> E{"CI Checks Pass?"}
                E -->|No| F["Fix & Re-push"]
                F --> D
                E -->|Yes| G["Code Review"]
                G --> H{"Approved?"}
                H -->|No| F
                H -->|Yes| I["Merge to main/develop"]
            end

            subgraph CI["GitHub Actions"]
                I --> J{"Has Migrations?"}
                J -->|Yes| K["Test DB First"]
                K --> L{"Pass?"}
                L -->|No| F
                L -->|Yes| M["Prod DB"]
                M --> N["Deploy App to Railway"]
                J -->|No| N
            end

            subgraph RW["Railway"]
                N --> O["Docker Build"]
                O --> P{"Health Check"}
                P -->|Fail| Q["Auto-Rollback"]
                P -->|Pass| R["Live in Production"]
            end
    """))
    story.append(Spacer(1, 6))

    # Pipeline steps as a table
    story.append(tbl(
        ["Stage", "Action", "Tools"],
        [
            [p("<b>1. Develop</b>", CELL), p("Write code/migrations on feature branch", CELL),
             p("Git, IDE, Claude Code", CELL)],
            [p("<b>2. Test Locally</b>", CELL), p("Type checks, unit tests, lint", CELL),
             p("tsc, pytest, eslint", CELL)],
            [p("<b>3. Push</b>", CELL), p("Push feature branch, open PR", CELL),
             p("GitHub", CELL)],
            [p("<b>4. CI Checks</b>", CELL), p("Automated type check, unit tests, E2E tests", CELL),
             p("GitHub Actions", CELL)],
            [p("<b>5. Review</b>", CELL), p("Code review, ADR compliance check", CELL),
             p("GitHub PR review", CELL)],
            [p("<b>6. Merge</b>", CELL), p("Merge to main/develop", CELL),
             p("GitHub", CELL)],
            [p("<b>7. Deploy Migrations</b>", CELL), p("Test DB first, then production", CELL),
             p("Supabase CLI", CELL)],
            [p("<b>8. Deploy App</b>", CELL), p("Railway CLI builds Docker, health check", CELL),
             p("GitHub Actions, Railway", CELL)],
            [p("<b>9. Verify</b>", CELL), p("Health endpoints, migration tracker, data checks", CELL),
             p("curl, SQL queries", CELL)],
            [p("<b>10. Monitor</b>", CELL), p("Logs, metrics, error rates for 5 min", CELL),
             p("Railway dashboard", CELL)],
        ],
        [USABLE * 0.20, USABLE * 0.50, USABLE * 0.30],
    ))
    story.append(Spacer(1, 8))

    # ── 2. Service Inventory ──────────────────────────────────────────
    story.append(p("2. Service Inventory", H2))
    story.append(p(
        "Greenmark operates five services, all deployed to Railway. Each has its own repository, "
        "deployment trigger, and health check."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Service", "Language", "Deploy Branch", "Health Endpoint", "Railway Env"],
        [
            [p("<b>Cerebro</b>", CELL), p("Next.js / TS", CELL), p("main (prod), develop (dev)", CELL),
             p("/api/health", MONO), p("production, develop", CELL)],
            [p("<b>Data Daemon</b>", CELL), p("Python 3.11", CELL), p("develop", CELL),
             p("/health", MONO), p("develop", CELL)],
            [p("<b>AI Services</b>", CELL), p("Python 3.12 / FastAPI", CELL), p("main", CELL),
             p("/ready", MONO), p("production", CELL)],
            [p("<b>Bot Farm</b>", CELL), p("Python 3.12", CELL), p("main", CELL),
             p("(health check)", CELL), p("production", CELL)],
            [p("<b>Portal</b>", CELL), p("Node.js / Express", CELL), p("manual", CELL),
             p("/health", MONO), p("&mdash;", CELL)],
        ],
        [USABLE * 0.16, USABLE * 0.18, USABLE * 0.24, USABLE * 0.18, USABLE * 0.24],
    ))
    story.append(Spacer(1, 8))

    # Service dependency diagram
    story.append(mermaid("""
        graph LR
            subgraph Frontend
                C["Cerebro<br/>Next.js"]
            end
            subgraph Backend
                D["Data Daemon<br/>Python"]
                AI["AI Services<br/>FastAPI"]
                BF["Bot Farm<br/>Python"]
            end
            subgraph DB["Supabase PostgreSQL"]
                B[("Bronze<br/>hubspot_bronze")]
                S[("Silver<br/>hubspot_silver")]
                G[("Gold<br/>gold.*")]
            end
            subgraph Ext["External APIs"]
                HS["HubSpot"]
                SG["Sage Intacct"]
            end
            D -->|extract| HS
            D -->|extract| SG
            D -->|write| B
            B -.->|refresh| S
            S -.->|refresh| G
            C -->|read| G
            C -->|call| AI
            C -->|trigger| BF
            BF -->|read| G
    """))
    story.append(Spacer(1, 6))

    # ── 3. Tech Stack ─────────────────────────────────────────────────
    story.append(p("3. Tech Stack Reference", H2))

    story.append(p("3.1 Infrastructure Components", H3))
    story.append(tbl(
        ["Component", "Role", "Notes"],
        [
            [p('<b>GitHub</b> <font color="#6B7B73">github.com</font>', CELL),
             p("Source control, CI/CD via Actions", CELL),
             p("All repos under greenmark-waste-solutions org", CELL)],
            [p('<b>Railway</b> <font color="#6B7B73">railway.app</font>', CELL),
             p("Container hosting, zero-downtime deploys", CELL),
             p("Docker-based, health check gating", CELL)],
            [p('<b>Supabase</b> <font color="#6B7B73">supabase.com</font>', CELL),
             p("PostgreSQL database, auth, RLS", CELL),
             p("Prod: wwmcgtyngnziepeynccz / Test: izmuckuepryqneebwwol", CELL)],
            [p('<b>Docker</b> <font color="#6B7B73">docker.com</font>', CELL),
             p("Containerization for all services", CELL),
             p("Multi-stage Alpine builds", CELL)],
            [p('<b>Slack</b> <font color="#6B7B73">slack.com</font>', CELL),
             p("Deployment failure notifications", CELL),
             p("Bot Farm alerts to channel C0AD03NG53Q", CELL)],
        ],
        [USABLE * 0.25, USABLE * 0.35, USABLE * 0.40],
    ))
    story.append(Spacer(1, 4))

    story.append(p("3.2 Build Tools", H3))
    story.append(tbl(
        ["Tool", "Version", "Used By"],
        [
            [p("Node.js", CELL_BOLD), p("22", CELL), p("Cerebro, Portal", CELL)],
            [p("Python", CELL_BOLD), p("3.11 &ndash; 3.12", CELL), p("Data Daemon, AI Services, Bot Farm", CELL)],
            [p("TypeScript", CELL_BOLD), p("(project)", CELL), p("Cerebro", CELL)],
            [p("Supabase CLI", CELL_BOLD), p("latest", CELL), p("Cerebro migrations", CELL)],
            [p("Railway CLI", CELL_BOLD), p("latest", CELL), p("All service deployments", CELL)],
        ],
        [USABLE * 0.25, USABLE * 0.20, USABLE * 0.55],
    ))
    story.append(Spacer(1, 8))

    # ── 4. Pre-Flight Checklist ───────────────────────────────────────
    story.append(p("4. Pre-Flight Checklist", H2))
    story.append(p(
        "Before any merge to a deploy branch, verify every item. AI agents and humans alike must "
        "follow this sequence."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["#", "Check", "How", "Required For"],
        [
            [p("1", CELL), p("Type check passes", CELL_BOLD), p("npx tsc --noEmit", MONO), p("Cerebro", CELL)],
            [p("2", CELL), p("Unit tests pass", CELL_BOLD), p("pytest tests/ -v", MONO), p("Daemon, Bot Farm", CELL)],
            [p("3", CELL), p("E2E tests pass", CELL_BOLD), p("pytest test_sales_e2e.py", MONO), p("Bot Farm (main)", CELL)],
            [p("4", CELL), p("Schema ownership verified", CELL_BOLD), p("See SOP-002", CELL), p("Any migration", CELL)],
            [p("5", CELL), p("Migration tested on test DB", CELL_BOLD), p("supabase db push --db-url", MONO), p("Cerebro migrations", CELL)],
            [p("6", CELL), p("IF NOT EXISTS used", CELL_BOLD), p("Manual review", CELL), p("All migrations", CELL)],
            [p("7", CELL), p("GRANT statements included", CELL_BOLD), p("Manual review", CELL), p("New tables/views", CELL)],
            [p("8", CELL), p("RLS policies included", CELL_BOLD), p("Manual review", CELL), p("Gold tables", CELL)],
            [p("9", CELL), p("SECURITY DEFINER used", CELL_BOLD), p("Manual review", CELL), p("Forge functions", CELL)],
            [p("10", CELL), p("No hard DELETEs", CELL_BOLD), p('grep "DELETE FROM"', MONO), p("All migrations", CELL)],
            [p("11", CELL), p("Governance check passed", CELL_BOLD), p("check-governance skillflow", CELL), p("All changes", CELL)],
            [p("12", CELL), p("ADRs consulted", CELL_BOLD), p("cerebro_adrs() search", CELL), p("Schema changes", CELL)],
        ],
        [0.25 * inch, USABLE * 0.25, USABLE * 0.35, USABLE * 0.30],
    ))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "AI agents: Items 4, 8, 9, and 11 are non-negotiable. Skipping governance or "
                           "RLS has caused production security gaps before."))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 5. Database Migration Deployment ──────────────────────────────
    story.append(p("5. Database Migration Deployment", H2))
    story.append(AccentBox(USABLE,
                           "Migrations are the highest-risk part of any deployment. They modify shared state "
                           "that cannot be easily undone. Follow this procedure exactly.",
                           bg=RED_BG, border=RED_BORDER, text_color=RED))
    story.append(Spacer(1, 6))

    story.append(p("5.1 Two Migration Systems, One Database", H3))
    story.append(p(
        "Greenmark uses two independent migration systems that write to the same Postgres database. "
        "Never cross the streams. See SOP-002 for full schema ownership table."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["System", "File Format", "Tracker Table", "Schemas Owned", "Apply Method"],
        [
            [p("<b>Data Daemon</b>", CELL),
             p("NNN_desc.sql", MONO),
             p("daemon.migration_history", MONO),
             p("bronze, daemon, vault", CELL),
             p("Auto on startup", CELL)],
            [p("<b>Cerebro</b>", CELL),
             p("YYYYMMDDHHMMSS_desc.sql", MONO),
             p("supabase_migrations.schema_migrations", MONO),
             p("silver, gold, forge, public, rbac, audit, platform", CELL),
             p("Supabase CLI", CELL)],
        ],
        [USABLE * 0.14, USABLE * 0.20, USABLE * 0.27, USABLE * 0.22, USABLE * 0.17],
    ))
    story.append(Spacer(1, 6))

    # Migration systems diagram
    story.append(mermaid("""
        flowchart TB
            subgraph DD["Data Daemon Migrations"]
                DD1["migrations/NNN_desc.sql"] --> DD2["daemon.migration_history"]
                DD2 --> DD3["Auto-applied on startup"]
                DD3 --> DD4["bronze, daemon, vault"]
            end
            subgraph CB["Cerebro Migrations"]
                C1["supabase/migrations/YYYYMMDD_desc.sql"] --> C2["schema_migrations"]
                C2 --> C3["Applied via Supabase CLI"]
                C3 --> C4["silver, gold, forge, rbac, audit"]
            end
            subgraph PG["Supabase PostgreSQL"]
                DD4 --> DB[("Single Database")]
                C4 --> DB
            end
    """))
    story.append(Spacer(1, 4))

    story.append(p("5.2 Cerebro Migration Procedure", H3))
    story.append(tbl(
        ["Step", "Action", "Command / Detail"],
        [
            [p("1", CELL), p("<b>Write migration</b>", CELL),
             p("npx supabase migration new description_here", MONO)],
            [p("2", CELL), p("<b>Test on test DB</b>", CELL),
             p("npx supabase db push --db-url postgresql://postgres:&lt;pw&gt;@db.izmuckuepryqneebwwol.supabase.co:5432/postgres", MONO)],
            [p("3", CELL), p("<b>Verify on test</b>", CELL),
             p("Check tables, RLS, functions exist. Run forge.refresh_all().", CELL)],
            [p("4", CELL), p("<b>Deploy to production</b>", CELL),
             p("npx supabase db push --linked", MONO)],
            [p("5", CELL), p("<b>Verify on production</b>", CELL),
             p("Same verification queries as step 3", CELL)],
            [p("6", CELL), p("<b>Populate gold tables</b>", CELL),
             p("SELECT forge.refresh_all();", MONO)],
        ],
        [0.3 * inch, USABLE * 0.22, USABLE * 0.66],
    ))
    story.append(Spacer(1, 4))

    story.append(p("5.3 Data Daemon Migration Procedure", H3))
    story.append(tbl(
        ["Step", "Action", "Detail"],
        [
            [p("1", CELL), p("<b>Write migration</b>", CELL),
             p("Place in data-daemon/migrations/ with next sequential number", CELL)],
            [p("2", CELL), p("<b>Test locally</b>", CELL),
             p("DATABASE_URL=&lt;test-url&gt; python -m src.main", MONO)],
            [p("3", CELL), p("<b>Verify</b>", CELL),
             p("Check daemon.migration_history for new entry", CELL)],
            [p("4", CELL), p("<b>Push to develop</b>", CELL),
             p("Railway redeploys, startup runs src/db/migrate.py", CELL)],
            [p("5", CELL), p("<b>Verify in prod</b>", CELL),
             p("Check daemon.migration_history in production", CELL)],
        ],
        [0.3 * inch, USABLE * 0.22, USABLE * 0.66],
    ))
    story.append(Spacer(1, 6))

    story.append(p("5.4 Migration Ordering Rules", H3))
    story.append(p(
        "When a release includes both silver and gold changes, apply in this order:"))
    story.append(Spacer(1, 4))
    story.append(tbl(
        ["Order", "What", "Why"],
        [
            [p("1", CELL_BOLD), p("Bronze schema changes", CELL), p("Tables that silver reads from", CELL)],
            [p("2", CELL_BOLD), p("Silver materialized views", CELL), p("Views that gold reads from", CELL)],
            [p("3", CELL_BOLD), p("Gold tables", CELL), p("Tables with RLS", CELL)],
            [p("4", CELL_BOLD), p("RLS policies", CELL), p("Security on gold tables", CELL)],
            [p("5", CELL_BOLD), p("Forge refresh functions", CELL), p("Populate gold from silver", CELL)],
            [p("6", CELL_BOLD), p("forge.refresh_all() update", CELL), p("Master refresh function", CELL)],
            [p("7", CELL_BOLD), p("Initial population", CELL), p("SELECT forge.refresh_all()", CELL)],
        ],
        [0.4 * inch, USABLE * 0.35, USABLE * 0.52],
    ))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "Silver must exist before gold refresh functions that reference it. Gold tables "
                           "must exist before RLS policies reference them. forge.refresh_all() must be "
                           "updated before calling it."))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 6. Application Deployment ─────────────────────────────────────
    story.append(p("6. Application Deployment", H2))
    story.append(p(
        "Each service has a GitHub Actions workflow that deploys on merge. All use the Railway CLI."))
    story.append(Spacer(1, 4))

    story.append(p("6.1 Cerebro (Next.js)", H3))
    story.append(tbl(
        ["Step", "Action"],
        [
            [p("1", CELL), p("Push to <b>main</b> (prod) or <b>develop</b> (dev)", CELL)],
            [p("2", CELL), p("GitHub Actions: checkout, Node 22, npm ci", CELL)],
            [p("3", CELL), p("Type check: npx tsc --noEmit", CELL)],
            [p("4", CELL), p("Install Railway CLI", CELL)],
            [p("5", CELL), p("railway up --service cerebro --environment &lt;env&gt; --detach", CELL)],
            [p("6", CELL), p("Railway builds Docker (multi-stage Alpine: deps &rarr; build &rarr; final)", CELL)],
            [p("7", CELL), p("Health check: /api/health (120s timeout, 3 retries)", CELL)],
        ],
        [0.3 * inch, USABLE - 0.3 * inch],
    ))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Build args:</b> NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_ENV_LABEL",
        CELL))
    story.append(Spacer(1, 6))

    story.append(p("6.2 Data Daemon (Python)", H3))
    story.append(tbl(
        ["Step", "Action"],
        [
            [p("1", CELL), p("Push to <b>develop</b>", CELL)],
            [p("2", CELL), p("GitHub Actions: checkout, install Railway CLI", CELL)],
            [p("3", CELL), p("railway up --service data-daemon --environment develop --detach", CELL)],
            [p("4", CELL), p("Startup: run migrations &rarr; init pool &rarr; start scheduler &rarr; start workers", CELL)],
            [p("5", CELL), p("Health check: /health (120s timeout, 5 retries)", CELL)],
        ],
        [0.3 * inch, USABLE - 0.3 * inch],
    ))
    story.append(Spacer(1, 6))

    story.append(p("6.3 AI Services (FastAPI)", H3))
    story.append(tbl(
        ["Step", "Action"],
        [
            [p("1", CELL), p("Push to <b>main</b>", CELL)],
            [p("2", CELL), p("GitHub Actions: checkout, install Railway CLI", CELL)],
            [p("3", CELL), p("railway up --service cerebro-ai-services --environment production --detach", CELL)],
            [p("4", CELL), p("Health check: /ready (<b>300s timeout</b> &mdash; models take time to load)", CELL)],
        ],
        [0.3 * inch, USABLE - 0.3 * inch],
    ))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "AI Services has a persistent volume at /data/models that survives redeploys. "
                           "If the model cache is corrupted, a fresh redeploy will re-download."))
    story.append(Spacer(1, 6))

    story.append(p("6.4 Bot Farm (Python) &mdash; Most Sophisticated Pipeline", H3))
    story.append(tbl(
        ["Step", "Action", "On Failure"],
        [
            [p("1", CELL), p("Push to <b>main</b> or open PR", CELL), p("&mdash;", CELL)],
            [p("2", CELL), p("Setup Python 3.12, cache pip, install deps", CELL), p("&mdash;", CELL)],
            [p("3", CELL), p("Unit tests (all except E2E)", CELL),
             p('<font color="#C0392B">Slack alert</font>', CELL)],
            [p("4", CELL), p("E2E tests against live Supabase (main push only)", CELL),
             p('<font color="#C0392B">Slack alert</font>', CELL)],
            [p("5", CELL), p("railway up --service cerebro-bot-farm --environment production", CELL),
             p('<font color="#C0392B">Slack alert</font>', CELL)],
        ],
        [0.3 * inch, USABLE * 0.52, USABLE * 0.35],
    ))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 7. Post-Deploy Verification ───────────────────────────────────
    story.append(p("7. Post-Deployment Verification", H2))
    story.append(p(
        "After every deployment, run through this verification matrix. Depth depends on what changed."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Changed", "Verify", "Expected"],
        [
            [p("Application code", CELL), p("curl health endpoint &rarr; 200 OK", CELL),
             p("200 OK", GREEN_TEXT)],
            [p("Cerebro migrations", CELL),
             p("SELECT * FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 5", CELL),
             p("New migration present", GREEN_TEXT)],
            [p("Daemon migrations", CELL),
             p("SELECT * FROM daemon.migration_history ORDER BY applied_at DESC LIMIT 5", CELL),
             p("New migration present", GREEN_TEXT)],
            [p("Gold tables", CELL),
             p("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'gold'", CELL),
             p("All rowsecurity = true", GREEN_TEXT)],
            [p("Gold tables", CELL),
             p("SET request.jwt.claims to test entity; SELECT from gold table", CELL),
             p("Only matching entity rows", GREEN_TEXT)],
            [p("Forge functions", CELL), p("SELECT forge.refresh_all()", CELL),
             p("No errors", GREEN_TEXT)],
            [p("Silver views", CELL), p("SELECT COUNT(*) FROM hubspot_silver.&lt;view&gt;", CELL),
             p("> 0", GREEN_TEXT)],
            [p("RLS policies", CELL), p("SET ROLE service_role; SELECT from gold table", CELL),
             p("Permission denied", GREEN_TEXT)],
        ],
        [USABLE * 0.18, USABLE * 0.55, USABLE * 0.27],
    ))
    story.append(Spacer(1, 4))

    story.append(p("Smoke Test SQL", H3))
    story.append(p(
        "Run this after any deployment that touches the database:", CELL))
    story.append(Spacer(1, 2))
    story.append(p(
        "1. SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 3;<br/>"
        "2. SELECT tablename FROM pg_tables WHERE schemaname = 'gold' AND rowsecurity = false; -- expect 0 rows<br/>"
        "3. SELECT forge.refresh_all();<br/>"
        "4. SELECT COUNT(*) FROM gold.pipeline_summary; -- expect > 0<br/>"
        "5. SET request.jwt.claims = '{\"entity_id\":\"ntx\"}'; SELECT DISTINCT entity_id FROM gold.pipeline_summary; -- expect only 'ntx'",
        MONO))
    story.append(Spacer(1, 8))

    # ── 8. Rollback Procedures ────────────────────────────────────────
    story.append(p("8. Rollback Procedures", H2))
    story.append(p(
        "Not all rollbacks are equal. The correct procedure depends on what was deployed and what went wrong."))
    story.append(Spacer(1, 4))

    # Rollback decision tree
    story.append(mermaid("""
        flowchart TB
            A["Something Went Wrong"] --> B{"What was deployed?"}
            B -->|App Only| C{"Health check failing?"}
            C -->|Yes| D["Railway auto-rolled back"]
            C -->|No, bugs| E["Revert commit & push"]
            B -->|Migration Only| F{"Data corrupted?"}
            F -->|No| G["Write corrective migration"]
            F -->|Yes| H["INCIDENT: Restore backup"]
            B -->|Both| I{"App depends on new schema?"}
            I -->|Yes| J["Roll back app first"]
            I -->|No| K["Roll back app only"]
    """))
    story.append(Spacer(1, 4))

    story.append(p("8.1 Application Rollback", H3))
    story.append(tbl(
        ["Method", "When", "How"],
        [
            [p("<b>Railway auto-rollback</b>", CELL),
             p("Health check fails", CELL),
             p("Automatic &mdash; Railway reverts to previous deployment", CELL)],
            [p("<b>Revert commit</b>", CELL),
             p("Bugs in production", CELL),
             p("git revert &lt;sha&gt; && git push origin main", MONO)],
            [p("<b>Redeploy previous</b>", CELL),
             p("Need immediate rollback", CELL),
             p("Railway dashboard &rarr; previous deployment &rarr; Redeploy", CELL)],
        ],
        [USABLE * 0.22, USABLE * 0.25, USABLE * 0.53],
    ))
    story.append(Spacer(1, 6))

    story.append(p("8.2 Migration Rollback", H3))
    story.append(AccentBox(USABLE,
                           "Migrations cannot be automatically rolled back. There is no DOWN migration system. "
                           "Write a corrective migration that undoes the damage, test on test DB, then apply.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 4))
    story.append(tbl(
        ["Scenario", "Action"],
        [
            [p("Added wrong column", CELL),
             p("ALTER TABLE ... DROP COLUMN IF EXISTS bad_column;", MONO)],
            [p("Created wrong table", CELL),
             p("DROP TABLE IF EXISTS gold.bad_table;", MONO)],
            [p("Dropped something needed", CELL),
             p("Recreate from original migration SQL", CELL)],
            [p("Data corrupted/lost", CELL),
             p('<font color="#C0392B"><b>INCIDENT:</b> Restore from Supabase backup (7-day daily retention)</font>', CELL)],
        ],
        [USABLE * 0.28, USABLE * 0.72],
    ))
    story.append(Spacer(1, 6))

    story.append(p("8.3 Forge Function Rollback", H3))
    story.append(tbl(
        ["Step", "Action"],
        [
            [p("1", CELL), p("<b>Stop the bleeding</b> &mdash; remove from forge.refresh_all()", CELL)],
            [p("2", CELL), p("<b>Fix the function</b> &mdash; CREATE OR REPLACE FUNCTION in corrective migration", CELL)],
            [p("3", CELL), p("<b>Re-run refresh</b> &mdash; SELECT forge.refresh_&lt;table&gt;()", CELL)],
            [p("4", CELL), p("<b>Verify</b> &mdash; check row counts and spot-check data", CELL)],
        ],
        [0.3 * inch, USABLE - 0.3 * inch],
    ))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 9. Environment Management ─────────────────────────────────────
    story.append(p("9. Environment Management", H2))

    story.append(p("9.1 Environment Matrix", H3))
    story.append(tbl(
        ["Environment", "Purpose", "Database", "Railway", "Branch"],
        [
            [p("<b>Production</b>", CELL), p("Live users", CELL),
             p("wwmcgtyngnziepeynccz", MONO), p("production", CELL), p("main", CELL)],
            [p("<b>Development</b>", CELL), p("Pre-prod testing", CELL),
             p("wwmcgtyngnziepeynccz (same!)", MONO), p("develop", CELL), p("develop", CELL)],
            [p("<b>Test</b>", CELL), p("Migration testing only", CELL),
             p("izmuckuepryqneebwwol", MONO), p("&mdash;", CELL), p("&mdash;", CELL)],
        ],
        [USABLE * 0.16, USABLE * 0.18, USABLE * 0.30, USABLE * 0.16, USABLE * 0.20],
    ))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "Development and production share the same database. The Railway develop environment "
                           "is for application testing (different URL), but database changes affect production "
                           "immediately. This is why migrations MUST be tested on the test project first.",
                           bg=RED_BG, border=RED_BORDER, text_color=RED))
    story.append(Spacer(1, 6))

    story.append(p("9.2 Secret Management", H3))
    story.append(tbl(
        ["Secret Type", "Stored In", "Accessed Via"],
        [
            [p("API keys (HubSpot, Sage)", CELL), p("vault.secrets (encrypted)", CELL),
             p("secure.get_secret() in SQL", CELL)],
            [p("Railway tokens", CELL), p("GitHub Secrets", CELL),
             p("${{ secrets.RAILWAY_TOKEN }}", MONO)],
            [p("Supabase credentials", CELL), p("GitHub Secrets / Knox", CELL),
             p("CI/CD and local dev", CELL)],
            [p("Slack bot token", CELL), p("GitHub Secrets", CELL),
             p("Bot Farm failure alerts", CELL)],
        ],
        [USABLE * 0.28, USABLE * 0.32, USABLE * 0.40],
    ))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Rules:</b> Never commit secrets to code. Rotate API keys quarterly. "
        "Railway tokens are per-environment. Vault access is audited.", CELL))
    story.append(Spacer(1, 6))

    story.append(p("9.3 Connection Strings", H3))
    story.append(tbl(
        ["Target", "Format"],
        [
            [p("<b>Prod (direct)</b>", CELL),
             p("postgresql://postgres.&lt;ref&gt;:&lt;pw&gt;@db.wwmcgtyngnziepeynccz.supabase.co:5432/postgres", MONO)],
            [p("<b>Prod (pooler)</b>", CELL),
             p("postgresql://postgres.&lt;ref&gt;:&lt;pw&gt;@aws-0-us-east-1.pooler.supabase.com:6543/postgres", MONO)],
            [p("<b>Test (direct)</b>", CELL),
             p("postgresql://postgres:&lt;pw&gt;@db.izmuckuepryqneebwwol.supabase.co:5432/postgres", MONO)],
        ],
        [USABLE * 0.18, USABLE * 0.82],
    ))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Note:</b> Test uses direct (port 5432). Production should use Supavisor session-mode "
        "pooler (port 6543) for migrations per ADR-2026-03.", CELL))
    story.append(Spacer(1, 8))

    # ── 10. Emergency Hotfix ──────────────────────────────────────────
    story.append(p("10. Emergency Hotfix Process", H2))

    # Hotfix flow diagram
    story.append(mermaid("""
        flowchart LR
            A["PRODUCTION DOWN"] --> B["Assess Severity"]
            B -->|Users Blocked| C["HOTFIX PATH"]
            B -->|Degraded| D["Normal PR Flow"]
            C --> E["hotfix branch from main"]
            E --> F["Minimal fix only"]
            F --> G{"Has migration?"}
            G -->|Yes| H["Test DB 5 min max"]
            G -->|No| I["Push to main"]
            H --> I
            I --> J["Monitor deploy"]
            J --> K["Post-mortem 24h"]
    """))
    story.append(Spacer(1, 4))

    story.append(AccentBox(USABLE,
                           "When production is broken and users are affected, use this expedited process. "
                           "Minimal change only. Skip PR review ONLY if users are blocked.",
                           bg=RED_BG, border=RED_BORDER, text_color=RED))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Step", "Action", "Notes"],
        [
            [p("1", CELL), p("<b>Assess severity</b>", CELL),
             p("Users blocked = hotfix path. Degraded = normal PR flow.", CELL)],
            [p("2", CELL), p("<b>Create hotfix branch</b> from main", CELL),
             p("git checkout -b hotfix/description main", MONO)],
            [p("3", CELL), p("<b>Write minimal fix</b>", CELL),
             p("Fix the bug. Nothing else.", CELL)],
            [p("4", CELL), p("<b>Test migration (if any)</b>", CELL),
             p("Still required. 5 min max on test DB.", CELL)],
            [p("5", CELL), p("<b>Push to main</b>", CELL),
             p("Triggers auto-deploy", CELL)],
            [p("6", CELL), p("<b>Monitor deploy</b>", CELL),
             p("Watch health check, verify fix", CELL)],
            [p("7", CELL), p("<b>Post-mortem within 24h</b>", CELL),
             p("What broke, why, how to prevent", CELL)],
            [p("8", CELL), p("<b>Backport to develop</b>", CELL),
             p("Keep branches in sync", CELL)],
        ],
        [0.3 * inch, USABLE * 0.32, USABLE * 0.56],
    ))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 11. AI Agent Rules ────────────────────────────────────────────
    story.append(p("11. AI Agent Deployment Rules", H2))
    story.append(p(
        "When an AI agent (Claude Code, taskr-worker, etc.) is deploying changes:"))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Operation", "AI Can Do Alone", "Needs Human"],
        [
            [p("Write migration SQL", CELL), p('<font color="#2D6B4A"><b>YES</b></font>', CELL), p("", CELL)],
            [p("Test migration on test DB", CELL), p('<font color="#2D6B4A"><b>YES</b></font>', CELL), p("", CELL)],
            [p("Create PR", CELL), p('<font color="#2D6B4A"><b>YES</b></font>', CELL), p("", CELL)],
            [p("Run type checks / tests", CELL), p('<font color="#2D6B4A"><b>YES</b></font>', CELL), p("", CELL)],
            [p("Merge PR", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
            [p("Push to deploy branch", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
            [p("Modify CI/CD pipelines", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
            [p("Change secrets / env vars", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
            [p("Database backups / restores", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
            [p("Emergency hotfixes", CELL), p("", CELL), p('<font color="#C0392B"><b>REQUIRED</b></font>', CELL)],
        ],
        [USABLE * 0.40, USABLE * 0.30, USABLE * 0.30],
    ))
    story.append(Spacer(1, 4))

    story.append(p("Mandatory Escalation Triggers", H3))
    story.append(p(
        "AI agents <b>must</b> escalate to a human when encountering:"))
    story.append(Spacer(1, 2))
    story.append(tbl(
        ["Trigger", "Why"],
        [
            [p("Any RLS policy change", CELL), p("Security boundary &mdash; wrong policy = data leakage", CELL)],
            [p("Any GRANT/REVOKE statement", CELL), p("Permission changes affect all users", CELL)],
            [p("Any SECURITY DEFINER function", CELL), p("Runs with elevated privileges", CELL)],
            [p("Auth/authorization changes", CELL), p("Access control is business-critical", CELL)],
            [p("Railway config changes", CELL), p("Affects all deployments", CELL)],
            [p("Deploy failure after 2 retries", CELL), p("Indicates systemic issue, not transient", CELL)],
            [p("Conflicting ADR guidance", CELL), p("Human resolves architectural ambiguity", CELL)],
        ],
        [USABLE * 0.35, USABLE * 0.65],
    ))
    story.append(Spacer(1, 8))

    # ── 12. Monitoring ────────────────────────────────────────────────
    story.append(p("12. Monitoring and Observability", H2))

    story.append(tbl(
        ["Signal", "Where to Check", "Red Flag"],
        [
            [p("Health status", CELL), p("Railway dashboard", CELL),
             p('<font color="#C0392B">Any unhealthy service</font>', CELL)],
            [p("Error logs", CELL), p("Railway logs", CELL),
             p('<font color="#C0392B">Error spike post-deploy</font>', CELL)],
            [p("Migration status", CELL), p("migration_history / schema_migrations", CELL),
             p('<font color="#C0392B">Missing expected migration</font>', CELL)],
            [p("Gold row counts", CELL), p("SELECT COUNT(*) FROM gold.*", CELL),
             p('<font color="#C0392B">Sudden drop to 0</font>', CELL)],
            [p("RLS working", CELL), p("Entity isolation query", CELL),
             p('<font color="#C0392B">Cross-entity data leakage</font>', CELL)],
            [p("API latency", CELL), p("Railway metrics", CELL),
             p('<font color="#C0392B">&gt;2x increase post-deploy</font>', CELL)],
        ],
        [USABLE * 0.20, USABLE * 0.40, USABLE * 0.40],
    ))
    story.append(Spacer(1, 8))

    # ── 13. Post-Mortem ───────────────────────────────────────────────
    story.append(p("13. Post-Mortem Template", H2))
    story.append(p(
        "When an incident occurs (data loss, extended downtime, security breach), document within 24 hours."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Section", "Content"],
        [
            [p("<b>Title</b>", CELL), p("Incident: [Short Title]", CELL)],
            [p("<b>Metadata</b>", CELL), p("Date, duration, severity (P1/P2/P3), services affected", CELL)],
            [p("<b>Timeline</b>", CELL), p("What happened, when detected, actions taken, resolution", CELL)],
            [p("<b>Root Cause</b>", CELL), p("What specifically broke and why", CELL)],
            [p("<b>Impact</b>", CELL), p("Users affected, data affected, duration", CELL)],
            [p("<b>Resolution</b>", CELL), p("What fixed it", CELL)],
            [p("<b>Prevention</b>", CELL), p("Specific action items with owners to prevent recurrence", CELL)],
            [p("<b>Lessons Learned</b>", CELL), p("What applies broadly across the organization", CELL)],
        ],
        [USABLE * 0.18, USABLE * 0.82],
    ))
    story.append(Spacer(1, 8))

    # ── 14. Release Cadence ───────────────────────────────────────────
    story.append(p("14. Release Cadence and Maturity", H2))
    story.append(p(
        "Greenmark uses continuous deployment &mdash; every merge to the deploy branch triggers "
        "production. There are no scheduled release windows or version numbers."))
    story.append(Spacer(1, 4))

    story.append(tbl(
        ["Practice", "Status", "Notes"],
        [
            [p("Feature branches", CELL), p('<font color="#2D6B4A"><b>Active</b></font>', CELL),
             p("All work on feature branches", CELL)],
            [p("PR reviews", CELL), p('<font color="#2D6B4A"><b>Active</b></font>', CELL),
             p("Required before merge", CELL)],
            [p("Automated type checking", CELL), p('<font color="#2D6B4A"><b>Active</b></font>', CELL),
             p("Cerebro: tsc --noEmit", CELL)],
            [p("Automated unit tests", CELL), p('<font color="#2D6B4A"><b>Active</b></font>', CELL),
             p("Bot Farm", CELL)],
            [p("Automated E2E tests", CELL), p('<font color="#2D6B4A"><b>Active</b></font>', CELL),
             p("Bot Farm against live Supabase", CELL)],
            [p("Automated migration gate", CELL), p('<font color="#92700A"><b>Planned</b></font>', CELL),
             p("GitHub Action &rarr; test DB on PR", CELL)],
            [p("Deploy notifications", CELL), p('<font color="#92700A"><b>Partial</b></font>', CELL),
             p("Bot Farm only (Slack)", CELL)],
            [p("Git tags for releases", CELL), p('<font color="#C0392B"><b>Not active</b></font>', CELL),
             p("Consider for major releases", CELL)],
            [p("Changelog generation", CELL), p('<font color="#C0392B"><b>Not active</b></font>', CELL),
             p("Consider git log per release", CELL)],
        ],
        [USABLE * 0.28, USABLE * 0.18, USABLE * 0.54],
    ))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 15. GitHub Actions Workflow Structure ─────────────────────────
    story.append(p("15. GitHub Actions Workflow Structure", H2))
    story.append(p(
        "All deployment workflows live at <i>.github/workflows/deploy.yml</i> in each repo. "
        "They share a common structure but differ in CI depth. This section documents the YAML "
        "anatomy so anyone (human or AI) can read, modify, or create new workflows."))
    story.append(Spacer(1, 4))

    story.append(p("15.1 Workflow Anatomy", H3))
    story.append(p(
        "Every workflow has three sections: <b>trigger</b> (when), <b>environment</b> (what secrets), "
        "and <b>steps</b> (how). Here is the annotated structure:", CELL))
    story.append(Spacer(1, 2))
    story.append(p(
        "name: Deploy &lt;service&gt;<br/>"
        "on:<br/>"
        "&nbsp;&nbsp;push:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;branches: [main]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# or [develop], or [main, develop]<br/>"
        "&nbsp;&nbsp;pull_request:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Bot Farm only &mdash; runs tests on PR<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;branches: [main]<br/>"
        "<br/>"
        "jobs:<br/>"
        "&nbsp;&nbsp;deploy:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;runs-on: ubuntu-latest<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;steps:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- uses: actions/checkout@v4<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# === LANGUAGE SETUP (service-specific) ===<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- uses: actions/setup-node@v4&nbsp;&nbsp;# Cerebro<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;with: { node-version: 22 }<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- uses: actions/setup-python@v5 # Python services<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;with: { python-version: '3.12' }<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# === CI CHECKS (service-specific) ===<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- run: npm ci &amp;&amp; npx tsc --noEmit&nbsp;&nbsp;# Cerebro<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- run: pip install -r requirements.txt&nbsp;# Python<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- run: pytest tests/ -v&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Bot Farm<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# === DEPLOY ===<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- run: npm i -g @railway/cli<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- run: railway up --service $SVC --environment $ENV --detach<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;env:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}",
        MONO))
    story.append(Spacer(1, 6))

    story.append(p("15.2 Workflow Comparison Matrix", H3))
    story.append(tbl(
        ["Feature", "Cerebro", "Data Daemon", "AI Services", "Bot Farm"],
        [
            [p("<b>Trigger branch</b>", CELL),
             p("main + develop", CELL), p("develop", CELL), p("main", CELL), p("main + PR", CELL)],
            [p("<b>Language setup</b>", CELL),
             p("Node 22", CELL), p("(none)", CELL), p("(none)", CELL), p("Python 3.12", CELL)],
            [p("<b>Dependency install</b>", CELL),
             p("npm ci", CELL), p("(none)", CELL), p("(none)", CELL), p("pip install", CELL)],
            [p("<b>Type checking</b>", CELL),
             p("tsc --noEmit", CELL), p("(none)", CELL), p("(none)", CELL), p("(none)", CELL)],
            [p("<b>Unit tests</b>", CELL),
             p("(none)", CELL), p("(none)", CELL), p("(none)", CELL), p("pytest", CELL)],
            [p("<b>E2E tests</b>", CELL),
             p("(none)", CELL), p("(none)", CELL), p("(none)", CELL), p("pytest E2E (main only)", CELL)],
            [p("<b>pip caching</b>", CELL),
             p("(none)", CELL), p("(none)", CELL), p("(none)", CELL), p("actions/cache", CELL)],
            [p("<b>Multi-env deploy</b>", CELL),
             p("Yes (prod/dev)", CELL), p("No (dev only)", CELL), p("No (prod only)", CELL), p("No (prod only)", CELL)],
            [p("<b>Slack on failure</b>", CELL),
             p("No", CELL), p("No", CELL), p("No", CELL), p("Yes", CELL)],
            [p("<b>Docker health timeout</b>", CELL),
             p("120s", CELL), p("120s", CELL), p("300s", CELL), p("(default)", CELL)],
        ],
        [USABLE * 0.22, USABLE * 0.18, USABLE * 0.18, USABLE * 0.18, USABLE * 0.24],
    ))
    story.append(Spacer(1, 4))

    story.append(p("15.3 Key GitHub Secrets", H3))
    story.append(tbl(
        ["Secret Name", "Used By", "Purpose"],
        [
            [p("RAILWAY_TOKEN", MONO), p("All services", CELL), p("Railway API auth for deploy", CELL)],
            [p("RAILWAY_TOKEN_DEV", MONO), p("Cerebro", CELL), p("Separate token for develop environment", CELL)],
            [p("RAILWAY_SERVICE", MONO), p("Data Daemon", CELL), p("Service name override", CELL)],
            [p("RAILWAY_ENVIRONMENT", MONO), p("Data Daemon", CELL), p("Environment name override", CELL)],
            [p("SUPABASE_URL", MONO), p("Bot Farm", CELL), p("E2E test database URL", CELL)],
            [p("SUPABASE_SERVICE_ROLE_KEY", MONO), p("Bot Farm", CELL), p("E2E test auth", CELL)],
            [p("SLACK_BOT_TOKEN", MONO), p("Bot Farm", CELL), p("Failure notification", CELL)],
        ],
        [USABLE * 0.35, USABLE * 0.20, USABLE * 0.45],
    ))
    story.append(Spacer(1, 4))

    story.append(p("15.4 Adding a New Workflow", H3))
    story.append(tbl(
        ["Step", "Action"],
        [
            [p("1", CELL), p("Copy the closest existing workflow (Bot Farm is the most complete)", CELL)],
            [p("2", CELL), p("Update: trigger branches, service name, environment name", CELL)],
            [p("3", CELL), p("Add language setup if needed (Node, Python, etc.)", CELL)],
            [p("4", CELL), p("Add CI checks appropriate to the service (tests, type check, lint)", CELL)],
            [p("5", CELL), p("Add RAILWAY_TOKEN to GitHub repo secrets", CELL)],
            [p("6", CELL), p("Test with a PR push first (if your workflow triggers on PR)", CELL)],
            [p("7", CELL), p("Add Slack notification for failures (copy from Bot Farm)", CELL)],
        ],
        [0.3 * inch, USABLE - 0.3 * inch],
    ))
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 16. CI/CD Maturity Assessment ─────────────────────────────────
    story.append(p("16. CI/CD Maturity Assessment", H2))
    story.append(p(
        "An honest comparison of Greenmark's release pipeline against industry benchmarks. "
        "Graded against two baselines: top-50 Silicon Valley firms circa 2024 and the same firms today (2026)."))
    story.append(Spacer(1, 6))

    story.append(p("16.1 Current Grade: B-", H3))
    story.append(AccentBox(USABLE,
                           "Greenmark's CI/CD is <b>above average for a 5-person team</b> and <b>ahead of most "
                           "SMBs</b>, but below the bar set by well-funded SV startups. The biggest gap is not "
                           "tooling &mdash; it's coverage. Only 1 of 5 services has full test + deploy + alert."))
    story.append(Spacer(1, 6))

    # Maturity radar as table
    story.append(tbl(
        ["Dimension", "Greenmark", "SV Top 50 (2024)", "SV Top 50 (2026)", "Gap"],
        [
            [p("<b>Source Control</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("None &mdash; feature branches, PRs, protected main", CELL)],
            [p("<b>CI: Type Safety</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("None &mdash; tsc --noEmit on every push (Cerebro)", CELL)],
            [p("<b>CI: Unit Tests</b>", CELL),
             p('<font color="#92700A"><b>C+</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("Only Bot Farm has unit tests in CI. Cerebro, Daemon, AI: none.", CELL)],
            [p("<b>CI: E2E Tests</b>", CELL),
             p('<font color="#92700A"><b>B-</b></font>', CELL),
             p("A-", CELL), p("A", CELL),
             p("Bot Farm has live-DB E2E. Others have zero.", CELL)],
            [p("<b>CI: Migration Gate</b>", CELL),
             p('<font color="#C0392B"><b>D</b></font>', CELL),
             p("B+", CELL), p("A", CELL),
             p("Manual only. No CI runs migrations against test DB on PR.", CELL)],
            [p("<b>CD: Auto-Deploy</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("None &mdash; merge-to-deploy on all active services", CELL)],
            [p("<b>CD: Health Checks</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("None &mdash; Railway health checks + auto-rollback", CELL)],
            [p("<b>CD: Canary/Blue-Green</b>", CELL),
             p('<font color="#C0392B"><b>F</b></font>', CELL),
             p("B+", CELL), p("A", CELL),
             p("No staged rollouts. All-or-nothing deploys.", CELL)],
            [p("<b>Observability</b>", CELL),
             p('<font color="#92700A"><b>C</b></font>', CELL),
             p("A-", CELL), p("A", CELL),
             p("Prometheus metrics (daemon), but no centralized logging, APM, or tracing.", CELL)],
            [p("<b>Alerting</b>", CELL),
             p('<font color="#C0392B"><b>D+</b></font>', CELL),
             p("A-", CELL), p("A", CELL),
             p("Slack alerts on Bot Farm only. No PagerDuty, no on-call rotation.", CELL)],
            [p("<b>Rollback</b>", CELL),
             p('<font color="#92700A"><b>B</b></font>', CELL),
             p("A-", CELL), p("A", CELL),
             p("Railway auto-rollback for apps. No migration rollback system.", CELL)],
            [p("<b>Secrets Management</b>", CELL),
             p('<font color="#2D6B4A"><b>A-</b></font>', CELL),
             p("A", CELL), p("A", CELL),
             p("vault.secrets + GitHub Secrets + Knox. Well-separated.", CELL)],
            [p("<b>Documentation</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("B", CELL), p("B+", CELL),
             p("Ahead of most. ADRs, SOPs, CLAUDE.md &mdash; unusually thorough.", CELL)],
            [p("<b>AI-Agent Governance</b>", CELL),
             p('<font color="#2D6B4A"><b>A</b></font>', CELL),
             p("N/A", CELL), p("B-", CELL),
             p("Pioneering. Most SV firms still lack AI deployment guardrails.", CELL)],
        ],
        [USABLE * 0.16, USABLE * 0.10, USABLE * 0.12, USABLE * 0.12, USABLE * 0.50],
    ))
    story.append(Spacer(1, 6))

    story.append(p("16.2 Strengths (What Top 50 Firms Would Envy)", H3))
    story.append(tbl(
        ["Strength", "Why It Matters"],
        [
            [p("<b>ADR + SOP discipline</b>", CELL),
             p("Most SV firms have tribal knowledge. Greenmark has 35 ADRs and 5 SOPs with branded PDFs. "
               "This is rare even at large companies.", CELL)],
            [p("<b>AI agent governance</b>", CELL),
             p("Explicit rules for what AI can deploy alone vs. what needs human approval. Most firms "
               "haven't even thought about this yet.", CELL)],
            [p("<b>Database security model</b>", CELL),
             p("RLS + SECURITY DEFINER + service_role revocation + entity isolation. This is enterprise-grade "
               "multi-tenant security on a startup budget.", CELL)],
            [p("<b>Merge-to-deploy simplicity</b>", CELL),
             p("No release trains, no deploy queues, no approval chains. Fast feedback loop.", CELL)],
        ],
        [USABLE * 0.28, USABLE * 0.72],
    ))
    story.append(Spacer(1, 4))

    story.append(p("16.3 Gaps (Highest-Impact Improvements)", H3))
    story.append(tbl(
        ["Priority", "Gap", "Fix", "Effort"],
        [
            [p('<font color="#C0392B"><b>P0</b></font>', CELL),
             p("No automated migration gate", CELL),
             p("GitHub Action: supabase db push --db-url on PR", CELL),
             p("S (2h)", CELL)],
            [p('<font color="#C0392B"><b>P0</b></font>', CELL),
             p("Deploy alerts on 1/5 services", CELL),
             p("Add Slack step to all deploy.yml workflows", CELL),
             p("S (1h)", CELL)],
            [p('<font color="#E67E22"><b>P1</b></font>', CELL),
             p("No unit tests for Cerebro or Daemon", CELL),
             p("Add pytest/jest to CI; start with critical paths", CELL),
             p("M (1-2 weeks)", CELL)],
            [p('<font color="#E67E22"><b>P1</b></font>', CELL),
             p("No centralized logging", CELL),
             p("Railway Logdrain &rarr; Axiom/Datadog/Loki", CELL),
             p("M (1 week)", CELL)],
            [p('<font color="#92700A"><b>P2</b></font>', CELL),
             p("No canary deploys", CELL),
             p("Railway environments for canary; traffic split", CELL),
             p("L (2-4 weeks)", CELL)],
            [p('<font color="#92700A"><b>P2</b></font>', CELL),
             p("No structured on-call", CELL),
             p("PagerDuty or Opsgenie + runbooks", CELL),
             p("M (1 week)", CELL)],
        ],
        [0.35 * inch, USABLE * 0.28, USABLE * 0.40, USABLE * 0.20],
    ))
    story.append(Spacer(1, 4))

    story.append(AccentBox(USABLE,
                           "The two P0 items would move the grade from B- to B+ in about 3 hours of work. "
                           "The P1 items get to A- over 2-3 weeks. Canary deploys and on-call are where "
                           "the top 50 firms live &mdash; those are stretch goals for a team this size."))
    story.append(Spacer(1, 8))

    hr_line = hr()
    story.append(hr_line)

    # ── Why This Exists ───────────────────────────────────────────────
    story.append(p("Why This Exists", H2))
    story.append(p(
        "Greenmark's infrastructure grew organically &mdash; five services, two migration systems, one "
        "shared database, and AI agents writing code. Without a documented release process, each deployment "
        "was an oral tradition passed between sessions. This SOP codifies the pipeline so that any developer, "
        "AI agent, or on-call responder can deploy safely and roll back confidently."))
    story.append(Spacer(1, 4))
    story.append(p(
        "The catalyst: a gold layer expansion requiring coordinated migrations across two systems "
        "(data-daemon bronze + cerebro silver/gold), where convention mismatches led to 7 discovered "
        "conflicts. A documented release process would have caught these earlier."))
    story.append(Spacer(1, 6))

    # ── References ────────────────────────────────────────────────────
    story.append(p("References", H2))
    story.append(tbl(
        ["Document", "Location"],
        [
            [p("SOP-002: Database Migrations", CELL), p("greenmark-docs/sops/SOP-002-database-migrations.md", MONO)],
            [p("SOP-004: Technical Debt Remediation", CELL), p("greenmark-docs/sops/SOP-004-technical-debt-remediation.md", MONO)],
            [p("ADR-2026-03: Supabase Connection Strategy", CELL), p("greenmark-docs/adrs/ADR-2026-03.md", MONO)],
            [p("ADR-2026-04: Gold Tables Not Views", CELL), p("greenmark-docs/adrs/ADR-2026-04.md", MONO)],
            [p("ADR-2026-09: service_role Revoked", CELL), p("greenmark-docs/adrs/ADR-2026-09.md", MONO)],
            [p("ADR-2026-10: SECURITY DEFINER Refresh", CELL), p("greenmark-docs/adrs/ADR-2026-10.md", MONO)],
            [p("ADR-2026-11: Default Deny RLS", CELL), p("greenmark-docs/adrs/ADR-2026-11.md", MONO)],
        ],
        [USABLE * 0.38, USABLE * 0.62],
    ))


if __name__ == "__main__":
    build_doc(OUTPUT, "SOP-005: Release and Deployment", content)
