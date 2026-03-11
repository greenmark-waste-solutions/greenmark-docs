# ADR-2026-04: Gold Layer Uses Regular Tables, Not Materialized Views

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-05, ADR-2026-06, Project Cerebro

## Context

- The Cerebro data platform uses a medallion architecture (bronze → silver → gold) in PostgreSQL/Supabase.
- Gold is the only layer exposed to the Next.js dashboard via PostgREST.
- Greenmark operates three entities (NTX, Hometown, Memphis) that must be isolated via Row-Level Security (RLS).
- Initial design used materialized views for gold. PostgreSQL does not support RLS on materialized views or regular views — RLS policies can only be attached to regular tables.
- Wrapper views over RLS-protected tables were considered but rejected: views don't have native RLS, and SECURITY BARRIER views add complexity without real security guarantees at the view level.

## Decision

- All gold-layer objects are **regular tables**, not materialized views or views.
- RLS policies are applied directly to gold tables.
- `FORCE ROW LEVEL SECURITY` is enabled on every gold table so even table owners are subject to policies.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A. Materialized views (rejected) | Simple refresh, good read perf | No RLS support — fundamental blocker |
| B. Regular views over RLS tables (rejected) | Thin layer, auto-updates | Views don't have native RLS, SECURITY BARRIER is a hack |
| C. Regular tables with RLS (selected) | Full RLS support, FORCE RLS, industry standard | Requires explicit refresh mechanism |

## Consequences

- Gold tables require an explicit refresh mechanism (see ADR-2026-05: MERGE Refresh).
- Gold table DDL (CREATE, ALTER) is managed by migrations and the forge tool, never by dbt (see ADR-2026-06).
- Dashboard queries hit real tables with real RLS enforcement — no bypass path exists.
