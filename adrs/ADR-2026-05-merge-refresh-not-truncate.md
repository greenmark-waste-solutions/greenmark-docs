# ADR-2026-05: Gold Refresh Uses MERGE, Not TRUNCATE+INSERT

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-04, ADR-2026-10

## Context

- Gold tables are regular tables that need periodic refresh from silver data (see ADR-2026-04).
- TRUNCATE+INSERT creates a window where the table is empty — any dashboard query during that window returns zero rows.
- TRUNCATE also acquires an ACCESS EXCLUSIVE lock, blocking all concurrent reads.
- PostgreSQL 15 introduced the MERGE statement, which provides atomic INSERT/UPDATE/DELETE in a single operation with no empty-table window.

## Decision

- Gold refresh uses **PostgreSQL 15 MERGE** statements, not TRUNCATE+INSERT.
- Refresh functions load silver data into a TEMP TABLE (staging), validate it, then MERGE into the gold target.
- TEMP TABLE is used instead of UNLOGGED TABLE because UNLOGGED tables are truncated to zero on crash recovery.

## Refresh Pattern

```sql
CREATE TEMP TABLE _staging AS SELECT ... FROM silver_schema.source_table;

-- Guard: non-empty source
IF (SELECT count(*) FROM _staging) = 0 THEN
    RAISE EXCEPTION 'Silver source empty — aborting refresh';
END IF;

-- Guard: delete ratio < 50%
-- Guard: PK uniqueness

MERGE INTO gold.target AS t
USING _staging AS s
ON t.entity = s.entity AND t.business_key = s.business_key
WHEN MATCHED AND (t.col1, t.col2) IS DISTINCT FROM (s.col1, s.col2) THEN UPDATE SET ...
WHEN NOT MATCHED BY TARGET THEN INSERT ...
WHEN NOT MATCHED BY SOURCE THEN DELETE;

DROP TABLE _staging;
```

## Consequences

- Zero-downtime refresh — readers always see a complete dataset.
- Requires stable business keys for deterministic row matching.
- Guards prevent catastrophic scenarios (empty source, mass deletion).
- Advisory locks serialize concurrent refresh per table (see ADR-2026-10).
