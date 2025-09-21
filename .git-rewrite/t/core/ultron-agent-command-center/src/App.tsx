import React, { useState, useEffect } from 'react'
import { ModelNavigator } from './components/ModelNavigator'
import { ChatConsole } from './components/ChatConsole'
import { VoiceTerminal } from './components/VoiceTerminal'
import { ToolHub } from './components/ToolHub'
import { MemoryCore } from './components/MemoryCore'
import { SystemStatusBar } from './components/SystemStatusBar'
import { SecurityOverlay } from './components/SecurityOverlay'
import { UltronCore } from './components/UltronCore'
import { useAppState } from './hooks/useAppState'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const {
    models,
    activeModel,
    conversations,
    currentConversation,
    isLoading,
    setActiveModel,
    addMessage,
    createNewConversation,
    loadConversations
  } = useAppState()

  const [showSecurity, setShowSecurity] = useState(false)
  const [safeMode, setSafeMode] = useState(true)
  const [isVoiceActive, setIsVoiceActive] = useState(false)
  const [systemStatus, setSystemStatus] = useState({
    ollama: false,
    elevenlabs: false,
    websocket: false
  })

  const { sendMessage, connectionStatus } = useWebSocket({
    onMessage: (data) => {
      if (data.type === 'stream-chunk') {
        // Handle streaming response
        console.log('Received chunk:', data.content)
      }
    }
  })

  useEffect(() => {
    // Initialize app
    loadConversations()
    checkSystemStatus()
  }, [])

  // Auto-create conversation if none exists and model is available
  useEffect(() => {
    if (activeModel && !currentConversation && conversations.length === 0) {
      createNewConversation()
    }
  }, [activeModel, currentConversation, conversations.length, createNewConversation])

  const checkSystemStatus = async () => {
    try {
      // Check Ollama connection
      const models = await window.electronAPI.getOllamaModels()
      const ollamaOnline = models.length > 0
      
      // Check ElevenLabs connection
      const voices = await window.electronAPI.getElevenLabsVoices()
      const elevenLabsOnline = voices.length > 0
      
      setSystemStatus({
        ollama: ollamaOnline,
        elevenlabs: elevenLabsOnline,
        websocket: connectionStatus === 'connected'
      })
    } catch (error) {
      console.error('Failed to check system status:', error)
    }
  }

  const handleSendMessage = async (content: string, images?: string[]) => {
    if (!activeModel) return
    
    // Auto-create conversation if none exists
    let conversation = currentConversation
    if (!conversation) {
      conversation = createNewConversation()
      if (!conversation) return
    }

    // Add user message
    const userMessage = {
      role: 'user' as const,
      content,
      images,
      timestamp: new Date().toISOString()
    }
    
    addMessage(userMessage)

    try {
      // Send to model via WebSocket for streaming or direct API
      if (connectionStatus === 'connected') {
        sendMessage({
          type: 'stream-chat',
          id: Date.now().toString(),
          modelName: activeModel.name,
          messages: [...conversation.messages, userMessage]
        })
      } else {
        // Fallback to direct API
        const response = await window.electronAPI.chatWithModel(
          activeModel.name,
          [...conversation.messages, userMessage]
        )
        
        const assistantMessage = {
          role: 'assistant' as const,
          content: response,
          timestamp: new Date().toISOString()
        }
        
        addMessage(assistantMessage)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      
      const errorMessage = {
        role: 'assistant' as const,
        content: 'Error: Failed to get response from model',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      addMessage(errorMessage)
    }
  }

  const handleVoiceInput = async (text: string) => {
    await handleSendMessage(text)
  }

  const handleToolExecution = async (toolName: string, params: any) => {
    try {
      const result = await window.electronAPI.executeTool(toolName, params)
      return result
    } catch (error) {
      console.error('Tool execution failed:', error)
      throw error
    }
  }

  return (
    <div className="flex flex-col h-screen min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 overflow-hidden">
      {/* Scanline effect */}
      <div className="scanline" />
      
      {/* Security Overlay */}
      {showSecurity && (
        <SecurityOverlay
          onClose={() => setShowSecurity(false)}
          safeMode={safeMode}
          onSafeModeChange={setSafeMode}
        />
      )}
      
      {/* Top Bar */}
      <div className="flex items-center justify-between p-md bg-black/20 border-b border-slate-700">
        <div className="flex items-center gap-md">
          <h1 className="ultron-heading h2 glow-text" style={{ color: 'var(--color-accent-primary)' }}>
            ULTRON AGENT COMMAND CENTER
          </h1>
          <div className="flex items-center gap-xs">
            <div className={`status-indicator ${systemStatus.ollama ? 'online' : 'offline'}`} />
            <span className="text-xs text-slate-400">OLLAMA</span>
          </div>
        </div>
        
        <div className="flex items-center gap-sm">
          <button
            className="ultron-button"
            onClick={() => setShowSecurity(true)}
          >
            SECURITY
          </button>
          <button
            className="ultron-button danger"
            onClick={() => window.close?.()}
          >
            SHUTDOWN
          </button>
        </div>
      </div>
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-80 min-w-80 flex flex-col border-r border-slate-700 bg-black/10 overflow-hidden">
          {/* Model Navigator */}
          <div className="h-1/2 border-b border-slate-700">
            <ModelNavigator
              models={models}
              activeModel={activeModel}
              onModelSelect={setActiveModel}
              isLoading={isLoading}
            />
          </div>
          
          {/* Memory Core */}
          <div className="flex-1">
            <MemoryCore
              conversations={conversations}
              currentConversation={currentConversation}
              onConversationSelect={(conv) => {
                // Load conversation
                console.log('Load conversation:', conv)
              }}
              onNewConversation={createNewConversation}
            />
          </div>
        </div>
        
        {/* Center Content */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Ultron Core Display */}
          <div className="h-64 border-b border-slate-700 bg-gradient-to-b from-black/20 to-transparent">
            <UltronCore
              activeModel={activeModel}
              systemStatus={systemStatus}
              isProcessing={isLoading}
            />
          </div>
          
          {/* Chat Console */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <ChatConsole
              conversation={currentConversation}
              activeModel={activeModel}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
          
          {/* Voice Terminal */}
          <div className="h-32 border-t border-slate-700">
            <VoiceTerminal
              onVoiceInput={handleVoiceInput}
              isActive={isVoiceActive}
              onActiveChange={setIsVoiceActive}
            />
          </div>
        </div>
        
        {/* Right Sidebar */}
        <div className="w-80 min-w-80 border-l border-slate-700 bg-black/10 overflow-hidden">
          <ToolHub
            onToolExecute={handleToolExecution}
            safeMode={safeMode}
          />
        </div>
      </div>
      
      {/* System Status Bar */}
      <SystemStatusBar
        systemStatus={systemStatus}
        activeModel={activeModel}
        connectionStatus={connectionStatus}
      />
    </div>
  )
}

export default App
