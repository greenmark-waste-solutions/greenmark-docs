# SOP-004: Technical Debt Remediation

- **Effective**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Applies to**: Any AI agent or developer resolving conflicting patterns, outdated code, or schema drift across Greenmark systems

## BLUF

When you find conflicting patterns across repos, **stop coding and start searching.** Query ADRs, SOPs, and cerebro memory to find the canonical pattern, classify every deviation by severity, write a reconciliation plan, execute against the test environment first, and verify. This SOP exists because an AI agent that copies the nearest code example has a 50/50 chance of propagating the wrong pattern — and a wrong pattern in a migration is a production incident.

## Definitions

| Term | Meaning |
|------|---------|
| **Technical debt** | Code, schema, or configuration that works today but violates established conventions, creating future cost |
| **Schema drift** | Database objects that deviate from the canonical pattern defined in ADRs (wrong column names, missing RLS, wrong schema) |
| **Reconciliation** | The migration or code change that brings a drifted object back into compliance with ADRs |
| **Canonical pattern** | The pattern defined by the most recent, non-superseded ADR for that domain |
| **Conflicting pattern** | Two implementations of the same concept that follow different conventions |

## Phase 1: Detection — "Something Doesn't Match"

You will encounter technical debt in one of these ways:

### Trigger 1: Conflicting code across repos
You're writing a migration and notice that `data-daemon` uses `entity` while `cerebro` uses `entity_id`. **Stop. Do not pick one and keep going.**

### Trigger 2: A build, test, or audit fails
An elt-forge audit returns warnings about gold materialized views when ADR-2026-04 says gold must use regular tables. **Stop. The audit is smarter than your instinct.**

### Trigger 3: A feature doesn't work and the root cause is a pattern mismatch
PostgREST returns 404 on a gold table because the RLS policy references `entity` but the column is `entity_id`. **Stop. This is debt manifesting as a bug.**

### Trigger 4: Cerebro memory or devlog mentions "deprecated" or "superseded"
A search returns an entry saying "data-daemon migrations 009-012 are superseded by cerebro." **Stop. Understand the full scope before touching anything.**

### What to do when triggered

**Do not write code yet.** Proceed to Phase 2.

## Phase 2: Discovery — "What Does the Canon Say?"

### Step 2.1: Search ADRs

```
cerebro_search(query="<the concept>", sources="docs")
```

ADRs are the law. They define what the canonical pattern IS. Read every ADR that matches your domain. Pay attention to:

- **Status**: Only `Accepted` ADRs are active. `Rejected` means we considered and refused. `Superseded` means a newer ADR replaced it.
- **Date**: Later ADRs take precedence over earlier ones on the same topic.
- **Consequences section**: This tells you what trade-offs were accepted — don't try to "fix" an accepted trade-off.

**Example from this session**: We found 8 ADRs governing gold schema conventions:

| ADR | Rule |
|-----|------|
| ADR-2026-04 | Gold uses regular tables, not materialized views |
| ADR-2026-05 | Gold refresh uses MERGE, not TRUNCATE+INSERT |
| ADR-2026-07 | Per-vendor bronze and silver schemas (hubspot_silver, not silver) |
| ADR-2026-08 | Single gold schema with business-named tables |
| ADR-2026-09 | service_role revoked from gold schema |
| ADR-2026-10 | SECURITY DEFINER refresh functions with hardened search_path |
| ADR-2026-11 | Default deny RLS policy on all gold tables |
| ADR-2026-14 | Gold security drift audit |

Without searching, an agent would have to *guess* all 8 of these. With searching, it takes 30 seconds.

### Step 2.2: Search SOPs

```
cerebro_search(query="<the process>", sources="docs")
```

SOPs tell you HOW to do things. If there's an SOP for migrations (SOP-002), follow it. If there's an SOP for Excel exports (SOP-003), follow it. SOPs are living documents — they're always current.

### Step 2.3: Search cerebro memory

```
cerebro_recall(query="<the concept>", context="debugging")
```

