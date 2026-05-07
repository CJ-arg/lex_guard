# Roadmap

Phases are intentionally focused — each one is a shippable slice of work, independently reviewable and testable.

---

## Phase 1 — Hello LexGuard ✅
- FastAPI app running locally and on Render, single `GET /health` route returning `{ "status": "LexGuard is live" }`
- Next.js app running locally and on Vercel, fetches `/health` and renders the response
- Confirms split deployment pipeline: Render ↔ Vercel communication works end-to-end
- Environment variable wiring in place (API base URL configurable per environment)

## Phase 2 — Document Ingestion ✅
- File upload UI in Next.js (drag-and-drop or file picker, PDF and DOCX only)
- `POST /upload` endpoint in FastAPI receives the file
- PyMuPDF extracts text from PDF; python-docx extracts text from DOCX
- Extracted plain text returned to frontend and displayed — no agents yet
- Basic validation: file type check, size limit

## Phase 3 — Extractor Agent ✅
- Wire Claude Haiku as the Extractor agent
- Input: extracted plain text from Phase 2
- Output: structured list of citation objects — attorney claim, case name, court, year, tomo/folio
- Display extracted citations as a simple list in the UI
- Edge case: multiple citations in a single paragraph (chained citations) handled here

## Phase 4 — Investigator Agent (Stubbed) ✅
- Add the Investigator agent with a deterministic stub: returns `found: true` with placeholder ruling text for known test cases, `found: false` otherwise
- Define the full data contract the real Investigator will honor (input/output schema locked here)
- Pipeline runs: Extractor → Investigator stub → JSON result displayed per citation
- Fuzzy-match helper introduced (Levenshtein on case name + year) — ready for Phase 7

## Phase 5 — Judge Agent & Traffic-Light Dashboard ✅
- Wire Claude Sonnet 4.6 as the Judge agent
- Full pipeline operational: Extractor → Investigator (stub) → Judge
- Judge returns verdict (`approved` / `warning` / `danger`) + plain-language justification per citation
- Dashboard displays the original document alongside the verdict panel: green / yellow / red per citation with justification text
- This is the first end-to-end demo of the product's core value

## Phase 6 — Supabase Persistence ✅
- Supabase Postgres schema: `sessions` table (document name, timestamp, user note) + `citation_results` table (verdict, justification, linked to session)
- `POST /sessions` saves a completed audit to the database
- "Save report" button in the dashboard triggers the save
- `GET /sessions/:id` retrieves a saved report — permalink URL for sharing within the firm

## Phase 7 — Real Investigator
- Replace the stub with a real source-adapter layer querying three official repositories: **CSJN** (canonical lookup by `Fallos: TOMO:PÁGINA`), **SAIJ** (national + provincial jurisprudence), and **JUBA** (Buenos Aires jurisprudence)
- Adapter contract internal-only (`SourceResult`); public Phase 4 contract `{found, ruling_text}` extended with **optional** fields `source`, `source_url`, `match_score`, `canonical_caratula`, `source_routing` — backward compatible with Phase 5 Judge and Phase 4 UI badges
- **Deterministic Router** (`backend/app/services/router.py`) maps each citation to the source that natively covers its court, based on the `court` field and the shape of `year_tomo_folio`. The Router returns an ordered dispatch list `[primary, secondary?]`. Fan-out to all three adapters is reserved as fallback when the court is empty, ambiguous, or unrecognizable
- Investigator orchestrates: calls primary; if `found: false`, tries secondary; if both fail (or fan-out fallback is in effect), runs the remaining adapters via `asyncio.gather`. Per-source rate limiter via `asyncio.Semaphore`; Supabase `citation_cache` for repeated lookups (30-day TTL)
- Routing rules (initial, lives in `router.py` as a list of `(regex, primary, secondary)` tuples):
  - `Fallos: T:P` format detected → primary CSJN, secondary SAIJ
  - `court` matches `CSJN` / `Corte Suprema` / `C.S.J.N.` → primary CSJN, secondary SAIJ
  - `court` matches `SCBA` / `Suprema Corte de Buenos Aires` → primary JUBA, secondary SAIJ
  - `court` matches federal/national chambers (`CNCiv`, `CNCom`, `CNFed`, etc.) → primary SAIJ, no secondary
  - `court` matches Buenos Aires provincial chambers → primary JUBA, secondary SAIJ
  - `court` matches other provincial supreme courts → primary SAIJ, no secondary
  - `court` empty / ambiguous → fan-out to CSJN + SAIJ + JUBA
- Fuzzy matcher upgraded from pure-Python Levenshtein (Phase 4 reference impl) to `rapidfuzz` for production; typos and transposed carátulas surface as correction suggestions, not false `danger` verdicts
- Attorney sees, alongside each verdict, which source was the primary, whether the secondary was needed, and the canonical source URL — communicating the level of confidence honestly (a result confirmed by the canonical source reads as stronger than one confirmed only by the cross-validator)
- Graceful degradation: if all consulted sources fail (network error, source down, captcha), verdict is flagged as `unverifiable` (not `danger`); HTTP 502 from a single adapter does not poison the verdict for the citation if other adapters succeed
- Out of scope for Phase 7: PJN cámaras nacionales beyond what SAIJ already indexes, other provincial cortes, doctrine, and international citations (CIDH / TJUE — flagged as `unverifiable_out_of_scope`). These are Phase 9+ work

## Phase 8 — Hardening & Edge Cases
- Large document support: chunk briefs over a configurable page threshold before passing to the Extractor
- Error pages (upload failure, pipeline timeout, Supabase unreachable)
- Input sanitization on all file uploads and form fields
- Responsive layout audit across the dashboard (mobile-first, keyboard navigable)
- Basic request logging middleware in FastAPI

---

Later phases (not yet planned): user authentication, multi-user firm accounts, batch processing of multiple briefs, export to PDF report.