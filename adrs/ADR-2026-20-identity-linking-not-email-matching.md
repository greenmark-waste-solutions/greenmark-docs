# ADR-2026-20: Identity Linking, Not Email Matching

**Status**: Accepted
**Date**: 2026-03-09
**Author**: Daniel Shanklin

## Context

Cerebro supports multiple login methods (email/password, GitHub OAuth, future Microsoft Entra). A single person may use different emails across providers — e.g., `dshanklin@greenmarkwaste.com` for password login and `daniel@boone.voyage` on GitHub.

The naive approach — matching users by email — breaks when provider emails differ. We discovered this when GitHub OAuth created a second `auth.users` record instead of resolving to the existing Greenmark account.

## Decision

**Identity is determined by `auth.users.id`, not by email.** Multiple login methods are linked to a single auth user via `auth.identities`. The provider's email is irrelevant to authorization.

### How it works

```
auth.users        1 row per person (canonical identity)
auth.identities   N rows per person (one per login method)
user_roles        1 row per person (role + entity scope)
```

- `user_roles.email` is the person's **Greenmark email** — used for display and email-based login matching.
- `user_roles.github_username` is their **GitHub handle** — used for first-time GitHub OAuth matching only.
- `user_roles.github_user_id` is their **GitHub numeric ID** (permanent, immutable) — used for all subsequent GitHub logins. Auto-populated on first login.
- All three columns are optional. You only need whichever login methods the person uses.
- On first OAuth login, the GitHub identity is **linked to the existing auth user**, not used to create a new one.

### Matching order (middleware)

1. `user_id` — returning users (instant match)
2. `email` — first login via email/password
3. `github_user_id` — GitHub login with immutable numeric ID (survives username renames)
4. `github_username` — first-ever GitHub login (before numeric ID is captured)

Any match auto-links the `user_id` for future logins. If `github_user_id` is missing, it is backfilled from `user.user_metadata.sub` on the next GitHub login. Once set, `github_username` is never consulted again for that user.

### Auth hook (JWT claims) — kept simple

The `rbac.custom_access_token_hook` runs on every token issue. It queries `user_roles` **by `user_id` only** to build the JWT:

```json
{
  "app_metadata": {
    "role": "superadmin",
    "entities": ["*"],
    "permissions": ["financial:view", ...]
  }
}
```

This JWT drives RLS on gold tables. The provider email never enters the authorization chain.

**Why the auth hook doesn't do multi-field matching:** We evaluated duplicating the middleware's three-step matching logic (user_id → email → github_username) inside the auth hook. PAL (Gemini 2.5 Pro) reviewed this and flagged it as fragile — the Supabase hook event JSON schema for extracting provider metadata is underdocumented, and maintaining matching logic in two places (SQL + TypeScript) doubles the bug surface. Two bugs were found before deployment: a wrong JSON path for GitHub username, and a column name mismatch.

Instead, the middleware handles all identity resolution and then calls `supabase.auth.refreshSession()` after auto-linking. This triggers the auth hook again — and by then, `user_id` is linked, so the simple lookup works.

### Token refresh on first login

On a user's very first login (before `user_id` is linked in `user_roles`):

1. Auth hook fires → no `user_id` match → JWT gets empty entities (`[]`)
2. Middleware fires → matches by email, github_user_id, or github_username → auto-links `user_id` + backfills `github_user_id`
3. Middleware calls `refreshSession()` → auth hook fires again → `user_id` now linked → correct JWT
4. Response goes to browser with the correct JWT — user sees data immediately

The empty-entities JWT from step 1 never reaches the browser in the final response.

### MITM analysis

All five attack vectors were evaluated (PAL / Gemini 2.5 Pro, 2026-03-09):

| Vector | Result | Reason |
|--------|--------|--------|
| Steal empty JWT during OAuth redirects | Safe | Empty entities = 0 rows via RLS |
| Intercept response after refresh | N/A | Standard session theft; mitigated by HTTPS + secure cookies |
| MITM the `refreshSession()` call | Safe | Server-to-server over HTTPS, never touches browser |
| Race condition (hit API before refresh) | Safe | Empty entities = 0 rows via RLS |
| Replay old empty JWT after refresh | Safe | Still valid until TTL but grants zero data access |

**Key principle:** The database (RLS) enforces access, not the middleware. Any interceptable token in this flow has `entities: []`, which returns 0 rows. There is no privilege escalation path.

## Consequences

### Positive
- A person's GitHub email can be anything — personal, work, doesn't matter
- One `user_roles` row per person regardless of how many login methods they use
- Adding a new provider (Microsoft) just means adding a column and a matching step
- No email domain restrictions needed — the allowlist is explicit per-person

### Negative
- The allowlist must be pre-seeded before someone can log in — no self-registration
- Admin must know the person's GitHub username to pre-authorize GitHub login

### Risks
- If a user has never logged in (no `github_user_id` yet) and someone else claims their old GitHub username, the wrong person could claim the row on first login. Mitigated by the admin-seeded allowlist — you only pre-seed usernames you trust.
- `github_username` column may go stale if a user renames on GitHub. This is harmless — once `github_user_id` is set, usernames are ignored for matching. No frontend notification needed.

## Alternatives Considered

1. **Email-only matching** — Rejected. Breaks when provider emails differ. Would force users to use the same email everywhere.
2. **Domain whitelist** — Rejected. Too restrictive (blocks legitimate users with non-Greenmark GitHub emails) and too permissive (allows anyone with a Greenmark email).
3. **Let OAuth create separate auth users** — Rejected. Creates orphaned accounts, splits JWT claims, desynchronizes middleware and auth hook.
4. **Duplicate matching logic in auth hook** — Rejected. Evaluated and code-reviewed (PAL / Gemini 2.5 Pro). Fragile: Supabase hook event JSON schema is underdocumented, and two bugs were found pre-deployment (wrong JSON path, column name mismatch). Middleware-only matching with `refreshSession()` is simpler and keeps logic in one place.
