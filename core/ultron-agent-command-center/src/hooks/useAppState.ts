import { useState, useEffect, useCallback } from 'react'

export interface OllamaModel {
  name: string
  model: string
  modified_at: string
  size: number
  digest: string
  details: {
    parent_model?: string
    format: string
    family: string
    families?: string[]
    parameter_size: string
    quantization_level: string
  }
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  images?: string[]
  timestamp: string
  error?: boolean
}

export interface Conversation {
  id: string
  title: string
  model: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export function useAppState() {
  const [models, setModels] = useState<OllamaModel[]>([])
  const [activeModel, setActiveModel] = useState<OllamaModel | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Load models on initialization
  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      setIsLoading(true)
      const modelList = await window.electronAPI.getOllamaModels()
      setModels(modelList)
      
      // Set first model as active if none selected
      if (modelList.length > 0 && !activeModel) {
        setActiveModel(modelList[0])
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadConversations = async () => {
    try {
      const convList = await window.electronAPI.loadConversations()
      setConversations(convList)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  const createNewConversation = useCallback(() => {
    if (!activeModel) return null

    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: `New Chat - ${activeModel.name}`,
      model: activeModel.name,
      messages: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    setConversations(prev => [newConversation, ...prev])
    setCurrentConversation(newConversation)
    return newConversation
  }, [activeModel])

  const addMessage = useCallback((message: ChatMessage) => {
    let conversation = currentConversation
    
    if (!conversation) {
      // Create new conversation if none exists
      conversation = createNewConversation()
      if (!conversation) return
    }

    const updatedConversation = {
      ...conversation,
      messages: [...conversation.messages, message],
      updated_at: new Date().toISOString()
    }
    
    // Update title based on first user message
    if (message.role === 'user' && conversation.messages.length === 0) {
      updatedConversation.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
    }
    
    setCurrentConversation(updatedConversation)

    // Update conversations list
    setConversations(prev => 
      prev.map(conv => 
        conv.id === conversation.id
          ? updatedConversation
          : conv
      )
    )
  }, [currentConversation, createNewConversation])

  const saveCurrentConversation = async () => {
    if (!currentConversation) return

    try {
      await window.electronAPI.saveConversation(currentConversation)
    } catch (error) {
      console.error('Failed to save conversation:', error)
    }
  }

  const selectConversation = useCallback((conversation: Conversation) => {
    setCurrentConversation(conversation)
  }, [])

  const deleteConversation = useCallback((conversationId: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== conversationId))
    
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(null)
    }
  }, [currentConversation])

  const clearCurrentConversation = useCallback(() => {
    setCurrentConversation(null)
  }, [])

  // Auto-save conversation when messages change
  useEffect(() => {
    if (currentConversation && currentConversation.messages.length > 0) {
      const timeoutId = setTimeout(() => {
        saveCurrentConversation()
      }, 2000) // Save after 2 seconds of inactivity
      
      return () => clearTimeout(timeoutId)
    }
  }, [currentConversation?.messages])

  return {
    models,
    activeModel,
    conversations,
    currentConversation,
    isLoading,
    setActiveModel,
    addMessage,
    createNewConversation,
    loadConversations,
    selectConversation,
    deleteConversation,
    clearCurrentConversation,
    saveCurrentConversation,
    loadModels
  }
}
