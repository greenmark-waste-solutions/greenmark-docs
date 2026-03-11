# ADR-2026-12: Entity Isolation via JWT app_metadata

- **Status**: Amended (2026-03-09)
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-11, ADR-2026-04, ADR-2026-22

## Context

- Greenmark operates three entities: NTX, Hometown, Memphis. Some users see one entity; executives see all ("consolidated" view).
- RLS policies need a trusted source for the user's entity assignment.
- Supabase JWTs contain two metadata fields:
  - `user_metadata` — editable by the user via `supabase.auth.updateUser()`. **Not trusted.**
  - `app_metadata` — only editable server-side via the admin API or service role. **Tamper-proof.**
- Using `user_metadata` for entity claims would let any authenticated user change their entity to see other entities' data.

## Decision

- Entity assignment is stored in `app_metadata.entity_id` (e.g., `"ntx"`, `"hometown"`, `"memphis"`).
- Consolidated access is stored in `app_metadata.is_consolidated` (boolean).
- RLS policies read from `app_metadata` only: `current_setting('request.jwt.claims', true)::jsonb -> 'app_metadata' ->> 'entity_id'`.
- Entity assignment is set during user provisioning via the Supabase admin API and cannot be changed by the user.

## RLS Policy Pattern

```sql
-- Single-entity users
CREATE POLICY entity_isolation ON gold.deals
    AS PERMISSIVE FOR SELECT TO authenticated
    USING (entity = (current_setting('request.jwt.claims', true)::jsonb
           -> 'app_metadata' ->> 'entity_id'));

-- Consolidated users (executives)
CREATE POLICY consolidated_access ON gold.deals
    AS PERMISSIVE FOR SELECT TO authenticated
    USING ((current_setting('request.jwt.claims', true)::jsonb
           -> 'app_metadata' ->> 'is_consolidated')::boolean = true);
```

## Consequences

- Entity claims are tamper-proof — no client-side attack can change entity assignment.
- User provisioning must set `app_metadata` correctly. Wrong assignment = wrong data visibility.
- Consolidated flag is separate from entity — an executive can have both `entity_id: 'ntx'` and `is_consolidated: true` if needed.
- Every gold table must have the `entity` column for RLS to function.

## Amendment: 2026-03-09 — Entities Array

### Single `entity_id` Evolved to `entities[]` Array

The original design used a single `entity_id` string and a separate `is_consolidated` boolean. This has been replaced with an `entities` array in both the database and JWT claims.

**Database (`user_roles` table):**

```sql
-- Old: entity TEXT (single value like 'ntx', 'both')
-- New: entities TEXT[] (array like ['ntx'], ['ntx','hometown'], ['*'])
```

- `['*']` = wildcard = all entities (replaces `is_consolidated: true`)
- `['ntx']` = single entity access
- `['ntx', 'hometown']` = multi-entity access without full consolidated view

**JWT claims (`app_metadata`):**

```json
{
  "app_metadata": {
    "role": "cfo",
    "entities": ["*"],
    "permissions": ["financial:view", ...]
  }
}
```

**Auth hook** (`rbac.custom_access_token_hook`): Reads `entities` from `user_roles` and copies the array directly into `app_metadata.entities`. A migration hook also handles the legacy `entity` text column by expanding it to an array (e.g., `'both'` → `['*']`, `'ntx'` → `['ntx']`).

### Updated RLS Pattern

```sql
-- Array-based entity isolation
CREATE POLICY entity_isolation ON gold.deals
    AS PERMISSIVE FOR SELECT TO authenticated
    USING (
      (current_setting('request.jwt.claims', true)::jsonb
       -> 'app_metadata' -> 'entities') ? '*'
      OR
      (current_setting('request.jwt.claims', true)::jsonb
       -> 'app_metadata' -> 'entities') ? entity
    );
```

The `?` operator checks if the JSONB array contains the value. `'*'` grants access to all rows; otherwise the row's `entity` column must be present in the user's `entities` array.

### Single-Tenant-Per-User Constraint

A `UNIQUE (user_id)` constraint on `user_roles` ensures one row per user (ADR-2026-22). The `entities` array on that single row defines the user's full entity scope within their tenant.
