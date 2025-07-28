CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'success' CHECK (status IN ('success',
    'error',
    'warning',
    'info')),
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);