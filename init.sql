-- Database initialization script
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS dataset_processor;

-- Create user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dataset_user') THEN
        CREATE ROLE dataset_user WITH LOGIN PASSWORD 'secure_password_123';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dataset_processor TO dataset_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dataset_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dataset_user;

-- Create indexes for better performance
-- These will be created after the tables are created by SQLAlchemy

-- Index for job lookups by session
-- CREATE INDEX IF NOT EXISTS idx_processing_jobs_session_id ON processing_jobs(session_id);

-- Index for job lookups by status
-- CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);

-- Index for job lookups by created_at
-- CREATE INDEX IF NOT EXISTS idx_processing_jobs_created_at ON processing_jobs(created_at);

-- Index for element lookups by job_id
-- CREATE INDEX IF NOT EXISTS idx_processed_elements_job_id ON processed_elements(job_id);

-- Index for element lookups by type
-- CREATE INDEX IF NOT EXISTS idx_processed_elements_type ON processed_elements(element_type);

-- Index for session lookups by last_activity
-- CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity);
