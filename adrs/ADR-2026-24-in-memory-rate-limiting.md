# ADR-2026-24: In-Memory Rate Limiting with Per-IP Buckets

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-23, ADR-2026-18

## Context

- Cerebro API routes need protection against brute-force attacks, credential stuffing, and abuse.
- The app runs on Railway (single instance). No Redis, no external rate-limit service.
- Rate limiting must differentiate between authenticated and unauthenticated requests — unauthenticated requests get a tighter limit because they're more likely to be attacks.
- Localhost traffic (dev/test) should be exempt to prevent E2E test suites from exhausting rate limit buckets.

## Decision

### Implementation: In-Memory Map

```typescript
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
```

- **Key**: Client IP address (from `x-forwarded-for` header, first entry).
- **Window**: 60 seconds (sliding reset).
- **Limits**: 10 requests/minute (unauthenticated), 60 requests/minute (authenticated).
- **Cleanup**: Stale entries purged every 5 minutes via `setInterval`.

### Why In-Memory (Not Redis/DB)

| Approach | Latency | Persistence | Complexity | Multi-Instance |
|----------|---------|-------------|------------|----------------|
| In-memory Map | ~0ms | None (resets on deploy) | Minimal | No |
| Redis | 1-5ms | Yes | Moderate | Yes |
| PostgreSQL | 5-20ms | Yes | Moderate | Yes |

For a single-instance Railway deployment with <50 users:
- In-memory is the simplest correct solution.
- Rate limit state resetting on deploy is acceptable — deploys are infrequent and the 60-second window means state is short-lived anyway.
- If Cerebro scales to multiple instances, migrate to Redis. This is a future concern, not a current one.

### Localhost Exemption

```typescript
if (pathname.startsWith("/api/") && !isLocalhost) {
  // rate limit check
}
```

Localhost IPs (`127.0.0.1`, `::1`, `::ffff:127.0.0.1`, `unknown`) are exempt from rate limiting. Rationale:
- Dev server generates many requests during development.
- Playwright E2E tests make 30+ requests per run — a 60/min auth limit would cause flaky failures.
- IP allowlisting already handles localhost security.

### Rate Limit Tiers

| Tier | Limit | Window | Rationale |
|------|-------|--------|-----------|
| Unauthenticated | 10/min | 60s | Tight limit — legitimate users authenticate quickly. Attackers get 10 attempts before lockout. |
| Authenticated | 60/min | 60s | Generous for normal usage. A user navigating dashboards makes ~5-15 requests/minute. |

The tier is determined by whether `getUser()` returns a valid user — the rate check runs after auth validation but before auth rejection (see ADR-2026-23).

### Response

```
HTTP 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
Retry-After: 60

{ "error": "Too many requests" }
```

### Security Alerting

Rate limit triggers fire a security alert via `alertSecurity()`:
```typescript
alertSecurity({
  event: "rate_limited",
  ip: clientIp,
  metadata: { pathname, limit: rateCheck.limit },
});
```

In production, this posts to a Slack webhook (`SECURITY_WEBHOOK_URL`). In dev/test, it's a no-op.

### Scope

Rate limiting applies to `/api/` routes only. Page routes are not rate-limited because:
- Pages are server-rendered and already gated by auth + RBAC.
- Browser page navigation is inherently slower than API abuse.
- Rate limiting pages would interfere with normal navigation.

## Consequences

### Positive
- Zero external dependencies. No Redis to provision, no additional latency.
- Differentiates attack traffic (unauthenticated) from normal usage (authenticated).
- `Retry-After` header enables well-behaved clients to back off gracefully.
- Localhost exemption prevents E2E test flakiness.

### Negative
- State is lost on deploy/restart. An attacker could wait for a deploy to reset their counter. Acceptable for an internal app.
- Not shared across instances. If Cerebro scales horizontally, each instance has its own counter — an attacker could distribute requests across instances. Migrate to Redis when this becomes relevant.
- Memory grows with unique IPs. The 5-minute cleanup prevents unbounded growth, but a large-scale distributed attack could temporarily consume memory. Behind IP allowlisting, this is unlikely.

### Migration Path to Redis

When needed (multi-instance deployment):
1. Replace `Map` with Redis `INCR` + `EXPIRE` pattern.
2. Same key structure (`ip:{address}`), same window/limits.
3. No middleware logic changes — only the storage backend changes.
