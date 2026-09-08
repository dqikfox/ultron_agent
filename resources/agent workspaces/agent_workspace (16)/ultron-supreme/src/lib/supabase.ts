import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = 'https://njesbdmuhbqkdqdkkxun.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5qZXNiZG11aGJxa2RxZGtreHVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIyNjI0OTIsImV4cCI6MjA2NzgzODQ5Mn0.lP9QbNUJU3IZ0m4gvBFBQw2k1ivQxdyAK8x9naBYZSU'

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface ChatMessage {
  id: number
  user_id?: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  model_name?: string
  tokens_used?: number
  response_time_ms?: number
  metadata?: any
  created_at: string
  updated_at: string
}

export interface SystemLog {
  id: number
  user_id?: string
  action_type: string
  action_description: string
  status: 'success' | 'error' | 'warning' | 'info'
  metadata?: any
  ip_address?: string
  user_agent?: string
  created_at: string
}

export interface UserPreferences {
  id: number
  user_id: string
  selected_model: string
  voice_enabled: boolean
  voice_language: string
  theme_mode: 'ultron' | 'classic' | 'neon'
  auto_save_chats: boolean
  system_monitoring: boolean
  chat_history_limit: number
  preferences?: any
  created_at: string
  updated_at: string
}

export interface OllamaModel {
  id: number
  name: string
  display_name: string
  description?: string
  size_gb?: number
  is_available: boolean
  is_downloading: boolean
  download_progress: number
  last_used?: string
  usage_count: number
  created_at: string
  updated_at: string
}

export interface SystemStats {
  id: number
  cpu_usage: number
  memory_usage: number
  memory_total_gb: number
  disk_usage: number
  disk_total_gb: number
  ollama_status: 'running' | 'stopped' | 'error' | 'unknown'
  active_model?: string
  gpu_usage?: number
  temperature?: number
  uptime_seconds: number
  recorded_at: string
}

// Edge function helpers
export const callEdgeFunction = async (functionName: string, data?: any, authToken?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }
  
  const response = await fetch(`${supabaseUrl}/functions/v1/${functionName}`, {
    method: 'POST',
    headers,
    body: data ? JSON.stringify(data) : undefined
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || 'Function call failed')
  }
  
  return response.json()
}

// Auth helpers
export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error) {
    console.error('Error getting user:', error)
    return null
  }
  return user
}

export const signIn = async (email: string, password: string) => {
  return await supabase.auth.signInWithPassword({ email, password })
}

export const signUp = async (email: string, password: string) => {
  return await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${window.location.protocol}//${window.location.host}/auth/callback`
    }
  })
}

export const signOut = async () => {
  return await supabase.auth.signOut()
}