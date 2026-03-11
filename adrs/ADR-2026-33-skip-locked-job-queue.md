# ADR-2026-33: Postgres SKIP LOCKED for Job Queue

**Status:** Accepted
**Date:** 2026-02-27
**Author:** Daniel Shanklin

## Context

The CI engine needs a job queue to manage crawl, fusion, scoring, and alert jobs. Jobs execute sequentially via `claude -p` (one at a time), with throughput of ~10 jobs/hour constrained by source ToS rate limits. We need concurrent-safe claiming, parent-child relationships, and full audit trails.

Options considered:
1. Redis + Celery — industry standard for Python task queues
2. Postgres `SELECT ... FOR UPDATE SKIP LOCKED` — job queue in the database
3. RabbitMQ / SQS — managed message brokers

## Decision

Use Postgres `SELECT ... FOR UPDATE SKIP LOCKED` on `ci.jobs` table for the job queue. Same pattern as data-daemon.

```sql
SELECT * FROM ci.jobs
WHERE status = 'pending' AND deleted_at IS NULL
ORDER BY
    CASE WHEN parent_id IS NOT NULL THEN 0 ELSE 1 END,
    created_at ASC
LIMIT 1
FOR UPDATE SKIP LOCKED
```

## Why

1. **No new infrastructure** — we already have Postgres (Supabase). Adding Redis means another service to operate, monitor, and pay for.
2. **Jobs need rich state** — trust levels, parent-child trees, context blobs, message threads. These are relational data, not fire-and-forget messages. A database table handles this naturally. Redis would need a separate data layer.
3. **Throughput doesn't justify it** — ~10 jobs/hour. SKIP LOCKED handles thousands per second. We're 100x under capacity.
4. **Audit trail is built in** — `ci.job_events` captures every state transition. With Redis/Celery you'd need separate event tracking.
5. **Consistency with data-daemon** — same org, same Supabase, same pattern. One mental model for the team.
6. **No new dependencies** — psycopg2/SQLAlchemy already required for signal storage.

## Why Not Redis/Celery

- Celery adds ~15 transitive dependencies and requires a broker (Redis/RabbitMQ) running alongside the app
- We'd need both Postgres (for signals, trust, dossiers) AND Redis (for queuing) — two data stores for one app
- Celery's retry/backoff is powerful but we don't need it — source rate limits are the bottleneck, not infrastructure
- data-daemon already proved SKIP LOCKED works at our scale

## Consequences

- Job queue is coupled to the database — if Supabase is down, no jobs run (acceptable: signals also need the DB)
- No distributed workers across machines — fine for sequential `claude -p` execution
- If we ever need 100+ concurrent workers, we'd revisit (but `claude -p` is inherently single-threaded per job)
- NullPool (no connection pooling) is appropriate for this model — fresh connection per operation
