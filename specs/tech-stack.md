# Tech Stack

LexGuard is a split-deployment MVP: a Python/FastAPI backend running the agent pipeline, and a Next.js frontend delivering the audit dashboard. Both layers communicate over a REST API; the browser receives a fully interactive client-side UI backed by server-rendered data.

## Core

| Layer | Choice | Rationale |
|---|---|---|
| Backend language | Python | Natural fit for AI/ML tooling, document parsing libraries, and the Anthropic SDK |
| Backend framework | **FastAPI** | Async-first, automatic OpenAPI docs, type-safe with Pydantic — ideal for an agent orchestration API |
| Frontend language | TypeScript | Type safety end-to-end; catches integration errors between the API contract and the UI at compile time |
| Frontend framework | **Next.js** | React-based, supports server components and API routes; native Vercel deployment |
| AI agents | **Anthropic SDK (Python)** | Powers the three-agent pipeline (Extractor, Investigator, Judge) |
| Database | **Supabase (Postgres)** | Hosted free tier; persists audit sessions and citation verdicts; works across both Render and Vercel |
| Backend hosting | **Render** | Free-tier Python web service; handles long-running agent chains without serverless timeout constraints |
| Frontend hosting | **Vercel** | Native Next.js platform; zero-config deployment on push |

## Agent Model Strategy

The three internal agents have different complexity profiles; model selection reflects that:

| Agent | Model | Rationale |
|---|---|---|
| Extractor | `claude-haiku-4-5` | Structured extraction task — fast and cheap; the output is metadata, not judgment |
| Investigator | `claude-haiku-4-5` | Search and match logic; speed matters here as it runs once per citation |
| Judge | `claude-sonnet-4-6` | Semantic reasoning is the core value of the product — this agent justifies the premium |

## Data

- **Supabase (Postgres)** for all persistent storage: audit sessions, citation results, and verdict justifications
- Schema managed via plain SQL migration files; no ORM for MVP
- Each audit session is stored with its full verdict trail to satisfy the traceability requirement from the spec

## Document Parsing

- **PyMuPDF (`fitz`)** — PDF text extraction; handles scanned layout and multi-column formats
- **python-docx** — DOCX ingestion
- Large documents (100+ pages) are chunked before being passed to the Extractor agent to stay within context limits

## Source Adapters (Phase 7+)

The real Investigator agent does not call external sources directly. It dispatches via a **deterministic Router** to a **source adapter layer**, with one adapter per official repository. Each adapter exposes the same internal contract so the Investigator can consolidate results without per-source branching logic.

| Adapter | Source | Strategy |
|---|---|---|
| `csjn_adapter.py` | CSJN Secretaría de Jurisprudencia | Direct lookup by `Fallos: TOMO:PÁGINA` (URL-addressable); HTML scrape of carátula, fecha, voces, jueces |
| `saij_adapter.py` | SAIJ | Search by carátula + tribunal + año on `/buscador/jurisprudencia-nacional`; HTML scrape of result list and detail page |
| `juba_adapter.py` | JUBA | Search by carátula + nº de causa on `/busquedas.aspx`; HTML scrape of summary table |

### Routing layer (deterministic)

Before any adapter is called, the Router (`backend/app/services/router.py`) decides which source(s) the citation should be checked against, based on the `court` field extracted by the Extractor and on the structural shape of `year_tomo_folio`.

- The Router is pure regex + lookup tables; no LLM, no I/O. Fast (microseconds per citation), free, fully testable.
- Its output is an ordered list `[primary, secondary?]` of source keys.
- The Investigator then dispatches in order: it calls the **primary**; if `found: false`, it tries the **secondary** (cross-validator); if both fail it stops — a `not found` from the natural source is already strongly informative.
- If the `court` field is missing or unrecognizable, the Router returns the full list `[CSJN, SAIJ, JUBA]` (fan-out preserved as fallback).

#### Routing rules (initial)

| Signal in citation | Primary | Secondary |
|---|---|---|
| `Fallos: T:P` format detected in `year_tomo_folio` | CSJN | SAIJ |
| `court` matches CSJN patterns (`CSJN`, `Corte Suprema`, `C.S.J.N.`) | CSJN | SAIJ |
| `court` matches SCBA patterns (`SCBA`, `Suprema Corte de Buenos Aires`) | JUBA | SAIJ |
| `court` matches federal / national chamber patterns (`CNCiv`, `CNCom`, `CNFed`, `CNTrab`, `CNCAF`, `CNCrim`) | SAIJ | — |
| `court` matches Buenos Aires provincial chamber patterns (`Cám. Apel.` + bonaerense locality) | JUBA | SAIJ |
| `court` matches other provincial supreme courts | SAIJ | — |
| `court` empty / ambiguous | (fan-out: CSJN + SAIJ + JUBA) | — |

The rule table lives as a list of `(regex, primary, secondary)` tuples — extending it later (e.g., to add JUSCABA when its adapter ships) is a one-line change.

