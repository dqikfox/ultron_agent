import React from 'react'
import { useSystemMonitor } from '@/hooks/useSystemMonitor'
import { useOllama } from '@/hooks/useOllama'
import { 
  RefreshCw, 
  Download, 
  Trash2, 
  Settings, 
  Terminal, 
  FileText,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'

export const QuickActions: React.FC = () => {
  const { getStats, getLogs, loading } = useSystemMonitor()
  const { loadModels } = useOllama()

  const actions = [
    {
      id: 'refresh-stats',
      label: 'Refresh Stats',
      icon: RefreshCw,
      action: getStats,
      description: 'Update system statistics'
    },
    {
      id: 'refresh-models',
      label: 'Refresh Models',
      icon: Download,
      action: loadModels,
      description: 'Reload available models'
    },
    {
      id: 'refresh-logs',
      label: 'Refresh Logs',
      icon: FileText,
      action: () => getLogs(50),
      description: 'Update system logs'
    },
    {
      id: 'clear-cache',
      label: 'Clear Cache',
      icon: Trash2,
      action: () => {
        localStorage.clear()
        window.location.reload()
      },
      description: 'Clear browser cache'
    }
  ]

  const handleAction = async (actionFn: () => void | Promise<void>) => {
    try {
      await actionFn()
    } catch (error) {
      console.error('Action failed:', error)
    }
  }

  return (
    <div className="p-4 space-y-4">
      {/* Quick Actions */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <h3 className="font-orbitron font-bold text-sm mb-4">QUICK ACTIONS</h3>
        <div className="space-y-2">
          {actions.map((action) => {
            const Icon = action.icon
            return (
              <button
                key={action.id}
                onClick={() => handleAction(action.action)}
                disabled={loading}
                className="w-full btn-ultron flex items-center space-x-3 p-3 text-left disabled:opacity-50"
              >
                <Icon className="w-4 h-4" />
                <div className="flex-1">
                  <div className="font-medium">{action.label}</div>
                  <div className="text-xs text-gray-400">{action.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* System Commands */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <h3 className="font-orbitron font-bold text-sm mb-4">SYSTEM COMMANDS</h3>
        <div className="space-y-2">
          <button
            onClick={() => window.open('http://localhost:11434', '_blank')}
            className="w-full btn-ultron flex items-center space-x-3 p-3 text-left"
          >
            <Terminal className="w-4 h-4" />
            <div className="flex-1">
              <div className="font-medium">Open Ollama</div>
              <div className="text-xs text-gray-400">localhost:11434</div>
            </div>
          </button>
          
          <button
            onClick={() => window.open('/api/health', '_blank')}
            className="w-full btn-ultron flex items-center space-x-3 p-3 text-left"
          >
            <Activity className="w-4 h-4" />
            <div className="flex-1">
              <div className="font-medium">Health Check</div>
              <div className="text-xs text-gray-400">System diagnostics</div>
            </div>
          </button>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <h3 className="font-orbitron font-bold text-sm mb-4">STATUS INDICATORS</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <div className="text-sm font-roboto">
              <div className="font-medium">Online</div>
              <div className="text-xs text-gray-400">System operational</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            <div className="text-sm font-roboto">
              <div className="font-medium">Warning</div>
              <div className="text-xs text-gray-400">Monitor resources</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Clock className="w-4 h-4 text-blue-400" />
            <div className="text-sm font-roboto">
              <div className="font-medium">Pending</div>
              <div className="text-xs text-gray-400">Processing requests</div>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <h3 className="font-orbitron font-bold text-sm mb-4">SYSTEM INFO</h3>
        <div className="space-y-2 text-sm font-roboto">
          <div className="flex justify-between">
            <span className="text-gray-400">Version:</span>
            <span className="text-red-400">v1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Build:</span>
            <span className="text-red-400">#{Date.now().toString().slice(-6)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Platform:</span>
            <span className="text-red-400">Web</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Status:</span>
            <span className="text-green-400">Operational</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-gray-500 font-roboto">
        Ultron Supreme AI Command Center
        <br />
        Powered by Ollama & Supabase
      </div>
    </div>
  )
}