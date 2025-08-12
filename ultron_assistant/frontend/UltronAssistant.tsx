import React, { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Mic, 
  Send, 
  Bot, 
  User, 
  Monitor, 
  Type, 
  Camera, 
  Power, 
  AlertCircle, 
  CheckCircle,
  Volume2,
  VolumeX,
  Settings,
  Trash2,
  MessageSquare
} from 'lucide-react'
import io, { Socket } from 'socket.io-client'

interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
  timestamp: Date
  type?: 'text' | 'automation' | 'voice' | 'error' | 'success'
  imageUrl?: string
}

interface SystemStatus {
  server_running: boolean
  microphone_available: boolean
  main_agent_available: boolean
  conversations: number
  agent_status?: string
}

export default function UltronAssistant() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [conversationId, setConversationId] = useState('default')
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [continuousVoiceMode, setContinuousVoiceMode] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const socketRef = useRef<Socket | null>(null)
  const recognitionRef = useRef<any>(null)
  const synthesisRef = useRef<SpeechSynthesis | null>(null)

  const API_BASE = 'http://127.0.0.1:8000'

  useEffect(() => {
    // Initialize Socket.IO connection
    socketRef.current = io(API_BASE)
    
    socketRef.current.on('connect', () => {
      setIsConnected(true)
      console.log('Connected to Ultron Assistant')
    })

    socketRef.current.on('disconnect', () => {
      setIsConnected(false)
      console.log('Disconnected from Ultron Assistant')
    })

    socketRef.current.on('status', (data) => {
      addMessage('assistant', data.message, 'success')
    })

    socketRef.current.on('assistant_chunk', (data) => {
      // Handle streaming response
      updateLastAssistantMessage(data.chunk)
    })

    socketRef.current.on('assistant_done', () => {
      setIsProcessing(false)
    })

    socketRef.current.on('error', (data) => {
      addMessage('assistant', data.message, 'error')
      setIsProcessing(false)
    })

    socketRef.current.on('conversation_history', (data) => {
      const historyMessages = data.history.map((msg: any, index: number) => ({
        id: `history-${index}`,
        text: msg.content,
        sender: msg.role === 'user' ? 'user' : 'assistant',
        timestamp: new Date(),
        type: 'text'
      }))
      setMessages(historyMessages)
    })

    // Continuous voice events
    socketRef.current.on('continuous_voice_started', (data) => {
      setContinuousVoiceMode(true)
      addMessage('assistant', data.message, 'success')
    })

    socketRef.current.on('continuous_voice_stopped', (data) => {
      setContinuousVoiceMode(false)
      addMessage('assistant', data.message, 'success')
    })

    socketRef.current.on('voice_recognized', (data) => {
      addMessage('user', data.text, 'voice')
    })

    // Initialize speech synthesis
    synthesisRef.current = window.speechSynthesis
    
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputText(transcript)
        handleSendMessage(transcript)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        addMessage('assistant', `Voice recognition error: ${event.error}`, 'error')
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    // Get system status
    fetchSystemStatus()

    // Add welcome message
    addMessage('assistant', 'ULTRON ASSISTANT INITIALIZED. All systems operational. Ready for commands.', 'success')

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`)
      const data = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error('Failed to fetch system status:', error)
    }
  }

  const addMessage = (sender: 'user' | 'assistant', text: string, type?: Message['type'], imageUrl?: string) => {
    const message: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date(),
      type: type || 'text',
      imageUrl
    }
    setMessages(prev => [...prev, message])
    
    if (sender === 'assistant' && voiceEnabled && text.length > 0) {
      speak(text)
    }
  }

  const updateLastAssistantMessage = (chunk: string) => {
    setMessages(prev => {
      const newMessages = [...prev]
      const lastMessage = newMessages[newMessages.length - 1]
      
      if (lastMessage && lastMessage.sender === 'assistant' && lastMessage.type !== 'error') {
        lastMessage.text += chunk
      } else {
        // Start new assistant message
        newMessages.push({
          id: Date.now().toString(),
          text: chunk,
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text'
        })
      }
      
      return newMessages
    })
  }

  const speak = (text: string) => {
    if (synthesisRef.current && !isSpeaking && voiceEnabled) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.85
      utterance.pitch = 0.6
      utterance.volume = 0.8
      
      // Try to use a more robotic voice
      const voices = synthesisRef.current.getVoices()
      const roboticVoice = voices.find(voice => 
        voice.name.includes('David') || 
        voice.name.includes('Mark') ||
        voice.name.toLowerCase().includes('male')
      )
      if (roboticVoice) {
        utterance.voice = roboticVoice
      }
      
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      synthesisRef.current.speak(utterance)
    }
  }

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isProcessing || !socketRef.current) return

    addMessage('user', text)
    setInputText('')
    setIsProcessing(true)

    // Send message via Socket.IO
    socketRef.current.emit('user_message', {
      text: text,
      conversation_id: conversationId
    })
  }

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      addMessage('assistant', 'Speech recognition not supported in your browser', 'error')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const toggleVoiceOutput = () => {
    setVoiceEnabled(!voiceEnabled)
    if (synthesisRef.current && isSpeaking) {
      synthesisRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  const startContinuousVoice = () => {
    if (!socketRef.current) return
    
    socketRef.current.emit('start_continuous_voice', {
      conversation_id: conversationId
    })
  }

  const stopContinuousVoice = () => {
    if (!socketRef.current) return
    
    socketRef.current.emit('stop_continuous_voice', {})
  }

  const toggleContinuousVoice = () => {
    if (continuousVoiceMode) {
      stopContinuousVoice()
    } else {
      startContinuousVoice()
    }
  }

  const clearConversation = async () => {
    try {
      await fetch(`${API_BASE}/conversations/${conversationId}`, {
        method: 'DELETE'
      })
      setMessages([])
      addMessage('assistant', 'Conversation cleared. Ready for new commands.', 'success')
    } catch (error) {
      addMessage('assistant', 'Failed to clear conversation', 'error')
    }
  }

  const executeQuickCommand = (command: string) => {
    handleSendMessage(command)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getStatusColor = () => {
    if (!isConnected) return 'bg-red-500'
    if (isProcessing) return 'bg-yellow-500 animate-pulse'
    if (isListening) return 'bg-red-500 animate-pulse'
    return 'bg-green-500'
  }

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected'
    if (isProcessing) return 'Processing...'
    if (isListening) return 'Listening...'
    return 'Ready'
  }

  return (
    <div className="min-h-screen bg-black text-white font-mono">
      <div className="flex flex-col h-screen max-w-6xl mx-auto">
        {/* Header */}
        <Card className="bg-gray-900 border-purple-500/30 rounded-none">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Bot className="w-10 h-10 text-purple-400" />
                <div>
                  <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    ULTRON ASSISTANT
                  </CardTitle>
                  <p className="text-sm text-gray-400 mt-1">
                    Advanced AI System • Voice • Automation • Real-time
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
                  <span className="text-sm text-gray-400">{getStatusText()}</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleVoiceOutput}
                    className={`text-purple-400 hover:text-purple-300 ${!voiceEnabled ? 'opacity-50' : ''}`}
                  >
                    {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearConversation}
                    className="text-purple-400 hover:text-purple-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
            
            {/* System Status Bar */}
            {systemStatus && (
              <div className="flex items-center space-x-4 mt-3 text-xs">
                <Badge variant={systemStatus.server_running ? "default" : "destructive"}>
                  Server: {systemStatus.server_running ? 'Online' : 'Offline'}
                </Badge>
                <Badge variant={systemStatus.microphone_available ? "default" : "secondary"}>
                  Microphone: {systemStatus.microphone_available ? 'Available' : 'Unavailable'}
                </Badge>
                <Badge variant={systemStatus.main_agent_available ? "default" : "secondary"}>
                  AI Brain: {systemStatus.main_agent_available ? 'Connected' : 'Standalone'}
                </Badge>
                <Badge variant="outline">
                  Conversations: {systemStatus.conversations}
                </Badge>
              </div>
            )}
          </CardHeader>
        </Card>

        {/* Quick Actions */}
        <Card className="bg-gray-900/50 border-purple-500/20 rounded-none border-t-0">
          <CardContent className="py-3">
            <div className="flex items-center space-x-2 overflow-x-auto">
              <span className="text-sm text-gray-400 mr-2 whitespace-nowrap">Quick Commands:</span>
              <Button
                variant="ghost"
                size="sm"
                className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 whitespace-nowrap"
                onClick={() => executeQuickCommand('open notepad')}
                disabled={isProcessing}
              >
                <Type className="w-4 h-4 mr-1" />
                Open Notepad
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 whitespace-nowrap"
                onClick={() => executeQuickCommand('type Hello from Ultron Assistant!')}
                disabled={isProcessing}
              >
                <Type className="w-4 h-4 mr-1" />
                Type Text
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 whitespace-nowrap"
                onClick={() => executeQuickCommand('take screenshot')}
                disabled={isProcessing}
              >
                <Camera className="w-4 h-4 mr-1" />
                Screenshot
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 whitespace-nowrap"
                onClick={() => executeQuickCommand('search for artificial intelligence')}
                disabled={isProcessing}
              >
                <Monitor className="w-4 h-4 mr-1" />
                Search Web
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Messages */}
        <Card className="flex-1 bg-gray-950 border-purple-500/20 rounded-none border-t-0 overflow-hidden">
          <ScrollArea className="h-full">
            <CardContent className="p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex max-w-2xl ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    {/* Avatar */}
                    <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                      message.sender === 'user' 
                        ? 'bg-purple-600 ml-3' 
                        : message.type === 'error'
                        ? 'bg-red-600 mr-3'
                        : message.type === 'success'
                        ? 'bg-green-600 mr-3'
                        : 'bg-gray-700 mr-3 border border-purple-500/30'
                    }`}>
                      {message.sender === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : message.type === 'error' ? (
                        <AlertCircle className="w-5 h-5 text-white" />
                      ) : message.type === 'success' ? (
                        <CheckCircle className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-purple-400" />
                      )}
                    </div>
                    
                    {/* Message Content */}
                    <div>
                      <div className={`px-4 py-3 rounded-lg ${
                        message.sender === 'user'
                          ? 'bg-purple-600 text-white'
                          : message.type === 'error'
                          ? 'bg-red-900/30 border border-red-500/30 text-red-200'
                          : message.type === 'success'
                          ? 'bg-green-900/30 border border-green-500/30 text-green-200'
                          : message.type === 'automation'
                          ? 'bg-gray-800 border border-purple-500/30 text-purple-200'
                          : 'bg-gray-800 border border-gray-600/30 text-gray-200'
                      }`}>
                        <p className="text-sm leading-relaxed font-mono">{message.text}</p>
                        {message.imageUrl && (
                          <img 
                            src={`${API_BASE}${message.imageUrl}`} 
                            alt="Screenshot" 
                            className="mt-3 rounded border border-purple-500/30 max-w-full h-auto"
                          />
                        )}
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <p className={`text-xs ${message.sender === 'user' ? 'text-right ml-auto' : 'text-left'} text-gray-500`}>
                          {formatTime(message.timestamp)}
                        </p>
                        {message.type && (
                          <Badge variant="outline" className="text-xs ml-2">
                            {message.type}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </CardContent>
          </ScrollArea>
        </Card>

        {/* Input */}
        <Card className="bg-gray-900 border-purple-500/30 rounded-none border-t-0">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="icon"
                className={`border-purple-500/50 ${
                  isListening 
                    ? 'bg-red-500/20 border-red-500 text-red-400' 
                    : 'hover:bg-purple-500/10 text-purple-400'
                }`}
                onClick={toggleVoiceInput}
                disabled={isProcessing || continuousVoiceMode}
              >
                <Mic className={`w-5 h-5 ${isListening ? 'animate-pulse' : ''}`} />
              </Button>
              
              <Button
                variant="outline"
                size="icon"
                className={`border-purple-500/50 ${
                  continuousVoiceMode 
                    ? 'bg-green-500/20 border-green-500 text-green-400' 
                    : 'hover:bg-purple-500/10 text-purple-400'
                }`}
                onClick={toggleContinuousVoice}
                disabled={isProcessing}
                title={continuousVoiceMode ? 'Stop Continuous Voice' : 'Start Continuous Voice'}
              >
                <MessageSquare className={`w-5 h-5 ${continuousVoiceMode ? 'animate-pulse' : ''}`} />
              </Button>
              
              <Input
                type="text"
                placeholder="Enter command or message..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
                className="flex-1 bg-gray-800 border-purple-500/30 text-white placeholder-gray-400 font-mono"
                disabled={isProcessing}
              />
              
              <Button
                onClick={() => handleSendMessage(inputText)}
                className="bg-purple-600 hover:bg-purple-700 text-white"
                disabled={isProcessing || !inputText.trim()}
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
            
            <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Commands: open [app] • type [text] • screenshot • search for [query]</span>
              </div>
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-3 h-3" />
                <span>ID: {conversationId}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
