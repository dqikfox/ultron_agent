-- Initial ULTRON Agent schema migration

-- === profiles.sql ===
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email VARCHAR(255),
    full_name VARCHAR(255),
    avatar_url TEXT,
    preferred_ai_provider VARCHAR(50) DEFAULT 'ollama',
    voice_enabled BOOLEAN DEFAULT false,
    theme_preference VARCHAR(20) DEFAULT 'dark',
    system_monitoring_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- === ai_providers.sql ===
CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    provider_name VARCHAR(50),
    api_key_encrypted TEXT,
    base_url TEXT,
    model_list TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- === conversations.sql ===
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    title VARCHAR(500),
    ai_provider VARCHAR(50),
    model_name VARCHAR(100),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- === messages.sql ===
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
-- === file_uploads.sql ===
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    filename VARCHAR(500),
    file_url TEXT,
    file_type VARCHAR(100),
    file_size INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_result TEXT,
    ocr_text TEXT,
    ai_analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);