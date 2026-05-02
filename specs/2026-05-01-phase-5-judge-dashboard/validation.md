# Phase 5 — Judge Agent & Traffic-Light Dashboard: Validation

## Local Validation (required before pushing)

### Backend
- [ ] `POST /judge` with a known citation (`found: true`) returns `verdict` and non-empty `justification`
- [ ] `POST /judge` with `found: false` citation returns `verdict: "danger"` and fixed justification — no API call made
- [ ] All three verdicts (`approved`, `warning`, `danger`) are reachable with appropriate inputs
- [ ] `POST /judge` with empty `citations` array returns `{"citations": []}` with HTTP 200
- [ ] `GET /docs` shows `/judge` with correct request/response schema
- [ ] `pytest` passes for `test_judge.py`

### Frontend
- [ ] Upload "prueba 2.pdf" (Siri Angel + Halabi) → all four spinners in sequence → green "Aprobado" or yellow "Advertencia" verdict pills with justification text
- [ ] Upload "prueba 1.pdf" (unknown case) → red "Peligro" verdict pill with auto-danger justification
- [ ] Justification text is visible inline on each card without any click
- [ ] "Upload another document" resets to idle state
- [ ] With `/judge` failing: inline error + "Try again" appears; retry works without re-uploading

## Deployment Validation (required before merging to main)

- [ ] Render redeploys without errors — `/judge` visible in `/docs`
- [ ] Full pipeline in production: upload → extract → investigate → judge → verdict cards
- [ ] "prueba 2.pdf" produces green/yellow verdict in production
- [ ] "prueba 1.pdf" produces red "Peligro" verdict in production

## Definition of Done

All checkboxes ticked. An attorney uploads a real Argentine legal brief through the production URL and sees each citation with a traffic-light verdict and a plain-language justification they can act on immediately. This is the first end-to-end demo of LexGuard's core value.
