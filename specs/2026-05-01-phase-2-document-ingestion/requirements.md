# Phase 2 — Document Ingestion: Requirements

## Goal

Accept a legal brief from the attorney, extract its full text, and display it on screen. No agents run yet — this phase proves the document pipeline works before any AI processing is introduced.

## Scope

### In
- File upload UI in Next.js: drag-and-drop zone + file picker button
- Accepted formats: PDF and DOCX only — all other types rejected at the UI and the API
- File size limit: **1 MB** — enforced on the frontend before upload and on the backend before processing
- `POST /upload` endpoint in FastAPI receives the file as multipart form data
- PyMuPDF (`fitz`) extracts plain text from PDF; `python-docx` extracts plain text from DOCX
- Extracted text returned to the frontend as JSON and displayed in a scrollable panel
- Clear error messages for: wrong file type, file too large, extraction failure

### Out
- Any agent (Extractor, Investigator, Judge) — no AI in this phase
- File storage — the file is processed in memory and discarded; nothing is persisted
- Authentication
- Multiple file upload in a single session

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Size limit | 1 MB | Conservative cap suitable for typical briefs; avoids timeouts on Render free tier |
| Validation location | Both frontend and backend | Frontend gives instant feedback; backend is the authority |
| File persistence | None — in-memory only | No database in scope until Phase 6 |
| Text display | Scrollable pre-formatted panel | Raw extraction output; formatting comes in later phases |

## Context

- Backend: `backend/app/main.py` — add `POST /upload` route; extraction logic in `backend/app/services/extractor.py`
- Frontend: `frontend/src/app/` — new upload page or replace placeholder in `page.tsx`
- PDF extraction: `PyMuPDF` already installed in `.venv`
- DOCX extraction: `python-docx` already installed in `.venv`
- See `specs/tech-stack.md` for stack rationale
- See `specs/mission.md` — this phase enables the Extractor agent (Phase 3) which is the first step of the audit pipeline
