# ADR-2026-34: claude -p Only — No Direct Anthropic API

**Status:** Accepted (Hard Constraint)
**Date:** 2026-02-27
**Author:** Daniel Shanklin

## Context

The CI engine needs LLM capabilities for crawl agents — reading public data sources, extracting structured signals, and generating intelligence products. The natural approach for a Python app would be to use the `anthropic` SDK directly.

## Decision

All LLM execution goes through `claude -p` (Claude CLI piped mode). Never import the `anthropic` SDK. Never call the API directly. This is a hard constraint — it stands even when debugging timeouts or failures.

```python
# YES — this is how we do it
result = subprocess.run(
    ["claude", "-p", prompt],
    capture_output=True, text=True, timeout=300,
)

# NO — never do this
# from anthropic import Anthropic
# client = Anthropic()
# response = client.messages.create(...)
```

## Why

1. **`claude -p` is a full agent** — it has tool use, file access, and context that a bare API call doesn't. Crawl agents need to read web pages, follow links, and extract structured data. The CLI handles this end-to-end.
2. **No API key management** — `claude -p` uses the authenticated CLI session. No `ANTHROPIC_API_KEY` to rotate, store in Knox, or accidentally leak.
3. **Consistent with AIC org pattern** — all AIC services use `claude -p` for LLM execution. One pattern, one debugging playbook.
4. **Cost isolation** — CLI usage is tracked under the org's Claude subscription, not per-API-key billing.
5. **Structured output parsing is already built** — `runner.py` has a `parse_job_output()` function that handles JSON extraction from `claude -p` responses with fallback strategies.

## What This Means in Practice

- **Timeouts** — `claude -p` can hang on complex prompts. Debug the prompt, reduce scope, or increase timeout. Do not switch to API as a workaround.
- **Rate limits** — source ToS rate limits (~10 jobs/hour) are the bottleneck, not Claude throughput.
- **Testing** — mock `subprocess.run` in tests. No API mocking needed.
- **Error handling** — `FileNotFoundError` (CLI not installed), `TimeoutExpired` (prompt too complex), non-zero exit code (execution failed). All handled in `runner.py`.

## Consequences

- Adds a subprocess per job (acceptable — jobs are already sequential)
- Requires `claude` CLI installed on the deployment host (Railway Dockerfile includes it)
- Output parsing is text-based, not typed — `parse_job_output()` handles this with JSON block extraction
- Cannot use streaming responses (acceptable — jobs complete before result is needed)
