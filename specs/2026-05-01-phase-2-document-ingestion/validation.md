# Phase 2 — Document Ingestion: Validation

## Local Validation (required before pushing)

### Backend
- [ ] `POST /upload` with a valid PDF returns HTTP 200 and `{"text": "..."}` with non-empty text
- [ ] `POST /upload` with a valid DOCX returns HTTP 200 and `{"text": "..."}` with non-empty text
- [ ] `POST /upload` with a `.txt` or any non-PDF/DOCX file returns HTTP 415
- [ ] `POST /upload` with a file over 1 MB returns HTTP 413
- [ ] `GET /docs` shows the `/upload` endpoint with correct request/response schema

### Frontend
- [ ] Drag-and-drop a PDF onto the upload zone — spinner appears, then extracted text displays
- [ ] Drag-and-drop a DOCX onto the upload zone — spinner appears, then extracted text displays
- [ ] Drop a `.txt` file — inline error shown immediately, no network request made
- [ ] Drop a file over 1 MB — inline error shown immediately, no network request made
- [ ] "Upload another document" resets the UI to the idle upload state
- [ ] With the backend stopped: uploading shows a clear API error, not a blank screen or crash

## Deployment Validation (required before merging to main)

- [ ] Render redeploys with the new `/upload` route — build succeeds, no import errors
- [ ] Vercel redeploys with the new upload UI — build succeeds
- [ ] Upload a PDF through the Vercel production URL — text renders correctly from the Render backend
- [ ] 1 MB limit enforced end-to-end: a 1.1 MB file is rejected by the frontend before it reaches Render

## Definition of Done

All checkboxes above are ticked. An attorney can drag a real legal brief (PDF or DOCX, under 1 MB) onto the production URL and see its full text extracted on screen. The phase is mergeable to `main` when this works end-to-end in production.
