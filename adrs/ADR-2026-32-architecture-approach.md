# ADR-2026-32: Architecture Approach

**Status:** Accepted
**Date:** 2026-02-27
**Author:** Daniel Shanklin

## Context

Greenmark needs competitive intelligence capabilities across three dimensions: detecting new market entrants (SHIELD), identifying competitor weakness (SWORD), and predicting customer churn (RADAR). The waste management industry is data-rich with public signals but nobody in the mid-market is systematically collecting and fusing them.

## Decision

Build an autonomous intelligence engine using:

1. **AI agent fleet** — specialized agents per source class and mission layer, running on scheduled crawls
2. **Embedding-based semantic layer** — all signals vectorized for hybrid retrieval (RRF: keyword + semantic)
3. **Hierarchical memory with compression** — signals → trends → profiles → market maps, compressing over time so the system scales without drowning in raw data
4. **Entity resolution as the core fusion mechanism** — cross-source entity matching is the hardest and most valuable technical problem
5. **Probabilistic scoring with confidence intervals** — never bare numbers, always bounds and contributing signal counts
6. **Tiered alerting with fatigue prevention** — intelligence only valuable if consumed, not ignored

## Approach

**Hybrid repo** — this repo serves as both orchestration cockpit (market definitions, source catalogs, intelligence products) and codebase (agent configs, scoring models, entity resolver). Code lives alongside the intelligence it produces.

**Crawl → Embed → Fuse → Score → Alert** pipeline, with each stage independently testable and auditable.

## Consequences

- Requires maintaining 9 source class integrations across 3+ markets — significant crawl infrastructure
- Entity resolution will require ongoing tuning — expect false positives early
- Alert routing must be carefully managed to avoid fatigue with senior leadership
- The system gets more valuable over time as memory compounds — early outputs will be sparse

## Alternatives Considered

1. **Manual competitive analysis** — doesn't scale, depends on one person's attention, no memory
2. **Third-party CI platform** (Crayon, Klue, etc.) — designed for SaaS/tech companies, not waste haulers. No coverage of regulatory filings, equipment auctions, or municipal contracts
3. **Simple dashboard of public data** — misses the fusion layer, which is where all the real value lives
