# ADR-2026-19: Supabase Vault for Credential Management

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-10, Migration 013, Runbook vault-secret-management.md

## Context

- data-daemon connects to 15 vendor APIs, each requiring API keys/tokens.
- These credentials were previously stored as Railway environment variables, which are visible to anyone with Railway project access and not auditable.
- Greenmark needs a credential store that is: encrypted at rest, access-controlled, auditable, and doesn't require a new external service.
- Supabase Vault is a built-in Postgres extension that encrypts secrets using pgsodium (AES-256-GCM). The encryption key is managed by Supabase and never stored in the database.

## Decision

- **Supabase Vault** (`vault.secrets` table) stores all vendor API credentials, webhook URLs, and sensitive configuration.
- **`secure.get_secret(name)`** is the only approved way to read secrets in application code — it logs every access to `audit.vault_access_log`.
- **Only `svc_etl_runner`** can read decrypted secrets. No other role (including `service_role`, `authenticated`, `anon`) has access.
- **Secret values are never in git** — migrations register placeholder names, real values set via Supabase SQL Editor from AIC office IP.
- **Rotation** follows the runbook: rotate at vendor first, then update Vault, then verify data-daemon reconnects.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| Railway env vars (current) | Simple | Not encrypted at rest, no audit trail, visible to all project members |
| AWS Secrets Manager / HashiCorp Vault | Industry standard, full KMS | New service to deploy, maintain, and pay for. Overkill for 15 keys. |
| Supabase Vault (selected) | Already in the stack, encrypted, auditable, zero new infra | Key managed by Supabase (acceptable trust level) |
| Encrypted column in custom table | Full control | pgsodium being deprecated on Supabase, high misconfiguration risk |

## Consequences

- data-daemon connectors must be updated to call `secure.get_secret()` instead of reading `os.environ`.
- Secret management is auditable — `audit.vault_access_log` tracks who read what and when.
- Secrets are encrypted in database dumps — a dump doesn't expose plaintext credentials.
- Adding a new vendor requires: register placeholder in migration, set real value via runbook, update data-daemon YAML.
