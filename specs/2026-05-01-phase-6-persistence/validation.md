# Phase 6 — Supabase Persistence: Validation

## Manual Setup Validation (before any code)
- [ ] Supabase project created and SQL migration run successfully
- [ ] `sessions` and `citation_results` tables visible in Supabase Table Editor
- [ ] `DATABASE_URL` added to `backend/.env`

## Local Validation (required before pushing)

### Backend
- [ ] `POST /sessions` with a valid session payload returns HTTP 200 and a UUID `session_id`
- [ ] `GET /sessions/{id}` with the returned UUID returns the full session with all citation fields
- [ ] `GET /sessions/{id}` with a non-existent UUID returns HTTP 404
- [ ] Saving a session with `user_note: null` works without error
- [ ] Supabase Table Editor shows the inserted rows after a save
- [ ] `GET /docs` shows both `/sessions` endpoints with correct schemas

### Frontend
- [ ] After the Judge pipeline completes, "Save report" button is visible on the results page
- [ ] Clicking "Save report" reveals an optional note input and a "Confirm" button
- [ ] Confirming saves the session and displays the permalink URL
- [ ] Clicking the permalink opens the read-only session page with the full verdict results
- [ ] Read-only page shows document name, date, user note, and all citation cards with verdicts
- [ ] Saving with no note (empty field) works correctly
- [ ] If the backend is unreachable during save: inline error shown with retry option

## Deployment Validation (required before merging to main)

- [ ] `DATABASE_URL` set in Render environment variables — redeploy succeeds
- [ ] `POST /sessions` works through the production Vercel URL
- [ ] Permalink URL opens correctly in production
- [ ] Supabase Table Editor shows production data after a real save

## Definition of Done

All checkboxes ticked. An attorney completes an audit in production, saves it with a note, and can share the permalink URL with a colleague who sees the full verdict results without re-running the pipeline.
