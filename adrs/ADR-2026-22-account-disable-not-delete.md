# ADR-2026-22: Account Disable (Not Delete) with Single-Tenant-Per-User Constraint

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-15, ADR-2026-11, ADR-2026-20

## Context

- Superadmins need the ability to revoke a user's access to Cerebro.
- Hard deleting a user destroys audit trails, breaks foreign key references, and violates the soft-delete policy (ADR-2026-15).
- Soft deleting (`deleted_at`) semantically means "this record no longer exists" — but a disabled user's record DOES exist, they're just not allowed in. Different intent, different column.
- Supabase Auth provides `banned_until` on `auth.users`, but this is a blunt global instrument — it blocks the user from the entire Supabase project across all applications. We need application-level control.
- The system is multi-tenant from day one (NTX, Hometown, Memphis), but a user belongs to exactly one tenant. There is no cross-tenant user scenario.

## Decision

### Schema: `is_active` on `user_roles`

```sql
ALTER TABLE user_roles ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE user_roles ADD COLUMN suspended_at TIMESTAMPTZ;
ALTER TABLE user_roles ADD COLUMN suspended_by UUID;
ALTER TABLE user_roles ADD COLUMN suspension_reason TEXT;
```

Since a user has exactly one `user_roles` row (enforced by unique constraint), `is_active` on `user_roles` IS the global gate. No separate `user_accounts` table needed.

### Single-Tenant-Per-User Constraint

```sql
ALTER TABLE user_roles ADD CONSTRAINT uq_user_roles__user_id UNIQUE (user_id);
```

This prevents a user from having roles in multiple tenants. One person, one tenant, one row. If a user needs to move tenants, the existing row is updated — not a second row created.

### Why Not `banned_until`?

| Approach | Scope | Reversibility | Separation of Concerns |
|----------|-------|---------------|----------------------|
| `is_active` on `user_roles` | Application-level | Toggle on/off | Auth ≠ Authorization |
| `banned_until` on `auth.users` | Supabase-wide | Must clear timestamp | Conflates auth + authz |

We use `is_active` as the source of truth. Optionally, `auth.admin.signOut(user_id)` is called on disable to revoke refresh tokens immediately — but this is a belt-and-suspenders measure, not the primary control.

### Enforcement: Middleware + RLS (Defense in Depth)

**Middleware** (fast UX gate):
- During role resolution, if `is_active = false`: sign out the user and redirect to `/login?error=account_disabled` (pages) or return `401` (API routes).
- Prevents self-lockout: a superadmin cannot disable their own account.

**RLS** (hard database gate):
- All RLS policies on protected tables include `is_active = true` via a central function:
  ```sql
  CREATE FUNCTION app_is_active(uid uuid) RETURNS boolean AS $$
    SELECT COALESCE(
      (SELECT is_active FROM user_roles WHERE user_id = uid AND deleted_at IS NULL),
      false
    );
  $$ LANGUAGE sql STABLE SECURITY DEFINER;
  ```
- Every gold table RLS policy includes `app_is_active(auth.uid())` as an AND condition.
- This catches any code path that bypasses middleware (service-role endpoints acting on behalf of users, direct Supabase client queries).

### Session Invalidation

- **Primary**: Block on next request via middleware. The disabled user's current JWT remains valid until expiry, but middleware catches them on the next page load or API call.
- **Secondary**: Call `auth.admin.signOut(user_id)` to revoke refresh tokens. This prevents new JWTs from being issued.
- **JWT TTL**: Keep access token expiry at 15–30 minutes to minimize the exposure window.
- **Not implemented**: Token denylist / immediate JWT invalidation. Overkill for an internal app with short-lived tokens.

### Admin UI

- Toggle button on `/admin/users` page with confirmation dialog.
- Requires typing the user's email to confirm (same pattern as password reset).
- Optional reason field logged to audit.
- Status shown inline on user table (active/disabled badge).

### Audit Logging

Every disable/enable action logs to `audit.access_log`:
- `event`: `"user_disabled"` or `"user_enabled"`
- `metadata`: `{ target_user_id, target_email, reason, previous_status }`
- Actor identified by the admin's user_id and email.

## Consequences

### Positive
- Disabled users are locked out at both application (middleware) and database (RLS) layers.
- Full audit trail — who was disabled, by whom, when, and why.
- Reversible — re-enabling is a single toggle, no re-provisioning needed.
- Single-tenant constraint prevents role row proliferation and simplifies all authorization logic.
- Consistent with soft-delete policy — `is_active = false` is conceptually different from `deleted_at IS NOT NULL`.

### Negative
- Disabled users can still authenticate with Supabase (get a JWT) — they're just blocked at the app layer. For an internal app this is acceptable.
- Adding `app_is_active()` to all RLS policies is a migration effort. Must be done for every existing and future gold table.

### Risks
- If the `app_is_active()` function has a bug or the `user_roles` table is inaccessible, the function returns `false` (fail-closed) — disabled by default.
- RLS policy updates must be applied atomically. A partially-applied migration could leave some tables without the `is_active` check.

## Alternatives Considered

1. **Separate `user_accounts` table** — Rejected. With single-tenant-per-user, `user_roles` has exactly one row per user. A separate table adds a join with no benefit.
2. **Supabase `banned_until` only** — Rejected. Too blunt (blocks all Supabase access globally), conflates authentication with authorization.
3. **Soft delete (`deleted_at`)** — Rejected for disable. Soft delete means "this record no longer exists." Disable means "this record exists but access is revoked." Different semantics, different column. Both can coexist on the same row.
4. **Immediate JWT invalidation via denylist** — Rejected. Requires Redis or fast-access store checked on every request. Disproportionate complexity for an internal app with <50 users and 15-minute JWT TTL.
