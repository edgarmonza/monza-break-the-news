-- Migration 001: Initial Schema for Colombia News
-- PostgreSQL + pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Articles table
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL, -- 'eltiempo', 'elespectador', 'semana', etc.
    author TEXT,
    published_at TIMESTAMPTZ,
    image_url TEXT,
    embedding vector(1536), -- OpenAI text-embedding-3-small dimension
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Threads table
CREATE TABLE IF NOT EXISTS threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title_id TEXT UNIQUE NOT NULL, -- '@ReformaTributaria'
    display_title TEXT NOT NULL,
    summary TEXT NOT NULL,
    trending_score REAL NOT NULL DEFAULT 0.0,
    article_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Thread-Article relationship (many-to-many)
CREATE TABLE IF NOT EXISTS thread_articles (
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0, -- Order within thread
    PRIMARY KEY (thread_id, article_id)
);

-- Suggested questions for threads
CREATE TABLE IF NOT EXISTS thread_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON articles(scraped_at DESC);

-- Vector similarity search index (HNSW for fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_articles_embedding ON articles
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_threads_trending_score ON threads(trending_score DESC);
CREATE INDEX IF NOT EXISTS idx_threads_created_at ON threads(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_thread_articles_thread_id ON thread_articles(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_articles_article_id ON thread_articles(article_id);

CREATE INDEX IF NOT EXISTS idx_thread_questions_thread_id ON thread_questions(thread_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threads_updated_at
    BEFORE UPDATE ON threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update thread article_count
CREATE OR REPLACE FUNCTION update_thread_article_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE threads
        SET article_count = article_count + 1
        WHERE id = NEW.thread_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE threads
        SET article_count = article_count - 1
        WHERE id = OLD.thread_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update article_count
CREATE TRIGGER update_thread_article_count_trigger
    AFTER INSERT OR DELETE ON thread_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_thread_article_count();

-- View for thread with article sources
CREATE OR REPLACE VIEW thread_stats AS
SELECT
    t.id,
    t.title_id,
    t.display_title,
    t.trending_score,
    t.article_count,
    t.created_at,
    array_agg(DISTINCT a.source) as sources,
    COUNT(DISTINCT a.source) as source_count
FROM threads t
LEFT JOIN thread_articles ta ON t.id = ta.thread_id
LEFT JOIN articles a ON ta.article_id = a.id
GROUP BY t.id, t.title_id, t.display_title, t.trending_score, t.article_count, t.created_at;

-- Comments for documentation
COMMENT ON TABLE articles IS 'News articles scraped from Colombian media';
COMMENT ON TABLE threads IS 'Aggregated news threads (stories)';
COMMENT ON TABLE thread_articles IS 'Many-to-many relationship between threads and articles';
COMMENT ON TABLE thread_questions IS 'AI-generated suggested questions for threads';
COMMENT ON COLUMN articles.embedding IS 'OpenAI embedding vector for semantic search (1536 dimensions)';
COMMENT ON COLUMN threads.title_id IS 'Twitter-style handle, e.g. @ReformaTributaria';
COMMENT ON COLUMN threads.trending_score IS 'Score from 0.0 to 1.0 based on recency, volume, diversity';
