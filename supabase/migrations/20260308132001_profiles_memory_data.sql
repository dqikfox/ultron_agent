-- Add memory_data column to profiles for agent long-term memory persistence
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS memory_data JSONB;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
