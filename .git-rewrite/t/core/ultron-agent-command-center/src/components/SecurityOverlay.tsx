import React, { useState, useEffect } from 'react'

interface SecurityOverlayProps {
  onClose: () => void
  safeMode: boolean
  onSafeModeChange: (enabled: boolean) => void
}

export function SecurityOverlay({ onClose, safeMode, onSafeModeChange }: SecurityOverlayProps) {
  const [pinInput, setPinInput] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showPinPrompt, setShowPinPrompt] = useState(false)
  const [autoLockEnabled, setAutoLockEnabled] = useState(true)
  const [autoLockTimeout, setAutoLockTimeout] = useState(30)
  const [contentFiltering, setContentFiltering] = useState(true)
  const [auditLogging, setAuditLogging] = useState(true)

  const handlePinSubmit = async () => {
    // In a real implementation, this would verify against a stored hash
    if (pinInput === '1234') {
      setIsAuthenticated(true)
      setShowPinPrompt(false)
      
      // Add security event
      try {
        await window.electronAPI.addSecurityEvent(
          'Authentication successful', 
          'success', 
          { method: 'PIN', timestamp: new Date().toISOString() }
        )
        await loadSecurityEvents()
      } catch (error) {
        console.error('Failed to add security event:', error)
      }
    } else {
      // Add failed authentication event
      try {
        await window.electronAPI.addSecurityEvent(
          'Authentication failed - Invalid PIN', 
          'error', 
          { method: 'PIN', timestamp: new Date().toISOString() }
        )
        await loadSecurityEvents()
      } catch (error) {
        console.error('Failed to add security event:', error)
      }
      
      alert('Invalid PIN')
    }
    setPinInput('')
  }

  const handleSafeModeToggle = async () => {
    if (!safeMode && !isAuthenticated) {
      setShowPinPrompt(true)
      return
    }
    
    onSafeModeChange(!safeMode)
    
    // Add security event
    try {
      await window.electronAPI.addSecurityEvent(
        `Safe mode ${!safeMode ? 'enabled' : 'disabled'}`, 
        'info', 
        { previousState: safeMode, newState: !safeMode }
      )
      await loadSecurityEvents() // Refresh events
    } catch (error) {
      console.error('Failed to add security event:', error)
    }
  }

  const [securityEvents, setSecurityEvents] = useState<any[]>([])

  useEffect(() => {
    loadSecurityEvents()
  }, [])

  const loadSecurityEvents = async () => {
    try {
      const events = await window.electronAPI.getSecurityEvents(10)
      setSecurityEvents(events)
    } catch (error) {
      console.error('Failed to load security events:', error)
      // Fallback to mock data
      setSecurityEvents([
        { timestamp: '12:34:56', event: 'Safe mode enabled', level: 'info' },
        { timestamp: '12:33:12', event: 'Tool execution blocked', level: 'warning' },
        { timestamp: '12:30:45', event: 'Authentication successful', level: 'success' },
        { timestamp: '12:28:30', event: 'Permission denied: shell access', level: 'error' },
        { timestamp: '12:25:15', event: 'System startup', level: 'info' }
      ])
    }
  }

  const getEventColor = (level: string) => {
    switch (level) {
      case 'success': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      case 'info': return 'text-blue-400'
      default: return 'text-slate-400'
    }
  }

  const getEventIcon = (level: string) => {
    switch (level) {
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      case 'info': return 'ℹ️'
      default: return '📋'
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-md">
      <div className="ultron-panel max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-md border-b border-slate-700 flex items-center justify-between">
          <h2 className="ultron-heading h2" style={{ color: 'var(--color-accent-primary)' }}>
            SECURITY & PERMISSIONS OVERLAY
          </h2>
          <button
            onClick={onClose}
            className="ultron-button text-xl leading-none p-xs"
          >
            ×
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto ultron-scroll">
          {/* Security Status */}
          <div className="p-md border-b border-slate-700">
            <h3 className="ultron-heading h3 mb-md text-cyan-400">SECURITY STATUS</h3>
            
            <div className="grid grid-cols-2 gap-md">
              <div className="ultron-panel p-sm">
                <div className="flex items-center justify-between mb-xs">
                  <span className="text-sm font-medium">Safe Mode</span>
                  <div className={`status-indicator ${safeMode ? 'online' : 'error'}`} />
                </div>
                <div className="text-xs text-slate-400 mb-sm">
                  {safeMode ? 'System protected from dangerous operations' : 'Full access enabled - use caution'}
                </div>
                <button
                  onClick={handleSafeModeToggle}
                  className={`ultron-button text-xs w-full ${
                    safeMode ? 'danger' : 'primary'
                  }`}
                >
                  {safeMode ? 'DISABLE SAFE MODE' : 'ENABLE SAFE MODE'}
                </button>
              </div>
              
              <div className="ultron-panel p-sm">
                <div className="flex items-center justify-between mb-xs">
                  <span className="text-sm font-medium">Authentication</span>
                  <div className={`status-indicator ${isAuthenticated ? 'online' : 'offline'}`} />
                </div>
                <div className="text-xs text-slate-400 mb-sm">
                  {isAuthenticated ? 'Authenticated session active' : 'No active authentication'}
                </div>
                <button
                  onClick={() => setIsAuthenticated(!isAuthenticated)}
                  className="ultron-button text-xs w-full"
                >
                  {isAuthenticated ? 'SIGN OUT' : 'AUTHENTICATE'}
                </button>
              </div>
            </div>
          </div>
          
          {/* Permission Settings */}
          <div className="p-md border-b border-slate-700">
            <h3 className="ultron-heading h3 mb-md text-yellow-400">PERMISSION SETTINGS</h3>
            
            <div className="space-y-sm">
              <div className="flex items-center justify-between ultron-panel p-sm">
                <div>
                  <div className="text-sm font-medium">Auto-Lock</div>
                  <div className="text-xs text-slate-400">Automatically lock after inactivity</div>
                </div>
                <label className="flex items-center gap-xs">
                  <input
                    type="checkbox"
                    checked={autoLockEnabled}
                    onChange={(e) => setAutoLockEnabled(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                    autoLockEnabled ? 'border-cyan-500 bg-cyan-500' : 'border-slate-500'
                  }`}>
                    {autoLockEnabled && <div className="w-2 h-2 bg-white rounded" />}
                  </div>
                </label>
              </div>
              
              {autoLockEnabled && (
                <div className="ultron-panel p-sm">
                  <label className="text-sm mb-xs block">Auto-lock timeout (minutes):</label>
                  <input
                    type="range"
                    min="5"
                    max="120"
                    value={autoLockTimeout}
                    onChange={(e) => setAutoLockTimeout(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-xs text-slate-400 mt-xs">{autoLockTimeout} minutes</div>
                </div>
              )}
              
              <div className="flex items-center justify-between ultron-panel p-sm">
                <div>
                  <div className="text-sm font-medium">Content Filtering</div>
                  <div className="text-xs text-slate-400">Filter potentially harmful content</div>
                </div>
                <label className="flex items-center gap-xs">
                  <input
                    type="checkbox"
                    checked={contentFiltering}
                    onChange={(e) => setContentFiltering(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                    contentFiltering ? 'border-cyan-500 bg-cyan-500' : 'border-slate-500'
                  }`}>
                    {contentFiltering && <div className="w-2 h-2 bg-white rounded" />}
                  </div>
                </label>
              </div>
              
              <div className="flex items-center justify-between ultron-panel p-sm">
                <div>
                  <div className="text-sm font-medium">Audit Logging</div>
                  <div className="text-xs text-slate-400">Log all security events</div>
                </div>
                <label className="flex items-center gap-xs">
                  <input
                    type="checkbox"
                    checked={auditLogging}
                    onChange={(e) => setAuditLogging(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                    auditLogging ? 'border-cyan-500 bg-cyan-500' : 'border-slate-500'
                  }`}>
                    {auditLogging && <div className="w-2 h-2 bg-white rounded" />}
                  </div>
                </label>
              </div>
            </div>
          </div>
          
          {/* Security Events Log */}
          <div className="p-md">
            <h3 className="ultron-heading h3 mb-md text-red-400">SECURITY EVENTS</h3>
            
            <div className="space-y-xs">
              {securityEvents.map((event, index) => (
                <div key={index} className="ultron-panel p-sm">
                  <div className="flex items-center gap-sm">
                    <span className="text-sm">{getEventIcon(event.level)}</span>
                    <div className="flex-1">
                      <div className={`text-sm ${getEventColor(event.level)}`}>
                        {event.event}
                      </div>
                      <div className="text-xs text-slate-500">
                        {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : event.time}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* PIN Input Modal */}
        {showPinPrompt && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="ultron-panel p-md m-md max-w-sm">
              <h4 className="ultron-heading h4 mb-sm text-yellow-400">AUTHENTICATION REQUIRED</h4>
              <p className="text-sm text-slate-300 mb-md">
                Enter PIN to disable safe mode
              </p>
              <input
                type="password"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value)}
                placeholder="Enter PIN..."
                className="ultron-input w-full mb-md text-center font-mono"
                maxLength={6}
                onKeyPress={(e) => e.key === 'Enter' && handlePinSubmit()}
              />
              <div className="flex gap-sm">
                <button
                  onClick={() => {
                    setShowPinPrompt(false)
                    setPinInput('')
                  }}
                  className="ultron-button flex-1"
                >
                  CANCEL
                </button>
                <button
                  onClick={handlePinSubmit}
                  className="ultron-button primary flex-1"
                  disabled={!pinInput}
                >
                  CONFIRM
                </button>
              </div>
              <div className="text-xs text-slate-500 mt-sm text-center">
                Default PIN: 1234 (for demo)
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
