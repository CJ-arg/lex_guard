# Phase 7 — Real Investigator: Validation

## Pre-implementation (before writing any code)
- [ ] `002_citation_cache.sql` migration run successfully in Supabase SQL Editor
- [ ] `citation_cache` table visible in Supabase Table Editor
- [ ] `citation_results` verdict constraint updated to include `'unverifiable'`
- [ ] `selectolax` and `rapidfuzz` installed locally and importable

## Unit tests (run via `pytest backend/`)

### Rate limiter
- [ ] `test_rate_limiter.py` — semaphore limits concurrent requests per source
- [ ] Env var overrides (`CSJN_RPS`, `SAIJ_RPS`, `JUBA_RPS`) are respected

### Citation cache
- [ ] Cache hit returns stored `SourceResult` without adapter call
- [ ] Cache miss triggers adapter call and writes result
- [ ] Entry older than 30 days is treated as a miss

### Adapters (fixture HTML, no live HTTP)
- [ ] `csjn_adapter.py` — parses carátula and ruling excerpt from fixture HTML
- [ ] `csjn_adapter.py` — returns empty list on HTTP error without raising
- [ ] `saij_adapter.py` — parses result list and detail page from fixture HTML
- [ ] `saij_adapter.py` — returns empty list on HTTP error without raising
- [ ] `juba_adapter.py` — parses summary table from fixture HTML
- [ ] `juba_adapter.py` — returns empty list on HTTP error without raising

### Investigator orchestrator
- [ ] 0 results from all adapters → `{found: false, unverifiable: true}`
- [ ] 1 result with score ≥ 0.85 → returned directly, no LLM call
- [ ] Multiple candidates → Haiku called, winner returned
- [ ] Winning result written to `citation_cache`
- [ ] Extended public schema fields (`source`, `source_url`, `match_score`, `canonical_caratula`) present in output

### Judge
- [ ] `unverifiable: true` input → `verdict = "unverifiable"`, semantic LLM call skipped
- [ ] All other citation paths unchanged

## Frontend tests (run via `npm run test:run` in `frontend/`)
- [ ] `CitationCard` renders grey "No verificable" pill when `verdict === "unverifiable"`
- [ ] Inline correction suggestion renders when `canonical_caratula !== case_name`
- [ ] Source URL link renders when `source_url` is present
- [ ] Cards without new fields render identically to Phase 6 (no regression)

## Local integration (manual, with live network)
- [ ] Upload brief with a known real CSJN citation (e.g. `Fallos: 330:4921`):
  - Card shows `CSJN` source badge
  - Card shows source URL as a clickable link
  - `match_score` ≥ 0.85
- [ ] Upload brief with a fabricated citation:
  - All three adapters return empty
  - Verdict is `danger` (not found in any source), not `unverifiable`
- [ ] Simulate all sources unreachable (kill network / return 502 from mocked adapters):
  - Verdict is `unverifiable`
  - Grey "No verificable" pill shown in UI
  - No `danger` verdict emitted
- [ ] Upload brief with a near-match citation (typo in carátula):
  - Inline correction suggestion shown with `canonical_caratula`
  - `match_score` between 0.70 and 0.85
- [ ] Save report with unverifiable citation → `citation_results` row has `verdict = 'unverifiable'`
- [ ] `GET /sessions/{id}` returns `unverifiable` verdict correctly in response body
- [ ] Second request for same citation hits cache (check Supabase `citation_cache` table — no new row, same `fetched_at`)

## Deployment validation (before merging to main)
- [ ] `CSJN_RPS`, `SAIJ_RPS`, `JUBA_RPS` env vars set in Render (even if default values)
- [ ] Render redeploy succeeds with new dependencies
- [ ] Live audit through production Vercel URL shows source badge and source URL on a real citation
- [ ] Supabase `citation_cache` table receives rows after a production audit

## Definition of Done

All checkboxes ticked. An attorney uploads a real brief in production, receives verdicts with source badges and canonical URLs for verified citations, a grey "No verificable" badge for any unverifiable ones, and inline correction suggestions wherever the carátula differs from the canonical form. A second audit of the same brief is served from cache (no adapter calls fired).
