# ADR-2026-37: pg_depend + Context Reasoning for Migration Validation

- **Status**: Accepted
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: [ADR-2026-38](ADR-2026-38-unified-migration-authority.md) (Unified Migration Authority), [elt-forge Feature Spec](../../repos-eidos-agi/elt-forge/specs/DAG-DEPLOY-PLAN.md)

## BLUF (Bottom Line Up Front)

When validating migrations, use PostgreSQL's `pg_depend` for existing object dependencies and AI context reasoning for pending migrations. No SQL parsing. This is how the CI gate in cerebro-migrations knows whether a migration stack is safe to merge.

## The Problem

Before a migration merges, we need to answer: "will this migration succeed against the real database?" That means knowing what depends on what.

Two sources of dependency information exist:

| What we need to know | Where the answer lives |
|---------------------|----------------------|
| What objects exist today and how they relate | PostgreSQL's `pg_depend` catalog — ground truth |
| What a pending migration will create and reference | The raw SQL text of the migration file |

## The Decision

Use both sources. Merge them into one dependency graph.

**Source 1: `pg_depend`** — PostgreSQL tracks every dependency between every object. If `silver.crm_deals` depends on `hubspot_bronze.deals`, the database knows it. One query extracts the complete graph:

```sql
SELECT DISTINCT
    dep_ns.nspname || '.' || dep_cl.relname AS dependent,
    ref_ns.nspname || '.' || ref_cl.relname AS dependency
FROM pg_depend d
JOIN pg_class dep_cl ON d.classid = 'pg_class'::regclass AND d.objid = dep_cl.oid
JOIN pg_namespace dep_ns ON dep_cl.relnamespace = dep_ns.oid
JOIN pg_class ref_cl ON d.refclassid = 'pg_class'::regclass AND d.refobjid = ref_cl.oid
JOIN pg_namespace ref_ns ON ref_cl.relnamespace = ref_ns.oid
WHERE dep_ns.nspname IN (...)
```

**Source 2: Raw SQL context** — For migrations that haven't been applied yet, the AI agent reads the SQL text and identifies what it creates and what it references. No regex, no AST parser, no manifest files. The agent reasons over the text naturally.

**The merge:** `pg_depend` graph (known world) + context-inferred dependencies (pending changes) = complete picture. If a pending migration depends on something that's neither in `pg_depend` nor in an earlier migration, it's a blocker.

## Why Not Parse SQL?

| Approach | Why we rejected it |
|----------|-------------------|
| Regex parsing | Brittle. Breaks on dynamic DDL, PL/pgSQL, conditional creates. High maintenance. |
| Full AST parser (pglast/sqlglot) | Fails on Supabase extensions and PL/pgSQL. Heavy dependency for marginal gain. |
| Manifest/header files | Developer burden. Drifts from reality. Another thing to keep in sync. |
| `pg_depend` alone | Can't see pending migrations. Only knows the current state. |
| Context reasoning alone | Works but has no ground-truth anchor. May miss subtle dependencies. |

`pg_depend` + context reasoning gives ground truth for what exists and flexible reasoning for what's pending. Zero parsing code to maintain. Improves as models improve.

## How It Fits

This decision answers **how** we validate migrations. [ADR-2026-38](ADR-2026-38-unified-migration-authority.md) answers **where** migrations live and **who** owns them. Together:

1. All migrations live in `cerebro-migrations` (ADR-2026-38)
2. CI spins up ephemeral Postgres, applies the full stack
3. elt-forge uses `pg_depend` + context reasoning to validate the dependency graph (this ADR)
4. If validation passes, PR can merge

Implementation details (snapshot-queries, build-dag, verify-node intents) are in the [elt-forge feature spec](../../repos-eidos-agi/elt-forge/specs/DAG-DEPLOY-PLAN.md).

## When to Revisit

- If schema count exceeds ~50 and context window pressure becomes real — consider schema pruning
- If a production failure traces back to AI misreading a pending migration — consider structured dependency hints as a supplement
- If PostgreSQL changes `pg_depend` semantics (unlikely — stable since 8.0)
