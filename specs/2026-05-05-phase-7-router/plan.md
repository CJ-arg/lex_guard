# Phase 7 Router — Implementation Plan

## Group 1 — Router module

1. Create `backend/app/services/router.py`
   - `SourceKey = Literal["CSJN", "SAIJ", "JUBA"]`
   - `RouteDecision(TypedDict)`: `primary`, `secondary | None`, `fallback: bool`
   - `RULES`: list of `(compiled_regex, primary, secondary | None)` covering all patterns from requirements
   - `route(citation: dict) -> RouteDecision` — iterate rules, return first match; default fan-out
   - `JUBA_DISABLED = True` constant; SCBA/BA rules substitute SAIJ while True
2. Write `backend/tests/test_router.py` covering every rule row and the fan-out fallback

## Group 2 — Investigator sequential dispatch

3. Update `backend/app/services/investigator.py`
   - Import `router.route`
   - Replace the parallel `asyncio.gather` with sequential dispatch:
     - `fallback=True` → existing `asyncio.gather` path
     - `fallback=False` → call primary; if no result, call secondary; record each outcome
   - Build `SourceRouting` dict at each step
   - Pass `source_routing` through `_build_result` and into the returned citation dict
4. Update `backend/tests/test_investigator.py`
   - Add tests: primary succeeds (secondary never called), primary fails + secondary succeeds, fan-out path, all fail

## Group 3 — Persistence

5. Write `backend/migrations/003_source_routing.sql`
   - `ALTER TABLE citation_results ADD COLUMN IF NOT EXISTS source_routing JSONB`
6. Update `backend/app/services/sessions.py`
   - INSERT includes `source_routing` (serialised to JSON)
   - GET returns `source_routing` in the citation dict

## Group 4 — Frontend

7. Update `frontend/src/components/CitationCard.tsx`
   - Add `source_routing?: SourceRouting` to the `Citation` interface
   - Add `SourceRouting` type (mirrors backend TypedDict)
   - Render one-line routing trace below tribunal/reference:
     - primary found → `"Verificado vía {primary} (primaria)"`
     - secondary found → `"{primary} sin resultado → confirmado por {secondary}"`
     - fallback → `"Búsqueda en todas las fuentes"`
   - Only shown when `source_routing` is present
8. Update `frontend/src/components/CitationCard.test.tsx`
   - Tests for each routing trace variant
   - Test that card renders normally when `source_routing` is absent

## Group 5 — Cleanup & commit

9. Commit spec files, then each group as its own commit
10. Run `pytest` (backend) and `npm run test:run` (frontend) — both must pass
11. Push `phase-7/router` and open PR targeting `main`
