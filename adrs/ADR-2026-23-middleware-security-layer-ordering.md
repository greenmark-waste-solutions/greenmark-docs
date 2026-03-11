# ADR-2026-23: Middleware Security Layer Ordering

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-18, ADR-2026-11, ADR-2026-21, ADR-2026-22

## Context

- Cerebro's Next.js middleware is the single enforcement point for multiple security layers: public path bypass, IP allowlist, CSRF protection, rate limiting, authentication, MFA, role resolution, and RBAC page gating.
- The ORDER of these checks matters critically. A wrong ordering can create security bypasses:
  - Rate limiting after auth → unauthenticated attackers can never be rate-limited (they get 401 before the rate check runs). This was a real bug found during security review.
  - CSRF after auth → unauthenticated cross-origin requests waste auth resources.
  - MFA after RBAC → a user with a valid password but no MFA could access pages if RBAC passes first.

## Decision

### Execution Order (top to bottom)

```
1. Public path bypass     — /login, /auth/callback, /api/health, /brand, /_next, /favicon
2. IP allowlist           — fail-closed, localhost always allowed, toggleable via DISABLE_IP_ALLOWLIST
3. CSRF protection        — origin/referer validation on mutating methods (POST/PUT/PATCH/DELETE)
4. Authentication         — Supabase session validation (getUser)
5. Rate limiting          — per-IP buckets, runs AFTER auth check but BEFORE auth rejection
6. Auth rejection         — no user → 401 (API) or redirect to /login (pages)
7. MFA enforcement        — email/password users only, GitHub OAuth exempt (ADR-2026-21)
8. Account active check   — is_active = false → sign out + redirect/401 (ADR-2026-22)
9. Role resolution        — 4-step cascade match + auto-linking (ADR-2026-20)
10. Permission resolution — role → pages + adminAccess
11. RBAC page gating      — /admin requires adminAccess, /dashboard pages require page permission
12. Security headers      — CSP, X-Frame-Options, HSTS, etc.
```

### Why This Order

**Public paths first**: No processing waste on static assets, health checks, or login page.

**IP allowlist before everything else**: Blocks untrusted networks before any expensive operations (DB calls, rate limit lookups). Fail-closed: if `ALLOWED_IPS` is unset and request isn't localhost, return 403.

**CSRF before auth**: Reject cross-origin mutating requests immediately. No point authenticating a CSRF attack.

**Rate limiting between auth check and auth rejection**: This is the critical ordering decision.
- We call `getUser()` first to know whether the requester is authenticated (determines rate limit tier: 10/min unauth vs 60/min auth).
- Rate check runs BEFORE the `if (!user) return 401` rejection.
- If rate limiting ran AFTER auth rejection, unauthenticated attackers would always get 401 before the rate limiter could count their request. They'd have unlimited attempts.

**MFA before role resolution**: A user who passes auth but fails MFA should never reach role resolution or see any data.

**Account active check during role resolution**: Checked when the role row is fetched. Disabled = signed out immediately.

**Security headers last**: Applied to the response object that passes through all checks.

### Responses by Layer

| Layer | API Routes | Page Routes |
|-------|-----------|-------------|
| IP blocked | `403 { error: "Forbidden" }` | `403 { error: "Forbidden" }` |
| CSRF blocked | `403 { error: "Forbidden" }` | N/A (GET only) |
| Rate limited | `429 { error: "Too many requests" }` + `Retry-After: 60` | N/A (pages exempt) |
| Unauthenticated | `401 { error: "Unauthorized" }` | `302 → /login` |
| MFA required | `403 { error: "MFA verification required" }` | `302 → /verify-mfa` |
| Account disabled | `401 { error: "Account disabled" }` | `302 → /login?error=account_disabled` |
| No role | `302 → /login?error=not_authorized` | `302 → /login?error=not_authorized` |
| RBAC denied | N/A | `302 → /dashboard` |

## Consequences

### Positive
- Each layer has a clear, documented position in the chain.
- Rate limiting actually works against unauthenticated attackers (the pre-fix bug is impossible with this ordering).
- Fail-closed at every layer: IP check fails → blocked. MFA check errors → blocked. No role → blocked.
- Security alerts fire at IP block, CSRF block, rate limit, and login rejection layers.

### Negative
- Every authenticated request makes at least 2 Supabase calls (getUser + role resolution). For an internal app with <50 users, this is acceptable.
- The ordering is implicit in a single middleware function. A future refactor could extract each layer into named functions for clarity.

### Risks
- Reordering layers during a refactor could reintroduce the rate-limit bypass bug. The ordering is documented here and tested in `e2e/security-middleware.spec.ts`.
- Adding a new security layer requires updating this ADR to define its position.
