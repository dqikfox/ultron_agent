import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { useAuth } from '../contexts/AuthContext'
import { useVoice } from '../hooks/useVoice'
import { supabase } from '../lib/supabase'
import { formatTime } from '../lib/utils'
import {
  PaperAirplaneIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  StopIcon,
  SparklesIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  provider?: string
  model?: string
  processingTime?: number
}

interface ChatInterfaceProps {
  selectedProvider: string
  selectedModel: string
}

export function ChatInterface({ selectedProvider, selectedModel }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    speakText,
    isSpeaking,
    isSupported
  } = useVoice()

  useEffect(() => {
    if (transcript) {
      setInput(transcript)
      resetTranscript()
    }
  }, [transcript, resetTranscript])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const { data, error } = await supabase.functions.invoke('ai-chat', {
        body: {
          message: input,
          provider: selectedProvider,
          model: selectedModel,
          conversationId
        }
      })

      if (error) throw error

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.data.content,
        timestamp: new Date().toISOString(),
        provider: data.data.provider,
        model: data.data.model,
        processingTime: data.data.processingTime
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (data.data.conversationId && !conversationId) {
        setConversationId(data.data.conversationId)
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error('Failed to send message: ' + error.message)
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleVoiceInput = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  const handleSpeakMessage = (content: string) => {
    speakText(content)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="bg-ultron-dark/50 border-b border-ultron-blue/30 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-ultron rounded-full flex items-center justify-center">
              <CpuChipIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-orbitron font-semibold text-white">
                AI Neural Interface
              </h2>
              <p className="text-xs text-gray-400 capitalize">
                {selectedProvider} • {selectedModel}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-xs text-gray-400">
              {messages.filter(m => m.role === 'user').length} messages
            </div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <SparklesIcon className="w-16 h-16 text-ultron-blue mx-auto mb-4" />
              <h3 className="text-xl font-orbitron text-white mb-2">
                Welcome to Ultron AI
              </h3>
              <p className="text-gray-400 max-w-md mx-auto">
                Start a conversation with advanced AI models. Ask questions, get insights, or explore capabilities.
              </p>
            </motion.div>
          )}
          
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`message-bubble ${message.role}`}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-r from-ultron-red to-ultron-purple'
                    : 'bg-gradient-to-r from-ultron-blue to-ultron-purple'
                }`}>
                  {message.role === 'user' ? (
                    <span className="text-white text-sm font-semibold">U</span>
                  ) : (
                    <CpuChipIcon className="w-4 h-4 text-white" />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-white">
                      {message.role === 'user' ? 'You' : 'Ultron AI'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatTime(message.timestamp)}
                    </span>
                    {message.provider && (
                      <span className="text-xs text-ultron-blue px-2 py-0.5 bg-ultron-blue/10 rounded">
                        {message.provider}
                      </span>
                    )}
                  </div>
                  
                  <div className="text-gray-100 whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                  
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2 mt-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSpeakMessage(message.content)}
                        disabled={isSpeaking}
                        className="text-gray-400 hover:text-ultron-blue"
                      >
                        <SpeakerWaveIcon className="w-4 h-4" />
                      </Button>
                      
                      {message.processingTime && (
                        <span className="text-xs text-gray-500">
                          {message.processingTime}ms
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
          
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="message-bubble assistant"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-ultron-blue to-ultron-purple rounded-full flex items-center justify-center">
                  <CpuChipIcon className="w-4 h-4 text-white animate-pulse" />
                </div>
                <div className="typing-indicator text-ultron-blue">
                  Ultron AI is thinking...
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <Card className="m-4 glass-morphism border-ultron-blue/30">
        <div className="p-4">
          <div className="flex items-center space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message or use voice input..."
              disabled={loading}
              className="flex-1 bg-ultron-dark/50 border-ultron-blue/30 text-white placeholder:text-gray-400"
            />
            
            {isSupported && (
              <Button
                variant={isListening ? "destructive" : "ultron-outline"}
                size="icon"
                onClick={handleVoiceInput}
                disabled={loading}
                className={isListening ? 'animate-pulse' : ''}
              >
                {isListening ? (
                  <StopIcon className="w-4 h-4" />
                ) : (
                  <MicrophoneIcon className="w-4 h-4" />
                )}
              </Button>
            )}
            
            <Button
              variant="ultron"
              size="icon"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
            >
              <PaperAirplaneIcon className="w-4 h-4" />
            </Button>
          </div>
          
          {isListening && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 text-sm text-ultron-blue flex items-center space-x-2"
            >
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span>Listening... Speak now</span>
            </motion.div>
          )}
        </div>
      </Card>
    </div>
  )
}