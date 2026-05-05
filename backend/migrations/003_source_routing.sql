-- Phase 7 router: add source_routing column to citation_results
ALTER TABLE citation_results
  ADD COLUMN IF NOT EXISTS source_routing JSONB;
