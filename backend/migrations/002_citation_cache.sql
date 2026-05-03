-- Phase 7: citation cache + widen verdict constraint + persist new source fields

-- 1. Widen verdict constraint to include 'unverifiable'
ALTER TABLE citation_results
  DROP CONSTRAINT IF EXISTS citation_results_verdict_check;
ALTER TABLE citation_results
  ADD CONSTRAINT citation_results_verdict_check
    CHECK (verdict IN ('approved', 'warning', 'danger', 'unverifiable'));

-- 2. Optional Phase-7 columns on citation_results (backward-compatible)
ALTER TABLE citation_results
  ADD COLUMN IF NOT EXISTS source             TEXT,
  ADD COLUMN IF NOT EXISTS source_url         TEXT,
  ADD COLUMN IF NOT EXISTS match_score        REAL,
  ADD COLUMN IF NOT EXISTS canonical_caratula TEXT,
  ADD COLUMN IF NOT EXISTS unverifiable       BOOLEAN NOT NULL DEFAULT FALSE;

-- 3. Citation cache table (30-day TTL, evicted at read)
CREATE TABLE IF NOT EXISTS citation_cache (
  cache_key           TEXT PRIMARY KEY,
  source              TEXT NOT NULL,
  source_url          TEXT,
  canonical_caratula  TEXT,
  ruling_text         TEXT,
  match_score         REAL NOT NULL,
  fetched_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS citation_cache_fetched_at_idx ON citation_cache (fetched_at);
