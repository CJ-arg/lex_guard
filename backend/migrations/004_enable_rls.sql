-- Enable Row-Level Security on all public tables.
-- The backend connects as the postgres superuser (DATABASE_URL), which bypasses
-- RLS entirely, so no policies are needed for backend access.
-- With RLS enabled and no permissive policies, the Supabase anon role cannot
-- read, insert, update, or delete any rows via the REST API.

ALTER TABLE sessions          ENABLE ROW LEVEL SECURITY;
ALTER TABLE citation_results  ENABLE ROW LEVEL SECURITY;
ALTER TABLE citation_cache    ENABLE ROW LEVEL SECURITY;
