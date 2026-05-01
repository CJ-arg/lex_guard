# Phase 2 — Document Ingestion: Plan

## Group 1 — Backend: Upload Endpoint & Text Extraction

1.1 Create `backend/app/services/` directory and add `extractor.py` with two functions:
   - `extract_pdf(file_bytes: bytes) -> str` using PyMuPDF (`fitz`)
   - `extract_docx(file_bytes: bytes) -> str` using `python-docx`

1.2 Add `POST /upload` route to `backend/app/main.py`:
   - Accepts `multipart/form-data` with a single file field
   - Rejects non-PDF/DOCX with HTTP 415
   - Rejects files over 1 MB with HTTP 413
   - Calls the appropriate extractor and returns `{"text": "..."}` with HTTP 200
   - Returns `{"detail": "..."}` on extraction failure with HTTP 422

1.3 Smoke-test locally with `curl.exe` posting a real PDF and a real DOCX

## Group 2 — Frontend: Upload UI

2.1 Create `frontend/src/components/UploadZone.tsx`:
   - Drag-and-drop area that accepts `.pdf` and `.docx` files
   - File picker button as fallback
   - Validates file type and size (1 MB) client-side before sending
   - Shows clear error message for rejected files inline (no modal)

2.2 Replace the placeholder content in `frontend/src/app/page.tsx` with the upload flow:
   - Idle state: UploadZone centered on screen with LexGuard header
   - Loading state: spinner / "Extracting text…" message while `POST /upload` is in flight
   - Success state: transition to extracted text panel (Group 3)
   - Error state: API error message shown inline, upload zone resets

## Group 3 — Frontend: Extracted Text Display

3.1 Create `frontend/src/components/TextPanel.tsx`:
   - Scrollable panel displaying the raw extracted text
   - "Upload another document" button to reset back to the upload state
   - Document name shown as a label above the text

## Group 4 — Wiring & Environment

4.1 Confirm `NEXT_PUBLIC_API_URL` is read correctly in the upload fetch call (reuse `frontend/src/lib/api.ts`)
4.2 Update `frontend/.env.example` if any new env vars are needed
4.3 Verify the full flow locally: upload PDF → see text, upload DOCX → see text, upload wrong type → see error, upload oversized file → see error
