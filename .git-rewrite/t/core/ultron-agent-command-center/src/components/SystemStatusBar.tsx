import React, { useState, useEffect } from 'react'
import { OllamaModel } from '../hooks/useAppState'

interface SystemStatusBarProps {
  systemStatus: {
    ollama: boolean
    elevenlabs: boolean
    websocket: boolean
  }
  activeModel: OllamaModel | null
  connectionStatus: string
}

export function SystemStatusBar({ systemStatus, activeModel, connectionStatus }: SystemStatusBarProps) {
  const [systemMetrics, setSystemMetrics] = useState<any>(null)
  const [uptime, setUptime] = useState(0)
  const [networkActivity, setNetworkActivity] = useState(false)

  useEffect(() => {
    // Load initial system metrics
    loadSystemMetrics()
    
    // Update metrics every 2 seconds
    const interval = setInterval(() => {
      loadSystemMetrics()
      setUptime(prev => prev + 1)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const loadSystemMetrics = async () => {
    try {
      const metrics = await window.electronAPI.getSystemMetrics()
      setSystemMetrics(metrics)
      setNetworkActivity(metrics.network?.activity || false)
    } catch (error) {
      console.error('Failed to load system metrics:', error)
      // Fallback to simulated data
      setSystemMetrics({
        cpu: { usage: Math.random() * 100 },
        memory: { usage: Math.random() * 100 },
        uptime: { app: Math.floor(Date.now() / 1000) }
      })
    }
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'var(--color-accent-success)'
      case 'connecting': return 'var(--color-accent-warning)'
      case 'disconnected': return 'var(--color-text-muted)'
      case 'error': return 'var(--color-accent-danger)'
      default: return 'var(--color-text-muted)'
    }
  }

  const getOverallSystemHealth = () => {
    const services = Object.values(systemStatus)
    const healthyServices = services.filter(status => status).length
    const healthPercentage = (healthyServices / services.length) * 100
    
    if (healthPercentage === 100) return { status: 'optimal', color: 'var(--color-accent-success)' }
    if (healthPercentage >= 66) return { status: 'good', color: 'var(--color-accent-warning)' }
    if (healthPercentage >= 33) return { status: 'degraded', color: 'var(--color-accent-danger)' }
    return { status: 'critical', color: 'var(--color-accent-danger)' }
  }

  const systemHealth = getOverallSystemHealth()
  const cpuUsage = systemMetrics?.cpu?.usage || 0
  const memoryUsage = systemMetrics?.memory?.usage || 0
  const appUptime = systemMetrics?.uptime?.app || uptime

  return (
    <div className="h-8 bg-black/40 border-t border-slate-700 flex items-center px-md text-xs">
      {/* Left side - System health */}
      <div className="flex items-center gap-md">
        <div className="flex items-center gap-xs">
          <div 
            className="w-2 h-2 rounded-full" 
            style={{ backgroundColor: systemHealth.color }}
          />
          <span className="ultron-heading" style={{ color: systemHealth.color }}>
            SYSTEM {systemHealth.status.toUpperCase()}
          </span>
        </div>
        
        <div className="flex items-center gap-sm text-slate-400">
          <span>CPU: {cpuUsage.toFixed(0)}%</span>
          <span>MEM: {memoryUsage.toFixed(0)}%</span>
          <span>UPTIME: {formatUptime(appUptime)}</span>
        </div>
      </div>
      
      {/* Center - Active model info */}
      <div className="flex-1 flex justify-center">
        {activeModel ? (
          <div className="flex items-center gap-sm">
            <span className="text-slate-400">MODEL:</span>
            <span className="font-medium" style={{ color: 'var(--color-accent-primary)' }}>
              {activeModel.name}
            </span>
            <span className="text-slate-500">
              ({activeModel.details.parameter_size})
            </span>
          </div>
        ) : (
          <span className="text-slate-500">No model selected</span>
        )}
      </div>
      
      {/* Right side - Connection statuses */}
      <div className="flex items-center gap-md">
        {/* Network activity indicator */}
        <div className="flex items-center gap-xs">
          <div className={`w-2 h-2 rounded-full ${
            networkActivity ? 'bg-green-400 pulse' : 'bg-slate-600'
          }`} />
          <span className="text-slate-400">NET</span>
        </div>
        
        {/* Service statuses */}
        <div className="flex items-center gap-xs">
          <div className={`status-indicator ${systemStatus.ollama ? 'online' : 'offline'}`} />
          <span className="text-slate-400">OL</span>
        </div>
        
        <div className="flex items-center gap-xs">
          <div className={`status-indicator ${systemStatus.elevenlabs ? 'online' : 'offline'}`} />
          <span className="text-slate-400">EL</span>
        </div>
        
        <div className="flex items-center gap-xs">
          <div 
            className="w-2 h-2 rounded-full" 
            style={{ backgroundColor: getConnectionColor() }}
          />
          <span className="text-slate-400">WS</span>
        </div>
        
        {/* Current time */}
        <div className="text-slate-400 font-mono">
          {new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
          })}
        </div>
      </div>
    </div>
  )
}
