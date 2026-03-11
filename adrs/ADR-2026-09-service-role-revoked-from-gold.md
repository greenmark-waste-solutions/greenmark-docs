# ADR-2026-09: service_role Revoked from Gold Schema

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-04, ADR-2026-10

## Context

- Supabase's `service_role` has the `BYPASSRLS` attribute, meaning it ignores all Row-Level Security policies.
- Even with `FORCE ROW LEVEL SECURITY` enabled on gold tables, `service_role` bypasses RLS because `BYPASSRLS` overrides `FORCE RLS`.
- Any code using the Supabase service key (server-side SDK, edge functions, background jobs) would see all entity data without restriction.
- Gold refresh doesn't need `service_role` — it uses SECURITY DEFINER functions that run with the function owner's privileges.

## Decision

- **REVOKE ALL ON ALL TABLES IN SCHEMA gold FROM service_role.**
- Gold refresh functions are owned by `svc_etl_runner` and declared SECURITY DEFINER — they don't need service_role's BYPASSRLS.
- If a server-side function needs gold data, it must use the `authenticated` role with a proper JWT, subject to RLS like everyone else.

## Consequences

- Eliminates the most dangerous bypass path for RLS on gold.
- Any existing server-side code using `supabase.from('deals').select('*')` with the service key will get permission denied. This is intentional.
- Edge functions and background jobs must be refactored to use user-context JWTs or SECURITY DEFINER functions.
- DEFAULT PRIVILEGES must also revoke future grants: `ALTER DEFAULT PRIVILEGES IN SCHEMA gold REVOKE ALL FROM service_role;`
