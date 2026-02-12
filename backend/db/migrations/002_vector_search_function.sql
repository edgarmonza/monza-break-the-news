-- Migration 002: Vector Search Function
-- Función para búsqueda por similitud vectorial

CREATE OR REPLACE FUNCTION match_articles(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    url text,
    title text,
    content text,
    source text,
    author text,
    published_at timestamptz,
    image_url text,
    embedding vector(1536),
    scraped_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        articles.id,
        articles.url,
        articles.title,
        articles.content,
        articles.source,
        articles.author,
        articles.published_at,
        articles.image_url,
        articles.embedding,
        articles.scraped_at,
        articles.created_at,
        articles.updated_at,
        1 - (articles.embedding <=> query_embedding) AS similarity
    FROM articles
    WHERE articles.embedding IS NOT NULL
        AND 1 - (articles.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Comentario
COMMENT ON FUNCTION match_articles IS 'Busca artículos por similitud vectorial usando embeddings';
