# ADR-2026-18: IP Whitelist + Passkey Authentication with Office-Only Registration

- **Status**: Amended (2026-03-09)
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-12, ADR-2026-16, ADR-2026-23, ADR-2026-24

## Context

- Cerebro dashboards display sensitive financial, operational, and CRM data for three entities.
- RLS isolates entities at the row level, but authentication is the first gate — if credentials are stolen, the attacker gets that user's full entity view.
- Password-based auth is vulnerable to phishing, credential stuffing, and replay attacks.
- Supabase supports WebAuthn/passkey authentication, which is phishing-resistant by design.
- Even with passkeys, a compromised session could be used to register a NEW passkey, giving persistent access. Registration must be physically controlled.

## Decision

### IP Whitelist

- Supabase network restrictions limit API access to AIC Holdings office IP ranges only.
- Direct database connections (port 5432) restricted to the same IP whitelist + Railway service IPs (for data-daemon and dbt).
- VPN access for remote work routes through AIC office IP, maintaining the whitelist.
- Whitelist managed in Supabase dashboard → Settings → Network.

### Passkey Authentication

- All Cerebro users authenticate via WebAuthn passkey (FIDO2). No password fallback.
- **Passkey registration is restricted to AIC office IP range.** A user must be physically at the office (or on office VPN) to register or reset a passkey.
- **Passkey reset requires physical presence at AIC HQ** — cannot be done remotely, by email, or by support ticket alone. A user must appear in person or be verified by office staff.
- This prevents: remote attackers registering new passkeys on compromised accounts, social engineering of passkey resets, and credential theft via phishing (passkeys are phishing-proof by design).

### Implementation

1. Supabase Auth configuration: enable WebAuthn, disable password auth for Cerebro users.
2. Custom RPC function `secure.register_passkey()` that checks `request.headers->>'x-forwarded-for'` against allowed office IPs before permitting registration.
3. Edge function middleware: reject passkey registration requests from non-office IPs with a clear error ("Passkey registration requires office network access").
4. Audit log: all passkey registration and reset attempts logged to `audit.auth_events`.

## Consequences

- Users must visit the AIC office to set up their initial passkey. This is a feature, not a bug.
- Lost passkeys require office visit to re-register. No remote reset path exists.
- Remote workers must use VPN that routes through office IP for both access and registration.
- IP whitelist + passkey = two independent layers: network restriction + phishing-proof authentication.
- If office IP changes, whitelist must be updated in Supabase AND in the registration check function.

## Amendment: 2026-03-09

### IP Allowlist is Now Toggleable

The IP allowlist can be disabled via environment variable:

```
DISABLE_IP_ALLOWLIST=true
```

- When `true`, the IP allowlist check is skipped entirely. All IPs pass through to authentication.
- When unset or `false`, the allowlist is enforced (fail-closed).
- This toggle exists in Next.js middleware (`middleware.ts`), not at the Supabase network level.

**Current state by environment:**

| Environment | `DISABLE_IP_ALLOWLIST` | Rationale |
|-------------|----------------------|-----------|
| Local dev | `true` | Avoids blocking during development |
| Staging | `true` | Allows testing from any network |
| Production | `true` | IP filtering disabled while auth hardening (MFA, rate limiting) is validated |

**Intent**: Re-enable IP filtering in production once the security stack is fully validated. The toggle allows progressive hardening without lockout risk.

### Passkey Authentication: Not Yet Implemented

The passkey/WebAuthn section of this ADR describes the target state. Current authentication is:

- **Email/password + TOTP MFA** (ADR-2026-21) — all email users must enroll TOTP.
- **GitHub OAuth** — GitHub enforces its own 2FA.

Passkey migration is planned but deferred until the current MFA + rate limiting + account disable stack is stable.

### IP Allowlist Values

Current allowed IPs (when filtering is enabled):

```
ALLOWED_IPS=127.0.0.1,::1,::ffff:127.0.0.1,12.228.203.178
```

- `127.0.0.1`, `::1`, `::ffff:127.0.0.1` — localhost (dev/test)
- `12.228.203.178` — AIC Holdings office IP

Localhost IPs are also hardcoded as always-allowed in middleware, separate from the env var list.
