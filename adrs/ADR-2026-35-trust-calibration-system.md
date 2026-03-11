# ADR-2026-35: Trust Calibration System — 4-Level Autonomy

**Status:** Accepted
**Date:** 2026-02-27
**Author:** Daniel Shanklin

## Context

The CI engine runs autonomous agents that crawl data, score competitors, and generate alerts for Greenmark leadership. Some actions are safe to automate fully (crawling a public SOS website). Others are dangerous to automate (sending an alert to the President about a competitor acquisition).

We need a system that:
- Starts conservative (block everything, ask for human approval)
- Learns from experience (successes upgrade trust, corrections downgrade it)
- Has hard boundaries that can never be crossed (certain actions always require approval)
- Respects explicit user policy overrides

## Decision

Implement a 4-level trust system with learned calibration, hard boundaries, and user overrides. Every autonomous action passes through `can_i()` before execution.

### Trust Levels (least → most autonomous)

| Level | Behavior | When Used |
|-------|----------|-----------|
| **defer** | Block the job. Create an interrupt for human decision. | Unknown actions, low confidence, no calibration data |
| **propose** | Draft the action. Show it for approval before executing. | Partially trusted, sensitive context keywords detected |
| **inform** | Execute the action. Notify after the fact. | Trusted actions with good track record |
| **silent** | Execute and log. No notification. | Fully autonomous, many consecutive successes |

### Calibration State Machine

```
unknown → calibrating → trusted → autonomous
  (defer)   (propose)    (inform)   (silent)
```

- **5 consecutive successes** → upgrade one level
- **1 correction** → immediately downgrade one level
- **2 corrections within 24 hours** → double downgrade (detects oscillation)
- Success counter resets on each upgrade

### Hard Boundaries (immune system)

9 preseeded boundaries that cap trust levels regardless of calibration:

| Action | Max Level | Rationale |
|--------|-----------|-----------|
| `send_alert_executive` | propose | Avoid alert fatigue with leadership |
| `publish_briefing` | propose | Reaches the President, CRO, CFO |
| `crawl_new_source` | propose | Legal/ToS implications |
| `entity_merge` | propose | Hard to reverse |
| `entity_split` | propose | Hard to reverse |
| `delete_signal` | defer | Always requires explicit approval |
| `modify_dossier` | inform | Log but don't block |
| `update_threat_score` | inform | Scores change frequently |
| `update_churn_score` | inform | Scores change frequently |

### Evaluation Order in `can_i()`

1. **Hard boundary** — ceiling that can never be exceeded
2. **User override** — explicit policy rules (entity-specific > domain-wide)
3. **Calibration signal** — learned trust from success/correction history
4. **Low confidence penalty** — confidence < 0.7 downgrades one level
5. **Sensitive context detection** — keywords like "executive", "acquisition", "bankruptcy" cap to propose
6. **Apply boundary ceiling** — final enforcement

## Why This Design

1. **Starts safe, earns trust** — new actions default to `defer`. The system must prove reliability before gaining autonomy. This prevents day-one embarrassment.
2. **Corrections are expensive** — one correction undoes 5 successes. This is intentional: false autonomy is worse than false caution.
3. **Rapid correction detection** — two corrections within 24 hours signals the system is unreliable for this action type, triggering a double downgrade. Prevents oscillation.
4. **Hard boundaries are immune** — no amount of success will let the system send executive alerts without approval. Some decisions are too consequential for full autonomy.
5. **User overrides are final** — explicit policy ("always defer on publish_briefing for Alex Kaye") overrides calibration. Human judgment trumps statistical learning.
6. **Per-entity granularity** — trust for "crawl Republic Services" can differ from "crawl generic LLC filings". Entity-specific overrides take priority over domain-wide defaults.

## Consequences

- Every job execution has a trust lookup overhead (one SELECT query — negligible vs. the `claude -p` execution time)
- Trust data compounds over time — the system gets faster as it earns autonomy
- New source classes or action types always start at `defer` — explicit human approval required for first use
- The interrupt queue (`ci.interrupts`) handles blocked jobs — dashboard shows them with approve/reject/modify buttons
- Calibration data is visible: `success_count`, `correction_count`, `calibration_state` tracked per action type + domain + entity

## Related

- `src/ci/common/trust.py` — implementation
- `src/ci/common/interrupts.py` — attention queue for blocked jobs
- `src/ci/common/runner.py` — trust gate in `run_job()` (step 3)
- `infra/database.md` — `ci.trust_signals`, `ci.trust_overrides`, `ci.trust_boundaries` table definitions
