import React, { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Paperclip, Upload } from 'lucide-react'
import { useOllama } from '@/hooks/useOllama'
import { useAuth } from '@/contexts/AuthContext'
import { ChatMessage } from './ChatMessage'
import { TypingIndicator } from './TypingIndicator'
import { VoiceInput } from './VoiceInput'
import { FileUpload } from './FileUpload'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  model?: string
  tokens?: number
  responseTime?: number
}

interface ChatInterfaceProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  selectedModel, 
  onModelChange 
}) => {
  const { user } = useAuth()
  const { chat, loading, error } = useOllama()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sessionId] = useState(() => crypto.randomUUID())
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async (content: string, isVoice: boolean = false) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')

    try {
      const response = await chat(content.trim(), selectedModel, sessionId)
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        model: response.model,
        tokens: response.tokensUsed,
        responseTime: response.responseTime
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'system',
        content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(input)
    }
  }

  const handleVoiceResult = (transcript: string) => {
    setInput(transcript)
    handleSendMessage(transcript, true)
  }

  const handleFileUpload = (fileData: any) => {
    const fileMessage: Message = {
      id: crypto.randomUUID(),
      role: 'system',
      content: `File uploaded: ${fileData.fileName}`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, fileMessage])
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 circuit-bg">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="glass p-8 rounded-lg max-w-md mx-auto">
              <h2 className="font-orbitron text-xl font-bold text-glow-red mb-4">
                Welcome to Ultron Supreme
              </h2>
              <p className="text-gray-300 font-roboto mb-6">
                Your AI command center is ready. Ask me anything or upload files to get started.
              </p>
              <div className="flex justify-center">
                <div className="spinner-ultron" />
              </div>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {loading && <TypingIndicator model={selectedModel} />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-900/30 border border-red-500/50 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Input Area */}
      <div className="glass-intense border-t border-red-500/20 p-4">
        <div className="flex items-end space-x-3">
          {/* File Upload Button */}
          <button
            onClick={() => setShowFileUpload(!showFileUpload)}
            className={`btn-ultron p-3 ${showFileUpload ? 'glow-red' : ''}`}
            title="Upload File"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Voice Input Button */}
          <button
            onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
            className={`btn-ultron p-3 ${isVoiceEnabled ? 'glow-red' : ''}`}
            title={isVoiceEnabled ? 'Stop Voice Input' : 'Start Voice Input'}
          >
            {isVoiceEnabled ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${selectedModel}...`}
              className="input-ultron w-full resize-none min-h-[48px] max-h-32"
              rows={1}
              disabled={loading || isVoiceEnabled}
            />
            
            {/* Voice Input Overlay */}
            {isVoiceEnabled && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
                <VoiceInput
                  onResult={handleVoiceResult}
                  onStop={() => setIsVoiceEnabled(false)}
                />
              </div>
            )}
          </div>

          {/* Send Button */}
          <button
            onClick={() => handleSendMessage(input)}
            disabled={!input.trim() || loading || isVoiceEnabled}
            className="btn-ultron p-3 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Send Message"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {/* File Upload Panel */}
        {showFileUpload && (
          <div className="mt-4">
            <FileUpload
              sessionId={sessionId}
              onUpload={handleFileUpload}
              onClose={() => setShowFileUpload(false)}
            />
          </div>
        )}

        {/* Model Info */}
        <div className="mt-2 text-xs text-gray-400 font-roboto">
          Model: <span className="text-red-400">{selectedModel}</span>
          {user && (
            <span className="ml-4">
              Session: <span className="text-blue-400">{sessionId.slice(0, 8)}...</span>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}