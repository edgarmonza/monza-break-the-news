-- Migration 004: Add country support + constraints for multi-country scaling
-- Run this on your Supabase SQL editor

-- 1. Add country column to articles
ALTER TABLE articles ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'CO';
CREATE INDEX IF NOT EXISTS idx_articles_country ON articles(country);

-- 2. Add country column to threads
ALTER TABLE threads ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'CO';
CREATE INDEX IF NOT EXISTS idx_threads_country ON threads(country);

-- 3. Add constraints for data integrity
ALTER TABLE threads ADD CONSTRAINT IF NOT EXISTS trending_score_range
    CHECK (trending_score >= 0.0 AND trending_score <= 1.0);

ALTER TABLE threads ADD CONSTRAINT IF NOT EXISTS article_count_non_negative
    CHECK (article_count >= 0);

-- 4. Pipeline runs tracking table
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running', -- 'running', 'completed', 'failed'
    country TEXT NOT NULL DEFAULT 'CO',
    articles_scraped INTEGER DEFAULT 0,
    articles_new INTEGER DEFAULT 0,
    threads_created INTEGER DEFAULT 0,
    threads_updated INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);

-- 5. Update thread_stats view to include country
CREATE OR REPLACE VIEW thread_stats AS
SELECT
    t.id,
    t.title_id,
    t.display_title,
    t.trending_score,
    t.article_count,
    t.country,
    t.created_at,
    array_agg(DISTINCT a.source) as sources,
    COUNT(DISTINCT a.source) as source_count
FROM threads t
LEFT JOIN thread_articles ta ON t.id = ta.thread_id
LEFT JOIN articles a ON ta.article_id = a.id
GROUP BY t.id, t.title_id, t.display_title, t.trending_score, t.article_count, t.country, t.created_at;

COMMENT ON COLUMN articles.country IS 'ISO 3166-1 alpha-2 country code (CO, MX, AR, CL, PE, EC, etc.)';
COMMENT ON COLUMN threads.country IS 'Primary country this thread relates to';
COMMENT ON TABLE pipeline_runs IS 'Tracks each pipeline execution for monitoring and debugging';
