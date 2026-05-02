# Phase 7 — Real Investigator: Plan

## Task Groups

### 1. Database migration
1.1. Write `backend/migrations/002_citation_cache.sql` — `citation_cache` table with primary key, source, url, canonical carátula, ruling text, match score, fetched_at.
1.2. Run migration in Supabase SQL Editor (same process as 001).
1.3. Update `citation_results` verdict CHECK constraint to include `'unverifiable'`.

### 2. Dependencies
2.1. Add `selectolax` and `rapidfuzz` to `backend/requirements.txt`.
2.2. Install locally (`pip install selectolax rapidfuzz`).

### 3. Rate-limiter utility
3.1. Create `backend/app/services/rate_limiter.py` — `RateLimiter` wrapping `asyncio.Semaphore`, reads `CSJN_RPS`, `SAIJ_RPS`, `JUBA_RPS` from env (defaults: 1, 1, 0.5).
3.2. Unit-test: confirm semaphore is acquired and released correctly.

### 4. Citation cache
4.1. Create `backend/app/services/citation_cache.py` — `get_cached()` and `set_cached()` using `get_conn()`.  
4.2. Cache key: `sha256(source + "|" + normalized_caratula + "|" + tomo + "|" + pagina)`.  
4.3. TTL check at read: if `fetched_at < now() - 30 days` treat as miss.

### 5. Source adapters
5.1. Create `backend/app/services/csjn_adapter.py` — lookup by `Fallos: TOMO:PÁGINA`, parse carátula + ruling excerpt from HTML response.
5.2. Create `backend/app/services/saij_adapter.py` — search by carátula + tribunal + año; parse result list and detail page.
5.3. Create `backend/app/services/juba_adapter.py` — search by carátula + nº de causa; parse summary table.
5.4. Each adapter: returns `list[SourceResult]` (empty list on failure, never raises).
5.5. Unit-tests per adapter with fixture HTML responses (no live HTTP in tests).

### 6. Fuzzy matching upgrade
6.1. Update `backend/app/services/investigator.py` (formerly the stub) — replace `fuzzy.py` calls with `rapidfuzz.fuzz.token_sort_ratio`.
6.2. Keep `backend/app/services/fuzzy.py` intact (used in unit-test reference implementations).

### 7. Investigator orchestrator
7.1. Rewrite `backend/app/services/investigator.py`:
  - Parallel fan-out via `asyncio.gather(csjn, saij, juba)`.
  - Aggregate all `SourceResult`s, deduplicate, rank by `match_score`.
  - If 0 results → return `{found: false, unverifiable: true}`.
  - If 1 result with `match_score >= 0.85` → return directly.
  - If multiple candidates → call Haiku LLM to disambiguate; return winner.
  - Write winning result to `citation_cache`.
  - Map `SourceResult` fields onto extended public schema.
7.2. Integration test: mock all three adapters + LLM, assert correct merging and cache write.

### 8. Judge update
8.1. In `agent_judge.py` — skip semantic check when `unverifiable: true`; set `verdict = "unverifiable"` and provide a fixed Spanish justification ("No se pudo verificar la fuente; el sistema se reintentará automáticamente.").
8.2. Update `citation_results` INSERT to allow verdict `'unverifiable'` (migration 002 already widens the constraint).

### 9. API / schema
9.1. No new endpoints. Existing `POST /extract → POST /investigate → POST /judge` chain passes the extended fields transparently.
9.2. Verify FastAPI serialisation includes new optional fields without breaking clients that don't read them.

### 10. Frontend
10.1. Add grey "No verificable" pill to `CitationCard` for `verdict === "unverifiable"` or `unverifiable === true`.
10.2. When `canonical_caratula` differs from `case_name`, render an inline correction suggestion (yellow info box beneath the card header).
10.3. When `source_url` is present, render it as a clickable link on the card.
10.4. Vitest: snapshot test for each new UI state (unverifiable pill, correction suggestion, source link).

### 11. End-to-end smoke test
11.1. Upload a brief containing one known CSJN citation and one fabricated citation.
11.2. Confirm: real citation shows source badge + source URL; fabricated citation shows `danger`; if sources are unreachable stub returns `unverifiable` pill (simulate by disabling network).
11.3. Save report; verify `citation_results` rows include `source` and `source_url` values.
