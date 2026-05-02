# Phase 6 — Supabase Persistence: Requirements

## Goal

Add an audit trail. After reviewing citation verdicts, the attorney can save the session to Supabase Postgres with an optional note. A permalink is returned so the session can be retrieved and shared within the firm.

## Scope

### In scope
- Supabase Postgres as the database (free tier)
- `psycopg2-binary` as the Python client — no compilation required, works on Windows and Render
- Two tables: `sessions` and `citation_results` (schema below)
- `POST /sessions` — saves an audit session and its citation results
- `GET /sessions/{id}` — retrieves a saved session by UUID
- "Save report" button on the results page with an optional note field
- Permalink displayed after saving so the attorney can copy and share it

### Out of scope
- Authentication / user accounts (post-MVP)
- Listing all sessions (post-MVP)
- Deleting or editing sessions
- Storing the full extracted document text

## Database Schema

```sql
CREATE TABLE sessions (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_name TEXT NOT NULL,
  user_note  TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE citation_results (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
  claim       TEXT NOT NULL,
  case_name   TEXT NOT NULL,
  court       TEXT,
  year_tomo_folio TEXT,
  found       BOOLEAN NOT NULL,
  verdict     TEXT NOT NULL CHECK (verdict IN ('approved', 'warning', 'danger')),
  justification TEXT NOT NULL,
  position    INTEGER NOT NULL
);
```

## API Contract

### POST /sessions
Request:
```json
{
  "document_name": "string",
  "user_note": "string | null",
  "citations": [{ ...full citation with verdict + justification }]
}
```
Response:
```json
{ "session_id": "uuid" }
```

### GET /sessions/{id}
Response:
```json
{
  "id": "uuid",
  "document_name": "string",
  "user_note": "string | null",
  "created_at": "ISO timestamp",
  "citations": [{ ...full citation with verdict + justification }]
}
```

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Postgres client | `psycopg2-binary` | No C++ build tools required; works on Windows and Render Linux |
| No ORM | Raw SQL | Simple schema; consistent with tech-stack spec decision |
| UUID primary keys | `gen_random_uuid()` | Unguessable — safe to expose as permalink |
| Save trigger | Manual button | Attorney chooses when to commit; allows discarding a bad run |
| User note | Optional text field | Lets attorney label the session (e.g. case name) for future reference |
| No full text storage | Omitted | Reduces storage; text can be re-extracted by re-uploading |
