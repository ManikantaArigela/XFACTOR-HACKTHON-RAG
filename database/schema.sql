CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    image_path VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_contents_category ON contents(category);
CREATE INDEX IF NOT EXISTS ix_contents_created_at ON contents(created_at DESC);

CREATE TABLE IF NOT EXISTS content_embeddings (
    id UUID PRIMARY KEY,
    content_id UUID NOT NULL UNIQUE REFERENCES contents(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    source_text TEXT NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_content_embeddings_vector
ON content_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE OR REPLACE FUNCTION set_contents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS contents_updated_at ON contents;
CREATE TRIGGER contents_updated_at
BEFORE UPDATE ON contents
FOR EACH ROW EXECUTE FUNCTION set_contents_updated_at();
