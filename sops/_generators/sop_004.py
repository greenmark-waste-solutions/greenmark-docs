#!/usr/bin/env python3
"""SOP-004 — Technical Debt Remediation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "sops" / "SOP-004-technical-debt-remediation.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "SOP-004", "Technical Debt Remediation"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Effective:</b> 2026-03-11  |  <b>Owner:</b> Daniel Shanklin  |  "
                   "<b>Applies to:</b> Any AI agent or developer resolving conflicting patterns, "
                   "outdated code, or schema drift across Greenmark systems",
                   META))
    story.append(Spacer(1, 6))

    # BLUF
    story.append(p("BLUF", H2))
    story.append(p(
        "When you find conflicting patterns across repos, <b>stop coding and start searching.</b> "
        "Query ADRs, SOPs, and cerebro memory to find the canonical pattern, classify every "
        "deviation by severity, write a reconciliation plan, execute against the test environment "
        "first, and verify. This SOP exists because an AI agent that copies the nearest code "
        "example has a 50/50 chance of propagating the wrong pattern — and a wrong pattern in a "
        "migration is a production incident."))
    story.append(Spacer(1, 8))

    # Definitions
    story.append(p("Definitions", H2))
    story.append(tbl(["Term", "Meaning"], [
        [p("<b>Technical debt</b>", CELL),
         p("Code, schema, or config that works today but violates established conventions", CELL)],
        [p("<b>Schema drift</b>", CELL),
         p("Database objects that deviate from the canonical pattern defined in ADRs", CELL)],
        [p("<b>Reconciliation</b>", CELL),
         p("The migration or code change that brings a drifted object back into compliance", CELL)],
        [p("<b>Canonical pattern</b>", CELL),
         p("The pattern defined by the most recent, non-superseded ADR for that domain", CELL)],
        [p("<b>Conflicting pattern</b>", CELL),
         p("Two implementations of the same concept that follow different conventions", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(Spacer(1, 8))

    # Phase 1: Detection
    story.append(p('Phase 1: Detection — "Something Doesn\'t Match"', H2))
    story.append(p("You will encounter technical debt in one of these ways:", BODY))
    story.append(Spacer(1, 4))
    story.append(tbl(["Trigger", "Example", "Action"], [
        [p("<b>Conflicting code across repos</b>", CELL),
         p("data-daemon uses <i>entity</i>, cerebro uses <i>entity_id</i>", CELL),
         p("STOP. Do not pick one.", CELL)],
        [p("<b>Audit failure</b>", CELL),
         p("elt-forge warns about gold mat views when ADR says tables", CELL),
         p("STOP. The audit is smarter.", CELL)],
        [p("<b>Feature fails from mismatch</b>", CELL),
         p("PostgREST 404 because RLS references wrong column", CELL),
         p("STOP. Debt manifesting as bug.", CELL)],
        [p("<b>Memory says deprecated</b>", CELL),
         p("Cerebro search returns \"superseded by cerebro\"", CELL),
         p("STOP. Understand full scope.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.45, USABLE * 0.30]))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "When triggered: Do NOT write code yet. Proceed to Phase 2."))
    story.append(Spacer(1, 8))

    # Phase 2: Discovery
    story.append(p('Phase 2: Discovery — "What Does the Canon Say?"', H2))
    story.append(p("Search in this order. Each step takes seconds and prevents hours of debugging.", BODY))
    story.append(Spacer(1, 4))
    story.append(tbl(["Step", "Tool", "What You're Looking For"], [
        [p("<b>2.1 Search ADRs</b>", CELL),
         p("cerebro_search(query, sources=\"docs\")", MONO),
         p("The law. Which pattern is canonical. Status: Accepted/Rejected/Superseded.", CELL)],
        [p("<b>2.2 Search SOPs</b>", CELL),
         p("cerebro_search(query, sources=\"docs\")", MONO),
         p("The procedure. How to do it. Which migration system to use.", CELL)],
        [p("<b>2.3 Search memory</b>", CELL),
         p("cerebro_recall(query, context=\"debugging\")", MONO),
         p("Gotchas, patterns that failed, deployment rules, column conventions.", CELL)],
        [p("<b>2.4 Read actual code</b>", CELL),
         p("Read both implementations", MONO),
         p("Every specific deviation between canonical and drifted.", CELL)],
    ], [USABLE * 0.18, USABLE * 0.35, USABLE * 0.47]))
    story.append(Spacer(1, 4))

    story.append(p("Real Example from This SOP's Discovery", H3))
    story.append(p("Searching ADRs for \"gold\" returned 8 rules in 30 seconds:", BODY))
    story.append(Spacer(1, 2))
    story.append(tbl(["ADR", "Rule"], [
        [p("ADR-2026-04", MONO), p("Gold uses regular tables, not materialized views", CELL)],
        [p("ADR-2026-05", MONO), p("Gold refresh uses MERGE, not TRUNCATE+INSERT", CELL)],
        [p("ADR-2026-07", MONO), p("Per-vendor bronze and silver schemas (hubspot_silver)", CELL)],
        [p("ADR-2026-08", MONO), p("Single gold schema with business-named tables", CELL)],
        [p("ADR-2026-09", MONO), p("service_role revoked from gold schema", CELL)],
        [p("ADR-2026-10", MONO), p("SECURITY DEFINER refresh with hardened search_path", CELL)],
        [p("ADR-2026-11", MONO), p("Default deny RLS policy on all gold tables", CELL)],
        [p("ADR-2026-14", MONO), p("Gold security drift audit", CELL)],
    ], [USABLE * 0.20, USABLE * 0.80]))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "Without searching, an agent would have to guess all 8 of these. "
                           "With searching, it takes 30 seconds."))
    story.append(hr())

    # Phase 3: Classification
    story.append(p('Phase 3: Classification — "How Bad Is It?"', H2))
    story.append(tbl(["Tier", "Severity", "Examples", "Action"], [
        [p("<b>1</b>", CELL), p("CRITICAL", RED_TEXT),
         p("RLS bypass, service_role not revoked, hard deletes where soft required, "
           "missing entity isolation, SECURITY DEFINER in wrong schema", CELL),
         p("Fix immediately. Block all other work.", CELL)],
        [p("<b>2</b>", CELL), p("<b>HIGH</b>", CELL_BOLD),
         p("Tables in wrong schema (406/404), column name mismatches, "
           "missing indexes, functions referencing non-existent objects", CELL),
         p("Fix before next deploy.", CELL)],
        [p("<b>3</b>", CELL), p("<b>MEDIUM</b>", CELL_BOLD),
         p("Column type mismatches, missing advisory locks, "
           "missing safety checks, inconsistent naming in non-RLS contexts", CELL),
         p("Fix in reconciliation migration.", CELL)],
        [p("<b>4</b>", CELL), p("LOW", CELL),
         p("Comment style, file naming, redundant IF NOT EXISTS, "
           "YAML warnings", CELL),
         p("Fix opportunistically.", CELL)],
    ], [0.25 * inch, USABLE * 0.12, USABLE * 0.52, USABLE - 0.25 * inch - USABLE * 0.64]))
    story.append(Spacer(1, 8))

    # Phase 4: Reconciliation Plan
    story.append(p('Phase 4: Reconciliation Plan — "Write It Down Before You Write Code"', H2))
    story.append(p("<b>Step 4.1:</b> List every object that needs to change — table, current state, "
                   "target state, severity, which migration.", BODY))
    story.append(Spacer(1, 4))
    story.append(p("<b>Step 4.2:</b> Determine migration order. Standard for Greenmark:", BODY))
    story.append(Spacer(1, 2))
    story.append(tbl(["#", "Layer", "What"], [
        [p("1", CELL), p("<b>Silver first</b>", CELL), p("Create/update materialized views", CELL)],
        [p("2", CELL), p("<b>Gold tables</b>", CELL), p("Create tables with correct conventions", CELL)],
        [p("3", CELL), p("<b>RLS + grants</b>", CELL), p("Enable RLS, create policies, grant to roles", CELL)],
        [p("4", CELL), p("<b>Forge functions</b>", CELL), p("Create SECURITY DEFINER refresh functions", CELL)],
        [p("5", CELL), p("<b>Master refresh</b>", CELL), p("Update forge.refresh_all()", CELL)],
        [p("6", CELL), p("<b>Initial population</b>", CELL), p("Run refresh to populate from silver", CELL)],
    ], [0.25 * inch, USABLE * 0.20, USABLE - 0.25 * inch - USABLE * 0.20]))
    story.append(Spacer(1, 4))
    story.append(p("<b>Step 4.3:</b> One migration per logical unit. Migrations must be idempotent. "
                   "Use IF NOT EXISTS, IF EXISTS, CREATE OR REPLACE.", BODY))
    story.append(Spacer(1, 4))
    story.append(p("<b>Step 4.4:</b> Write the plan as a comment block at the top of each migration, "
                   "listing ADRs followed, dependencies, and test instructions.", BODY))
    story.append(hr())

    # Phase 5: Execution
    story.append(p('Phase 5: Execution — "Test Project First, Always"', H2))
    story.append(tbl(["Step", "Action"], [
        [p("<b>5.1</b>", CELL),
         p("Apply to Cerebro Test (izmuckuepryqneebwwol) via "
           "<i>npx supabase db push --db-url ...</i>", CELL)],
        [p("<b>5.2</b>", CELL),
         p("Run CRITICAL verification queries: RLS enabled+forced, entity_id exists, "
           "service_role revoked. Then HIGH: forge functions exist, identity PKs present.", CELL)],
        [p("<b>5.3</b>", CELL),
         p("Apply to production: <i>npx supabase db push --linked</i>", CELL)],
        [p("<b>5.4</b>", CELL),
         p("Run <i>SELECT forge.refresh_all();</i> to populate gold from silver", CELL)],
        [p("<b>5.5</b>", CELL),
         p("Run same verification queries against production", CELL)],
    ], [0.4 * inch, USABLE - 0.4 * inch]))
    story.append(Spacer(1, 8))

    # Phase 6: Escalation
    story.append(p('Phase 6: Escalation — "When to Stop and Ask"', H2))
    story.append(AccentBox(USABLE,
                           "The most expensive mistake an AI agent makes is not being wrong — "
                           "it's being wrong confidently."))
    story.append(Spacer(1, 6))

    story.append(p("When to Ask the Human", H3))
    story.append(tbl(["#", "Situation", "What to Say"], [
        [p("1", CELL), p("<b>No ADR exists</b> for the domain", CELL),
         p("\"I found X and Y patterns. No ADR covers this. Which is canonical?\"", CELL)],
        [p("2", CELL), p("<b>Two ADRs conflict</b>", CELL),
         p("\"ADR-04 says X but ADR-07 implies Y. Which takes precedence?\"", CELL)],
        [p("3", CELL), p("<b>Fix would break production</b>", CELL),
         p("\"Reconciling requires changes in [list]. Proceed or phase it?\"", CELL)],
        [p("4", CELL), p("<b>Spans ownership boundaries</b>", CELL),
         p("\"This fix spans data-daemon and cerebro. Need coordination guidance.\"", CELL)],
        [p("5", CELL), p("<b>Security implications</b>", CELL),
         p("\"Changing RLS/SECURITY DEFINER/GRANTs. Here's the list. Confirm?\"", CELL)],
        [p("6", CELL), p("<b>Debt is load-bearing</b>", CELL),
         p("\"Wrong per ADR but live in production. Here's my zero-downtime plan.\"", CELL)],
        [p("7", CELL), p("<b>Stuck &gt;20 minutes</b>", CELL),
         p("\"I'm stuck on [X]. Here's what I tried. I need a different angle.\"", CELL)],
    ], [0.25 * inch, USABLE * 0.30, USABLE - 0.25 * inch - USABLE * 0.30]))
    story.append(Spacer(1, 6))

    story.append(p("When to Ask a Second AI", H3))
    story.append(tbl(["#", "Situation", "Why"], [
        [p("1", CELL), p("<b>Architecture review</b> of reconciliation plan", CELL),
         p("Second AI catches blind spots — no sunk cost in your approach", CELL)],
        [p("2", CELL), p("<b>Security audit</b> of RLS/SECURITY DEFINER changes", CELL),
         p("RLS is unforgiving — wrong policy silently leaks or blocks data", CELL)],
        [p("3", CELL), p("<b>SQL correctness</b> for complex MERGE operations", CELL),
         p("MERGE + soft deletes + advisory locks + safety checks is intricate", CELL)],
        [p("4", CELL), p("<b>Blast radius assessment</b>", CELL),
         p("List every downstream dependency: views, functions, API, app code", CELL)],
        [p("5", CELL), p("<b>Ambiguous user request</b>", CELL),
         p("Ask second AI to interpret, then confirm with human if still unclear", CELL)],
    ], [0.25 * inch, USABLE * 0.35, USABLE - 0.25 * inch - USABLE * 0.35]))
    story.append(Spacer(1, 4))

    story.append(p("Escalation Format", H3))
    story.append(AccentBox(USABLE,
                           "ESCALATION: [one-line summary]  •  CONTEXT: [what you were doing]  •  "
                           "FINDING: [the conflict or risk]  •  OPTIONS: [A, B, C + recommendation]  •  "
                           "QUESTION: [the specific thing you need answered]",
                           bold=False, size=8))
    story.append(Spacer(1, 4))
    story.append(p("When NOT to escalate (just do it)", H3))
    story.append(p("ADR is clear and you match it exactly. Adding IF NOT EXISTS. "
                   "Creating wrapper views. Change is test-only. Debt is Tier 4.", BODY))
    story.append(hr())

    # Phase 7: Prevention
    story.append(p('Phase 7: Prevention — "Don\'t Create New Debt"', H2))
    story.append(p("Cardinal Rules for AI Agents", H3))
    story.append(tbl(["#", "Rule"], [
        [p("1", CELL), p("<b>Never copy the nearest code without searching ADRs first.</b> "
                         "The nearest example might be the drifted one.", CELL)],
        [p("2", CELL), p("<b>When you find two patterns, STOP.</b> "
                         "Search cerebro_search() for the canonical one. If no ADR, ask the human.", CELL)],
        [p("3", CELL), p("<b>Always search before implementing.</b> "
                         "30 seconds of searching prevents 4 hours of debugging.", CELL)],
        [p("4", CELL), p("<b>Check schema ownership</b> per SOP-002. "
                         "Bronze/daemon/vault = data-daemon. Everything else = cerebro.", CELL)],
        [p("5", CELL), p("<b>Use the governance check.</b> "
                         "Verify changes don't violate org constraints before shipping.", CELL)],
        [p("6", CELL), p("<b>Log what you learn.</b> "
                         "cerebro_remember() with topic, tags, emotional weights.", CELL)],
        [p("7", CELL), p("<b>Don't fix debt you weren't asked to fix.</b> "
                         "Note Tier 3-4 debt in memory and move on. Don't scope-creep.", CELL)],
        [p("8", CELL), p("<b>Match the CANONICAL pattern exactly.</b> "
                         "Don't create a third pattern. Read the actual implementation.", CELL)],
    ], [0.25 * inch, USABLE - 0.25 * inch]))
    story.append(Spacer(1, 6))

    story.append(p("Structural Prevention (for humans)", H3))
    story.append(tbl(["Action", "Frequency"], [
        [p("Run elt-forge audit after every migration", CELL), p("Per deploy", CELL)],
        [p("Keep ADRs current — new ADR supersedes old, don't just change code", CELL), p("As needed", CELL)],
        [p("Keep cerebro memory current — update entries when patterns change", CELL), p("Per session", CELL)],
        [p("Review deprecated data-daemon migrations for cleanup", CELL), p("Quarterly", CELL)],
    ], [USABLE * 0.75, USABLE * 0.25]))
    story.append(Spacer(1, 8))

    # Agent Decision Flowchart
    story.append(p("Agent Decision Flowchart", H2))
    story.append(tbl(["Step", "Action", "Tool"], [
        [p("1", CELL), p("Search ADRs for the domain", CELL),
         p("cerebro_search(query, sources=\"docs\")", MONO)],
        [p("2", CELL), p("Search memory for gotchas and patterns", CELL),
         p("cerebro_recall(query, context=\"debugging\")", MONO)],
        [p("3", CELL), p("Check schema ownership (SOP-002)", CELL),
         p("Which migration system?", CELL)],
        [p("4", CELL), p("Read the CANONICAL implementation", CELL),
         p("Match its patterns exactly", CELL)],
        [p("5", CELL), p("Read the DRIFTED implementation", CELL),
         p("Identify every deviation", CELL)],
        [p("6", CELL), p("Classify deviations by severity tier", CELL),
         p("CRITICAL → HIGH → MEDIUM → LOW", CELL)],
        [p("7", CELL), p("Write migration with ADR comment header", CELL),
         p("IF NOT EXISTS for idempotency", CELL)],
        [p("8", CELL), p("Test → Verify → Production → Verify", CELL),
         p("Per SOP-002", CELL)],
        [p("9", CELL), p("Log to cerebro memory", CELL),
         p("cerebro_remember()", MONO)],
    ], [0.3 * inch, USABLE * 0.50, USABLE - 0.3 * inch - USABLE * 0.50]))
    story.append(hr())

    # Case study
    story.append(p("Case Study: The Discovery That Created This SOP", H2))
    story.append(p("On 2026-03-11, data-daemon migrations 018-019 were found to define 16 gold "
                   "tables using conventions that conflict with cerebro's established patterns:", BODY))
    story.append(Spacer(1, 4))
    story.append(tbl(["Convention", "Data-daemon 018/019", "Cerebro canonical"], [
        [p("Entity column", CELL), p("entity", RED_TEXT), p("entity_id", GREEN_TEXT)],
        [p("Primary key", CELL), p("No identity PK", RED_TEXT),
         p("id BIGINT GENERATED ALWAYS AS IDENTITY", GREEN_TEXT)],
        [p("Deletion", CELL), p("Hard delete (MERGE ... DELETE)", RED_TEXT),
         p("Soft delete (deleted_at)", GREEN_TEXT)],
        [p("Refresh schema", CELL), p("secure", RED_TEXT), p("forge", GREEN_TEXT)],
        [p("Safety checks", CELL), p("None", RED_TEXT),
         p("Advisory locks + empty-source + delete ratio", GREEN_TEXT)],
        [p("RLS extraction", CELL), p("Raw JWT ->>'entity'", RED_TEXT),
         p("gold.current_entity_id() helper", GREEN_TEXT)],
        [p("Silver source", CELL), p("silver.crm_*", RED_TEXT),
         p("hubspot_silver.*", GREEN_TEXT)],
    ], [USABLE * 0.20, USABLE * 0.38, USABLE * 0.42]))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "Searching ADRs and cerebro memory took 3 minutes. "
                           "Blindly copying the wrong pattern would have cost 20-40 hours + "
                           "a production incident.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))
    story.append(Spacer(1, 8))

    # Why
    story.append(p("Why This Exists", H2))
    story.append(p(
        "AI agents are powerful but pattern-matching machines. When they see code, they copy it. "
        "When there are two conflicting patterns in a codebase, they have no way to know which "
        "one is right without external guidance. ADRs, SOPs, and cerebro memory ARE that external "
        "guidance — but only if the agent knows to search them first. This SOP makes \"search "
        "before you code\" a non-negotiable step in every remediation."))
    story.append(Spacer(1, 6))
    story.append(AccentBox(USABLE,
                           "No exceptions. Every technical debt remediation follows this process. "
                           "If you don't have time to search ADRs, you don't have time to write "
                           "the migration — because you'll spend 10x longer fixing the wrong one."))


if __name__ == "__main__":
    build_doc(OUTPUT, "SOP-004: Technical Debt Remediation", content)
