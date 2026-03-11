# ADR-2026-06: dbt Manages Bronze→Silver Only, Never Gold

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-04, ADR-2026-05, ADR-2026-13

## Context

- dbt's default table materialization uses DROP + CREATE, which destroys all table metadata: RLS policies, grants, indexes, constraints, and comments.
- Even `dbt run --full-refresh` on incremental models performs DROP + CREATE.
- Gold tables carry RLS policies, FORCE ROW LEVEL SECURITY, grants to specific roles, and named constraints — all of which would be destroyed by dbt's DDL cycle.
- An accidental `dbt run --full-refresh` against gold in production would silently remove all security policies, leaving entity data exposed.

## Decision

- **dbt operates exclusively on bronze→silver transformations.** Its schemas are `*_bronze` and `*_silver`.
- **dbt has zero access to the gold schema.** The `svc_dbt_runner` role has no CREATE, INSERT, UPDATE, or DELETE grants on `gold`.
- **Gold table lifecycle** (DDL, RLS, grants) is managed by SQL migrations and the forge tool.
- **Gold data loading** (DML via MERGE) is performed by SECURITY DEFINER refresh functions owned by `svc_etl_runner`.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A. dbt manages all layers (rejected) | Single tool for everything | DROP+CREATE destroys RLS — fatal flaw |
| B. dbt incremental-only on gold (rejected) | dbt handles gold DML | No protection against --full-refresh; still needs grants dbt shouldn't have |
| C. dbt bronze→silver, forge does gold (selected) | Clean separation, gold security preserved | Two tools to understand |

## Consequences

- Clear ownership boundary: dbt = transformation, forge = security hardening + data loading.
- CI/CD should include a check that rejects any dbt model targeting the `gold` schema.
- The forge tool must be reliable for gold refresh — it's the only path.
