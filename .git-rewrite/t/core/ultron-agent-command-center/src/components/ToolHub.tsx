import React, { useState, useEffect } from 'react'

interface ToolHubProps {
  onToolExecute: (toolName: string, params: any) => Promise<any>
  safeMode: boolean
}

export function ToolHub({ onToolExecute, safeMode }: ToolHubProps) {
  const [activeTab, setActiveTab] = useState<'tools' | 'logs' | 'settings'>('tools')
  const [executionLogs, setExecutionLogs] = useState<any[]>([])
  const [isExecuting, setIsExecuting] = useState(false)
  const [webUrl, setWebUrl] = useState('')
  const [pythonCode, setPythonCode] = useState('')
  const [filePath, setFilePath] = useState('')
  const [fileContent, setFileContent] = useState('')
  const [shellCommand, setShellCommand] = useState('')

  const addLog = (log: any) => {
    setExecutionLogs(prev => [{
      ...log,
      timestamp: new Date().toISOString(),
      id: Date.now()
    }, ...prev.slice(0, 49)])
  }

  const executeWebFetch = async () => {
    if (!webUrl) return
    
    setIsExecuting(true)
    addLog({ type: 'info', message: `Fetching: ${webUrl}`, tool: 'web-fetch' })
    
    try {
      const result = await onToolExecute('web-fetch', { url: webUrl })
      addLog({ 
        type: 'success', 
        message: `Fetched ${webUrl}`, 
        tool: 'web-fetch',
        result: {
          status: result.result?.status,
          size: result.result?.data?.length || 0
        }
      })
      setWebUrl('')
    } catch (error) {
      addLog({ 
        type: 'error', 
        message: `Failed to fetch ${webUrl}`, 
        tool: 'web-fetch',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const executePython = async () => {
    if (!pythonCode) return
    
    setIsExecuting(true)
    addLog({ type: 'info', message: 'Executing Python code', tool: 'python-exec' })
    
    try {
      const result = await onToolExecute('python-exec', { code: pythonCode })
      addLog({ 
        type: result.success ? 'success' : 'error', 
        message: result.success ? 'Python executed successfully' : 'Python execution failed', 
        tool: 'python-exec',
        result: result.output || result.error
      })
      if (result.success) setPythonCode('')
    } catch (error) {
      addLog({ 
        type: 'error', 
        message: 'Python execution error', 
        tool: 'python-exec',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const readFile = async () => {
    if (!filePath) return
    
    setIsExecuting(true)
    addLog({ type: 'info', message: `Reading file: ${filePath}`, tool: 'file-read' })
    
    try {
      const result = await onToolExecute('file-read', { path: filePath })
      addLog({ 
        type: result.success ? 'success' : 'error', 
        message: result.success ? `File read: ${filePath}` : `Failed to read: ${filePath}`, 
        tool: 'file-read',
        result: result.success ? `${result.result?.length || 0} characters` : result.error
      })
      if (result.success && result.result) {
        setFileContent(result.result)
      }
    } catch (error) {
      addLog({ 
        type: 'error', 
        message: `File read error: ${filePath}`, 
        tool: 'file-read',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const writeFile = async () => {
    if (!filePath || !fileContent) return
    
    setIsExecuting(true)
    addLog({ type: 'info', message: `Writing file: ${filePath}`, tool: 'file-write' })
    
    try {
      const result = await onToolExecute('file-write', { path: filePath, content: fileContent })
      addLog({ 
        type: result.success ? 'success' : 'error', 
        message: result.success ? `File written: ${filePath}` : `Failed to write: ${filePath}`, 
        tool: 'file-write',
        result: result.success ? `${fileContent.length} characters` : result.error
      })
      if (result.success) {
        setFileContent('')
      }
    } catch (error) {
      addLog({ 
        type: 'error', 
        message: `File write error: ${filePath}`, 
        tool: 'file-write',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const executeShell = async () => {
    if (!shellCommand) return
    
    setIsExecuting(true)
    addLog({ type: 'info', message: `Executing: ${shellCommand}`, tool: 'shell-exec' })
    
    try {
      const result = await onToolExecute('shell-exec', { command: shellCommand })
      addLog({ 
        type: result.success ? 'success' : 'error', 
        message: result.success ? `Command executed: ${shellCommand}` : `Command failed: ${shellCommand}`, 
        tool: 'shell-exec',
        result: result.output || result.error
      })
      if (result.success) setShellCommand('')
    } catch (error) {
      addLog({ 
        type: 'error', 
        message: `Shell execution error: ${shellCommand}`, 
        tool: 'shell-exec',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const clearLogs = () => {
    setExecutionLogs([])
  }

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'success': return '✅'
      case 'error': return '❌'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      default: return '📋'
    }
  }

  const getLogColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-400'
      case 'error': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      case 'info': return 'text-blue-400'
      default: return 'text-slate-400'
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-md border-b border-slate-700">
        <h3 className="ultron-heading h3 mb-sm" style={{ color: 'var(--color-accent-primary)' }}>
          TOOL & API COMMAND HUB
        </h3>
        
        {/* Tabs */}
        <div className="flex gap-xs">
          {(['tools', 'logs', 'settings'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`ultron-button text-xs ${
                activeTab === tab ? 'primary' : ''
              }`}
            >
              {tab.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'tools' && (
          <div className="p-md space-y-md overflow-y-auto ultron-scroll h-full">
            {/* Web Fetch */}
            <div className="ultron-panel p-sm">
              <h4 className="ultron-heading h4 mb-sm text-cyan-400">WEB FETCH</h4>
              <div className="space-y-sm">
                <input
                  type="url"
                  placeholder="Enter URL..."
                  value={webUrl}
                  onChange={(e) => setWebUrl(e.target.value)}
                  className="ultron-input w-full text-sm"
                />
                <button
                  onClick={executeWebFetch}
                  disabled={!webUrl || isExecuting}
                  className="ultron-button primary text-sm"
                >
                  FETCH
                </button>
              </div>
            </div>
            
            {/* Python Execution */}
            <div className="ultron-panel p-sm">
              <h4 className="ultron-heading h4 mb-sm text-green-400">PYTHON SANDBOX</h4>
              <div className="space-y-sm">
                <textarea
                  placeholder="Enter Python code..."
                  value={pythonCode}
                  onChange={(e) => setPythonCode(e.target.value)}
                  className="ultron-input w-full text-sm h-20 resize-none font-mono"
                />
                <div className="flex gap-sm">
                  <button
                    onClick={executePython}
                    disabled={!pythonCode || isExecuting}
                    className="ultron-button primary text-sm flex-1"
                  >
                    EXECUTE
                  </button>
                  <button
                    onClick={() => setPythonCode('')}
                    className="ultron-button text-sm"
                  >
                    CLEAR
                  </button>
                </div>
              </div>
            </div>
            
            {/* File Operations */}
            <div className="ultron-panel p-sm">
              <h4 className="ultron-heading h4 mb-sm text-yellow-400">FILE OPERATIONS</h4>
              <div className="space-y-sm">
                <input
                  type="text"
                  placeholder="File path..."
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  className="ultron-input w-full text-sm"
                />
                <div className="flex gap-sm">
                  <button
                    onClick={readFile}
                    disabled={!filePath || isExecuting}
                    className="ultron-button text-sm flex-1"
                  >
                    READ
                  </button>
                  <button
                    onClick={writeFile}
                    disabled={!filePath || !fileContent || isExecuting}
                    className="ultron-button primary text-sm flex-1"
                  >
                    WRITE
                  </button>
                </div>
                <textarea
                  placeholder="File content..."
                  value={fileContent}
                  onChange={(e) => setFileContent(e.target.value)}
                  className="ultron-input w-full text-sm h-16 resize-none font-mono"
                />
              </div>
            </div>
            
            {/* Shell Commands */}
            <div className="ultron-panel p-sm">
              <h4 className="ultron-heading h4 mb-sm text-red-400">SHELL EXECUTION</h4>
              <div className="space-y-sm">
                <input
                  type="text"
                  placeholder="Shell command..."
                  value={shellCommand}
                  onChange={(e) => setShellCommand(e.target.value)}
                  className="ultron-input w-full text-sm font-mono"
                />
                <button
                  onClick={executeShell}
                  disabled={!shellCommand || isExecuting || safeMode}
                  className="ultron-button danger text-sm w-full"
                >
                  {safeMode ? 'DISABLED (SAFE MODE)' : 'EXECUTE'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'logs' && (
          <div className="flex flex-col h-full">
            <div className="p-sm border-b border-slate-700 flex justify-between items-center">
              <span className="text-sm text-slate-400">{executionLogs.length} logs</span>
              <button onClick={clearLogs} className="ultron-button text-xs">
                CLEAR
              </button>
            </div>
            <div className="flex-1 overflow-y-auto ultron-scroll p-sm">
              {executionLogs.length === 0 ? (
                <div className="text-center text-slate-400 mt-md">No logs yet</div>
              ) : (
                <div className="space-y-sm">
                  {executionLogs.map(log => (
                    <div key={log.id} className="ultron-panel p-sm">
                      <div className="flex items-start gap-sm">
                        <span className="text-sm">{getLogIcon(log.type)}</span>
                        <div className="flex-1">
                          <div className={`text-sm ${getLogColor(log.type)}`}>
                            {log.message}
                          </div>
                          <div className="text-xs text-slate-500">
                            {log.tool} • {new Date(log.timestamp).toLocaleTimeString()}
                          </div>
                          {log.result && (
                            <div className="text-xs text-slate-400 mt-xs font-mono">
                              {typeof log.result === 'string' ? log.result : JSON.stringify(log.result)}
                            </div>
                          )}
                          {log.error && (
                            <div className="text-xs text-red-400 mt-xs font-mono">
                              {log.error}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="p-md">
            <div className="space-y-md">
              <div className="ultron-panel p-sm">
                <h4 className="ultron-heading h4 mb-sm">SECURITY SETTINGS</h4>
                <div className="space-y-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Safe Mode</span>
                    <div className={`status-indicator ${safeMode ? 'online' : 'offline'}`} />
                  </div>
                  <div className="text-xs text-slate-400">
                    {safeMode ? 'Dangerous operations blocked' : 'All operations allowed'}
                  </div>
                </div>
              </div>
              
              <div className="ultron-panel p-sm">
                <h4 className="ultron-heading h4 mb-sm">EXECUTION STATS</h4>
                <div className="space-y-sm text-sm">
                  <div className="flex justify-between">
                    <span>Total Executions:</span>
                    <span>{executionLogs.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Successful:</span>
                    <span className="text-green-400">
                      {executionLogs.filter(log => log.type === 'success').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Failed:</span>
                    <span className="text-red-400">
                      {executionLogs.filter(log => log.type === 'error').length}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Status */}
      {isExecuting && (
        <div className="p-sm border-t border-slate-700">
          <div className="flex items-center gap-sm">
            <div className="status-indicator warning pulse" />
            <span className="text-sm text-yellow-400">Executing...</span>
          </div>
        </div>
      )}
    </div>
  )
}
