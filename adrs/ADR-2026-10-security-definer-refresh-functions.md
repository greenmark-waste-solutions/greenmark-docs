# ADR-2026-10: SECURITY DEFINER Refresh Functions with Hardened search_path

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-05, ADR-2026-09

## Context

- Gold tables need to be refreshed from silver data, but the API-facing roles (`authenticated`, `anon`) must not have write access to gold.
- PostgreSQL SECURITY DEFINER functions execute with the privileges of the function owner, not the caller — enabling a least-privilege ETL role to write to gold without granting write access broadly.
- SECURITY DEFINER functions are vulnerable to search_path hijacking: an attacker could create shadow objects in `pg_temp` or `public` that the function resolves instead of the intended schema objects.
- Advisory locks (`pg_advisory_xact_lock`) prevent concurrent refresh of the same gold table, avoiding race conditions.

## Decision

- Gold refresh functions are declared `SECURITY DEFINER` and owned by `svc_etl_runner`.
- Every refresh function includes `SET search_path = pg_catalog, gold, silver` to prevent search_path hijacking. No user-writable schemas (including `public`) in the path.
- Every refresh function acquires an advisory lock keyed to the target table: `PERFORM pg_advisory_xact_lock(hashtext('gold.table_name'));`
- Functions are placed in the `secure` schema, isolated from business logic.

## Pattern

```sql
CREATE OR REPLACE FUNCTION secure.refresh_deals()
RETURNS TEXT LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, gold, hubspot_silver
AS $$
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('gold.deals'));
    -- TEMP TABLE staging, guards, MERGE (see ADR-2026-05)
    RETURN 'OK';
END;
$$;

ALTER FUNCTION secure.refresh_deals() OWNER TO svc_etl_runner;
REVOKE EXECUTE ON FUNCTION secure.refresh_deals() FROM public;
GRANT EXECUTE ON FUNCTION secure.refresh_deals() TO svc_etl_runner;
```

## Consequences

- Only `svc_etl_runner` can trigger gold refresh. No other role can write to gold.
- search_path is locked — shadow object attacks are not possible.
- Advisory locks prevent double-refresh. Second caller blocks until first completes.
- Functions must be explicitly updated when silver schema names change.
