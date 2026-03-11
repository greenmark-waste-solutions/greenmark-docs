# ADR-2026-13: Forge Tool Separation — dbt for Transformation, Forge for Security

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-06, ADR-2026-05, ADR-2026-10

## Context

- dbt is the industry-standard tool for data transformation. It excels at bronze→silver: deduplication, type casting, cleaning, conforming.
- dbt is **not designed** for security hardening. It doesn't manage RLS policies, it doesn't do MERGE-based refresh, and its DDL cycle actively destroys security metadata.
- The gold layer requires: RLS policy management, FORCE RLS, SECURITY DEFINER functions, advisory locks, drift auditing, and MERGE-based refresh. None of these are dbt's job.
- Two MCP forge tools handle different aspects:
  - **elt-forge**: Diagnostic/audit tool — scans any ELT pipeline for issues, validates schema health.
  - **next-analytics-forge**: Security hardening + dashboard wiring — manages silver→gold MERGE, RLS policies, grants, and connects gold tables to Cerebro dashboard.

## Decision

- **dbt**: Owns bronze→silver transformations. Runs in `*_bronze` and `*_silver` schemas. Role: `svc_dbt_runner`.
- **Forge**: Owns silver→gold security hardening + data loading. Manages gold DDL, RLS, grants, MERGE refresh. Role: `svc_etl_runner`.
- **Boundary**: dbt produces clean silver tables. Forge reads silver, validates, and loads into gold with full security enforcement.

## Consequences

- Two tools to learn and maintain, but each has a clear, non-overlapping responsibility.
- Forge tool must be as reliable as dbt for gold refresh — it's the only path to gold.
- CI/CD pipeline runs dbt first (bronze→silver), then forge (silver→gold), in sequence.
- elt-forge provides the audit layer that verifies both tools did their job correctly.
