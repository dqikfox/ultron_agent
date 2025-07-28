CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    session_id VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user',
    'assistant',
    'system')),
    content TEXT NOT NULL,
    model_name VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    response_time_ms INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);