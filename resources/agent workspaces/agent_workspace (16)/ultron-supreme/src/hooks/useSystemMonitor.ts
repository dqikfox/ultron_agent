import { useState, useEffect, useCallback } from 'react'
import { callEdgeFunction } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

export interface SystemStats {
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

export interface SystemLog {
  id: number
  user_id?: string
  action_type: string
  action_description: string
  status: 'success' | 'error' | 'warning' | 'info'
  metadata?: any
  created_at: string
}

export const useSystemMonitor = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [logs, setLogs] = useState<SystemLog[]>([])
  const [history, setHistory] = useState<SystemStats[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Get current system stats
  const getStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`https://njesbdmuhbqkdqdkkxun.supabase.co/functions/v1/system-monitor?action=stats`, {
        method: 'GET',
        headers: {
          'Authorization': user?.access_token ? `Bearer ${user.access_token}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch system stats')
      }
      
      const result = await response.json()
      setStats(result.data.stats)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch stats'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [user?.access_token])

  // Get system logs
  const getLogs = useCallback(async (limit: number = 50, type?: string) => {
    setLoading(true)
    setError(null)
    
    try {
      let url = `https://njesbdmuhbqkdqdkkxun.supabase.co/functions/v1/system-monitor?action=logs&limit=${limit}`
      if (type) {
        url += `&type=${type}`
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': user?.access_token ? `Bearer ${user.access_token}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch system logs')
      }
      
      const result = await response.json()
      setLogs(result.data.logs)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch logs'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [user?.access_token])

  // Get stats history
  const getHistory = useCallback(async (limit: number = 100) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`https://njesbdmuhbqkdqdkkxun.supabase.co/functions/v1/system-monitor?action=history&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': user?.access_token ? `Bearer ${user.access_token}` : '',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch system history')
      }
      
      const result = await response.json()
      setHistory(result.data.history)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch history'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [user?.access_token])

  // Auto-refresh stats every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      getStats()
    }, 5000)
    
    // Initial load
    getStats()
    getLogs()
    
    return () => clearInterval(interval)
  }, [getStats, getLogs])

  return {
    stats,
    logs,
    history,
    loading,
    error,
    getStats,
    getLogs,
    getHistory
  }
}