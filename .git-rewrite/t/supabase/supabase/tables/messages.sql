CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID,
    user_id UUID,
    role VARCHAR(20) CHECK (role IN ('user',
    'assistant',
    'system')),
    content TEXT,
    message_type VARCHAR(20) DEFAULT 'text',
    file_url TEXT,
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);