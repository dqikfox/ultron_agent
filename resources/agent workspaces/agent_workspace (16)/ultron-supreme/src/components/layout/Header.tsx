import React from 'react'
import { UltronLogo } from '@/components/ui/UltronLogo'
import { useAuth } from '@/contexts/AuthContext'
import { useSystemMonitor } from '@/hooks/useSystemMonitor'
import { useOllama } from '@/hooks/useOllama'
import { Settings, Activity, Zap, User } from 'lucide-react'

interface HeaderProps {
  onSettingsClick: () => void
  onLogsClick: () => void
}

export const Header: React.FC<HeaderProps> = ({ onSettingsClick, onLogsClick }) => {
  const { user, signOut } = useAuth()
  const { stats } = useSystemMonitor()
  const { ollamaStatus } = useOllama()

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400'
      case 'stopped': return 'text-gray-400'
      case 'error': return 'text-red-400'
      default: return 'text-yellow-400'
    }
  }

  return (
    <header className="glass-intense border-b border-red-500/20 p-4">
      <div className="flex items-center justify-between">
        {/* Left: Logo and Title */}
        <div className="flex items-center space-x-4">
          <UltronLogo size="lg" />
          <div>
            <h1 className="font-orbitron text-2xl font-bold text-glow-red">
              ULTRON SUPREME
            </h1>
            <p className="text-sm text-gray-400 font-roboto">
              AI Command Center
            </p>
          </div>
        </div>

        {/* Center: System Status */}
        <div className="hidden md:flex items-center space-x-6">
          {/* Ollama Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getStatusColor(ollamaStatus)} pulse-red`} />
            <span className="text-sm font-orbitron">
              Ollama: <span className={getStatusColor(ollamaStatus)}>{ollamaStatus.toUpperCase()}</span>
            </span>
          </div>

          {/* CPU Status */}
          {stats && (
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-roboto">
                CPU: <span className="text-blue-400">{stats.cpu_usage.toFixed(1)}%</span>
              </span>
            </div>
          )}

          {/* Memory Status */}
          {stats && (
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-roboto">
                RAM: <span className="text-yellow-400">{stats.memory_usage.toFixed(1)}%</span>
              </span>
            </div>
          )}
        </div>

        {/* Right: User Actions */}
        <div className="flex items-center space-x-3">
          {/* Logs Button */}
          <button
            onClick={onLogsClick}
            className="btn-ultron p-2 text-sm"
            title="View Logs"
          >
            <Activity className="w-4 h-4" />
          </button>

          {/* Settings Button */}
          <button
            onClick={onSettingsClick}
            className="btn-ultron p-2 text-sm"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* User Menu */}
          <div className="flex items-center space-x-2">
            {user ? (
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center">
                  <User className="w-4 h-4" />
                </div>
                <div className="hidden sm:block">
                  <div className="text-sm font-medium">{user.email}</div>
                  <button
                    onClick={() => signOut()}
                    className="text-xs text-gray-400 hover:text-red-400 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-400">
                Guest Mode
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Status Bar */}
      <div className="md:hidden mt-3 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-4">
          <span className={`${getStatusColor(ollamaStatus)}`}>
            Ollama: {ollamaStatus.toUpperCase()}
          </span>
          {stats && (
            <>
              <span className="text-blue-400">CPU: {stats.cpu_usage.toFixed(1)}%</span>
              <span className="text-yellow-400">RAM: {stats.memory_usage.toFixed(1)}%</span>
            </>
          )}
        </div>
      </div>
    </header>
  )
}