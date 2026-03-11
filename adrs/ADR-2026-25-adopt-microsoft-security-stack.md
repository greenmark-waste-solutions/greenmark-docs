# ADR-2026-25: Adopt Microsoft Security Stack for Identity, Auth, and Secrets

- **Status**: Proposed
- **Date**: 2026-02-28
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Approver**: Michael D. Nguyen / President
- **Related**: `reference/security-standards.md`, `projects/data-integration/hubspot-security-audit.md`

## BLUF (Bottom Line Up Front)

Adopt Microsoft Entra ID, Azure Key Vault, and Microsoft Authenticator as Greenmark's unified identity, secrets, and MFA stack. It's already included in the M365 subscription, replaces three separate vendors (LastPass + Duo + Railway env vars), and gives one-click offboarding plus a full audit trail. Retire the shared `it@greenmarkwaste.com` account for interactive logins.

## Context

- Greenmark operates 15+ vendor systems (Sage, HubSpot, Navusoft, Fleetio, etc.) with no centralized identity or credential management.
- The shared `it@greenmarkwaste.com` account is used to log into HubSpot, Railway, Supabase, GitHub, and LastPass. If that password leaks from any one service, an attacker has the keys to everything.
- API keys for Cerebro integrations (HubSpot PAK, future Sage key) need a Greenmark-owned secrets store. The current interim is Railway environment variables.
- MFA is inconsistent — Duo on some accounts, nothing on others. No conditional access policies.
- Greenmark is already on Microsoft 365. Entra ID, Key Vault, and Authenticator are available within the existing subscription.

## Decision

- **Adopt Microsoft Entra ID as the single identity provider for all Greenmark systems.**
- **Adopt Azure Key Vault as the secrets store for all service credentials (API keys, tokens, database passwords).**
- **Adopt Microsoft Authenticator as the sole MFA method, replacing Duo.**
- **Retire the shared `it@greenmarkwaste.com` account for interactive logins.** Convert to a distribution list. Every person gets their own Entra ID identity.

Out of scope: SSO for vendor systems that don't support SAML/OIDC (we document those as exceptions, not blockers).

## Rationale

- **Already paying for it.** M365 Business Premium includes Entra ID P1 and Azure services. No new vendor contracts.
- **One ecosystem.** Identity + auth + secrets + MFA in one Microsoft tenant instead of three vendors (LastPass + Duo + Knox).
- **Offboarding in one click.** Disable an Entra ID account → locked out of every SSO-connected system within minutes.
- **Audit trail.** Entra ID logs every login. Key Vault logs every secret access. Compliance-ready without additional tooling.
- **Michael's team asked for Microsoft auth.** This aligns with what leadership already wants.

## Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Microsoft stack** | Entra ID + Key Vault + Authenticator | Already licensed, one ecosystem, what leadership wants | Requires Azure tenant setup, SSO rollout takes weeks |
| B. Keep current | LastPass + Duo + Railway env vars | No migration work | Shared account risk, three vendors, no central identity, no audit trail |
| C. Build custom (GreenKnox) | Self-hosted secrets store | Full control | Greenmark is a waste company, not a security company. Maintenance burden. |
| D. Third-party (HashiCorp Vault) | Industry-standard secrets manager | Powerful, vendor-neutral | New vendor, new cost, new expertise required. Overkill at this scale. |

## Consequences

- **Positive**: Central identity directory. One-click offboarding. Audit trail for compliance. API keys encrypted in Key Vault with RBAC. MFA on every account. Aligns with leadership preference.
- **Negative**: Migration effort — creating individual accounts, configuring SSO for each vendor, moving secrets from Railway env vars to Key Vault. Requires Michael to approve and provision the Azure tenant.
- **Neutral**: Vendor systems that don't support SAML (3rd Eye, WAM) remain on direct credentials. We accept this as a known gap and document it.

## Cost

| Component | Monthly | Notes |
|-----------|---------|-------|
| Entra ID P1 | $6/user/mo | May already be included in M365 Business Premium |
| Azure Key Vault | ~$1/mo | Usage-based, negligible |
| Microsoft Authenticator | Free | |
| **Total** | **~$25-50/mo** | For 4-8 users. Replaces LastPass ($4/user) + Duo ($3/user) |

## Implementation & Ownership

- **Michael**: Confirm M365 plan tier, approve Azure tenant creation, designate Global Admin
- **Daniel**: Provision Key Vault, migrate secrets, configure SSO for Cerebro, document runbooks
- **Timeline**: 4 weeks from approval to full migration (see `reference/security-standards.md` for week-by-week breakdown)

## Review & Sunset

- **Review trigger**: 90 days after implementation (Phase 3 checkpoint)
- **Conditions to revisit**: If Greenmark outgrows Entra ID P1 (unlikely at current scale), if Microsoft changes M365 licensing to exclude Key Vault, or if a vendor system requires a non-Microsoft identity provider
