import { useState, useEffect } from 'react'
import { callEdgeFunction, supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

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
}

export interface ChatResponse {
  response: string
  model: string
  sessionId: string
  responseTime: number
  tokensUsed: number
  metadata: any
}

export const useOllama = () => {
  const { user } = useAuth()
  const [models, setModels] = useState<OllamaModel[]>([])
  const [ollamaStatus, setOllamaStatus] = useState<'running' | 'stopped' | 'error' | 'unknown'>('unknown')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Chat with Ollama
  const chat = async (message: string, model: string = 'llama2', sessionId?: string): Promise<ChatResponse> => {
    setLoading(true)
    setError(null)
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const result = await callEdgeFunction(
        'ollama-chat',
        { message, model, sessionId },
        session?.access_token
      )
      
      return result.data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Chat failed'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Load available models
  const loadModels = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await fetch(`https://njesbdmuhbqkdqdkkxun.supabase.co/functions/v1/ollama-models?action=list`, {
        method: 'GET',
        headers: {
          'Authorization': session?.access_token ? `Bearer ${session.access_token}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to load models')
      }
      
      const result = await response.json()
      setModels(result.data.models || [])
      setOllamaStatus(result.data.ollama_status || 'unknown')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load models'
      setError(errorMessage)
      setOllamaStatus('error')
    } finally {
      setLoading(false)
    }
  }

  // Pull a new model
  const pullModel = async (modelName: string) => {
    setLoading(true)
    setError(null)
    
    try {
      await callEdgeFunction(
        'ollama-models',
        { modelName },
        session?.access_token
      )
      
      // Reload models after pull
      await loadModels()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to pull model'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Delete a model
  const deleteModel = async (modelName: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`https://njesbdmuhbqkdqdkkxun.supabase.co/functions/v1/ollama-models?action=delete`, {
        method: 'POST',
        headers: {
          'Authorization': user?.access_token ? `Bearer ${user.access_token}` : '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ modelName })
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete model')
      }
      
      // Reload models after deletion
      await loadModels()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete model'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Load models on mount
  useEffect(() => {
    loadModels()
  }, [])

  return {
    models,
    ollamaStatus,
    loading,
    error,
    chat,
    loadModels,
    pullModel,
    deleteModel
  }
}