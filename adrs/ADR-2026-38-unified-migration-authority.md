# ADR-2026-38: Unified Migration Authority for Shared Database

- **Status**: Accepted
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: [ADR-2026-37](ADR-2026-37-dag-aware-deploy-planning.md) (DAG validation), [ADR-2026-04](ADR-2026-04-medallion-architecture.md) (Medallion architecture), [ADR-2026-07](ADR-2026-07-per-vendor-bronze-silver-schemas.md) (Per-vendor schemas), [SOP-005](../sops/SOP-005-release-and-deployment.md) (Release & Deployment)

## BLUF (Bottom Line Up Front)

All medallion schema DDL — bronze, silver, gold, RLS, forge — moves to a dedicated `cerebro-migrations` repo with Supabase CLI as the single migration tool. data-daemon and cerebro become pure consumers: one writes data, the other reads it. Neither owns the database. This eliminates cross-repo migration ordering failures by removing the cross-repo migration pattern entirely.

## Context

On 2026-03-11, a cerebro silver expansion migration failed in production because it referenced `hubspot_bronze.tickets` — a bronze table created by data-daemon migration 016, which hadn't been deployed. The root cause: two repos independently mutating the same database with no coordination mechanism.

We evaluated 16+ architectural options including CI gates, consolidation into either repo, monorepos, git submodules, schema contracts, migration artifacts, and deploy manifests. We consulted multiple AI models and industry sources. Every credible source converged on the same answer: **one migration owner per shared database.**

The debate over whether cerebro or data-daemon should be that owner revealed a deeper problem: neither is the right owner. cerebro is a frontend — it shouldn't dictate database schema. data-daemon is an ETL runner — making it the migration authority turns it into a platform service with dangerous blast radius (RLS policy changes auto-applied on startup).

The database is a shared contract. It should have its own repo.

## Decision

Create a `cerebro-migrations` repo that serves as the single migration authority for the shared Greenmark PostgreSQL database.

### What moves to cerebro-migrations

| Artifact | Current Owner | Source |
|----------|--------------|--------|
| Bronze table DDL (`CREATE TABLE *_bronze.*`) | data-daemon | data-daemon migrations 001-019 |
| Bronze indexes and constraints | data-daemon | data-daemon migrations |
| Silver materialized views | cerebro | cerebro supabase/migrations |
| Gold materialized views | cerebro | cerebro supabase/migrations |
| RLS policies and grants | cerebro | cerebro supabase/migrations |
| Forge refresh functions | cerebro | cerebro supabase/migrations |
| Schema creation and role setup | cerebro | cerebro supabase/migrations |

### What stays where it is

| Artifact | Owner | Why |
|----------|-------|-----|
| `daemon.migration_history` table | data-daemon | Runtime-internal, not medallion |
| `daemon.sync_state`, `daemon.job_queue` | data-daemon | Runtime-internal |
| ETL connectors and sync logic | data-daemon | Writes data, doesn't define schema |
| Next.js app, API routes, UI | cerebro | Reads gold tables, renders pages |

### Service roles after migration

- **cerebro-migrations**: Owns all DDL. Runs `npm run migrate` via Supabase CLI. Has CI that validates full migration stack in ephemeral Postgres. The single source of truth for database schema.
- **data-daemon**: Pure ETL runner. Freezes at migration 019 for daemon-internal tables. Writes data to bronze tables that already exist. No new DDL.
- **cerebro**: Pure frontend consumer. Zero migrations. Reads gold tables via Supabase client. Renders UI.

### Migration execution

- All migrations use Supabase CLI timestamp format (`YYYYMMDDHHMMSS_description.sql`)
- `npm run migrate` applies all pending migrations in order
- Migrations are NOT auto-applied on any service startup
- CI spins up ephemeral Postgres, applies full migration stack, validates (powered by elt-forge DAG validation per ADR-2026-37)

### One-time cutover plan

1. Create `cerebro-migrations` repo with Supabase CLI toolchain
2. Copy cerebro's existing `supabase/migrations/` as the baseline
3. Translate data-daemon's bronze DDL (migrations 001-019) into timestamp-format migrations, ordered before cerebro's existing migrations
4. Insert migration history records into `supabase_migrations.schema_migrations` so existing migrations are marked as already-applied
5. Freeze data-daemon's `migrate.py` — it continues to apply daemon-internal migrations only, skips anything in `*_bronze` schemas
6. Remove `supabase/migrations/` from cerebro
7. Update SOP-005 deploy procedures to reference cerebro-migrations

