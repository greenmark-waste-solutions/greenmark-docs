# ADR-2026-29: All ADRs Require a BLUF

- **Status**: Superseded by [SOP-001](../sops/SOP-001-creating-adrs-and-sops.md)
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: All `decisions/ADR-*` files

## BLUF (Bottom Line Up Front)

Every ADR in this repo must open with a BLUF section — a 2-3 sentence summary that gives the reader the decision, the reason, and the consequence without reading anything else. Military-style. If the reader stops after the BLUF, they still know what happened and why.

## Context

Architecture Decision Records serve multiple audiences at Greenmark: technical staff (Daniel), leadership (Michael, Alex), and future engineers who inherit this codebase. Most readers are busy. Many will open an ADR from a GitHub link in a meeting, skim 10 seconds, and close it.

The existing ADRs (01-04) bury the decision under Context sections. A reader has to get through 2-3 paragraphs before learning what was actually decided. This is the opposite of how military communications work — and military comms are optimized for exactly this problem: high-stakes decisions that busy people need to absorb fast.

## Decision

**Every ADR must include a `## BLUF (Bottom Line Up Front)` section immediately after the metadata block and before `## Context`.** The BLUF must:

1. **State the decision** — what are we doing or not doing
2. **State the primary reason** — the one thing that tipped the scale
3. **State the consequence** — what this means in practice

All three in 2-3 sentences. No hedging, no "on the other hand." The BLUF is the decision, delivered with conviction.

### Format

```markdown
# ADR-YYYY-NN: Title

- **Status**: Accepted/Rejected/Superseded
- **Date**: YYYY-MM-DD
- **Owner**: Name / Role

## BLUF (Bottom Line Up Front)

[2-3 sentences. Decision + reason + consequence. No hedging.]

## Context
...
```

### Examples

**Good BLUF:**
> We will not build a secrets management UI in Cerebro. Any web-tier access to vault secrets creates a permanent privilege escalation path. The inconvenience of SQL Editor access is the security control.

**Bad BLUF:**
> After careful consideration of several options and their trade-offs, we have decided that it would be best to avoid building a vault UI at this time, pending further security review.

The bad one hedges, uses passive voice, and doesn't tell you why. The good one is a military briefing: here's what, here's why, move on.

## Rationale

| Factor | Assessment |
|--------|-----------|
| **Audience** | Michael and Alex read these in GitHub's web UI between meetings. They need the answer in 10 seconds. |
| **Precedent** | Military BLUF format is proven for exactly this use case — high-stakes decisions consumed by busy decision-makers. |
| **AI agents** | Future Claude sessions reference ADRs for architectural context. A BLUF lets the agent extract the decision without reading the full document. |
| **Cost** | Adding 2-3 sentences to each ADR costs nothing. The format is additive — everything else stays the same. |

## Options Considered

| Option | Description | Verdict |
|--------|-------------|---------|
| **A. BLUF required (chosen)** | Mandatory section after metadata, before Context | Fast comprehension, zero cost, military-proven |
| B. Executive Summary | Longer summary section (5-10 sentences) | Too long for the purpose — defeats the point |
| C. Status quo | Decision buried in Context/Decision sections | Readers miss the point, especially non-technical stakeholders |

## Consequences

- **Positive**: Every ADR is comprehensible in 10 seconds. Non-technical stakeholders (Michael, Alex) get the answer without wading through technical context. AI agents can extract decisions efficiently.
- **Negative**: Existing ADRs (01-04) should be backfilled with BLUFs. Minor one-time effort.
- **Action**: Backfill BLUFs on ADR-01 through ADR-04. ADR-04 already has one as of today.
