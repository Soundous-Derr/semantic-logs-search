CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    original_text TEXT NOT NULL,
    normalized_text TEXT,
    log_level VARCHAR(20),
    timestamp TIMESTAMP,
    source_ip INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS log_embeddings (
    id SERIAL PRIMARY KEY,
    log_id INTEGER NOT NULL,
    embedding vector(384),
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES logs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS error_clusters (
    id SERIAL PRIMARY KEY,
    cluster_name VARCHAR(255),
    centroid vector(384),
    error_type VARCHAR(100),
    log_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_level ON logs(log_level);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_embeddings_log ON log_embeddings(log_id);
CREATE INDEX idx_embeddings_vector ON log_embeddings USING ivfflat (embedding vector_cosine_ops);

CREATE OR REPLACE VIEW logs_with_embeddings AS
SELECT 
    l.id,
    l.original_text,
    l.log_level,
    l.timestamp,
    le.embedding,
    le.model_name
FROM logs l
LEFT JOIN log_embeddings le ON l.id = le.log_id;