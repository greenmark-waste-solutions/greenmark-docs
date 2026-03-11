# ADR-2026-15: Soft Deletes Propagated Through All Layers

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-05, data-daemon CLAUDE.md Rule #2

## Context

- Greenmark's universal rule: **never use DELETE FROM** — all tables have `deleted_at` timestamps (data-daemon CLAUDE.md, Rule #2).
- In a medallion architecture, deletes must propagate: if a HubSpot deal is deleted in the source, it should be soft-deleted in bronze, silver, and gold.
- The MERGE pattern (ADR-2026-05) uses `WHEN NOT MATCHED BY SOURCE THEN DELETE` — but this must be a soft delete, not a hard delete.
- dbt's incremental models handle this with scoped delete+insert by partition key, which is the industry standard.

## Decision

- Every table at every layer has a `deleted_at TIMESTAMPTZ DEFAULT NULL` column.
- Bronze: `deleted_at` set when source record disappears from vendor extract.
- Silver: dbt propagates `deleted_at` from bronze. Silver queries filter `WHERE deleted_at IS NULL` for active records.
- Gold: MERGE's `WHEN NOT MATCHED BY SOURCE` sets `deleted_at = NOW()` instead of hard DELETE.
- Dashboard queries always filter `WHERE deleted_at IS NULL`.

## Revised MERGE Pattern for Soft Delete

```sql
MERGE INTO gold.deals AS t
USING _staging AS s
ON t.entity = s.entity AND t.deal_id = s.deal_id
WHEN MATCHED AND (...) IS DISTINCT FROM (...) THEN
    UPDATE SET ..., updated_at = NOW()
WHEN NOT MATCHED BY TARGET THEN
    INSERT (...)
WHEN NOT MATCHED BY SOURCE AND t.deleted_at IS NULL THEN
    UPDATE SET deleted_at = NOW();
```

## Consequences

- No data is ever physically removed. Full audit trail at every layer.
- Storage grows over time — periodic archival of old soft-deleted records may be needed.
- Dashboard performance is not affected if `deleted_at` is indexed.
- Restoration is trivial: `UPDATE SET deleted_at = NULL`.
