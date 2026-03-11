# ADR-2026-21: MFA Enforcement — TOTP Required for Email/Password Users

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-18, ADR-2026-20

## Context

- Cerebro supports two authentication methods: email/password and GitHub OAuth.
- Email/password authentication is vulnerable to credential theft even with IP allowlisting — a stolen password from any allowed IP (office, VPN) grants full access.
- GitHub OAuth users are exempt because GitHub enforces its own 2FA at the provider level. Requiring a second TOTP on top of GitHub's 2FA would be redundant and friction-heavy.
- Supabase Auth supports TOTP-based MFA with AAL (Authenticator Assurance Level) tracking: AAL1 = password only, AAL2 = password + TOTP verified.

## Decision

### Enforcement Model

- **All email/password users MUST enroll and verify TOTP before accessing any protected route.**
- **GitHub OAuth users are exempt** — their `app_metadata.provider` is `"github"`, and GitHub already enforces 2FA.
- Enforcement happens in Next.js middleware, after authentication but before role resolution.

### Middleware Flow

```
authenticate → is email user? → check AAL level → enforce MFA → resolve role → RBAC
```

1. If `provider` is `"github"` or any OAuth provider → skip MFA check entirely.
2. If AAL check errors or returns null → **fail closed** (block access, redirect to verify-mfa).
3. If `nextLevel === "aal2"` and `currentLevel === "aal1"` → user has TOTP enrolled but hasn't verified this session → redirect to `/verify-mfa`.
4. If `currentLevel === "aal1"` and `nextLevel === "aal1"` and no TOTP factors enrolled → redirect to `/setup-mfa`.
5. If `currentLevel === "aal2"` → MFA verified, proceed.

### Exempt Paths

MFA pages themselves are exempt from the MFA gate to prevent redirect loops:
- `/setup-mfa` — TOTP enrollment (QR code + verification)
- `/verify-mfa` — TOTP code entry for existing enrollments
- `/update-password` — password change after temp password reset

### API Routes

API requests from email/password users without MFA return `403` with:
- `"MFA verification required"` (enrolled but not verified)
- `"MFA enrollment required"` (no TOTP factor enrolled)

### E2E Testing

- Playwright auth setup (`e2e/auth.setup.ts`) handles MFA auto-enrollment using the `otpauth` library.
- TOTP secrets are saved to `e2e/.auth/.totp-secrets.json` for reuse across test runs.
- Tests use serial mode with shared browser context to avoid TOTP replay rejections within 30-second windows.
- A dedicated test superadmin (`dshanklin+e2eadmin@greenmarkwaste.com`) is provisioned via `e2e/create-test-superadmin.ts`.

## Consequences

### Positive
- Email/password accounts are protected against credential theft — a stolen password alone is insufficient.
- Fail-closed design means MFA check errors block access rather than granting it.
- GitHub users experience zero additional friction.

### Negative
- Email/password users must have an authenticator app (Google Authenticator, 1Password, etc.).
- Lost TOTP devices require admin MFA reset via `/api/admin/mfa-reset` — no self-service recovery.
- First login for email/password users is longer (must complete TOTP enrollment).

### Risks
- If Supabase's AAL API changes behavior, the fail-closed design protects against regressions — worst case is users are blocked, not exposed.
- TOTP secrets in E2E test files must not be committed to public repos (`.gitignore` covers `.auth/`).
