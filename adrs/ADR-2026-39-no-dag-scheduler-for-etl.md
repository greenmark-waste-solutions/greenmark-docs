# ADR-2026-39: No DAG Scheduler for ETL Job Queue

- **Status**: Accepted
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: [ADR-2026-33](ADR-2026-33-skip-locked-job-queue.md) (SKIP LOCKED Job Queue), [ADR-2026-26](ADR-2026-26-no-separate-post-ingestion-worker.md) (No Separate Post-Ingestion Worker)

## BLUF (Bottom Line Up Front)

We will not build a DAG scheduler for the ETL job queue. Bronze extraction is inherently flat — objects then associations, two levels — and cross-source dependencies live at the silver/gold layer where materialized view refresh order handles them. Priority-based ordering plus a single `_depends_on` field is the correct tool at this scale and topology.

## Context

During architecture review of the data-daemon ETL pipeline, we implemented job dependency enforcement: association tables (priority 0) are blocked until their parent object tables (priority 10) complete. This uses a `_depends_on` field in the job payload, checked by the `claim_job` SQL query via a `NOT EXISTS` subquery.

The question arose: should we build a proper DAG scheduler? The pipeline is growing from 1 data source (HubSpot, 33 tables) toward 10+ sources (Sage, Navusoft, fleet telematics, QuickBooks, ServiceTitan). At first glance, 10+ sources sounds like it demands a DAG.

We challenged this assumption.

## Decision

**Do not build a DAG scheduler.** Keep the current priority-based ordering with single `_depends_on` dependency enforcement.

### Current Architecture

```
Scheduler tick
  → Load service YAML
  → Split tables: objects (priority 10) vs associations (priority 0)
  → Enqueue all, setting _depends_on for association tables
  → Workers claim jobs via SKIP LOCKED
  → claim_job SQL blocks associations until parent object completes
```

This handles the only dependency pattern that exists in bronze extraction: objects → associations.

## Rationale

| Factor | Assessment |
|--------|-----------|
| **Extraction is flat** | Every source follows the same two-level pattern: extract objects, then extract associations. There are no three-level chains, no diamond dependencies, no conditional branches at the bronze layer. |
| **Sources are independent** | HubSpot extraction doesn't wait for Salesforce. QuickBooks doesn't need Google Contacts. Each source extracts independently. 10 sources = 10 independent two-level trees, not one 10-source DAG. |
| **Cross-source dependencies live in silver/gold** | A silver view joining HubSpot deals with Salesforce accounts is a `REFRESH MATERIALIZED VIEW` — that's view refresh ordering in the executor, not job queue ordering. The executor already refreshes silver views after bronze load. |
| **`_depends_on` handles the actual pattern** | The single string dependency covers every real case: `assoc_deal_contact` depends on `deals`, `assoc_call_deal` depends on `calls`. No table depends on two different parents within the same extraction service. |
| **YAGNI** | `graphlib.TopologicalSorter`, cycle detection, multi-parent dependency arrays, and DAG visualization solve problems we don't have. Adding them now means maintaining code that serves no purpose until the topology changes. |
| **The YAML is the DAG** | `assoc_from_table: hubspot_bronze.deals` is a human-readable dependency declaration. A runtime `TopologicalSorter` would produce the same ordering that priority-based enqueuing already produces — objects first, associations second. |

## The "10+ Sources" Counterargument

The initial instinct was that 10+ data sources would create cross-service dependencies requiring a DAG. On closer examination:

**What 10+ sources actually looks like at the job queue level:**

| Source | Objects | Associations | Dependencies |
|--------|---------|-------------|-------------|
| HubSpot | 17 tables | 16 tables | Each assoc depends on its parent object |
| Sage | ~10 tables | ~5 tables | Same pattern, independent of HubSpot |
| Navusoft | ~8 tables | ~3 tables | Same pattern, independent of others |
| QuickBooks | ~6 tables | ~2 tables | Same pattern |
| ... | ... | ... | ... |

Each source is an independent two-level tree. 10 independent trees is not a DAG — it's 10 separate lists that happen to run in the same job queue. The SKIP LOCKED mechanism already handles concurrency. Priority ordering already handles intra-source dependencies.

**Where cross-source dependencies actually live:**

```
Bronze layer:  Source A extracts independently | Source B extracts independently
               (job queue handles this)        | (job queue handles this)

Silver layer:  CREATE VIEW silver.unified_deals AS
               SELECT ... FROM hubspot_bronze.deals
               UNION ALL SELECT ... FROM sage_bronze.deals
               (view refresh order handles this — already in executor)

Gold layer:    MERGE INTO gold.deals ...
               (refresh function handles this — already in executor)
```

The cross-source join happens at silver/gold via SQL view definitions, not at the extraction layer. The executor already refreshes views after loading their source tables. No DAG needed.

## Options Considered

| Option | Verdict |
|--------|---------|
| **Keep priority + `_depends_on` (chosen)** | Correct tool for a flat topology. Zero new code. Already working. |
| Build DAG with `graphlib.TopologicalSorter` | Solves problems we don't have. ~100 lines of code with no current consumer. |
| Adopt Airflow/Dagster/Prefect | Massive infrastructure for a pipeline that runs 33 tables every 15 minutes. 1000x overkill. |
| Extend `_depends_on` to a list now | Pre-optimizing for multi-parent dependencies that don't exist in bronze extraction. |

## Consequences

- **Positive**: No new code to write, test, or maintain. The architecture stays simple. Mental model stays simple: "objects first, associations second." New data sources plug in with zero changes to the scheduler — just add a YAML file.
- **Negative**: If a bronze table ever needs to depend on two different parent tables within the same service, the single `_depends_on` string won't handle it. This is a known limitation we accept because the pattern doesn't exist today.
- **Mitigation**: Extending `_depends_on` from a string to a list is a 30-minute change when the need arises. The SQL subquery changes from checking one table name to checking `ANY()` on an array. The YAML schema adds a `depends_on:` list field. This is a trivial upgrade, not a rewrite.

## When to Revisit

- If a bronze table needs to depend on two different parent tables within the same extraction service (multi-parent dependency)
- If the executor needs to orchestrate cross-service extraction order (Source B must finish before Source A starts) — unlikely, but would be a real DAG use case
- If the pipeline grows beyond ~500 tables and execution planning (parallelism optimization) becomes worth the complexity
- If the team grows beyond 3 people and "just read the YAML" stops being sufficient for understanding execution order
