-- Enable RLS on all tables and add appropriate policies

-- ai_providers: public read (provider name/url is non-sensitive)
ALTER TABLE ai_providers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_providers" ON ai_providers
  FOR SELECT USING (true);

-- conversations: users can only see their own
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_conversations" ON conversations
  FOR ALL USING (user_id IS NULL OR user_id = auth.uid());

-- messages: accessible via conversation ownership
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_messages" ON messages
  FOR ALL USING (
    conversation_id IN (
      SELECT id FROM conversations
      WHERE user_id IS NULL OR user_id = auth.uid()
    )
  );

-- tool_executions: fully public (no user_id column)
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_tool_executions" ON tool_executions
  FOR ALL USING (true);

-- agent_memory: public read/write (system memory)
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_agent_memory" ON agent_memory
  FOR ALL USING (true);