Use `context="debugging"` — this weights pain and novelty higher, surfacing gotchas and things that burned us before.

Memory contains:
- **Patterns that worked** — reuse them
- **Patterns that failed** — avoid them
- **Deployment rules** — don't violate them
- **Schema conventions** — column names, index patterns, RLS patterns

### Step 2.4: Read the actual code in BOTH locations

After you know what the canon says, read the actual implementations:

1. Read the canonical implementation (the one that matches ADRs)
2. Read the drifted implementation (the one that doesn't)
3. Identify every specific deviation

**Do not skip this step.** ADRs tell you the principle; code tells you the implementation details (advisory locks, delete-ratio checks, specific column types) that ADRs don't capture.

## Phase 3: Classification — "How Bad Is It?"

Classify every deviation into one of four severity tiers:

### Tier 1: CRITICAL — Security or data integrity risk

- RLS bypass (wrong column name in policy, missing FORCE ROW LEVEL SECURITY)
- service_role not revoked from protected schema
- Hard deletes where soft deletes are required (no audit trail)
- Missing entity isolation on multi-tenant tables
- SECURITY DEFINER functions in wrong schema or with wrong owner

**Action**: Fix immediately. Do not ship anything else until this is resolved.

### Tier 2: HIGH — Will cause runtime failures

- Tables/views in wrong schema (PostgREST returns 406/404)
- Column name mismatches between refresh function and table definition
- Missing indexes required for REFRESH CONCURRENTLY
- Functions referencing non-existent objects
- Migration system confusion (data-daemon migration creating cerebro-owned objects)

**Action**: Fix before next deployment. Block other work on this schema.

### Tier 3: MEDIUM — Convention violation, works but creates future cost

- Column type mismatch (NUMERIC vs NUMERIC(15,2))
- Missing advisory locks on refresh functions
- Missing delete-ratio safety check
- Inconsistent naming (entity vs entity_id) in non-RLS-critical contexts
- Deprecated code that still runs but is superseded

**Action**: Fix in the reconciliation migration. Don't leave it for "later."

### Tier 4: LOW — Cosmetic or informational

- Comment style differences
- Migration file naming conventions
- Redundant IF NOT EXISTS on objects that definitely exist
- YAML service definition naming warnings

**Action**: Fix opportunistically. Don't block work for these.

## Phase 4: Reconciliation Plan — "Write It Down Before You Write Code"

### Step 4.1: List every object that needs to change

Create a table:

```markdown
| Object | Current State | Target State | Severity | Migration |
|--------|--------------|--------------|----------|-----------|
| gold.deal_aging | Does not exist | Create with entity_id, identity PK, deleted_at | HIGH | B |
| gold.pipeline_summary.weighted_value | Missing column | Add NUMERIC(15,2) | MEDIUM | B |
| forge.refresh_deal_aging() | Does not exist | Create with advisory lock + safety checks | HIGH | B |
| hubspot_silver.engagements | Does not exist | Create mat view from bronze | HIGH | A |
| silver.crm_engagements | Exists in data-daemon 017 | Wrapper view to hubspot_silver | MEDIUM | A |
```

### Step 4.2: Determine migration order

Migrations have dependencies. Gold tables depend on silver views. Refresh functions depend on gold tables. RLS depends on tables existing.

Standard order for Greenmark:
1. **Silver first** — create/update materialized views
2. **Gold tables** — create tables with correct conventions
3. **RLS + grants** — enable RLS, create policies, grant to roles
4. **Forge functions** — create SECURITY DEFINER refresh functions
5. **Master refresh** — update forge.refresh_all()
6. **Initial population** — run the refresh to populate from silver

### Step 4.3: Decide number of migrations

**Rule**: One migration per logical unit. Don't put silver and gold in the same migration — if the gold part fails, you can't re-run without re-running silver.

**Rule**: Migrations must be idempotent. Use `IF NOT EXISTS`, `IF EXISTS`, `CREATE OR REPLACE`. Test by running the migration twice — the second run should be a no-op.

### Step 4.4: Write the plan as a comment block

Put the plan at the top of each migration file:

```sql
-- Migration: Gold expansion — deals, reps, customers, tickets
-- Reconciles data-daemon migrations 018-019 into cerebro conventions
-- Follows: ADR-2026-04 (tables not views), ADR-2026-05 (MERGE refresh),
--          ADR-2026-08 (single gold schema), ADR-2026-09 (service_role revoked),
--          ADR-2026-10 (SECURITY DEFINER), ADR-2026-11 (default deny RLS)
-- Depends on: Silver expansion migration (must run first)
-- Test: Apply to izmuckuepryqneebwwol first
```

## Phase 5: Execution — "Test Project First, Always"

### Step 5.1: Apply to test environment

Per SOP-002, always test against the Cerebro Test project (`izmuckuepryqneebwwol`) before production.

```bash
cd cerebro
npx supabase db push --db-url postgresql://postgres:<pw>@db.izmuckuepryqneebwwol.supabase.co:5432/postgres
```

### Step 5.2: Verify in test

Run verification queries for each severity tier:

**CRITICAL verification** (must all pass):
```sql
-- RLS enabled and forced on all gold tables
SELECT tablename, rowsecurity, forcerowsecurity
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname = 'gold'
  AND (NOT c.relrowsecurity OR NOT c.relforcerowsecurity);
-- Expected: 0 rows (all tables have both enabled)

-- Entity isolation column exists
SELECT tablename FROM pg_tables
WHERE schemaname = 'gold'
  AND tablename NOT IN (
    SELECT table_name FROM information_schema.columns
    WHERE table_schema = 'gold' AND column_name = 'entity_id'
  );
-- Expected: 0 rows

-- service_role has no gold access
SELECT grantee, privilege_type FROM information_schema.table_privileges
WHERE table_schema = 'gold' AND grantee = 'service_role';
-- Expected: 0 rows
```

**HIGH verification**:
```sql
-- All forge refresh functions exist
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'forge' AND routine_name LIKE 'refresh_%';

-- All gold tables have identity PK
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'gold'
  AND table_name NOT IN (
    SELECT table_name FROM information_schema.columns
    WHERE table_schema = 'gold' AND column_name = 'id'
  );
-- Expected: 0 rows
```

### Step 5.3: Apply to production

Only after test verification passes:

```bash
npx supabase db push --linked
```

### Step 5.4: Run forge.refresh_all()

Populate the new gold tables from silver:

```sql
SELECT forge.refresh_all();
```

### Step 5.5: Verify in production

Run the same verification queries against production.

## Phase 6: Escalation — "When to Stop and Ask"

The most expensive mistake an AI agent makes is not being wrong — it's being wrong *confidently*. These rules define when to stop working and escalate.

### When to Ask the Human

**ASK IMMEDIATELY — do not attempt to resolve on your own:**

1. **No ADR exists for the domain.** You found conflicting patterns but no ADR says which is right. You cannot create convention — only humans create convention. Say: *"I found X and Y patterns for [concept]. No ADR covers this. Which is canonical, or should we write an ADR?"*

2. **Two ADRs conflict.** One ADR says X, another says Y, and neither supersedes the other. Say: *"ADR-2026-04 says [X] but ADR-2026-07 implies [Y]. Which takes precedence for this case?"*

3. **The canonical pattern would break existing functionality.** You know entity_id is correct, but 47 API calls use entity. The remediation has blast radius. Say: *"Reconciling to entity_id will require changes in [list]. Should I proceed with the full scope, or do a phased approach?"*

4. **You're about to touch a schema you don't own.** Per SOP-002, bronze belongs to data-daemon, everything else to cerebro. If your remediation would require changes in both migration systems, say: *"This fix spans both data-daemon and cerebro ownership. I need guidance on coordination."*

5. **Security implications.** Any change to RLS policies, SECURITY DEFINER functions, GRANT/REVOKE statements, or service_role permissions. Say: *"This remediation changes security boundaries. Here's what I'm changing: [list]. Confirm before I proceed."*

6. **The debt is load-bearing.** The wrong pattern is actively being used in production by users. Fixing it means downtime or behavior change. Say: *"This pattern is wrong per ADR-2026-XX, but it's live in production. Here's my plan for zero-downtime migration: [plan]. Approve?"*

7. **You've been working for more than 20 minutes without progress.** If you're going in circles — reading the same files, trying variations of the same approach — stop. Say: *"I'm stuck on [specific issue]. Here's what I've tried: [list]. I need a different angle."*

### When to Ask a Second AI

Use a second AI (via PAL, mcp-openai, or similar) as a **specialist consultant** in these situations:

1. **Architecture review of your reconciliation plan.** Before writing 500+ lines of migration SQL, ask a second AI: *"Here's my plan to reconcile [X]. The canonical patterns from our ADRs are [list]. Does this plan have gaps? What could go wrong?"* The second AI catches blind spots because it has no sunk cost in your approach.

2. **Security audit of RLS/SECURITY DEFINER changes.** RLS is unforgiving — a wrong policy silently leaks data or silently blocks it. Ask: *"Review these RLS policies for entity isolation bypass. Can any role path reach gold data without passing through the entity_id check?"*

3. **SQL correctness for complex MERGE operations.** MERGE with soft deletes, advisory locks, and delete-ratio checks is intricate. Ask: *"Does this MERGE correctly handle: (a) new rows, (b) changed rows, (c) removed rows via soft delete, (d) the race condition where two refreshes run concurrently?"*

4. **When you're unsure about blast radius.** Ask: *"If I run this migration, what could break? List every downstream dependency: views, functions, API routes, and application code that references these objects."*

5. **When the human said something ambiguous.** Instead of guessing what the human meant, ask a second AI to interpret: *"The user said '[exact quote]'. In the context of [project state], does this mean A or B?"* Then confirm with the human if still unclear.

### When NOT to escalate (just do it)

- The ADR is clear and your implementation matches it exactly
- You're adding IF NOT EXISTS to an existing pattern
- You're creating a wrapper view for backward compatibility
- The change is in the test environment only
- The debt is Tier 4 (cosmetic) and you're fixing it while already in the file

### Escalation Format

When you escalate, use this structure so the human can respond quickly:

```
ESCALATION: [one-line summary]
CONTEXT: [what you were doing when you hit this]
FINDING: [what you found — the conflict, gap, or risk]
OPTIONS: [A, B, or C — with your recommendation]
QUESTION: [the specific thing you need answered]
```

Bad: "I'm not sure about the entity column."
Good: "ESCALATION: Column naming conflict in gold expansion. CONTEXT: Writing gold.deal_aging table per data-daemon 018. FINDING: data-daemon uses `entity`, cerebro uses `entity_id`. 8 ADRs reference entity_id as canonical. OPTION A: Use entity_id (matches ADRs, requires updating refresh functions). OPTION B: Use entity (matches data-daemon, creates new drift). RECOMMENDATION: A. QUESTION: Confirm entity_id before I write 16 table definitions?"

## Phase 7: Prevention — "Don't Create New Debt"

### For AI agents: The Cardinal Rules

1. **Never copy the nearest code example without searching ADRs first.** The nearest example might be the drifted one.

2. **When you find two patterns for the same thing, STOP.** Search `cerebro_search()` to find which one is canonical. If no ADR exists, ask the user — don't guess.

3. **Always search before implementing.** Run `cerebro_search(query="<concept>")` before writing any migration, refresh function, or schema change. 30 seconds of searching prevents 4 hours of debugging.

4. **Check schema ownership before writing SQL.** Per SOP-002:
   - Bronze + daemon + vault → data-daemon
   - Everything else → cerebro
   - If you're about to write a cerebro migration that touches bronze, STOP.

5. **Use the governance check.** Before shipping, verify your changes don't violate organizational constraints.

6. **Log what you learn.** If you discover new technical debt during a session, call `cerebro_remember()` with topic, tags, and emotional weights. Future agents will thank you.

7. **Don't fix debt you weren't asked to fix.** If you discover Tier 3-4 debt while working on something else, note it in cerebro memory and move on. Don't scope-creep into a remediation project.

8. **When reconciling, match the CANONICAL pattern exactly.** Don't create a third pattern that's "your interpretation" of the ADRs. Read the actual canonical implementation and match it.

### For humans: Structural prevention

- **Run elt-forge audit** after every migration. It checks for ADR violations.
- **Keep ADRs current.** If a convention changes, write a new ADR that supersedes the old one. Don't just change the code.
- **Keep cerebro memory current.** When you fix a pattern, update the memory entry. When a gotcha is resolved, update or forget the old entry.
- **Review data-daemon migrations** quarterly. Deprecated migrations (009, 010, 012, 017) should eventually be cleaned up or marked with comments.

## Agent Decision Flowchart

```
You need to write a migration / schema change / refresh function.

  Step 1: cerebro_search(query="<domain>", sources="docs")
  → Read every matching ADR. List the rules that apply.

  Step 2: cerebro_search(query="<domain>", sources="memory")
  → Read every matching memory. Note gotchas and patterns.

  Step 3: SOP-002 — which migration system?
  → Bronze/daemon/vault = data-daemon
  → Everything else = cerebro (Supabase CLI)

  Step 4: Read the CANONICAL implementation
  → Find the most recent cerebro migration that does the same kind of thing
  → Match its patterns exactly: column names, types, PK style, RLS style,
    refresh function schema, safety checks, GRANT/REVOKE patterns

  Step 5: Read the DRIFTED implementation (if reconciling)
  → Identify every deviation from canonical
  → Classify each by severity tier

  Step 6: Write the migration
  → Comment block at top listing ADRs followed
  → IF NOT EXISTS / IF EXISTS for idempotency
  → Test project first

  Step 7: Verify
  → CRITICAL checks must pass
  → HIGH checks must pass
  → MEDIUM checks should pass

  Step 8: Log
  → cerebro_remember() with what you did and why
  → Update any outdated memory entries
```

## The Reconciliation We Discovered This SOP For

On 2026-03-11, while building the Excel export tool, we discovered that data-daemon migrations 018-019 define 16 gold tables + refresh functions using conventions that conflict with cerebro's established patterns:

| Convention | Data-daemon 018/019 | Cerebro canonical |
|-----------|---------------------|-------------------|
| Entity column | `entity` | `entity_id` |
| Primary key | No identity PK | `id BIGINT GENERATED ALWAYS AS IDENTITY` |
| Deletion | Hard delete (MERGE ... DELETE) | Soft delete (`deleted_at TIMESTAMPTZ`) |
| Refresh schema | `secure` | `forge` |
| Safety checks | None | Advisory locks + empty-source abort + >50% delete ratio abort |
| RLS extraction | Raw JWT `->>'entity'` | `gold.current_entity_id()` helper function |
| Silver source | `silver.crm_*` | `hubspot_silver.*` |

If an AI agent had blindly copied the data-daemon 018 pattern into a cerebro migration, it would have:
1. Created tables invisible to RLS (wrong column name)
2. Allowed hard deletes (no audit trail)
3. Skipped safety checks (data corruption risk)
4. Put functions in the wrong schema (refresh_all wouldn't find them)
5. Referenced silver views that don't exist in the correct schema

**Total estimated cost of that mistake: 20-40 hours of debugging + a production incident.**

Searching ADRs and cerebro memory took 3 minutes.

## Why This Exists

AI agents are powerful but pattern-matching machines. When they see code, they copy it. When there are two conflicting patterns in a codebase, they have no way to know which one is right without external guidance. ADRs, SOPs, and cerebro memory ARE that external guidance — but only if the agent knows to search them first.

This SOP makes "search before you code" a non-negotiable step in every remediation. It turns tribal knowledge into searchable knowledge, and searchable knowledge into correct code.

## Exceptions

None. Every technical debt remediation follows this process. If you don't have time to search ADRs, you don't have time to write the migration — because you'll spend 10x longer fixing the wrong one.
