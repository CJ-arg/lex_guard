# Phase 3 — Extractor Agent: Validation

## Local Validation (required before pushing)

### Backend
- [ ] `POST /extract` with a real Argentine legal brief text returns HTTP 200 and a non-empty `citations` array
- [ ] Each citation in the response contains `claim`, `case_name`, `court`, and `year_tomo_folio` fields
- [ ] `POST /extract` with a text containing no citations returns HTTP 200 and `{"citations": []}`
- [ ] `POST /extract` with an empty `text` field returns HTTP 422
- [ ] `GET /docs` shows the `/extract` endpoint with correct request/response schema
- [ ] Removing `ANTHROPIC_API_KEY` from the environment causes a clear startup or request-time error (not a silent crash)

### Frontend
- [ ] Upload a PDF brief with citations → spinner → "Extracting citations…" → citation cards render with all four fields
- [ ] Upload a DOCX with citations → same happy path as above
- [ ] Upload a document with no citations → raw text panel is shown (no empty card list)
- [ ] With the backend stopped: uploading shows the existing Phase 2 API error
- [ ] With the backend running but `/extract` failing (simulate by temporarily breaking the route): inline extraction error appears with a "Try again" button
- [ ] "Try again" re-runs extraction without re-uploading the document
- [ ] "Upload another document" resets all the way back to the idle upload state

## Deployment Validation (required before merging to main)

- [ ] `ANTHROPIC_API_KEY` is set in Render environment variables — Render redeploys without errors
- [ ] Upload a real Argentine legal brief through the Vercel production URL — citation cards render correctly
- [ ] No citations case works end-to-end in production (upload a non-legal document)
- [ ] Render logs show the Haiku API call completing without errors

## Definition of Done

All checkboxes above are ticked. An attorney can upload a real legal brief through the production URL and see a structured list of every jurisprudential citation extracted from it. The phase is mergeable to `main` when the full pipeline — upload → extract → display cards — works end-to-end in production.
