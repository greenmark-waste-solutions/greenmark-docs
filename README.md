# Greenmark Docs

Architecture Decision Records and Standard Operating Procedures for Greenmark Waste Solutions.

## ADRs

| # | Title | Status |
|---|-------|--------|
| 01 | Classify Claude Code as Tier-1 Engineering Infrastructure | Accepted |
| 02 | Deterministic Checkpoint Architecture — Three-Tier Code Validation | Accepted |
| 03 | Supabase Migration Strategy — psycopg2 via Connection Pooler | Accepted |
| 04 | Gold Layer Uses Regular Tables, Not Materialized Views | Accepted |
| 05 | Gold Refresh Uses MERGE, Not TRUNCATE+INSERT | Accepted |
| 06 | dbt Manages Bronze→Silver Only, Never Gold | Accepted |
| 07 | Per-Vendor Bronze and Silver Schemas | Accepted |
| 08 | Single Gold Schema with Business-Named Tables | Accepted |
| 09 | service_role Revoked from Gold Schema | Accepted |
| 10 | SECURITY DEFINER Refresh Functions with Hardened search_path | Accepted |
| 11 | Default Deny RLS Policy on All Gold Tables | Accepted |
| 12 | Entity Isolation via JWT app_metadata | Accepted |
| 13 | Forge Tool Separation — dbt for Transformation, Forge for Security | Accepted |
| 14 | Gold Security Drift Audit | Accepted |
| 15 | Soft Deletes Propagated Through All Layers | Accepted |
| 16 | PostgREST Exposes Only the Gold Schema | Accepted |
| 17 | Role and Schema Naming Conventions | Accepted |
| 18 | IP Whitelist + Passkey Authentication with Office-Only Registration | Accepted |
| 19 | Supabase Vault for Credential Management | Accepted |
| 20 | Identity Linking, Not Email Matching | Accepted |
| 21 | MFA Enforcement — TOTP Required for Email/Password Users | Accepted |
| 22 | Account Disable (Not Delete) with Single-Tenant-Per-User Constraint | Accepted |
| 23 | Middleware Security Layer Ordering | Accepted |
| 24 | In-Memory Rate Limiting with Per-IP Buckets | Accepted |
| 25 | Adopt Microsoft Security Stack for Identity, Auth, and Secrets | Proposed |
| 26 | No Separate Post-Ingestion Worker — data-daemon Handles Extraction and Transformation | Accepted |
| 27 | HubSpot Entity Resolution — Single Account, No Entity Marker Yet | Accepted |
| 28 | Reject Vault Admin UI in Cerebro | Rejected |
| 29 | All ADRs Require a BLUF | Superseded by SOP-001 |
| 30 | All ADRs Require a Branded PDF | Superseded by SOP-001 |
| 31 | Establish SOP Document Type for Operating Procedures | Accepted |
| 32 | Architecture Approach (Competitive Intelligence) | Accepted |
| 33 | Postgres SKIP LOCKED for Job Queue | Accepted |
| 34 | claude -p Only — No Direct Anthropic API | Accepted |
| 35 | Trust Calibration System — 4-Level Autonomy | Accepted |
| 36 | RRF Hybrid Retrieval for Knowledge Search | Accepted |

## SOPs

| # | Title |
|---|-------|
| 001 | [Creating ADRs and SOPs](sops/SOP-001-creating-adrs-and-sops.md) |

## Quick Start

See [SOP-001](sops/SOP-001-creating-adrs-and-sops.md) for how to create new ADRs and SOPs with the required BLUF and branded PDF.
