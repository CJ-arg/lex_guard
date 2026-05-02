# Phase 7 — Real Investigator: Requirements

## Goal

Replace the hardcoded stub with a real source-adapter layer that queries three official Argentine jurisprudence repositories in parallel. The Investigator LLM (Haiku) disambiguates multiple candidates from adapters. Results are cached in Supabase to avoid hammering sources. When all sources fail, the citation is flagged `unverifiable` — not `danger`.

## Scope

### In scope
- Three source adapters: **CSJN**, **SAIJ**, **JUBA** — implemented in parallel via `asyncio.gather`
- `SourceResult` internal contract (does not change the public Phase 4 `{found, ruling_text}` schema)
- Public Phase 4 schema **extended** with optional fields: `source`, `source_url`, `match_score`, `canonical_caratula` — backward compatible
- `rapidfuzz` replaces the pure-Python `fuzzy.py` for production matching (Phase 4 helper kept for unit-test reference)
- `asyncio.Semaphore`-based rate limiter per source (CSJN: 1 req/s, SAIJ: 1 req/s, JUBA: 1 req/2s), configured via env vars
- Supabase `citation_cache` table (30-day TTL) — new SQL migration `002_citation_cache.sql`
- Haiku LLM call when adapter returns multiple candidates — selects best match
- `unverifiable` verdict when all sources fail — grey "No verificable" badge in UI
- Inline correction suggestion when `canonical_caratula` differs from the original `case_name`
- Canonical source URL shown as a link on the citation card when available
- Judge updated to handle `unverifiable` citations (skip semantic check, set verdict directly)
- `citation_results` verdict constraint updated to include `unverifiable`

### Out of scope
- PJN cámaras nacionales beyond SAIJ index
- Other provincial cortes
- Playwright/Selenium (all sources serve server-rendered HTML)
- Background eviction job (TTL checked synchronously at read)

## Sources of Truth

| Adapter | Source | Strategy |
|---|---|---|
| `csjn_adapter.py` | CSJN Secretaría de Jurisprudencia | Direct lookup by `Fallos: TOMO:PÁGINA`; HTML scrape of carátula, fecha, voces |
| `saij_adapter.py` | SAIJ (saij.gob.ar) | Search by carátula + tribunal + año; HTML scrape of result list and detail page |
| `juba_adapter.py` | JUBA (juba.scba.gov.ar) | Search by carátula + nº de causa; HTML scrape of summary table |

## Internal Contract

```python
class SourceResult(TypedDict):
    found: bool
    canonical_caratula: str | None
    ruling_text: str | None
    source: Literal["CSJN", "SAIJ", "JUBA"]
    source_url: str | None
    match_score: float  # 0.0–1.0
```

## Public Citation Schema (extended, backward compatible)

```json
{
  "claim": "string",
  "case_name": "string",
  "court": "string",
  "year_tomo_folio": "string | null",
  "found": true,
  "ruling_text": "string",
  "source": "CSJN | SAIJ | JUBA",
  "source_url": "string | null",
  "match_score": 0.95,
  "canonical_caratula": "string | null",
  "unverifiable": false
}
```

For all-sources-fail:
```json
{ ..., "found": false, "unverifiable": true }
```

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Adapters | All three (CSJN + SAIJ + JUBA) | Full coverage; fan-out is cheap with asyncio.gather |
| Fuzzy matching | `rapidfuzz` | C-extension, ~5× faster than pure Python; replaces Phase 4 helper in production |
| Rate limiting | asyncio.Semaphore per source | In-process, no extra infra; tunable via env vars |
| Cache | Supabase citation_cache, 30-day TTL | Prevents source hammering; jurisprudence is effectively immutable |
| LLM disambiguation | Haiku when multiple candidates | Adapter returns ranked list; LLM picks most likely; no LLM in single-exact-match path |
| Unverifiable | Grey pill, skip Judge | Neutral signal — sources down ≠ citation wrong |
| Near-match display | Inline correction suggestion | Attorney must see and verify the correction; silent auto-correct hides important information |
| Dependency | `httpx` (already in requirements), `selectolax`, `rapidfuzz` | selectolax: fast C-based HTML parser; no Chromium needed |
