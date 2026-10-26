import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { useSystemMonitoring } from '../hooks/useSystemMonitoring'
import {
  CpuChipIcon,
  CircleStackIcon,
  ServerIcon,
  SignalIcon,
  FireIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline'

export function SystemMonitoring() {
  const { stats, isConnected } = useSystemMonitoring()

  const StatCard = ({ title, value, unit, icon: Icon, color, percentage }: any) => (
    <Card className="glass-morphism border-ultron-blue/30">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Icon className={`w-6 h-6 text-${color}`} />
            <h3 className="text-sm font-medium text-gray-300">{title}</h3>
          </div>
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
          }`} />
        </div>
        
        <div className="space-y-3">
          <div className="text-2xl font-bold text-white">
            {typeof value === 'number' ? value.toFixed(1) : value}
            <span className="text-sm text-gray-400 ml-1">{unit}</span>
          </div>
          
          {percentage !== undefined && (
            <div className="space-y-1">
              <div className="w-full bg-ultron-darker rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  className={`h-2 bg-gradient-to-r from-${color} to-ultron-purple rounded-full`}
                />
              </div>
              <div className="text-xs text-gray-400 text-right">
                {percentage.toFixed(1)}%
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-orbitron font-bold text-white mb-2">
            System Neural Monitor
          </h2>
          <p className="text-gray-400">
            Real-time system performance and resource utilization
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-400' : 'bg-red-400'
          } animate-pulse`} />
          <span className="text-sm text-gray-300">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="CPU Usage"
          value={stats.cpu}
          unit="%"
          icon={CpuChipIcon}
          color="ultron-red"
          percentage={stats.cpu}
        />
        
        <StatCard
          title="Memory Usage"
          value={stats.memory}
          unit="%"
          icon={CircleStackIcon}
          color="ultron-blue"
          percentage={stats.memory}
        />
        
        <StatCard
          title="Disk Usage"
          value={stats.disk}
          unit="%"
          icon={ServerIcon}
          color="ultron-purple"
          percentage={stats.disk}
        />
        
        <StatCard
          title="Network Down"
          value={stats.network.download}
          unit="KB/s"
          icon={SignalIcon}
          color="ultron-blue"
        />
        
        <StatCard
          title="Network Up"
          value={stats.network.upload}
          unit="KB/s"
          icon={SignalIcon}
          color="ultron-red"
        />
        
        <StatCard
          title="Temperature"
          value={stats.temperature}
          unit="°C"
          icon={FireIcon}
          color="ultron-red"
        />
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Process Information */}
        <Card className="glass-morphism border-ultron-purple/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <CommandLineIcon className="w-5 h-5 text-ultron-purple" />
              <span>Process Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Active Processes</span>
              <span className="text-white font-mono">{stats.processes}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">System Uptime</span>
              <span className="text-white font-mono">4h 23m</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Load Average</span>
              <span className="text-white font-mono">1.2, 1.5, 1.8</span>
            </div>
          </CardContent>
        </Card>

        {/* System Information */}
        <Card className="glass-morphism border-ultron-red/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <CpuChipIcon className="w-5 h-5 text-ultron-red" />
              <span>System Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Operating System</span>
              <span className="text-white font-mono">Linux 5.10.134</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Architecture</span>
              <span className="text-white font-mono">x86_64</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Memory</span>
              <span className="text-white font-mono">16.0 GB</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Available Memory</span>
              <span className="text-white font-mono">
                {(16 * (100 - stats.memory) / 100).toFixed(1)} GB
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Charts */}
      <Card className="glass-morphism border-ultron-blue/30">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <SignalIcon className="w-5 h-5 text-ultron-blue" />
            <span>Performance Metrics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CPU Chart */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">CPU Utilization</span>
                <span className="text-ultron-red">{stats.cpu.toFixed(1)}%</span>
              </div>
              <div className="h-32 bg-ultron-darker rounded-lg flex items-end justify-center p-2">
                <motion.div
                  animate={{ height: `${stats.cpu}%` }}
                  className="w-8 bg-gradient-to-t from-ultron-red to-ultron-purple rounded-t"
                />
              </div>
            </div>
            
            {/* Memory Chart */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Memory Usage</span>
                <span className="text-ultron-blue">{stats.memory.toFixed(1)}%</span>
              </div>
              <div className="h-32 bg-ultron-darker rounded-lg flex items-end justify-center p-2">
                <motion.div
                  animate={{ height: `${stats.memory}%` }}
                  className="w-8 bg-gradient-to-t from-ultron-blue to-ultron-purple rounded-t"
                />
              </div>
            </div>
            
            {/* Disk Chart */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Disk Usage</span>
                <span className="text-ultron-purple">{stats.disk.toFixed(1)}%</span>
              </div>
              <div className="h-32 bg-ultron-darker rounded-lg flex items-end justify-center p-2">
                <motion.div
                  animate={{ height: `${stats.disk}%` }}
                  className="w-8 bg-gradient-to-t from-ultron-purple to-ultron-blue rounded-t"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}