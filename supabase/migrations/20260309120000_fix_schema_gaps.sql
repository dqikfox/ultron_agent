-- Fix schema gaps: add missing columns expected by supabase_client.py

-- conversations: add title, model_name, ai_provider, message_count
ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS title        TEXT    NOT NULL DEFAULT 'ULTRON Session',
  ADD COLUMN IF NOT EXISTS model_name   TEXT    NOT NULL DEFAULT 'local',
  ADD COLUMN IF NOT EXISTS ai_provider  TEXT    NOT NULL DEFAULT 'ollama',
  ADD COLUMN IF NOT EXISTS message_count INTEGER NOT NULL DEFAULT 0;

-- messages: add role, processing_time_ms, tokens_used
--   (content already exists; file_url kept for backwards compat)
ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS role               TEXT    NOT NULL DEFAULT 'user'
      CHECK (role IN ('user', 'assistant', 'system', 'tool')),
  ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS tokens_used        INTEGER NOT NULL DEFAULT 0;

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation  ON messages(conversation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_role          ON messages(role);
CREATE INDEX IF NOT EXISTS idx_agent_memory_key       ON agent_memory(key);
