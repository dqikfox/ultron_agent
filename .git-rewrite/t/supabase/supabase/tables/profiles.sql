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