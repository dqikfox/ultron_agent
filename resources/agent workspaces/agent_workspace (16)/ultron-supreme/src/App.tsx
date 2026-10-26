import React, { useState, useEffect } from 'react'
import { AuthProvider } from '@/contexts/AuthContext'
import { Header } from '@/components/layout/Header'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { SystemSidebar } from '@/components/sidebar/SystemSidebar'
import { SettingsPanel } from '@/components/settings/SettingsPanel'
import { LogsOverlay } from '@/components/logs/LogsOverlay'
import './styles/ultron.css'

function App() {
  const [selectedModel, setSelectedModel] = useState('llama2')
  const [showSettings, setShowSettings] = useState(false)
  const [showLogs, setShowLogs] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Load saved preferences
  useEffect(() => {
    const savedModel = localStorage.getItem('ultron-selected-model')
    const savedSidebarState = localStorage.getItem('ultron-sidebar-collapsed')
    
    if (savedModel) {
      setSelectedModel(savedModel)
    }
    
    if (savedSidebarState) {
      setSidebarCollapsed(JSON.parse(savedSidebarState))
    }
  }, [])

  // Save preferences
  useEffect(() => {
    localStorage.setItem('ultron-selected-model', selectedModel)
  }, [selectedModel])

  useEffect(() => {
    localStorage.setItem('ultron-sidebar-collapsed', JSON.stringify(sidebarCollapsed))
  }, [sidebarCollapsed])

  const handleModelChange = (model: string) => {
    setSelectedModel(model)
  }

  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 circuit-bg">
        {/* Header */}
        <Header 
          onSettingsClick={() => setShowSettings(true)}
          onLogsClick={() => setShowLogs(true)}
        />

        {/* Main Content */}
        <div className="flex h-[calc(100vh-80px)]">
          {/* Sidebar */}
          <SystemSidebar
            selectedModel={selectedModel}
            onModelChange={handleModelChange}
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          />

          {/* Chat Interface */}
          <div className="flex-1 flex flex-col">
            <ChatInterface
              selectedModel={selectedModel}
              onModelChange={handleModelChange}
            />
          </div>
        </div>

        {/* Overlays */}
        {showSettings && (
          <SettingsPanel
            selectedModel={selectedModel}
            onModelChange={handleModelChange}
            onClose={() => setShowSettings(false)}
          />
        )}

        {showLogs && (
          <LogsOverlay onClose={() => setShowLogs(false)} />
        )}
      </div>
    </AuthProvider>
  )
}

export default App