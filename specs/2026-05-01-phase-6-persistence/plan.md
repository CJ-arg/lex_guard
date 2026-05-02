# Phase 6 — Supabase Persistence: Plan

## Group 0 — Supabase Project Setup (manual steps)

0.1 Create a free Supabase project at supabase.com
0.2 In the Supabase dashboard → SQL Editor, run the migration in `backend/migrations/001_initial.sql`
0.3 In Project Settings → Database, copy the **Connection string (URI)** (Session mode, port 5432)
0.4 Add the connection string to `backend/.env` as `DATABASE_URL`
0.5 Add `DATABASE_URL` to Render environment variables

## Group 1 — Backend: Migration & Database Module

1.1 Create `backend/migrations/001_initial.sql` with the `sessions` and `citation_results` table definitions

1.2 Add `psycopg2-binary` to `backend/requirements.txt`

1.3 Create `backend/app/db.py`:
   - Reads `DATABASE_URL` from environment
   - `get_conn()` — returns a psycopg2 connection (simple connection per request for MVP; no pool needed at this scale)
   - Connection is opened lazily on first call

## Group 2 — Backend: Session Service

2.1 Create `backend/app/services/sessions.py`:
   - `save_session(document_name: str, user_note: str | None, citations: list[dict]) -> str`:
     - Inserts into `sessions`, returns the UUID as string
     - Inserts each citation into `citation_results` with `position` (0-indexed order)
     - Uses a single transaction — both inserts succeed or neither does
   - `get_session(session_id: str) -> dict`:
     - Fetches session row + all citation_results ordered by `position`
     - Returns combined dict matching the GET /sessions/{id} response schema
     - Raises `ValueError` if session not found

## Group 3 — Backend: API Routes

3.1 Add Pydantic model `SaveSessionRequest` to `backend/app/main.py`:
   - Fields: `document_name: str`, `user_note: str | None`, `citations: list[dict]`

3.2 Add `POST /sessions` route:
   - Calls `save_session(...)`, returns `{"session_id": uuid}`
   - HTTP 422 on DB error

3.3 Add `GET /sessions/{session_id}` route:
   - Calls `get_session(session_id)`, returns full session dict
   - HTTP 404 if not found

## Group 4 — Frontend: Save Flow in CitationList

4.1 Update `frontend/src/components/CitationList.tsx`:
   - Add save state machine: `idle | saving | saved | error`
   - "Save report" button opens an optional note input inline
   - On confirm: POST to `/sessions` with document_name, user_note, citations
   - On success: show permalink (`/sessions/{id}`) with a copy button
   - On error: show inline error with retry

4.2 Add `frontend/src/app/sessions/[id]/page.tsx`:
   - Client component that fetches `GET /sessions/{id}` from the API
   - Renders CitationList in read-only mode (no Save button, no Upload button)
   - Shows document name, date, user note at the top
   - 404 message if session not found
