CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    value JSONB,
    memory_type VARCHAR(50) DEFAULT 'long_term',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_memory_key ON agent_memory(key);
CREATE INDEX IF NOT EXISTS idx_agent_memory_type ON agent_memory(memory_type);
