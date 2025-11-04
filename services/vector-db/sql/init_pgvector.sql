-- Initialize pgvector extension for Vector DB Service
-- This script should be run once on the PostgreSQL database

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
