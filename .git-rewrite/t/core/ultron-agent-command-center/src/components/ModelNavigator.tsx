import React, { useState, useEffect } from 'react'
import { OllamaModel } from '../hooks/useAppState'

interface ModelNavigatorProps {
  models: OllamaModel[]
  activeModel: OllamaModel | null
  onModelSelect: (model: OllamaModel) => void
  isLoading: boolean
}

export function ModelNavigator({ models, activeModel, onModelSelect, isLoading }: ModelNavigatorProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'vision' | 'code' | 'chat'>('all')

  const getModelCapabilities = (modelName: string) => {
    const name = modelName.toLowerCase()
    return {
      isVision: name.includes('vision') || name.includes('vl') || name.includes('qwen2.5vl'),
      isCode: name.includes('coder') || name.includes('starcoder') || name.includes('code'),
      isChat: name.includes('chat') || name.includes('instruct') || name.includes('hermes')
    }
  }

  const getModelSize = (size: number) => {
    const gb = size / (1024 * 1024 * 1024)
    return gb > 1 ? `${gb.toFixed(1)}GB` : `${(size / (1024 * 1024)).toFixed(0)}MB`
  }

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (filterType === 'all') return matchesSearch
    
    const capabilities = getModelCapabilities(model.name)
    switch (filterType) {
      case 'vision': return matchesSearch && capabilities.isVision
      case 'code': return matchesSearch && capabilities.isCode
      case 'chat': return matchesSearch && capabilities.isChat
      default: return matchesSearch
    }
  })

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-md border-b border-slate-700">
        <h3 className="ultron-heading h3 mb-sm" style={{ color: 'var(--color-accent-primary)' }}>
          MODEL NAVIGATOR
        </h3>
        
        {/* Search */}
        <input
          type="text"
          placeholder="Search models..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="ultron-input w-full mb-sm"
        />
        
        {/* Filter Buttons */}
        <div className="flex gap-xs">
          {(['all', 'vision', 'code', 'chat'] as const).map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`ultron-button text-xs ${
                filterType === type ? 'primary' : ''
              }`}
            >
              {type.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      {/* Model List */}
      <div className="flex-1 overflow-y-auto ultron-scroll p-sm">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="pulse text-slate-400">Loading models...</div>
          </div>
        ) : filteredModels.length === 0 ? (
          <div className="text-center text-slate-400 mt-md">
            No models found
          </div>
        ) : (
          filteredModels.map(model => {
            const capabilities = getModelCapabilities(model.name)
            const isActive = activeModel?.name === model.name
            
            return (
              <div
                key={model.name}
                onClick={() => onModelSelect(model)}
                className={`ultron-panel p-sm mb-sm cursor-pointer transition-all hover:scale-105 ${
                  isActive ? 'active glow-border' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-xs">
                  <h4 className="ultron-heading h4 text-sm truncate flex-1">
                    {model.name}
                  </h4>
                  {isActive && (
                    <div className="status-indicator online ml-xs" />
                  )}
                </div>
                
                <div className="text-xs text-slate-400 mb-xs">
                  {model.details.parameter_size} • {getModelSize(model.size)}
                </div>
                
                {/* Capabilities */}
                <div className="flex gap-xs">
                  {capabilities.isVision && (
                    <span className="px-xs py-xs bg-cyan-600/20 text-cyan-300 rounded text-xs">
                      VISION
                    </span>
                  )}
                  {capabilities.isCode && (
                    <span className="px-xs py-xs bg-green-600/20 text-green-300 rounded text-xs">
                      CODE
                    </span>
                  )}
                  {capabilities.isChat && (
                    <span className="px-xs py-xs bg-blue-600/20 text-blue-300 rounded text-xs">
                      CHAT
                    </span>
                  )}
                </div>
                
                <div className="text-xs text-slate-500 mt-xs">
                  Modified: {new Date(model.modified_at).toLocaleDateString()}
                </div>
              </div>
            )
          })
        )}
      </div>
      
      {/* Footer Stats */}
      <div className="p-sm border-t border-slate-700">
        <div className="text-xs text-slate-400">
          {filteredModels.length} of {models.length} models
        </div>
        {activeModel && (
          <div className="text-xs" style={{ color: 'var(--color-accent-primary)' }}>
            Active: {activeModel.name}
          </div>
        )}
      </div>
    </div>
  )
}
