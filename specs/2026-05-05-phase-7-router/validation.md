# Phase 7 Router — Validation

## Automated tests

### Router unit tests (`test_router.py`)
- `Fallos: 330:4921` in `year_tomo_folio` → primary=CSJN, secondary=SAIJ, fallback=False
- `court="CSJN"` → primary=CSJN, secondary=SAIJ
- `court="Corte Suprema de Justicia de la Nación"` → primary=CSJN
- `court="C.S.J.N."` → primary=CSJN
- `court="SCBA"` → primary=SAIJ (JUBA disabled), secondary=None
- `court="CNCiv"` → primary=SAIJ, secondary=None
- `court="CNCom"` → primary=SAIJ
- `court="Cám. Apel. Civ. y Com. Mar del Plata"` → primary=SAIJ (BA chamber)
- `court=""` → fallback=True
- `court="Tribunal desconocido xyz"` → fallback=True
- All rules return a `RouteDecision` with valid fields

### Investigator tests (`test_investigator.py`)
- Primary found: secondary adapter is never called
- Primary not found, secondary found: result comes from secondary; `source_routing.secondary_result == "found"`
- Fan-out path: all three adapters are called via `asyncio.gather`
- All sources fail: `unverifiable=True`
- `source_routing` is present in every non-cached result

### Backend integration
- `pytest` — all existing tests still pass with no regressions

### Frontend tests (`CitationCard.test.tsx`)
- `source_routing` present, primary found → renders `"Verificado vía CSJN (primaria)"`
- `source_routing` present, secondary found → renders `"CSJN sin resultado → confirmado por SAIJ"`
- `source_routing` present, fallback → renders `"Búsqueda en todas las fuentes"`
- `source_routing` absent → routing line not rendered
- `npm run test:run` — all tests pass

## Manual test checklist

- [ ] Upload a doc with a CSJN citation (`Fallos: 239:459`) → CitationCard shows `"Verificado vía CSJN (primaria)"` (if CSJN responds) or `"CSJN sin resultado → confirmado por SAIJ"` (if CSJN is down)
- [ ] Upload a doc with a `CNCiv` citation → CitationCard shows `"Verificado vía SAIJ (primaria)"`
- [ ] Upload a doc with an unknown court → CitationCard shows `"Búsqueda en todas las fuentes"`
- [ ] Source routing line does not appear on cards where the verdict is `unverifiable`

## Definition of done

- All automated tests pass
- Manual checklist completed
- `source_routing` column exists in `citation_results` (migration applied)
- PR approved and merged to `main`
