import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { ChatInterface } from './ChatInterface'
import { FileUpload } from './FileUpload'
import { SystemMonitoring } from './SystemMonitoring'
import { SettingsPanel } from './SettingsPanel'
import { useAuth } from '../contexts/AuthContext'

interface VoiceInterfaceProps {
  selectedProvider: string
  selectedModel: string
}

function VoiceInterface({ selectedProvider, selectedModel }: VoiceInterfaceProps) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center space-y-4">
        <div className="w-32 h-32 bg-gradient-ultron rounded-full flex items-center justify-center mx-auto">
          <span className="text-4xl text-white font-orbitron">AI</span>
        </div>
        <h2 className="text-2xl font-orbitron text-white">Voice Interface</h2>
        <p className="text-gray-400">Voice features integrated with chat interface</p>
      </div>
    </div>
  )
}

function ComputerVision() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center space-y-4">
        <div className="w-32 h-32 bg-gradient-ultron rounded-full flex items-center justify-center mx-auto">
          <span className="text-4xl text-white font-orbitron">CV</span>
        </div>
        <h2 className="text-2xl font-orbitron text-white">Computer Vision</h2>
        <p className="text-gray-400">Upload images to the File Upload section for computer vision analysis</p>
      </div>
    </div>
  )
}

export function Dashboard() {
  const [activeView, setActiveView] = useState('chat')
  const [showSettings, setShowSettings] = useState(false)
  const { profile } = useAuth()
  
  const selectedProvider = profile?.preferred_ai_provider || 'openai'
  const selectedModel = getDefaultModel(selectedProvider)

  function getDefaultModel(provider: string) {
    switch (provider) {
      case 'openai':
        return 'gpt-3.5-turbo'
      case 'deepseek':
        return 'deepseek-chat'
      case 'google':
        return 'gemini-pro'
      case 'ollama':
        return 'llama2'
      default:
        return 'gpt-3.5-turbo'
    }
  }

  const renderContent = () => {
    switch (activeView) {
      case 'chat':
        return (
          <ChatInterface 
            selectedProvider={selectedProvider}
            selectedModel={selectedModel}
          />
        )
      case 'files':
        return <FileUpload />
      case 'voice':
        return (
          <VoiceInterface 
            selectedProvider={selectedProvider}
            selectedModel={selectedModel}
          />
        )
      case 'vision':
        return <ComputerVision />
      case 'monitoring':
        return <SystemMonitoring />
      default:
        return (
          <ChatInterface 
            selectedProvider={selectedProvider}
            selectedModel={selectedModel}
          />
        )
    }
  }

  return (
    <div className="h-screen flex flex-col bg-ultron-darker">
      <Header onSettingsClick={() => setShowSettings(true)} />
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar 
          activeView={activeView}
          onViewChange={setActiveView}
        />
        
        <main className="flex-1 overflow-hidden">
          <motion.div
            key={activeView}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="h-full p-6"
          >
            {renderContent()}
          </motion.div>
        </main>
      </div>

      <AnimatePresence>
        {showSettings && (
          <SettingsPanel onClose={() => setShowSettings(false)} />
        )}
      </AnimatePresence>
    </div>
  )
}