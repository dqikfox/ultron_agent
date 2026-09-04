import React, { useState, useEffect } from 'react'
import { X, Download, Filter, RefreshCw, Clock, User, Activity } from 'lucide-react'
import { useSystemMonitor, SystemLog } from '@/hooks/useSystemMonitor'

interface LogsOverlayProps {
  onClose: () => void
}

export const LogsOverlay: React.FC<LogsOverlayProps> = ({ onClose }) => {
  const { logs, getLogs, loading } = useSystemMonitor()
  const [filter, setFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [limit, setLimit] = useState(100)

  useEffect(() => {
    getLogs(limit)
  }, [limit, getLogs])

  const filteredLogs = logs.filter(log => {
    const matchesText = filter === '' || 
      log.action_description.toLowerCase().includes(filter.toLowerCase()) ||
      log.action_type.toLowerCase().includes(filter.toLowerCase())
    
    const matchesStatus = statusFilter === '' || log.status === statusFilter
    
    return matchesText && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400'
      case 'error': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      case 'info': return 'text-blue-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500/20 border-green-500/30'
      case 'error': return 'bg-red-500/20 border-red-500/30'
      case 'warning': return 'bg-yellow-500/20 border-yellow-500/30'
      case 'info': return 'bg-blue-500/20 border-blue-500/30'
      default: return 'bg-gray-500/20 border-gray-500/30'
    }
  }

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'ollama_chat': return '💬'
      case 'ollama_models_list': return '🤖'
      case 'system_monitor': return '📊'
      case 'file_upload': return '📎'
      default: return '⚡'
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  }

  const exportLogs = () => {
    const exportData = filteredLogs.map(log => ({
      timestamp: log.created_at,
      type: log.action_type,
      status: log.status,
      description: log.action_description,
      metadata: log.metadata
    }))
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ultron-logs-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-intense rounded-lg border border-red-500/30 w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-red-500/20">
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6 text-red-400" />
            <h2 className="font-orbitron text-xl font-bold text-glow-red">
              SYSTEM LOGS
            </h2>
            <div className="text-sm text-gray-400 font-roboto">
              ({filteredLogs.length} entries)
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-red-400 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Controls */}
        <div className="p-4 border-b border-red-500/20 space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search Filter */}
            <div className="flex-1 min-w-[200px]">
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Search logs..."
                className="input-ultron w-full"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-ultron"
            >
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>

            {/* Limit */}
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="input-ultron"
            >
              <option value={50}>50 entries</option>
              <option value={100}>100 entries</option>
              <option value={200}>200 entries</option>
              <option value={500}>500 entries</option>
            </select>

            {/* Actions */}
            <button
              onClick={() => getLogs(limit)}
              disabled={loading}
              className="btn-ultron flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>

            <button
              onClick={exportLogs}
              className="btn-ultron flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Logs List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading && logs.length === 0 ? (
            <div className="text-center py-12">
              <div className="spinner-ultron mx-auto mb-4" />
              <div className="text-gray-400 font-roboto">Loading logs...</div>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <div className="text-gray-400 font-roboto">
                {logs.length === 0 ? 'No logs available' : 'No logs match your filters'}
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className={`glass p-4 rounded-lg border ${getStatusBg(log.status)} hover:border-red-500/50 transition-colors`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Header */}
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-lg">{getActionIcon(log.action_type)}</span>
                        <div className="font-orbitron font-bold text-sm">
                          {log.action_type.toUpperCase().replace('_', ' ')}
                        </div>
                        <div className={`px-2 py-1 rounded text-xs font-roboto ${getStatusColor(log.status)}`}>
                          {log.status.toUpperCase()}
                        </div>
                      </div>

                      {/* Description */}
                      <div className="font-roboto text-gray-300 mb-2">
                        {log.action_description}
                      </div>

                      {/* Metadata */}
                      {log.metadata && Object.keys(log.metadata).length > 0 && (
                        <div className="text-xs text-gray-500 font-mono">
                          {Object.entries(log.metadata).map(([key, value]) => (
                            <span key={key} className="mr-3">
                              {key}: {JSON.stringify(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Timestamp */}
                    <div className="flex items-center space-x-2 text-xs text-gray-400 font-roboto">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(log.created_at)}</span>
                    </div>
                  </div>

                  {/* User Info */}
                  {log.user_id && (
                    <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-gray-600">
                      <User className="w-3 h-3 text-gray-500" />
                      <span className="text-xs text-gray-500 font-roboto">
                        User: {log.user_id.slice(0, 8)}...
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-red-500/20 text-center text-xs text-gray-500 font-roboto">
          Showing {filteredLogs.length} of {logs.length} log entries
          {filter && ` • Filtered by: "${filter}"`}
          {statusFilter && ` • Status: ${statusFilter}`}
        </div>
      </div>
    </div>
  )
}