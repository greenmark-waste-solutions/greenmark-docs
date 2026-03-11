# ADR-2026-31: Establish SOP Document Type for Operating Procedures

- **Status**: Accepted
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-05 (BLUF), ADR-2026-06 (branded PDF), `sops/` directory

## BLUF (Bottom Line Up Front)

We're creating a new document type — SOPs (Standard Operating Procedures) — to capture institutional knowledge for the technology role at Greenmark. SOPs record who to contact for what, how recurring tasks are performed, and what not to do. They live in `sops/`, follow the same BLUF + branded PDF format as ADRs, and are written so the next person in this seat can operate without tribal knowledge.

## Context

ADRs record architectural decisions — what we decided and why. But there's a category of institutional knowledge that doesn't fit the ADR format:

- "Alex handles Sage credentials, not Michael"
- "Weekly updates follow the `/weekly-update` skill and go to the `weekly-updates/` repo"
- "All vendor accounts use `it@greenmarkwaste.com` — passwords in LastPass"
- "Don't use Knox for Greenmark — that's AIC's vault. Use Railway env vars."
- "Duo 2FA is on Daniel's phone — browser auth requires him physically present"

This knowledge currently lives scattered across CLAUDE.md, memory files, and meeting notes. If Daniel gets hit by a bus, the next technology person would have to reconstruct it from scratch. SOPs formalize this knowledge into a searchable, browsable collection.

## Decision

**Create a `sops/` directory for Standard Operating Procedures.** Each SOP is a numbered document covering one procedure or policy.

### SOP Format

```markdown
# SOP-NNN: Title

- **Effective**: YYYY-MM-DD
- **Owner**: Name / Role
- **Applies to**: Who needs to follow this

## BLUF

[2-3 sentences. What to do, when, and why it matters.]

## Procedure

[Step-by-step instructions or rules]

## Why This Exists

[Brief backstory — what went wrong or what prompted this]

## Exceptions

[When this SOP doesn't apply, or who can override it]
```

### Key differences from ADRs:

| | ADR | SOP |
|---|-----|-----|
| **Purpose** | Record a decision | Record a procedure |
| **Audience** | Future architects | Current operator |
| **Tone** | "We decided X because Y" | "Do X. Don't do Y." |
| **Changes** | Superseded by new ADR | Updated in place |
| **BLUF** | Required (ADR-2026-05) | Required |
| **Branded PDF** | Required (ADR-2026-06) | Required |
| **Location** | `decisions/` | `sops/` |

### Numbering

SOPs use sequential numbers: SOP-001, SOP-002, etc. No year prefix — SOPs are living documents updated in place, not point-in-time records.

## Rationale

| Factor | Assessment |
|--------|-----------|
| **Bus factor** | Critical institutional knowledge is currently in one person's head (and AI memory files). SOPs make it transferable. |
| **Onboarding** | A new technology hire reads the `sops/` folder and knows how to operate within a day. |
| **AI agents** | Claude sessions reference SOPs for procedural guidance. Structured format enables reliable extraction. |
| **Accountability** | "It's in the SOP" is a defensible answer. Unwritten procedures are unenforceable. |

## Options Considered

| Option | Description | Verdict |
|--------|-------------|---------|
| **A. SOPs in `sops/` (chosen)** | Dedicated directory, numbered documents, same format standards | Clean separation from decisions. Searchable. Transferable. |
| B. Wiki / Notion | External documentation platform | Not version-controlled. Not in the repo. Breaks the single-source pattern. |
| C. Expand CLAUDE.md | Add procedures to the AI instruction file | CLAUDE.md is already long. Mixing AI instructions with human procedures creates confusion. |
| D. README sections | Add procedure sections to existing READMEs | Scattered across repos. Hard to find. No consistent format. |

## Consequences

- **Positive**: Institutional knowledge is formalized, searchable, and transferable. New hires have a runbook. AI agents have procedural guidance.
- **Negative**: Another document type to maintain. Initial effort to write the first batch of SOPs.
- **Action**: Create `sops/` directory and write the first 5-6 SOPs from existing institutional knowledge.
