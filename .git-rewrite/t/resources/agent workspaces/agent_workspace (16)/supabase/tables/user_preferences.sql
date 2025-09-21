CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE,
    selected_model VARCHAR(100) DEFAULT 'llama2',
    voice_enabled BOOLEAN DEFAULT false,
    voice_language VARCHAR(10) DEFAULT 'en-US',
    theme_mode VARCHAR(20) DEFAULT 'ultron' CHECK (theme_mode IN ('ultron',
    'classic',
    'neon')),
    auto_save_chats BOOLEAN DEFAULT true,
    system_monitoring BOOLEAN DEFAULT true,
    chat_history_limit INTEGER DEFAULT 1000,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);