import React from 'react'
import { useSystemMonitor } from '@/hooks/useSystemMonitor'
import { Cpu, HardDrive, Zap, Thermometer, Clock, Activity } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis } from 'recharts'

export const SystemStats: React.FC = () => {
  const { stats, loading, error } = useSystemMonitor()

  if (loading && !stats) {
    return (
      <div className="p-4 text-center">
        <div className="spinner-ultron mx-auto" />
        <div className="text-sm text-gray-400 mt-2 font-roboto">
          Loading system stats...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-400">
        <Activity className="w-8 h-8 mx-auto mb-2" />
        <div className="text-sm font-roboto">{error}</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="p-4 text-center text-gray-400">
        <Activity className="w-8 h-8 mx-auto mb-2" />
        <div className="text-sm font-roboto">No system data available</div>
      </div>
    )
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400'
      case 'stopped': return 'text-gray-400'
      case 'error': return 'text-red-400'
      default: return 'text-yellow-400'
    }
  }

  const getUsageColor = (usage: number) => {
    if (usage < 50) return 'text-green-400'
    if (usage < 80) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="p-4 space-y-4">
      {/* Ollama Status */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-orbitron font-bold text-sm">OLLAMA STATUS</h3>
          <div className={`w-2 h-2 rounded-full ${getStatusColor(stats.ollama_status)} pulse-red`} />
        </div>
        <div className={`font-roboto text-lg ${getStatusColor(stats.ollama_status)}`}>
          {stats.ollama_status.toUpperCase()}
        </div>
        {stats.active_model && (
          <div className="text-sm text-gray-400 mt-1">
            Active: {stats.active_model}
          </div>
        )}
      </div>

      {/* CPU Usage */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center space-x-2 mb-2">
          <Cpu className="w-4 h-4 text-blue-400" />
          <h3 className="font-orbitron font-bold text-sm">CPU USAGE</h3>
        </div>
        <div className={`font-roboto text-2xl font-bold ${getUsageColor(stats.cpu_usage)}`}>
          {stats.cpu_usage.toFixed(1)}%
        </div>
        <div className="mt-2 bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              stats.cpu_usage < 50 ? 'bg-green-400' : 
              stats.cpu_usage < 80 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${Math.min(stats.cpu_usage, 100)}%` }}
          />
        </div>
      </div>

      {/* Memory Usage */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          <h3 className="font-orbitron font-bold text-sm">MEMORY</h3>
        </div>
        <div className={`font-roboto text-2xl font-bold ${getUsageColor(stats.memory_usage)}`}>
          {stats.memory_usage.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-400">
          {((stats.memory_usage / 100) * stats.memory_total_gb).toFixed(1)}GB / {stats.memory_total_gb}GB
        </div>
        <div className="mt-2 bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              stats.memory_usage < 50 ? 'bg-green-400' : 
              stats.memory_usage < 80 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${Math.min(stats.memory_usage, 100)}%` }}
          />
        </div>
      </div>

      {/* Disk Usage */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center space-x-2 mb-2">
          <HardDrive className="w-4 h-4 text-purple-400" />
          <h3 className="font-orbitron font-bold text-sm">STORAGE</h3>
        </div>
        <div className={`font-roboto text-2xl font-bold ${getUsageColor(stats.disk_usage)}`}>
          {stats.disk_usage.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-400">
          {((stats.disk_usage / 100) * stats.disk_total_gb).toFixed(0)}GB / {stats.disk_total_gb}GB
        </div>
        <div className="mt-2 bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              stats.disk_usage < 50 ? 'bg-green-400' : 
              stats.disk_usage < 80 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${Math.min(stats.disk_usage, 100)}%` }}
          />
        </div>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-2 gap-4">
        {/* GPU Usage */}
        {stats.gpu_usage !== undefined && (
          <div className="glass p-3 rounded-lg border border-red-500/20">
            <div className="text-xs font-orbitron font-bold text-gray-400 mb-1">GPU</div>
            <div className={`font-roboto text-lg font-bold ${getUsageColor(stats.gpu_usage)}`}>
              {stats.gpu_usage.toFixed(1)}%
            </div>
          </div>
        )}

        {/* Temperature */}
        {stats.temperature !== undefined && (
          <div className="glass p-3 rounded-lg border border-red-500/20">
            <div className="flex items-center space-x-1 mb-1">
              <Thermometer className="w-3 h-3 text-orange-400" />
              <div className="text-xs font-orbitron font-bold text-gray-400">TEMP</div>
            </div>
            <div className={`font-roboto text-lg font-bold ${
              stats.temperature < 60 ? 'text-green-400' :
              stats.temperature < 80 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {stats.temperature.toFixed(1)}°C
            </div>
          </div>
        )}
      </div>

      {/* Uptime */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center space-x-2 mb-2">
          <Clock className="w-4 h-4 text-green-400" />
          <h3 className="font-orbitron font-bold text-sm">UPTIME</h3>
        </div>
        <div className="font-roboto text-lg font-bold text-green-400">
          {formatUptime(stats.uptime_seconds)}
        </div>
        <div className="text-xs text-gray-400 mt-1">
          Since last restart
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-xs text-gray-500 text-center font-roboto">
        Last updated: {new Date(stats.recorded_at).toLocaleTimeString()}
      </div>
    </div>
  )
}