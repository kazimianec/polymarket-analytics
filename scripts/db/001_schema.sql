-- scripts/db/001_schema.sql
-- Apply via: make db-apply FILE=scripts/db/001_schema.sql
-- Or:        psql $DATABASE_URL -f scripts/db/001_schema.sql

-- Example:
-- CREATE TABLE IF NOT EXISTS users (
--     id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     email TEXT NOT NULL UNIQUE,
--     created_at TIMESTAMPTZ NOT NULL DEFAULT now()
-- );
