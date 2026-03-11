# ADR-2026-26: No Separate Post-Ingestion Worker — data-daemon Handles Extraction and Transformation

- **Status**: Accepted
- **Date**: 2026-03-04
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: `projects/data-integration/`, `reference/infrastructure-map-walkthrough.srt`

## BLUF (Bottom Line Up Front)

Do not create a separate post-ingestion worker service. data-daemon handles extraction and transforms in one process, with Postgres materialized views doing the SQL-based Bronze-to-Silver-to-Gold work. At Greenmark's scale (15 systems, thousands of records), a separate worker is overhead with no performance justification — it costs $5/mo on Railway and adds monitoring surface for zero benefit.

## Context

With the medallion architecture (Bronze/Silver/Gold) taking shape, the question arose: should there be a separate `cerebro-worker` service to handle post-ingestion transformations (Bronze → Silver → Gold), or should that work stay within data-daemon and Postgres?

The current architecture:
- **data-daemon** extracts vendor data into Bronze schemas (YAML-driven, Postgres job queue, 82 tests)
- **Supabase** hosts the warehouse (PostgreSQL)
- **Cerebro** reads from Gold for dashboards
- **cerebro-qa** monitors data quality (separate service)

Post-ingestion work includes:
1. **Bronze → Silver**: Column renaming, type normalization, entity tagging, deduplication
2. **Silver crosswalks**: Identity resolution — fuzzy matching a Navusoft customer to a HubSpot contact to a Sage AR account
3. **Silver → Gold**: Cross-source joins, metric calculations
4. **Gold aggregates**: Daily/weekly/monthly rollups

## Decision

**Do not create a separate post-ingestion worker.** Instead:

- **Bronze → Silver transforms**: Postgres materialized views and SQL functions. No application code needed.
- **Identity resolution**: data-daemon `transform` job type. Runs after extraction, reads from Silver, writes crosswalk records. Uses Python libraries (fuzzywuzzy, etc.) that can't be done in SQL.
- **Silver → Gold**: Postgres materialized views with cross-source joins.
- **Gold aggregates**: Postgres materialized views refreshed by pg_cron or data-daemon scheduler.
- **Data quality**: Already handled by cerebro-qa (separate service, already deployed).

## Rationale

| Factor | Assessment |
|--------|-----------|
| **Scale** | 15 systems, 3 entities, thousands of records. Postgres handles transforms in milliseconds. A separate worker is overhead with no performance justification. |
| **Job queue exists** | data-daemon already uses Postgres `SKIP LOCKED` job queue. Adding `transform` jobs alongside `extract` jobs is trivial — same scheduler, same queue, same monitoring. |
| **Most transforms are SQL** | `CREATE MATERIALIZED VIEW sage_silver.gl_entries AS SELECT ... FROM sage_bronze.gl_entries` doesn't need Python, a container, or a deployment pipeline. |
| **Identity resolution** | The one exception — fuzzy matching genuinely needs Python. But it's a data-daemon job type, not a new service. |
| **Operational cost** | Each Railway service costs ~$5/mo minimum and adds monitoring, deployment, and debugging surface. Don't pay for what you don't need. |

## Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. data-daemon + Postgres** | Extraction + transform in one service, views in SQL | Simple, no new infra, fits current scale | data-daemon has dual responsibility |
| B. Separate cerebro-worker | Dedicated Python service for all post-ingestion transforms | Clean separation of concerns, independent scaling | New service to build/deploy/monitor, premature at this scale, $5+/mo on Railway |
| C. All in Postgres | pg_cron + SQL functions + materialized views for everything, including identity resolution | Zero application code for transforms | Identity resolution needs fuzzy matching libraries that don't exist in Postgres |
| D. dbt | Industry-standard transform layer | Well-documented patterns, lineage tracking | New tool to learn, new dependency, overkill for 15 sources |

## When to Revisit

Create a separate worker **only when one of these conditions is met**:

1. **Transform contention** — transforms take longer than extraction cycles, blocking the job queue
2. **ML-based identity resolution** — embeddings or model inference that needs GPU or heavy compute
3. **Real-time streaming** — vendor webhooks requiring instant Silver updates where batch scheduling doesn't work
4. **Fault isolation** — transform failures repeatedly blocking extraction runs

**None of these conditions exist at Greenmark's current scale.** Revisit when they do.

## Consequences

- **Positive**: No new service to build, deploy, or monitor. Faster time to value. data-daemon stays the single extraction+transform entry point. SQL-based transforms are transparent and auditable.
- **Negative**: data-daemon takes on transform responsibility in addition to extraction. If transforms grow complex, the codebase grows.
- **Neutral**: Gold materialized views need refresh scheduling — either pg_cron or data-daemon triggers. Both are straightforward.

## Implementation

1. Bronze → Silver: Write materialized views in migration files (one per source schema)
2. Identity resolution: Add `transform` job type to data-daemon's YAML config and job queue
3. Silver → Gold: Write cross-source materialized views
4. Refresh: data-daemon triggers `REFRESH MATERIALIZED VIEW CONCURRENTLY` after successful extraction runs
