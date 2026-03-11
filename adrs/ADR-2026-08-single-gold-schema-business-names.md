# ADR-2026-08: Single Gold Schema with Business-Named Tables

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-07, ADR-2026-04

## Context

- Gold is the only schema exposed to the Cerebro dashboard via PostgREST.
- Options for gold schema organization: per-domain schemas (`sales_gold`, `fleet_gold`), per-vendor schemas (`hubspot_gold`), or a single `gold` schema.
- RLS policies and grants are per-table, not per-schema — multiple gold schemas would add schema management overhead with no security benefit.
- PostgREST is cleanest when exposing a single schema (`PGRST_DB_SCHEMAS=gold`).
- dbt Labs and Databricks best practices recommend gold table names use business terminology, not source system names. "Assume your end-user will have no other context than the model name."

## Decision

- **Single `gold` schema** for all business-ready tables.
- **Business names only** — `gold.deals`, `gold.contacts`, `gold.vehicles`, `gold.invoices`. No vendor prefixes (`hubspot_deals`), no Kimball prefixes (`fct_deals`) at the database level.
- Kimball `fct_`/`dim_` prefixes are used in **dbt model filenames** only, stripped via dbt's `alias` config.
- Vendor lineage is traced via dbt's lineage graph (`dbt docs generate`), not via table names.
- Tables that serve only one vendor still use business names (`gold.routes` not `gold.navusoft_routes`) — the source is an implementation detail.
- Two vendors contributing to the same business concept (e.g., HubSpot contacts + Sage customers) are kept as **separate gold tables** (`gold.contacts`, `gold.customers`) until identity resolution logic is built in silver. Premature merging is worse than separate tables.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A. Per-domain gold schemas (rejected) | Logical grouping | Schema overhead, PostgREST complexity, no security benefit |
| B. Vendor-prefixed tables (rejected) | Clear lineage in name | Exposes implementation detail to dashboard; not industry practice |
| C. Kimball prefixes in DB (rejected) | Familiar to data engineers | Unnecessary for single-dashboard; clutters PostgREST API |
| D. Single schema, business names (selected) | Clean API, industry standard, business-friendly | Requires dbt lineage for debugging |

## Consequences

- PostgREST API is clean: `/rest/v1/deals`, `/rest/v1/vehicles`.
- Debugging requires dbt lineage graph or audit schema — the table name alone doesn't tell you the source. This is acceptable.
- Adding a new gold table is simple: create table, add RLS, add to forge refresh. No schema creation needed.
