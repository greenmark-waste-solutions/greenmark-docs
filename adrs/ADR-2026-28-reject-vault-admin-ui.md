# ADR-2026-28: Reject Vault Admin UI in Cerebro

- **Status**: Rejected
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: `projects/auth-upgrade/`, `cerebro/security/`, Knox vault infrastructure

## BLUF (Bottom Line Up Front)

We will not build a secrets management UI in Cerebro. Any web-tier access to vault secrets creates a permanent privilege escalation path — SECURITY DEFINER functions would let a compromised admin session exfiltrate every vendor API key and hijack the data pipeline. The inconvenience of SQL Editor access is the security control: it makes the attack economically unviable by ensuring the capability to touch secrets never exists in the web application.

## Context

As Cerebro's RBAC system matured (ADR-2026-02, task-16), the question arose: should we build a secrets management page inside Cerebro's admin panel? The proposed feature would allow owner/superadmin users to view, rotate, and manage API keys and connection strings through a web UI — replacing the current workflow of using Supabase SQL Editor and the `vault-helper.html` utility.

The feature was scoped as:
- **Owner/superadmin only** — gated behind the highest RBAC role
- **Full CRUD** — create, read, update, delete vault secrets
- **Audit logged** — every access and mutation recorded
- **Encrypted at rest** — leveraging Supabase Vault (`pgsodium` + `vault` extensions)

## Decision

**Reject the Vault Admin UI. Do not build it.**

Keep the current vault write path: Supabase SQL Editor (for Daniel) and `vault-helper.html` (for guided operations). Cerebro will never have a web interface for managing secrets.

## Rationale

### The Privilege Escalation Problem

The core issue is architectural, not implementational. Building this feature would require:

1. **SECURITY DEFINER functions** in Postgres — Cerebro's PostgREST connection uses `authenticated` role, but vault operations require `svc_etl_runner` (the service role that data-daemon uses). A SECURITY DEFINER function would bridge this gap, executing with elevated privileges regardless of the caller's role.

2. **Permanent escalation path** — Once a SECURITY DEFINER bridge exists from `service_role` → `svc_etl_runner`, it becomes a permanent privilege escalation vector. Anyone who compromises Cerebro (XSS, session hijack, admin account takeover) could:
   - Rotate API keys for Sage Intacct, HubSpot, and other production systems
   - Redirect data-daemon to malicious endpoints by changing connection strings
   - Exfiltrate credentials for all integrated vendor systems
   - Disrupt the entire data pipeline by invalidating existing keys

3. **RBAC is not sufficient protection** — RBAC controls who can access the page, but it doesn't control what happens after a breach. The attack surface isn't "unauthorized user visits the page" — it's "attacker gains access to any admin session and now has full vault write capability."

### Security Analysis Summary

| Risk | Severity | Description |
|------|----------|-------------|
| **Privilege escalation** | CRITICAL | SECURITY DEFINER creates permanent bridge from web tier to vault tier |
| **Credential exfiltration** | CRITICAL | Compromised admin session = all vendor API keys exposed |
| **Pipeline hijacking** | HIGH | Attacker could redirect data-daemon to malicious endpoints |
| **Blast radius** | HIGH | Single compromise affects all 15 vendor integrations |
| **Audit bypass** | MEDIUM | Attacker with admin access could clear or falsify audit logs |

### The Fundamental Principle

**The web tier should never have write access to production secrets.** This is defense in depth — even if every other security layer fails (RBAC, session management, input validation, CSP), the attacker still cannot touch vault secrets because the capability simply does not exist in the application.

### Friction Is the Security Control

The inconvenience of requiring SQL Editor access for secret rotation is deliberate. An attacker who compromises a web session faces a **capability gap**, not just an authorization check — the application literally cannot perform vault writes. There is no API to call, no function to invoke, no code path to exploit. The capability was never built.

This friction makes the attack economically unviable. A fully compromised Cerebro admin session yields zero access to production credentials. The attacker would need to separately compromise the Supabase SQL Editor (different authentication, different network path, different session) to reach secrets. Each additional system they must breach multiplies the cost and reduces the likelihood of success.

**The time it takes to rotate a key through SQL Editor is the security budget.** That 60 seconds of human friction buys permanent immunity from web-tier credential theft.

## Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Reject (chosen)** | No vault UI in Cerebro. SQL Editor + vault-helper.html only. | Zero attack surface for credential theft via web app. No SECURITY DEFINER functions. Defense in depth preserved. | Less convenient for non-technical admins. Requires SQL Editor access for secret rotation. |
| B. Full Vault Admin UI | Owner-only page with CRUD, audit logging, encrypted display | Convenient. Self-service rotation. Audit trail in app. | Creates permanent privilege escalation path. SECURITY DEFINER bridge from web tier to vault tier. Single breach = all credentials compromised. |
| C. Read-only Vault UI | Show secret names and metadata but no values or mutations | Moderate convenience. No write risk. | Still requires SECURITY DEFINER for reads. Leaks secret inventory to web tier. Half-measure with unclear value. |
| D. Rotation-only UI | Only allow key rotation (generate new, no read/delete) | Limits read exposure. | Still requires SECURITY DEFINER. Still a privilege escalation path. Rotation without read is operationally fragile. |

## Consequences

- **Positive**: Cerebro has zero capability to read or write production secrets. Defense in depth is preserved — web application compromise cannot escalate to credential theft. No SECURITY DEFINER functions in the codebase. Simpler security audit surface.
- **Negative**: Secret management requires Supabase SQL Editor access (currently Daniel only). Non-technical admins cannot self-service rotate keys. If Daniel is unavailable, secret rotation is blocked.
- **Mitigation**: The `vault-helper.html` utility provides a guided interface for common operations. A future CLI tool or separate, non-web-connected utility could provide safer self-service without the web-tier risk.

## When to Revisit

Revisit this decision **only if all** of these conditions are met:

1. **Greenmark hires a dedicated DevOps/security engineer** who can own the vault infrastructure
2. **A non-web-tier solution exists** — e.g., a CLI tool, desktop app, or VPN-only internal service that doesn't share Cerebro's attack surface
3. **Formal security review** by an external party validates the proposed architecture

**A web UI for secrets management in a customer-facing dashboard is not the right pattern, regardless of how many RBAC layers are added on top.**
