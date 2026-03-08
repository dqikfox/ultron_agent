-- Dedicated table for ULTRON agent long-term memory persistence
-- Replaces the profiles-reuse approach (profiles has auth.users FK constraint)
CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    value JSONB,
    memory_type VARCHAR(50) DEFAULT 'long_term',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_memory_key ON agent_memory(key);
CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
