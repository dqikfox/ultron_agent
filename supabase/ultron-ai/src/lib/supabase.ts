import { createClient } from '@supabase/supabase-js'

// Supabase project credentials – configure via environment variables.
// For local development, set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
// in a .env file at the project root.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    'Supabase credentials not found. Set VITE_SUPABASE_URL and ' +
    'VITE_SUPABASE_ANON_KEY in your .env file. ' +
    'The client will be created with placeholder values and most ' +
    'operations will fail until real credentials are provided.'
  )
}

// The fallback values allow the app to load without crashing during
// development / build, but all authenticated operations will fail.
export const supabase = createClient(
  supabaseUrl || 'http://127.0.0.1:54321',
  supabaseAnonKey || ''
)

// ─── Database row types ────────────────────────────────────────────────────

export interface Profile {
  id: string
  email?: string | null
  full_name?: string | null
  avatar_url?: string | null
  preferred_ai_provider?: string | null
  voice_enabled?: boolean
  theme_preference?: string | null
  system_monitoring_enabled?: boolean
  memory_data?: Record<string, unknown> | null
  created_at?: string
  updated_at?: string
}

export interface Conversation {
  id: string
  user_id?: string | null
  title?: string | null
  ai_provider?: string | null
  model_name?: string | null
  message_count?: number
  created_at?: string
  updated_at?: string
}

export interface Message {
  id: string
  conversation_id?: string | null
  user_id?: string | null
  role: 'user' | 'assistant' | 'system'
  content?: string | null
  message_type?: string
  file_url?: string | null
  processing_time_ms?: number | null
  tokens_used?: number | null
  created_at?: string
}

export interface FileUpload {
  id: string
  user_id?: string | null
  filename?: string | null
  file_url?: string | null
  file_type?: string | null
  file_size?: number | null
  processing_status?: string
  processing_result?: string | null
  ocr_text?: string | null
  ai_analysis?: string | null
  created_at?: string
  processed_at?: string | null
}

export interface AiProvider {
  id: string
  user_id?: string | null
  provider_name?: string | null
  api_key_encrypted?: string | null
  base_url?: string | null
  model_list?: string | null
  is_active?: boolean
  created_at?: string
  updated_at?: string
}
