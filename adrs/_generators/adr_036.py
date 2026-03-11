#!/usr/bin/env python3
"""ADR-2026-36 — RRF Hybrid Retrieval for Knowledge Search"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-36-rrf-hybrid-retrieval-for-knowledge-search.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-36", "RRF Hybrid Retrieval for Knowledge Search"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Accepted  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "Use Reciprocal Rank Fusion (RRF) to combine keyword search (Postgres tsvector) and "
        "semantic search (pgvector embeddings) for the Cerebro knowledge assistant. Neither signal "
        "alone is reliable at 150+ documents — keyword search misses conceptual queries, semantic "
        "search misses exact terms and ADR numbers. RRF fuses both ranked lists in a single SQL "
        "function with zero weight tuning."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Implement RRF hybrid search combining Postgres full-text search "
                           "(tsvector/BM25) and vector similarity search (pgvector) in a single SQL function. "
                           "k = 60 (standard constant). No weight tuning needed."))
    story.append(Spacer(1, 8))

    # RRF Formula
    story.append(p("How RRF Works", H2))
    story.append(p(
        "Each retriever produces a ranked list independently. RRF combines them using rank position "
        "only — it never compares raw scores across different systems:"))
    story.append(Spacer(1, 4))
    story.append(p("<font face='Courier' size='10'>RRF_score(doc) = 1/(k + keyword_rank) + 1/(k + semantic_rank)</font>"))
    story.append(Spacer(1, 4))
    story.append(p(
        "A document ranked #1 in both lists gets the highest possible score. A document ranked #1 in "
        "keyword but absent from semantic still scores well — one weak signal doesn't kill a strong match."))
    story.append(Spacer(1, 6))

    # Embedding Strategy
    story.append(p("Embedding Strategy", H2))
    story.append(tbl(["Level", "What", "Why"], [
        [p("<b>BLUF</b>", CELL),
         p("One embedding per document (~150 vectors)", CELL),
         p("Fast top-level matching. BLUFs are human-curated summaries — better than synthetic chunk summaries.", CELL)],
        [p("<b>Section</b>", CELL),
         p("One embedding per ## section", CELL),
         p("Precision retrieval. 'What are the consequences of the vault decision?' returns just that section.", CELL)],
    ], [USABLE * 0.12, USABLE * 0.33, USABLE * 0.55]))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Model:</b> OpenAI text-embedding-3-small (1536 dimensions). "
        "Cost: ~$0.02 per million tokens — embedding the entire corpus costs less than a penny."))
    story.append(hr())

    # Rationale
    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Keyword-only fails</b>", CELL),
         p("'credential management' won't match ADR-2026-19 if the query uses 'secrets handling'.", CELL)],
        [p("<b>Semantic-only fails</b>", CELL),
         p("Searching for 'ADR-2026-15' via embedding similarity is unreliable — embeddings compress exact strings.", CELL)],
        [p("<b>No weight tuning</b>", CELL),
         p("Unlike linear combination, RRF uses rank positions only. No hyperparameters beyond k=60.", CELL)],
        [p("<b>Single database</b>", CELL),
         p("Both tsvector and pgvector live in Supabase Postgres. One function, one query, one round-trip.", CELL)],
        [p("<b>BLUFs are an advantage</b>", CELL),
         p("Most RAG systems generate synthetic summaries. We already have human-written BLUFs on every doc.", CELL)],
        [p("<b>Proven at scale</b>", CELL),
         p("RRF is used by Elasticsearch, MongoDB Atlas Search, and Pinecone. Not experimental.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(hr())

    # Options Considered
    story.append(p("Options Considered", H2))
    story.append(tbl(["Option", "Verdict"], [
        [p("<b>A. Keyword only</b>", CELL),
         p("Works today, zero infra. Misses conceptual queries. Degrades past 100 docs.", CELL)],
        [p("<b>B. Semantic only</b>", CELL),
         p("Great for fuzzy queries. Misses exact terms, ADR numbers, acronyms.", CELL)],
        [p("<b>C. RRF hybrid ✓</b>", CELL),
         p("Best of both. No weight tuning. Single SQL function. Proven pattern.", CELL)],
        [p("<b>D. Agentic tool-use</b>", CELL),
         p("Best for multi-hop. Multiple LLM calls per query — overkill for single-hop policy questions.", CELL)],
        [p("<b>E. BLUF context stuffing</b>", CELL),
         p("Dead simple at 35 docs. Doesn't scale past ~100. No body text retrieval.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(hr())

    # Phased Rollout
    story.append(p("Phased Rollout", H2))
    story.append(tbl(["Phase", "What", "When"], [
        [p("<b>Now</b>", CELL),
         p("Keyword search + BLUF context stuffing", CELL),
         p("Ships with /v1/ask v1", CELL)],
        [p("<b>Next sprint</b>", CELL),
         p("pgvector embeddings (BLUF + section) + RRF fusion function", CELL),
         p("After /v1/ask is live", CELL)],
        [p("<b>Future</b>", CELL),
         p("One-tool-call agent — LLM can re-search if first pass insufficient", CELL),
         p("When compound questions become common", CELL)],
    ], [USABLE * 0.15, USABLE * 0.55, USABLE * 0.30]))
    story.append(Spacer(1, 6))

    # Consequences
    story.append(p("Consequences", H2))
    story.append(p(
        "<b>Positive:</b> Retrieval handles both exact and conceptual queries. Scales to 500+ docs "
        "without re-architecture. Single SQL function in Supabase. BLUFs serve as high-quality "
        "embedding targets. Foundation for future agentic upgrade."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Negative:</b> Requires pgvector extension in Supabase (free tier supports it). "
        "Requires an embedding pipeline to index new/updated documents. Adds ~200 lines of infra code."))
    story.append(Spacer(1, 4))
    story.append(p(
        "<b>Mitigation:</b> Ship keyword search immediately (works today). Layer in pgvector + RRF "
        "as the next sprint. Embedding pipeline runs on document push to greenmark-docs."))
    story.append(Spacer(1, 6))

    # When to Revisit
    story.append(p("When to Revisit", H2))
    story.append(p("• If corpus exceeds 1000 docs and RRF latency exceeds 100ms — consider a dedicated vector database"))
    story.append(p("• If >20% of queries are multi-hop compound questions — upgrade to agentic tool-use"))
    story.append(p("• If better fusion emerges (e.g., SPLADE) — evaluate as drop-in keyword replacement"))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-36: RRF Hybrid Retrieval for Knowledge Search", content)
