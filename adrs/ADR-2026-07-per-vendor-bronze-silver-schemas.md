# ADR-2026-07: Per-Vendor Bronze and Silver Schemas

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-08, data-daemon

## Context

- Greenmark integrates 15 data vendors across completely different domains: HubSpot (CRM), Sage Intacct (accounting), Fleetio (fleet management), Navusoft (waste operations), and others.
- These vendors are not competing sources of the same data — they are different business systems with different schemas, entities, and semantics.
- A shared `bronze` or `silver` schema would mix unrelated vendor tables, making blast radius containment impossible (a bad Sage transform could corrupt Navusoft data in the same schema).
- Scale: each vendor has 5–50 tables, totaling 75–750 tables across all vendors.

## Decision

- **Bronze**: One schema per vendor — `hubspot_bronze`, `sage_bronze`, `fleetio_bronze`, etc. (15 schemas)
- **Silver**: One schema per vendor — `hubspot_silver`, `sage_silver`, `fleetio_silver`, etc. (15 schemas)
- Per-vendor silver is correct here because the vendors represent different domains, not competing sources of the same data. There is no "unified invoice" concept that spans HubSpot and Sage — they have fundamentally different data models.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A. Shared bronze + shared silver (rejected) | Fewer schemas | No blast radius containment, table name collisions, security boundary too broad |
| B. Per-vendor bronze, shared silver (rejected) | Silver as "one canonical model" | Only makes sense when vendors overlap; ours don't — they're different domains |
| C. Per-vendor bronze + per-vendor silver (selected) | Blast radius containment, clear ownership, security boundary per vendor | 30 schemas — manageable with automation |

## Consequences

- 30 schemas for bronze+silver. PostgreSQL handles this without issue; dbt manages multi-schema via `generate_schema_name` macro.
- Grants are per-schema: `svc_dbt_runner` gets USAGE + SELECT on bronze, USAGE + CREATE + INSERT on silver.
- Adding a new vendor = creating two new schemas + YAML service definition + dbt models. Automatable.
- Silver tables keep vendor-specific names and structures. Cross-vendor unification happens only at gold.
