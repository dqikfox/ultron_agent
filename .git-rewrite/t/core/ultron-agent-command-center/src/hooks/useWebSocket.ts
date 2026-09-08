import { useState, useEffect, useRef, useCallback } from 'react'

export interface WebSocketMessage {
  type: string
  id?: string
  content?: string
  modelName?: string
  messages?: any[]
  [key: string]: any
}

export interface WebSocketHookOptions {
  url?: string
  onMessage?: (data: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export function useWebSocket(options: WebSocketHookOptions = {}) {
  const {
    url = 'ws://localhost:8080',
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000
  } = options

  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionHistory, setConnectionHistory] = useState<string[]>([])
  
  const ws = useRef<WebSocket | null>(null)
  const reconnectCount = useRef(0)
  const reconnectTimeoutId = useRef<NodeJS.Timeout | null>(null)
  const isManualClose = useRef(false)

  const addToHistory = useCallback((message: string) => {
    setConnectionHistory(prev => [
      `${new Date().toLocaleTimeString()}: ${message}`,
      ...prev.slice(0, 49) // Keep last 50 messages
    ])
  }, [])

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      setConnectionStatus('connecting')
      addToHistory('Attempting to connect...')
      
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        setConnectionStatus('connected')
        reconnectCount.current = 0
        addToHistory('Connected successfully')
        onConnect?.()
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          addToHistory(`Received: ${data.type}`)
          onMessage?.(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          addToHistory('Failed to parse message')
        }
      }

      ws.current.onclose = (event) => {
        setConnectionStatus('disconnected')
        addToHistory(`Connection closed: ${event.code}`)
        
        if (!isManualClose.current && reconnectCount.current < reconnectAttempts) {
          reconnectCount.current++
          addToHistory(`Reconnecting in ${reconnectInterval/1000}s (${reconnectCount.current}/${reconnectAttempts})`)
          
          reconnectTimeoutId.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (reconnectCount.current >= reconnectAttempts) {
          addToHistory('Max reconnection attempts reached')
          setConnectionStatus('error')
        }
        
        onDisconnect?.()
      }

      ws.current.onerror = (error) => {
        setConnectionStatus('error')
        addToHistory('Connection error occurred')
        onError?.(error)
      }

    } catch (error) {
      setConnectionStatus('error')
      addToHistory('Failed to create WebSocket connection')
      console.error('WebSocket connection error:', error)
    }
  }, [url, onConnect, onMessage, onDisconnect, onError, reconnectAttempts, reconnectInterval, addToHistory])

  const disconnect = useCallback(() => {
    isManualClose.current = true
    
    if (reconnectTimeoutId.current) {
      clearTimeout(reconnectTimeoutId.current)
      reconnectTimeoutId.current = null
    }
    
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    
    setConnectionStatus('disconnected')
    addToHistory('Manually disconnected')
  }, [addToHistory])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        const messageStr = JSON.stringify(message)
        ws.current.send(messageStr)
        addToHistory(`Sent: ${message.type}`)
        return true
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
        addToHistory('Failed to send message')
        return false
      }
    } else {
      console.warn('WebSocket is not connected')
      addToHistory('Cannot send - not connected')
      return false
    }
  }, [addToHistory])

  const reconnect = useCallback(() => {
    isManualClose.current = false
    reconnectCount.current = 0
    disconnect()
    setTimeout(() => connect(), 100)
  }, [connect, disconnect])

  // Auto-connect on mount
  useEffect(() => {
    isManualClose.current = false
    connect()

    return () => {
      isManualClose.current = true
      if (reconnectTimeoutId.current) {
        clearTimeout(reconnectTimeoutId.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  // Ping to keep connection alive
  useEffect(() => {
    if (connectionStatus === 'connected') {
      const pingInterval = setInterval(() => {
        sendMessage({ type: 'ping' })
      }, 30000) // Ping every 30 seconds
      
      return () => clearInterval(pingInterval)
    }
  }, [connectionStatus, sendMessage])

  return {
    connectionStatus,
    lastMessage,
    connectionHistory,
    sendMessage,
    connect,
    disconnect,
    reconnect,
    isConnected: connectionStatus === 'connected'
  }
}
