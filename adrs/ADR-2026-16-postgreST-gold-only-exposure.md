# ADR-2026-16: PostgREST Exposes Only the Gold Schema

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-08, ADR-2026-09, ADR-2026-04

## Context

- Supabase uses PostgREST to auto-generate a REST API from PostgreSQL schemas.
- The `PGRST_DB_SCHEMAS` configuration controls which schemas are API-accessible. This is the primary firewall for data exposure.
- Bronze and silver contain raw and intermediate vendor data — exposing these would bypass the security model entirely.
- With 30 bronze+silver schemas containing 75–750 tables, accidentally exposing any of them would be a significant data breach.

## Decision

- `PGRST_DB_SCHEMAS` is set to `gold` only. No other schemas are API-accessible.
- Bronze and silver schemas have no USAGE grant to `authenticated` or `anon` roles.
- The `public` schema is empty or contains only Supabase system objects — no business data.
- Any server-side function that needs silver/bronze data uses SECURITY DEFINER functions in the `secure` schema, not direct schema access.

## Verification

```sql
-- Confirm only gold is exposed
-- Check Supabase dashboard → Settings → API → Schema

-- Verify no USAGE grants on internal schemas
SELECT grantee, table_schema
FROM information_schema.role_usage_grants
WHERE table_schema LIKE '%_bronze' OR table_schema LIKE '%_silver';
-- Should return zero rows for authenticated/anon
```

## Consequences

- The Supabase client can only see `gold.*` tables. Bronze and silver are invisible.
- Server-side operations (edge functions, cron jobs) that need internal data must use the `secure` schema's SECURITY DEFINER functions.
- Adding a new schema to PostgREST requires an explicit configuration change — no accidental exposure.
