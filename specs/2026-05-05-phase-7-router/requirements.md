# Phase 7 — Deterministic Router: Requirements

## Context

Phase 7 shipped a real investigator that fans out to CSJN, SAIJ, and JUBA in parallel for every citation. The updated spec adds a deterministic Router that routes each citation to the source that natively covers its court — avoiding wasted calls and making the confidence level explicit to the attorney.

This spec completes Phase 7. It lives on the `phase-7/router` branch, based on `phase-7/real-investigator`.

## Scope

### In scope

- `backend/app/services/router.py` — pure regex + lookup table; no LLM, no I/O
- Updated `investigator.py` — sequential dispatch (primary → secondary if needed → fan-out fallback)
- `SourceRouting` TypedDict added to the response schema
- `source_routing` persisted in `citation_results` table (new nullable JSONB column)
- `CitationCard.tsx` shows a one-line routing trace ("Verificado vía CSJN (primaria)")

### Out of scope

- JUBA WebForms implementation (still disabled; routed away from until fixed)
- International citations (CIDH / TJUE) — flagged as `unverifiable` by existing logic
- PJN cámaras beyond what SAIJ already indexes

## Routing rules

Implemented as a list of `(pattern, primary, secondary)` tuples in `router.py`. First match wins.

| Signal | Primary | Secondary | Notes |
|---|---|---|---|
| `year_tomo_folio` matches `Fallos: T:P` | CSJN | SAIJ | |
| `court` matches CSJN patterns | CSJN | SAIJ | `CSJN`, `Corte Suprema`, `C.S.J.N.` |
| `court` matches SCBA patterns | SAIJ | — | JUBA disabled; intended primary is JUBA once fixed |
| `court` matches federal/national chambers | SAIJ | — | `CNCiv`, `CNCom`, `CNFed`, `CNTrab`, `CNCAF`, `CNCrim` |
| `court` matches BA provincial chambers | SAIJ | — | JUBA disabled; `Cám. Apel.` + bonaerense locality |
| `court` matches other provincial supreme courts | SAIJ | — | |
| `court` empty / ambiguous / unrecognised | fan-out | — | CSJN + SAIJ + JUBA (JUBA returns [] while disabled) |

`router.py` also exposes `juba_disabled: bool = True` so the routing rationale is explicit and easy to flip once JUBA is fixed.

## Dispatch logic (investigator.py)

1. Call `router.route(citation)` → `(primary, secondary | None, fallback: bool)`
2. If `fallback=True`: `asyncio.gather` on all sources (existing behaviour)
3. If `fallback=False`:
   a. Call primary adapter
   b. If result passes `MIN_SCORE` → done
   c. Else call secondary adapter (if any)
   d. If still no result → `unverifiable`
4. At each step, record outcome in `SourceRouting`

## SourceRouting schema

```python
class SourceRouting(TypedDict):
    primary_attempted: str                                      # "CSJN"
    primary_result: Literal["found", "not_found", "error"]
    secondary_attempted: str | None
    secondary_result: Literal["found", "not_found", "error"] | None
    fallback_used: bool
```

## UI

`CitationCard` shows a single line below tribunal/reference:

- `"Verificado vía CSJN (primaria)"` — primary found
- `"CSJN sin resultado → confirmado por SAIJ"` — secondary found
- `"Búsqueda en todas las fuentes"` — fan-out used

## Decisions

| Decision | Rationale |
|---|---|
| SCBA/BA routes to SAIJ while JUBA disabled | Avoids wasted call; `juba_disabled` flag makes the intent clear |
| Sequential not parallel for routed citations | Avoids hitting three sources when one suffices; reduces load on government servers |
| Fan-out preserved for ambiguous court | Safe fallback; no information lost |
| `source_routing` as JSONB in Postgres | Flexible; no migration needed if fields are added later |
