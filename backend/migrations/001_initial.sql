CREATE TABLE IF NOT EXISTS sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_name TEXT        NOT NULL,
  user_note     TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citation_results (
  id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      UUID    NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  position        INTEGER NOT NULL,
  claim           TEXT    NOT NULL,
  case_name       TEXT    NOT NULL,
  court           TEXT,
  year_tomo_folio TEXT,
  found           BOOLEAN NOT NULL,
  verdict         TEXT    NOT NULL CHECK (verdict IN ('approved', 'warning', 'danger')),
  justification   TEXT    NOT NULL
);
