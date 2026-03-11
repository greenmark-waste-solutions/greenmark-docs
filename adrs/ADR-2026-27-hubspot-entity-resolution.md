# ADR-2026-27: HubSpot Entity Resolution — Single Account, No Entity Marker Yet

- **Status**: Accepted
- **Date**: 2026-03-04
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-02 (medallion architecture), `services/hubspot.yaml`, `migrations/008_hubspot_bronze.sql`

## BLUF (Bottom Line Up Front)

Default all HubSpot records to the `ntx` entity. There is no reliable entity-distinguishing field in HubSpot today — the "Brands" field is 84% blank with no enum options, and no custom entity property exists. Attempting to infer entity from geography or owner would produce incorrect results. This is a config change away from being correct once Michael configures entity tagging.

## Context

Greenmark operates 3 business entities — NTX (North Texas), Hometown (Indiana), and Memphis (nascent). The data warehouse tags every record with an `entity` column so dashboards can filter by business unit.

HubSpot CRM is a single shared account (portal 244562652, greenmarkwaste.com). All entities share the same contacts, companies, deals, owners, and pipeline. The question: how do we assign the correct entity to each HubSpot record during extraction?

## Investigation (2026-03-04)

Queried production HubSpot via API to check for entity-distinguishing fields:

| Field | Exists? | Data |
|-------|---------|------|
| `hs_all_assigned_business_unit_ids` ("Brands") | Yes, on all object types | 84% blank, 16% have value `0`. No enum options configured. Not usable. |
| Custom `entity` or `business_unit` property | **No** | Does not exist on companies, contacts, or deals |
| Owner teams | **Partial** | Michael Nguyen assigned to team "NTX". 14 other owners have no team. |
| Deal pipelines | 1 pipeline only | "Sales Pipeline" — no per-entity pipeline split |
| State/geography | Unreliable | Inconsistent formats (TX, Texas, Tx, tx). All visible records are DFW area. No Indiana records in first 100. |

**Custom properties found on companies:** `account_class` (service tier), `line_of_business` (Commercial/Roll-off/Residential/Portable Toilets), `accountownerb` (secondary owner). **None are entity markers.**

**Custom properties found on deals:** `line_of_business`, `referral_source`, `site_class`, `haulsweeklyservices`. **None are entity markers.**

**Custom properties found on contacts:** `secondary_contact_owner`. **Not an entity marker.**

## Decision

**Phase 1: Default all HubSpot records to `ntx` entity.**

There is no reliable entity-distinguishing field in HubSpot today. Attempting to infer entity from geography, owner, or pipeline would produce incorrect results. The correct approach is:

1. Default to `ntx` in the connector config (`default_entity: ntx`)
2. Raise with Michael/Alex: should Greenmark configure the existing "Brands" field (`hs_all_assigned_business_unit_ids`) or create a custom `entity` property?
3. Once configured, update the YAML to use `entity_column` pointing to that HubSpot property — no connector code changes needed

## Multi-Tenant Considerations

### Current State: One Account Per Vendor
HubSpot has one account for all entities. This is the norm for Greenmark — they haven't split their vendors by entity. However, other vendors may differ:

| Vendor | Account Structure | Entity Strategy |
|--------|------------------|-----------------|
| **HubSpot** | 1 shared account | Field-based tagging (future) |
| **Sage Intacct** | Unknown — may have separate entities/locations within one tenant | Likely `LOCATIONID` or entity dimension |
| **Navusoft** | Unknown — Michael's team manages | May have separate databases per entity |
| **Fleetio** | Unknown | May be shared or per-entity |

### Connector Architecture Supports Both Patterns
- **Shared account (HubSpot today):** 1 YAML file, `default_entity` or `entity_column` maps a source field to the entity
- **Separate accounts per entity:** Duplicate the YAML file with different tokens (`hubspot-ntx.yaml`, `hubspot-hometown.yaml`). No connector code changes.
- **Hybrid:** Some vendors shared, some split — handled at the YAML layer, not the code layer

### Why Not Build Multi-Tenant Now
1. Only HubSpot is connected. We don't know the account structure for Sage, Navusoft, etc.
2. The YAML-per-entity pattern (Option A) requires zero code changes and handles 100% of known cases
3. Building a config-level entity loop adds complexity with no immediate user

### When to Revisit
- When connecting Sage Intacct (if it has separate tenants per entity)
- When Hometown's HubSpot data needs to be distinguished from NTX
- If Michael configures entity tagging in HubSpot (Brands field or custom property)

## Action Items

1. **Daniel → Michael**: Ask whether to use the existing "Brands" (`hs_all_assigned_business_unit_ids`) field or create a new custom property for entity tagging
2. **After decision**: Update `services/hubspot.yaml` to add the entity property to `properties` lists and set `entity_column`
3. **Before connecting Sage**: Investigate whether Sage uses separate entities/locations within one tenant

## Consequences

- **Positive**: Clean, simple extraction pipeline ships now. Entity resolution is a config change, not a code change.
- **Negative**: All HubSpot records tagged `ntx` until entity tagging is configured. If Hometown has records in HubSpot, they'll be mis-tagged.
- **Risk**: Low. Hometown's CRM activity in HubSpot appears minimal (no Indiana companies visible in first 100 records). The mis-tagging window is small.
