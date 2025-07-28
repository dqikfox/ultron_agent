import React, { useState } from 'react'
import { useOllama } from '@/hooks/useOllama'
import { Brain, Download, Trash2, CheckCircle, AlertCircle, Loader } from 'lucide-react'

interface ModelManagerProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export const ModelManager: React.FC<ModelManagerProps> = ({ 
  selectedModel, 
  onModelChange 
}) => {
  const { models, ollamaStatus, loading, error, loadModels, pullModel, deleteModel } = useOllama()
  const [newModelName, setNewModelName] = useState('')
  const [downloading, setDownloading] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)

  const handlePullModel = async () => {
    if (!newModelName.trim()) return
    
    setDownloading(newModelName)
    try {
      await pullModel(newModelName)
      setNewModelName('')
    } catch (err) {
      console.error('Failed to pull model:', err)
    } finally {
      setDownloading(null)
    }
  }

  const handleDeleteModel = async (modelName: string) => {
    if (!confirm(`Are you sure you want to delete ${modelName}?`)) return
    
    setDeleting(modelName)
    try {
      await deleteModel(modelName)
    } catch (err) {
      console.error('Failed to delete model:', err)
    } finally {
      setDeleting(null)
    }
  }

  const formatSize = (sizeGb: number) => {
    if (sizeGb < 1) {
      return `${(sizeGb * 1024).toFixed(0)}MB`
    }
    return `${sizeGb.toFixed(1)}GB`
  }

  const getStatusColor = () => {
    switch (ollamaStatus) {
      case 'running': return 'text-green-400'
      case 'stopped': return 'text-gray-400'
      case 'error': return 'text-red-400'
      default: return 'text-yellow-400'
    }
  }

  return (
    <div className="p-4 space-y-4">
      {/* Ollama Status */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center space-x-2 mb-2">
          <Brain className="w-4 h-4 text-red-400" />
          <h3 className="font-orbitron font-bold text-sm">OLLAMA STATUS</h3>
        </div>
        <div className={`font-roboto ${getStatusColor()}`}>
          {ollamaStatus.toUpperCase()}
        </div>
        {ollamaStatus !== 'running' && (
          <div className="text-xs text-gray-400 mt-1">
            Make sure Ollama is running on localhost:11434
          </div>
        )}
      </div>

      {/* Add New Model */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <h3 className="font-orbitron font-bold text-sm mb-3">DOWNLOAD MODEL</h3>
        <div className="space-y-3">
          <input
            type="text"
            value={newModelName}
            onChange={(e) => setNewModelName(e.target.value)}
            placeholder="e.g., llama2, codellama, mistral"
            className="input-ultron w-full text-sm"
            disabled={downloading !== null}
          />
          <button
            onClick={handlePullModel}
            disabled={!newModelName.trim() || downloading !== null || ollamaStatus !== 'running'}
            className="btn-ultron w-full flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {downloading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                <span>Downloading...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Download</span>
              </>
            )}
          </button>
        </div>
        
        {/* Popular Models */}
        <div className="mt-4">
          <div className="text-xs font-orbitron font-bold text-gray-400 mb-2">POPULAR MODELS</div>
          <div className="grid grid-cols-2 gap-2">
            {['llama2', 'codellama', 'mistral', 'vicuna'].map((modelName) => (
              <button
                key={modelName}
                onClick={() => setNewModelName(modelName)}
                className="text-xs p-2 rounded bg-gray-700 hover:bg-red-500/20 transition-colors font-roboto"
                disabled={downloading !== null}
              >
                {modelName}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Available Models */}
      <div className="glass p-4 rounded-lg border border-red-500/20">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-orbitron font-bold text-sm">AVAILABLE MODELS</h3>
          <button
            onClick={loadModels}
            disabled={loading}
            className="text-xs text-gray-400 hover:text-red-400 transition-colors"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        {error && (
          <div className="text-red-400 text-sm mb-3 font-roboto">
            {error}
          </div>
        )}

        <div className="space-y-2 max-h-64 overflow-y-auto">
          {models.length === 0 ? (
            <div className="text-center py-4">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <div className="text-sm text-gray-400 font-roboto">
                No models available
              </div>
            </div>
          ) : (
            models.map((model) => (
              <div
                key={model.id}
                className={`p-3 rounded-lg border transition-all cursor-pointer ${
                  selectedModel === model.name
                    ? 'border-red-500 bg-red-500/10 glow-subtle'
                    : 'border-gray-600 hover:border-red-500/50'
                }`}
                onClick={() => onModelChange(model.name)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        model.is_available ? 'bg-green-400' : 
                        model.is_downloading ? 'bg-yellow-400' : 'bg-gray-400'
                      }`} />
                      <div className="font-roboto font-medium text-sm">
                        {model.display_name}
                      </div>
                      {selectedModel === model.name && (
                        <CheckCircle className="w-4 h-4 text-red-400" />
                      )}
                    </div>
                    
                    {model.size_gb && (
                      <div className="text-xs text-gray-400 mt-1">
                        Size: {formatSize(model.size_gb)}
                      </div>
                    )}
                    
                    {model.is_downloading && (
                      <div className="text-xs text-yellow-400 mt-1">
                        Downloading... {model.download_progress}%
                      </div>
                    )}
                    
                    {model.usage_count > 0 && (
                      <div className="text-xs text-gray-400 mt-1">
                        Used {model.usage_count} times
                      </div>
                    )}
                  </div>
                  
                  {model.is_available && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteModel(model.name)
                      }}
                      disabled={deleting === model.name || selectedModel === model.name}
                      className="p-1 text-gray-400 hover:text-red-400 transition-colors disabled:opacity-50"
                      title="Delete Model"
                    >
                      {deleting === model.name ? (
                        <Loader className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Model Info */}
      {selectedModel && (
        <div className="glass p-4 rounded-lg border border-red-500/20">
          <h3 className="font-orbitron font-bold text-sm mb-2">ACTIVE MODEL</h3>
          <div className="font-roboto text-red-400 font-medium">
            {selectedModel}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Ready for chat
          </div>
        </div>
      )}
    </div>
  )
}