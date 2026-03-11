# ADR-2026-36: RRF Hybrid Retrieval for Knowledge Search

- **Status**: Accepted
- **Date**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-16 (PostgREST gold-only exposure), cerebro-ai-services `/v1/ask` endpoint, greenmark-docs repo

## BLUF (Bottom Line Up Front)

Use Reciprocal Rank Fusion (RRF) to combine keyword search (Postgres tsvector) and semantic search (pgvector embeddings) for the Cerebro knowledge assistant. Neither signal alone is reliable at 150+ documents — keyword search misses conceptual queries, semantic search misses exact terms and ADR numbers. RRF fuses both ranked lists in a single SQL function with zero weight tuning, giving us the retrieval quality of a production RAG system without external infrastructure.

## Context

Cerebro is gaining an AI knowledge assistant (`/v1/ask` endpoint in cerebro-ai-services). Users ask questions in the dashboard chat panel, and the system searches ADRs, SOPs, and remembered knowledge to answer with citations.

The knowledge corpus currently contains 35 ADRs, 2 SOPs, and ~50 Supabase memory entries. It will grow to 150+ documents as more decisions are recorded and SOPs are written. The retrieval strategy must:

1. Handle both exact queries ("What does ADR-2026-15 say?") and conceptual queries ("What's our approach to credential security?")
2. Work within Supabase Postgres — no external vector databases or search services
3. Return results in <100ms so the full `/v1/ask` round-trip stays under 3 seconds
4. Scale gracefully from 35 to 500+ documents without re-architecture

## Decision

**Implement RRF hybrid search combining Postgres full-text search (tsvector/BM25) and vector similarity search (pgvector) in a single SQL function.**

### How RRF Works

Each retriever produces a ranked list independently. RRF combines them using rank position only — it never compares raw scores across different systems:

```
RRF_score(doc) = 1/(k + keyword_rank) + 1/(k + semantic_rank)
```

Where `k = 60` (standard constant that prevents top-ranked results from dominating).

A document ranked #1 in both lists gets the highest possible score. A document ranked #1 in keyword but absent from semantic still scores well — one weak signal doesn't kill a strong match.

### Embedding Strategy

Embed documents at two levels:

| Level | What | Why |
|-------|------|-----|
| **BLUF** | One embedding per document (~150 vectors) | Fast top-level matching. BLUFs are human-curated summaries — better than synthetic chunk summaries. |
| **Section** | One embedding per `## ` section | Precision retrieval. "What are the consequences of the vault decision?" returns just the Consequences section, not the whole ADR. |

### Implementation

Single Postgres function in Supabase:

```sql
CREATE FUNCTION hybrid_search(query_text text, query_embedding vector(1536))
RETURNS TABLE (id bigint, rrf_score float) AS $$
DECLARE
    k int := 60;
BEGIN
    RETURN QUERY
    WITH keyword_results AS (
        SELECT doc_chunks.id,
               rank() OVER (ORDER BY ts_rank_cd(fts, websearch_to_tsquery('english', query_text)) DESC) as rank
        FROM doc_chunks
        WHERE fts @@ websearch_to_tsquery('english', query_text)
        LIMIT 100
    ),
    semantic_results AS (
        SELECT doc_chunks.id,
               rank() OVER (ORDER BY embedding <=> query_embedding) as rank
        FROM doc_chunks
        ORDER BY embedding <=> query_embedding
        LIMIT 100
    )
    SELECT COALESCE(kw.id, sr.id) as id,
           (1.0 / (k + COALESCE(kw.rank, k+1))) + (1.0 / (k + COALESCE(sr.rank, k+1))) as rrf_score
    FROM keyword_results kw
    FULL OUTER JOIN semantic_results sr ON kw.id = sr.id
    ORDER BY rrf_score DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;
```

### Embedding Model

Use OpenAI `text-embedding-3-small` (1536 dimensions) via OpenRouter or direct API. Cost: ~$0.02 per million tokens — embedding the entire corpus costs less than a penny.

## Rationale

| Factor | Assessment |
|--------|------------|
| **Keyword-only fails at scale** | "credential management" won't match ADR-2026-19 titled "Supabase Vault for Credential Management" via keyword alone if the query uses different terms like "secrets handling" |
| **Semantic-only fails on exact terms** | Searching for "ADR-2026-15" or "svc_etl_runner" via embedding similarity is unreliable — embeddings compress exact strings into semantic space |
| **RRF needs no weight tuning** | Unlike linear score combination (α × keyword + β × semantic), RRF uses rank positions only. No hyperparameters to tune beyond k=60. |
| **Single database** | Both tsvector and pgvector live in Supabase Postgres. One function, one query, one round-trip. No external services. |
| **BLUFs are a natural advantage** | Most RAG systems generate synthetic summaries for each chunk. We already have human-written BLUFs on every document — higher quality, zero compute cost. |
| **Proven at scale** | RRF is used by Elasticsearch, MongoDB Atlas Search, and Pinecone for hybrid retrieval. It's not experimental. |

## Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Keyword search only | Existing `search_docs()` with term scoring | Zero new infrastructure. Works today. | Misses conceptual queries. Fragile with synonyms. Degrades past 100 docs. |
| B. Semantic search only (pgvector) | Embed all docs, cosine similarity search | Great for fuzzy/conceptual queries. | Misses exact terms, ADR numbers, acronyms. Requires embedding pipeline. |
| **C. RRF hybrid (chosen)** | Fuse keyword + semantic via Reciprocal Rank Fusion | Best of both signals. No weight tuning. Single SQL function. Proven pattern. | Requires pgvector setup + embedding pipeline. Slightly more complex than A. |
| D. Full agentic tool-use | LLM decides what to search, iterates | Best for multi-hop compound questions. | Multiple LLM calls per query (latency, cost). Overkill for single-hop policy questions. Unpredictable. |
| E. Stuff all BLUFs into context | Send every BLUF to the LLM, let it pick | Dead simple. Works at 35 docs (~3k tokens). | Doesn't scale past ~100 docs. No body text retrieval. Brute force. |

## Consequences

- **Positive**: Retrieval handles both exact and conceptual queries. Scales to 500+ docs without re-architecture. Single SQL function in Supabase — no external services. BLUFs serve as high-quality embedding targets. Foundation for future agentic upgrade (RRF becomes the retrieval tool the agent calls).
- **Negative**: Requires pgvector extension enabled in Supabase (free tier supports it). Requires an embedding pipeline to index new/updated documents. Adds ~200 lines of infrastructure code (migration, embedding script, RRF function).
- **Mitigation**: Ship keyword search immediately (works today). Layer in pgvector + RRF as the next sprint. Embedding pipeline runs on document push to greenmark-docs (GitHub webhook → re-embed changed files only).

## Phased Rollout

| Phase | What | When |
|-------|------|------|
| **Now** | Keyword search (`search_docs()`) + BLUF context stuffing | Ships with `/v1/ask` v1 |
| **Next sprint** | pgvector embeddings (BLUF + section level) + RRF fusion function | After `/v1/ask` is live and tested |
| **Future** | One-tool-call agent — LLM can re-search if first pass insufficient | When compound questions become common |

## When to Revisit

- If the corpus exceeds 1000 documents and RRF latency exceeds 100ms — consider a dedicated vector database
- If >20% of user queries are multi-hop compound questions — upgrade to agentic tool-use (LLM calls `hybrid_search` as a tool, can iterate)
- If a better fusion method emerges (e.g., learned sparse retrieval like SPLADE) — evaluate as a drop-in replacement for the keyword leg
