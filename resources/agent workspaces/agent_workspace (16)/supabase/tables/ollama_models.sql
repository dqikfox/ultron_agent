CREATE TABLE ollama_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    size_gb DECIMAL(10,2),
    is_available BOOLEAN DEFAULT false,
    is_downloading BOOLEAN DEFAULT false,
    download_progress INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);