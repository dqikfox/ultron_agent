import React from 'react'
import { motion } from 'framer-motion'
import { Card } from './ui/card'
import { useSystemMonitoring } from '../hooks/useSystemMonitoring'
import {
  ChatBubbleLeftRightIcon,
  DocumentArrowUpIcon,
  MicrophoneIcon,
  EyeIcon,
  ChartBarIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface SidebarProps {
  activeView: string
  onViewChange: (view: string) => void
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const { stats, isConnected } = useSystemMonitoring()

  const menuItems = [
    { id: 'chat', label: 'AI Chat', icon: ChatBubbleLeftRightIcon },
    { id: 'files', label: 'File Upload', icon: DocumentArrowUpIcon },
    { id: 'voice', label: 'Voice AI', icon: MicrophoneIcon },
    { id: 'vision', label: 'Computer Vision', icon: EyeIcon },
    { id: 'monitoring', label: 'System Monitor', icon: ChartBarIcon },
  ]

  return (
    <motion.aside
      initial={{ x: -250, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-ultron-dark/50 backdrop-blur-sm border-r border-ultron-blue/30 p-4 space-y-4"
    >
      {/* Navigation Menu */}
      <Card className="glass-morphism border-ultron-blue/30">
        <div className="p-4">
          <h3 className="text-sm font-orbitron font-semibold text-ultron-blue mb-3">
            NEURAL MODULES
          </h3>
          <nav className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = activeView === item.id
              
              return (
                <motion.button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  whileHover={{ x: 4 }}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-ultron-red/20 to-ultron-blue/20 border border-ultron-red/50 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-ultron-gray/20'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-ultron-blue' : ''}`} />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="ml-auto w-2 h-2 bg-ultron-red rounded-full"
                    />
                  )}
                </motion.button>
              )
            })}
          </nav>
        </div>
      </Card>

      {/* System Stats */}
      <Card className="glass-morphism border-ultron-red/30">
        <div className="p-4">
          <div className="flex items-center space-x-2 mb-3">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
            <h3 className="text-sm font-orbitron font-semibold text-ultron-red">
              SYSTEM STATUS
            </h3>
          </div>
          
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">CPU</span>
                <span className="text-white">{stats.cpu.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-ultron-darker rounded-full h-1.5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.cpu}%` }}
                  className="h-1.5 bg-gradient-to-r from-ultron-red to-ultron-blue rounded-full"
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">Memory</span>
                <span className="text-white">{stats.memory.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-ultron-darker rounded-full h-1.5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.memory}%` }}
                  className="h-1.5 bg-gradient-to-r from-ultron-blue to-ultron-purple rounded-full"
                />
              </div>
            </div>
            
            <div className="text-xs text-gray-400 space-y-1">
              <div className="flex justify-between">
                <span>Temperature</span>
                <span className="text-white">{stats.temperature.toFixed(1)}°C</span>
              </div>
              <div className="flex justify-between">
                <span>Processes</span>
                <span className="text-white">{stats.processes}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="glass-morphism border-ultron-purple/30">
        <div className="p-4">
          <h3 className="text-sm font-orbitron font-semibold text-ultron-purple mb-3">
            QUICK ACTIONS
          </h3>
          <div className="space-y-2">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onViewChange('chat')}
              className="w-full bg-gradient-to-r from-ultron-red/10 to-ultron-blue/10 border border-ultron-blue/30 rounded-lg p-2 text-left transition-all hover:border-ultron-blue/50"
            >
              <div className="flex items-center space-x-2">
                <SparklesIcon className="w-4 h-4 text-ultron-blue" />
                <span className="text-xs text-white">New AI Chat</span>
              </div>
            </motion.button>
          </div>
        </div>
      </Card>
    </motion.aside>
  )
}