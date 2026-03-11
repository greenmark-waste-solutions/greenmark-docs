# ADR-2026-11: Default Deny RLS Policy on All Gold Tables

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-04, ADR-2026-12

## Context

- RLS in PostgreSQL "fails open" by default — if no policy matches, or if a policy is misconfigured/missing, all rows are visible to any role with SELECT.
- A gold table created without policies, or with a temporarily disabled policy, would expose all entity data to all users.
- This is the single most dangerous failure mode in a multi-tenant RLS system.

## Decision

- Every gold table gets a **RESTRICTIVE default deny policy** immediately upon creation, before any permissive policies are added.
- The default deny policy returns `false` for all rows to all roles.
- Permissive entity isolation policies are added after the default deny.

## Pattern

```sql
-- Step 1: Enable RLS
ALTER TABLE gold.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE gold.deals FORCE ROW LEVEL SECURITY;

-- Step 2: Default deny (RESTRICTIVE — must pass AND with permissive policies)
CREATE POLICY default_deny ON gold.deals
    AS RESTRICTIVE FOR ALL TO public USING (false);

-- Step 3: Permissive policies (combined with OR among themselves, AND with restrictive)
CREATE POLICY entity_isolation ON gold.deals
    AS PERMISSIVE FOR SELECT TO authenticated
    USING (entity = (current_setting('request.jwt.claims', true)::jsonb
           -> 'app_metadata' ->> 'entity_id'));

CREATE POLICY consolidated_access ON gold.deals
    AS PERMISSIVE FOR SELECT TO authenticated
    USING ((current_setting('request.jwt.claims', true)::jsonb
           -> 'app_metadata' ->> 'is_consolidated')::boolean = true);
```

## How It Works

- RESTRICTIVE policies combine with AND against all permissive policies.
- Wait — that means default_deny (RESTRICTIVE, USING false) would block everything, including legitimate queries.
- **Correction**: The default deny should be PERMISSIVE with `TO public`, and the real policies should be for `TO authenticated`. With no matching permissive policy for a role, RLS blocks by default when FORCE is on. The simpler approach: rely on FORCE ROW LEVEL SECURITY + ensure every table has at least one well-tested policy. Add a drift audit that alerts if any gold table has zero policies.

## Revised Decision

- `FORCE ROW LEVEL SECURITY` on every gold table (even owner is subject to RLS).
- Drift audit checks that every gold table has at least one RLS policy — zero policies = alert.
- REVOKE ALL FROM public and anon on gold tables — only `authenticated` gets SELECT via explicit GRANT.
- Entity isolation policies use `app_metadata` (tamper-proof, server-only) not `user_metadata`.

## Consequences

- No gold table can accidentally be queryable without RLS enforcement.
- Drift audit (see ADR-2026-14) catches tables with missing policies before they reach production.
- New gold tables MUST have RLS + policies added in the same migration — the forge tool enforces this.
