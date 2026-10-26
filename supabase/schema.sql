-- Ultron Agent Supabase Database Schema
-- This schema provides persistence for the ultron_agent AI platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Conversations table - stores chat conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 2. Messages table - stores individual messages in conversations
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model TEXT,
    tokens INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 3. Avatars table - stores avatar game characters
CREATE TABLE IF NOT EXISTS avatars (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    name TEXT NOT NULL,
    race TEXT,
    class TEXT,
    alignment TEXT,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    health INTEGER DEFAULT 100,
    mana INTEGER DEFAULT 100,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    inventory JSONB DEFAULT '[]'::jsonb,
    stats JSONB DEFAULT '{}'::jsonb,
    relationship_scores JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Agent sessions table - stores agent workflow states
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    state JSONB DEFAULT '{}'::jsonb,
    context JSONB DEFAULT '{}'::jsonb,
    memory JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- 5. Workflows table - stores workflow definitions
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    user_id TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. API keys table - stores user API keys securely
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    service TEXT NOT NULL CHECK (service IN ('openai', 'anthropic', 'ollama', 'aws', 'other')),
    key_name TEXT,
    encrypted_key TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- 7. User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_avatars_user_id ON avatars(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_session_id ON agent_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id ON agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatars ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (customize as needed)
CREATE POLICY "Enable read access for all users" ON conversations FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON conversations FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON conversations FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON messages FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON messages FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON messages FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON avatars FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON avatars FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON avatars FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON avatars FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON agent_sessions FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON agent_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON agent_sessions FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON agent_sessions FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON workflows FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON workflows FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON workflows FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON workflows FOR DELETE USING (true);

CREATE POLICY "Enable read access for own keys" ON api_keys FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON api_keys FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON api_keys FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON api_keys FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON user_preferences FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON user_preferences FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON user_preferences FOR UPDATE USING (true);
CREATE POLICY "Enable delete for all users" ON user_preferences FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON audit_logs FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON audit_logs FOR INSERT WITH CHECK (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_avatars_updated_at BEFORE UPDATE ON avatars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_sessions_updated_at BEFORE UPDATE ON agent_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
