# Phase 4 — Investigator Agent (Stubbed): Validation

## Local Validation (required before pushing)

### Backend
- [ ] `POST /investigate` with a citation whose `case_name` matches a known case returns `found: true` and non-null `ruling_text`
- [ ] `POST /investigate` with an unknown case name returns `found: false` and `ruling_text: null`
- [ ] All original citation fields (`claim`, `case_name`, `court`, `year_tomo_folio`) are preserved in the response
- [ ] `POST /investigate` with an empty `citations` array returns `{"citations": []}` with HTTP 200
- [ ] `GET /docs` shows the `/investigate` endpoint with correct request/response schema
- [ ] `pytest` passes for `test_fuzzy.py` and `test_investigator_stub.py`

### Frontend
- [ ] Upload a brief containing a known case name → "Verificando citas…" spinner appears → green "Encontrado" badge on the citation card
- [ ] Upload a brief with no known cases → red "No encontrado" badge on each card
- [ ] "Upload another document" resets all the way to idle
- [ ] With `/investigate` returning an error: inline error shown with "Try again" and "Upload another document" options
- [ ] "Try again" re-runs investigation without re-uploading or re-extracting

## Deployment Validation (required before merging to main)

- [ ] Render redeploys without errors — `/investigate` route visible in `/docs`
- [ ] Upload a brief through the Vercel production URL — found/not-found badges appear correctly
- [ ] Full pipeline confirmed in production: upload → extract → investigate → badges

## Definition of Done

All checkboxes above are ticked. An attorney can upload a legal brief in production and see each citation marked as found or not found. The data contract (`found`, `ruling_text`) is locked and documented. The fuzzy-match helper is tested and ready for Phase 7 to activate.