## Rationale

| Factor | Assessment |
|--------|-----------|
| Industry consensus | Every source (Reddit, CircleCI, Supabase community, medallion architecture guides) says: one migration owner per shared database |
| Incident prevention | Cross-repo ordering failures are structurally impossible — there's only one repo |
| Clean ownership | Neither service "owns" the database. The database has its own repo. Both services are consumers of the schema contract |
| AI agent workflow | Agent writes DDL in one place, runs one command. No cross-repo dependency reasoning required |
| RLS safety | RLS policy changes go through PR review in a dedicated repo, not auto-applied on ETL service startup |
| Scale | New vendor integrations (accelerating) require only one PR to one repo — bronze DDL + silver views + gold views in one sequence |
| Tooling | Supabase CLI is purpose-built for this workflow. Already proven in cerebro |

## Options Considered

| Option | Verdict |
|--------|---------|
| **Keep split ownership, add CI gate against production** | Rejected. Point-in-time check, race conditions, false sense of security |
| **Consolidate all DDL into cerebro** | Rejected. Frontend shouldn't own database schema. Semantic mismatch |
| **Consolidate all DDL into data-daemon** | Rejected. Turns ETL runner into platform service. Auto-apply on startup is dangerous for RLS/security changes |
| **Versioned migration artifacts** | Rejected. Package management overhead for a 2-person team |
| **Schema contract tests** | Rejected. Separate contract system that drifts from migration reality |
| **Monorepo** | Rejected. Solves the problem but blast radius to existing workflows is disproportionate |
| **Git submodule** | Rejected. Submodules are notoriously clunky and error-prone |
| **Idempotent pre-requisites (CREATE IF NOT EXISTS)** | Rejected. Dangerous — hides dependency problems, tangles schema ownership |
| **Do nothing, fix the SOP** | Rejected. Relies on perfect human/agent discipline |
| **Dedicated migrations repo (cerebro-migrations) ✓** | Accepted. Clean ownership, single authority, industry-standard pattern |

## Deploy Coordination: Schema-First, Apps Tolerant

Schema repo and app repos have independent CI/CD. No cross-repo triggers. No orchestrator. No release branches.

**Normal path**: Schema deploys first, apps lag slightly behind. Both apps are already forward-compatible:
- data-daemon: if a bronze table doesn't exist, ETL job fails gracefully, gets logged, scheduler moves on
- cerebro: if a gold view doesn't exist, page shows no data

**Deploy sequence**:
1. `cerebro-migrations`: `npm run migrate` — DB is now at schema version N
2. `data-daemon`: deploys whenever — ETL runs against whatever tables exist
3. `cerebro`: deploys whenever — UI reads whatever gold views exist

**Breaking changes** (drop column, rename table, change view shape) use expand/contract:
1. **Expand**: Migration adds the new thing alongside the old thing
2. **Update**: Apps update to use the new thing (separate deploys)
3. **Contract**: Migration removes the old thing

Three separate commits, three separate deploys, zero coordination needed. Each step is independently safe.

## Consequences

- **Positive**: Cross-repo migration ordering failures eliminated. One source of truth for database schema. Clean separation: migrations repo owns schema, data-daemon owns ETL, cerebro owns UI. RLS changes get proper review instead of auto-applying on startup. AI agents have a simple workflow: write DDL in one repo, one command to apply.
- **Negative**: Third repo to maintain. One-time cutover effort to translate and merge existing migrations. data-daemon developers must commit bronze DDL to a different repo than the connector code.
- **Mitigation**: AI agents handle multi-repo workflows trivially — repo count is not a friction factor. One-time cutover is scriptable. CODEOWNERS on cerebro-migrations ensures review discipline. data-daemon's CLAUDE.md documents "bronze DDL lives in cerebro-migrations."

## When to Revisit

- If team grows beyond 5 engineers and migration review becomes a bottleneck — consider domain-scoped CODEOWNERS (bronze reviewers, security reviewers)
- If a third service needs to write DDL — validates this pattern (just another consumer of the migrations repo)
- If Supabase CLI gains native multi-repo migration support — evaluate whether a dedicated repo is still needed
