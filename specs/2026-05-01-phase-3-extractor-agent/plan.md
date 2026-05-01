# Phase 3 — Extractor Agent: Plan

## Group 1 — Backend: Extractor Agent Service

1.1 Add `ANTHROPIC_API_KEY` loading to `backend/app/main.py` via `python-dotenv`; confirm `anthropic` is in `requirements.txt`

1.2 Create `backend/app/services/agent_extractor.py`:
   - `extract_citations(text: str) -> list[dict]` — calls Claude Haiku with a Spanish prompt
   - Prompt instructs the model to find every jurisprudential citation and return a JSON array with fields: `claim`, `case_name`, `court`, `year_tomo_folio`
   - Parse and validate the JSON response; raise `ValueError` on malformed output
   - Return empty list `[]` if the model finds no citations

1.3 Add `POST /extract` route to `backend/app/main.py`:
   - Body: `{"text": "..."}` (Pydantic model)
   - Calls `extract_citations(text)`
   - Returns `{"citations": [...]}` with HTTP 200
   - Returns HTTP 422 with `{"detail": "..."}` on extraction failure

1.4 Smoke-test locally with `curl.exe` posting a real brief text snippet

## Group 2 — Frontend: Citation Components

2.1 Create `frontend/src/components/CitationCard.tsx`:
   - Displays one citation: `claim` (prominent), `case_name`, `court`, `year_tomo_folio`
   - Subtle card styling consistent with existing dark theme
   - Fields that are null or empty are hidden gracefully

2.2 Create `frontend/src/components/CitationList.tsx`:
   - Receives `citations: Citation[]` and `filename: string`
   - Maps over citations and renders a `CitationCard` per item
   - Shows citation count above the list: "X citations found in filename.pdf"
   - "Upload another document" button to reset

## Group 3 — Frontend: Wire the Full Flow

3.1 Extend the state machine in `frontend/src/app/page.tsx`:
   - Add `extracting` state (shown after upload succeeds, while `/extract` is in flight)
   - Add `citations` state (holds `filename`, `text`, `citations[]`)
   - Add `extract_error` state (holds `message`, allows retry without re-uploading)

3.2 After a successful `/upload` response, automatically call `POST /extract` with the returned text:
   - Transition: `loading` → `extracting` → `citations` (or `extract_error`)

3.3 No-citations fallback: if `citations` array is empty, render `TextPanel` with the raw text instead of `CitationList`

3.4 Retry button in `extract_error` state re-calls `/extract` with the stored text (no re-upload needed)

## Group 4 — Environment & Wiring

4.1 Add `ANTHROPIC_API_KEY=` to `backend/.env.example`

4.2 Set `ANTHROPIC_API_KEY` in Render environment variables dashboard

4.3 Verify full local flow: upload PDF → spinner → "Extracting citations…" → citation cards displayed
