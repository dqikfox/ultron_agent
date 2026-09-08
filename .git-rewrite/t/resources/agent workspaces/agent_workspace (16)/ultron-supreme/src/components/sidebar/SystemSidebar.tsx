import React, { useState } from 'react'
import { SystemStats } from './SystemStats'
import { ModelManager } from './ModelManager'
import { QuickActions } from './QuickActions'
import { Activity, Cpu, Settings, ChevronLeft, ChevronRight } from 'lucide-react'

interface SystemSidebarProps {
  selectedModel: string
  onModelChange: (model: string) => void
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export const SystemSidebar: React.FC<SystemSidebarProps> = ({
  selectedModel,
  onModelChange,
  collapsed = false,
  onToggleCollapse
}) => {
  const [activeTab, setActiveTab] = useState<'stats' | 'models' | 'actions'>('stats')

  const tabs = [
    { id: 'stats', label: 'System', icon: Activity },
    { id: 'models', label: 'Models', icon: Cpu },
    { id: 'actions', label: 'Actions', icon: Settings }
  ]

  if (collapsed) {
    return (
      <div className="glass-intense border-r border-red-500/20 w-16 flex flex-col">
        {/* Collapse Toggle */}
        <button
          onClick={onToggleCollapse}
          className="p-4 hover:bg-red-500/10 transition-colors border-b border-red-500/20"
          title="Expand Sidebar"
        >
          <ChevronRight className="w-6 h-6 text-red-400" />
        </button>

        {/* Collapsed Tab Icons */}
        <div className="flex flex-col space-y-2 p-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id as any)
                  onToggleCollapse?.()
                }}
                className={`p-3 rounded-lg transition-all ${
                  activeTab === tab.id
                    ? 'bg-red-500/20 text-red-400 glow-subtle'
                    : 'text-gray-400 hover:text-red-400 hover:bg-red-500/10'
                }`}
                title={tab.label}
              >
                <Icon className="w-5 h-5" />
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  return (
    <div className="glass-intense border-r border-red-500/20 w-80 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-red-500/20">
        <div className="flex items-center justify-between">
          <h2 className="font-orbitron font-bold text-glow-red">
            SYSTEM CONTROL
          </h2>
          <button
            onClick={onToggleCollapse}
            className="text-gray-400 hover:text-red-400 transition-colors"
            title="Collapse Sidebar"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="flex space-x-1 mt-4">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-orbitron transition-all ${
                  activeTab === tab.id
                    ? 'bg-red-500/20 text-red-400 glow-subtle'
                    : 'text-gray-400 hover:text-red-400 hover:bg-red-500/10'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'stats' && <SystemStats />}
        {activeTab === 'models' && (
          <ModelManager 
            selectedModel={selectedModel}
            onModelChange={onModelChange}
          />
        )}
        {activeTab === 'actions' && <QuickActions />}
      </div>
    </div>
  )
}