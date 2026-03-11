# ADR-2026-17: Role and Schema Naming Conventions

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-07, ADR-2026-08, ADR-2026-10

## Context

- The Cerebro data platform has 33+ schemas, multiple service roles, RLS policies, constraints, and indexes.
- Ambiguous naming causes security incidents (wrong role gets wrong grant) and operational friction (which policy is on which table?).
- Names are visible in `pg_roles`, `pg_policies`, `pg_indexes` — they should be self-documenting for 2am debugging.

## Decision

### Schemas (33 total)

| Pattern | Example | Purpose |
|---------|---------|---------|
| `{vendor}_bronze` | `hubspot_bronze` | Raw vendor data (15 schemas) |
| `{vendor}_silver` | `hubspot_silver` | Cleaned vendor data (15 schemas) |
| `gold` | `gold` | Business-ready, RLS-protected |
| `secure` | `secure` | SECURITY DEFINER functions |
| `audit` | `audit` | Drift checks, change logs |

### Roles

| Prefix | Example | Purpose |
|--------|---------|---------|
| `grp_` | `grp_gold_reader` | Group roles (no login, hold privileges) |
| `svc_` | `svc_dbt_runner`, `svc_etl_runner` | Service accounts (login, granted group membership) |
| `usr_` | `usr_daniel` | Human operators (login, granted group membership) |

### RLS Policies

Pattern: `{table}_{action}_{audience}`

| Example | Meaning |
|---------|---------|
| `deals_sel_entity_member` | SELECT on deals for entity-matched users |
| `deals_sel_consolidated` | SELECT on deals for consolidated-view users |

### Constraints and Indexes

| Type | Pattern | Example |
|------|---------|---------|
| Primary key | `pk_{table}` | `pk_deals` |
| Foreign key | `fk_{from}__{to}` | `fk_deals__contacts` |
| Unique | `uq_{table}__{cols}` | `uq_deals__entity_deal_id` |
| Index | `ix_{table}__{cols}` | `ix_deals__entity` |
| Check | `ck_{table}__{rule}` | `ck_deals__positive_value` |

### Table Names

| Layer | Pattern | Example |
|-------|---------|---------|
| Bronze | `{vendor_entity}` | `hubspot_bronze.deals` |
| Silver | `{vendor_entity}` | `hubspot_silver.deals` |
| Gold | `{business_name}` | `gold.deals` |

Double underscore (`__`) separates namespace from entity in dbt model names: `stg_hubspot__deals`.

## Consequences

- All names are grep-friendly and self-documenting.
- New team members can read `pg_policies` and understand the security model without documentation.
- Automation scripts can pattern-match on prefixes (`grp_*`, `svc_*`, `ix_*`).
- Convention is enforced by the forge tool — non-conforming names are flagged.