### Adapter contract (internal — does not affect the public Phase 4 schema)

```python
class SourceResult(TypedDict):
    found: bool
    canonical_caratula: str | None
    ruling_text: str | None      # excerpt sufficient for Judge to compare
    source: Literal["CSJN", "SAIJ", "JUBA"]
    source_url: str | None
    match_score: float           # 0.0–1.0 (1.0 = exact, lower = fuzzy)
```

The Investigator merges `SourceResult`s into the **public** Phase 4 contract `{found, ruling_text}`. New fields (`source`, `source_url`, `match_score`, `canonical_caratula`, `source_routing`) are added as **optional** properties on the returned citation — the Judge agent and the frontend Phase 4 badges keep working unchanged because they only read fields they know about.

The `source_routing` field captures what the Router decided and what actually happened, for transparent reporting in the UI:

```python
class SourceRouting(TypedDict):
    primary_attempted: str            # e.g. "CSJN"
    primary_result: Literal["found", "not_found", "error"]
    secondary_attempted: str | None   # e.g. "SAIJ" or None
    secondary_result: Literal["found", "not_found", "error"] | None
    fallback_used: bool               # True when fan-out kicked in
```

### Adapter dependencies

| Library | Purpose | Why |
|---|---|---|
| `httpx` | Async HTTP client for adapter requests | Already a FastAPI ecosystem default; works with `asyncio.gather` to fan out source queries when needed |
| `selectolax` | Fast HTML parser | C-based, ~5× faster than BeautifulSoup; small footprint stays within Render free-tier memory |
| `rapidfuzz` | Fuzzy string matching | C-extension implementation of Levenshtein + token sort ratio; replaces the pure-Python `fuzzy.py` helper from Phase 4 (which stays for unit-test reference) |

> **Why not Playwright/Selenium?** Render's free tier does not allocate enough disk/RAM to run a headless Chromium reliably. All three sources serve **server-rendered HTML** for the URLs we need; no JavaScript execution is required for the MVP. If a target page later moves to client-side rendering, that adapter is upgraded in isolation — Playwright stays out of the core service.

### Caching strategy

External sources are **rate-limited**. Hitting them on every audit is wasteful and rude. The Investigator caches every successful lookup in a new Supabase table:

```sql
create table citation_cache (
  cache_key       text primary key,           -- normalized hash of (source, caratula, tomo, pagina)
  source          text not null,              -- 'CSJN' | 'SAIJ' | 'JUBA'
  source_url      text,
  canonical_caratula text,
  ruling_text     text,
  match_score     real not null,
  fetched_at      timestamptz not null default now()
);
create index citation_cache_fetched_at_idx on citation_cache (fetched_at);
```

- TTL: 30 days (jurisprudence is effectively immutable; only the index changes)
- Eviction: time-based at read; no background job needed (synchronous-only constraint preserved)
- Miss → adapter call → cache write → return

**Investigator scope clarification (Phase 7):** the Investigator agent's role is to *interpret* search results coming from the adapter layer, not to scrape directly. The LLM call disambiguates fuzzy matches and selects the most likely candidate when an adapter returns several. Adapters and the Router are deterministic (no LLM in the hot path).

### Rate limiting

Per-source token bucket inside the FastAPI process (in-memory `asyncio.Semaphore`-based). Defaults:

- CSJN: 1 req/sec, burst 3
- SAIJ: 1 req/sec, burst 3
- JUBA: 1 req/2 sec, burst 2

Configured via env vars (`CSJN_RPS`, `SAIJ_RPS`, `JUBA_RPS`) so the values can be tuned in Render without redeploying code changes.

## Testing

- **pytest** — backend unit and integration tests for agent logic and API routes
- **Vitest** — frontend component and utility tests; configured in `frontend/vitest.config.ts` with jsdom environment and `@testing-library/react`
- Frontend test setup file lives at `frontend/src/test/setup.ts` (imports `@testing-library/jest-dom` matchers)
- Tests live in a `tests/` directory at each layer
- Run via `pytest` (backend) and `npm test` (frontend, watch mode) or `npm run test:run` (frontend, CI single-pass); both must pass before merge

## Tooling

- `uvicorn` for local FastAPI development
- `ruff` for Python linting and formatting
- `eslint` + `prettier` for TypeScript/Next.js
- `python-dotenv` for local environment variable management

## What We Are Not Using

- No Docker — Render handles the Python environment directly; not needed for MVP
- No ORM — raw SQL via `supabase-py` is sufficient at this scale
- No message queue — agent calls are synchronous in the MVP; async job queue is a post-MVP concern
- No GitHub Pages — static hosting cannot serve the FastAPI backend or dynamic dashboard
- No headless browser (Playwright/Selenium) — official sources serve server-rendered HTML for the endpoints we use; adding Chromium would exceed Render's free-tier resources
- No background job queue for scraping — adapter calls are inline within the synchronous request lifecycle, with `asyncio.gather` providing parallelism only when the Router falls back to fan-out, and the Supabase cache absorbing repeated lookups