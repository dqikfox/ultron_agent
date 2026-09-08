import React, { useState, useEffect } from 'react'
import { OllamaModel } from '../hooks/useAppState'

interface UltronCoreProps {
  activeModel: OllamaModel | null
  systemStatus: {
    ollama: boolean
    elevenlabs: boolean
    websocket: boolean
  }
  isProcessing: boolean
}

export function UltronCore({ activeModel, systemStatus, isProcessing }: UltronCoreProps) {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [eyeGlow, setEyeGlow] = useState(false)
  const [scanlinePosition, setScanlinePosition] = useState(0)

  useEffect(() => {
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timeInterval)
  }, [])

  useEffect(() => {
    const glowInterval = setInterval(() => {
      setEyeGlow(prev => !prev)
    }, 2000)

    return () => clearInterval(glowInterval)
  }, [])

  useEffect(() => {
    const scanlineInterval = setInterval(() => {
      setScanlinePosition(prev => (prev + 1) % 100)
    }, 100)

    return () => clearInterval(scanlineInterval)
  }, [])

  const getSystemStatusColor = () => {
    const onlineCount = Object.values(systemStatus).filter(status => status).length
    const total = Object.keys(systemStatus).length
    
    if (onlineCount === total) return 'var(--color-accent-success)'
    if (onlineCount > 0) return 'var(--color-accent-warning)'
    return 'var(--color-accent-danger)'
  }

  const getModelStatusText = () => {
    if (!activeModel) return 'NO MODEL SELECTED'
    if (isProcessing) return 'PROCESSING...'
    return 'STANDBY'
  }

  return (
    <div className="relative flex items-center justify-center h-full bg-gradient-to-br from-black/40 to-slate-900/40 overflow-hidden">
      {/* Background circuit pattern */}
      <div className="absolute inset-0 opacity-10">
        <svg width="100%" height="100%" className="absolute inset-0">
          <defs>
            <pattern id="circuit" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
              <g stroke="var(--color-accent-primary)" strokeWidth="0.5" fill="none">
                <rect x="10" y="10" width="20" height="20" />
                <rect x="50" y="30" width="15" height="15" />
                <rect x="70" y="10" width="25" height="25" />
                <circle cx="20" cy="70" r="8" />
                <circle cx="80" cy="80" r="6" />
                <line x1="30" y1="20" x2="50" y2="37" />
                <line x1="65" y1="37" x2="70" y2="22" />
                <line x1="20" y1="62" x2="20" y2="45" />
                <line x1="74" y1="80" x2="95" y2="22" />
              </g>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#circuit)" />
        </svg>
      </div>

      {/* Scanline effect */}
      <div 
        className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-pink-500 to-transparent opacity-60"
        style={{
          top: `${scanlinePosition}%`,
          transition: 'top 0.1s linear'
        }}
      />

      {/* Central Ultron Head */}
      <div className="relative">
        {/* Head outline */}
        <div className="w-32 h-40 relative">
          <svg viewBox="0 0 100 120" className="w-full h-full">
            <defs>
              <linearGradient id="headGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#1a1a1a" />
                <stop offset="50%" stopColor="#2a2a2a" />
                <stop offset="100%" stopColor="#0a0a0a" />
              </linearGradient>
              <filter id="glow">
                <feMorphology operator="dilate" radius="2"/>
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge> 
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/> 
                </feMerge>
              </filter>
            </defs>
            
            {/* Head shape */}
            <path
              d="M20 30 L80 30 L85 40 L85 80 L75 100 L25 100 L15 80 L15 40 Z"
              fill="url(#headGradient)"
              stroke="var(--color-accent-primary)"
              strokeWidth="1"
              filter="url(#glow)"
            />
            
            {/* Face segments */}
            <line x1="15" y1="50" x2="85" y2="50" stroke="var(--color-accent-primary)" strokeWidth="0.5" opacity="0.7" />
            <line x1="15" y1="65" x2="85" y2="65" stroke="var(--color-accent-primary)" strokeWidth="0.5" opacity="0.7" />
            <line x1="30" y1="30" x2="30" y2="100" stroke="var(--color-accent-primary)" strokeWidth="0.5" opacity="0.5" />
            <line x1="70" y1="30" x2="70" y2="100" stroke="var(--color-accent-primary)" strokeWidth="0.5" opacity="0.5" />
            
            {/* Eyes */}
            <circle 
              cx="35" 
              cy="45" 
              r="4" 
              fill="var(--color-accent-danger)"
              className={eyeGlow || isProcessing ? 'glow-animate' : ''}
            />
            <circle 
              cx="65" 
              cy="45" 
              r="4" 
              fill="var(--color-accent-danger)"
              className={eyeGlow || isProcessing ? 'glow-animate' : ''}
            />
            
            {/* Mouth/speaker grille */}
            <rect x="40" y="70" width="20" height="8" fill="none" stroke="var(--color-accent-primary)" strokeWidth="1" />
            <line x1="42" y1="72" x2="42" y2="76" stroke="var(--color-accent-primary)" strokeWidth="0.5" />
            <line x1="46" y1="72" x2="46" y2="76" stroke="var(--color-accent-primary)" strokeWidth="0.5" />
            <line x1="50" y1="72" x2="50" y2="76" stroke="var(--color-accent-primary)" strokeWidth="0.5" />
            <line x1="54" y1="72" x2="54" y2="76" stroke="var(--color-accent-primary)" strokeWidth="0.5" />
            <line x1="58" y1="72" x2="58" y2="76" stroke="var(--color-accent-primary)" strokeWidth="0.5" />
          </svg>
        </div>
        
        {/* Status rings around head */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div 
            className="w-48 h-48 rounded-full border-2 opacity-30 animate-spin"
            style={{ 
              borderColor: getSystemStatusColor(),
              animationDuration: '20s'
            }}
          />
        </div>
        
        <div className="absolute inset-0 flex items-center justify-center">
          <div 
            className="w-56 h-56 rounded-full border opacity-20 animate-spin"
            style={{ 
              borderColor: getSystemStatusColor(),
              animationDuration: '30s',
              animationDirection: 'reverse'
            }}
          />
        </div>
      </div>

      {/* Status Information */}
      <div className="absolute top-4 left-4">
        <div className="ultron-panel p-sm space-y-xs">
          <div className="text-xs ultron-heading" style={{ color: 'var(--color-accent-primary)' }}>
            SYSTEM STATUS
          </div>
          <div className="space-y-xs text-xs">
            <div className="flex items-center gap-xs">
              <div className={`status-indicator ${systemStatus.ollama ? 'online' : 'offline'}`} />
              <span>OLLAMA</span>
            </div>
            <div className="flex items-center gap-xs">
              <div className={`status-indicator ${systemStatus.elevenlabs ? 'online' : 'offline'}`} />
              <span>ELEVENLABS</span>
            </div>
            <div className="flex items-center gap-xs">
              <div className={`status-indicator ${systemStatus.websocket ? 'online' : 'offline'}`} />
              <span>WEBSOCKET</span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Model Info */}
      <div className="absolute top-4 right-4">
        <div className="ultron-panel p-sm">
          <div className="text-xs ultron-heading mb-xs" style={{ color: 'var(--color-accent-primary)' }}>
            ACTIVE MODEL
          </div>
          {activeModel ? (
            <div className="text-xs space-y-xs">
              <div className="font-bold">{activeModel.name}</div>
              <div className="text-slate-400">{activeModel.details.parameter_size}</div>
              <div className="text-slate-500">
                {(activeModel.size / (1024 * 1024 * 1024)).toFixed(1)}GB
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-400">No model selected</div>
          )}
        </div>
      </div>

      {/* Time and Status */}
      <div className="absolute bottom-4 left-4">
        <div className="ultron-panel p-sm">
          <div className="text-xs ultron-heading mb-xs" style={{ color: 'var(--color-accent-primary)' }}>
            MISSION TIME
          </div>
          <div className="text-sm font-mono">
            {currentTime.toLocaleTimeString()}
          </div>
          <div className="text-xs text-slate-400 mt-xs">
            {currentTime.toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Processing Status */}
      <div className="absolute bottom-4 right-4">
        <div className="ultron-panel p-sm">
          <div className="text-xs ultron-heading mb-xs" style={{ color: 'var(--color-accent-primary)' }}>
            STATUS
          </div>
          <div className={`text-sm font-bold ${
            isProcessing ? 'text-yellow-400 pulse' : 'text-green-400'
          }`}>
            {getModelStatusText()}
          </div>
        </div>
      </div>

      {/* Central processing indicator */}
      {isProcessing && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-64 h-64 rounded-full border-2 border-pink-500 opacity-20 animate-ping" />
        </div>
      )}
    </div>
  )
}
