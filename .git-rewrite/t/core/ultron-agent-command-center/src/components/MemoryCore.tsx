import React, { useState, useEffect } from 'react'
import { Conversation } from '../hooks/useAppState'

interface MemoryCoreProps {
  conversations: Conversation[]
  currentConversation: Conversation | null
  onConversationSelect: (conversation: Conversation) => void
  onNewConversation: () => void
}

export function MemoryCore({ 
  conversations, 
  currentConversation, 
  onConversationSelect, 
  onNewConversation 
}: MemoryCoreProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'updated' | 'created' | 'title'>('updated')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)

  const filteredConversations = conversations
    .filter(conv => 
      conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.model.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'updated':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        case 'created':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case 'title':
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const getMessagePreview = (messages: any[]) => {
    const lastUserMessage = messages.filter(m => m.role === 'user').pop()
    if (!lastUserMessage) return 'No messages'
    
    return lastUserMessage.content.length > 50 
      ? lastUserMessage.content.slice(0, 50) + '...'
      : lastUserMessage.content
  }

  const deleteConversation = async (conversationId: string) => {
    // This would typically call an API to delete the conversation
    console.log('Delete conversation:', conversationId)
    setShowDeleteConfirm(null)
  }

  const exportConversation = (conversation: Conversation) => {
    const dataStr = JSON.stringify(conversation, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `conversation-${conversation.title.slice(0, 20).replace(/[^a-z0-9]/gi, '_')}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-md border-b border-slate-700">
        <div className="flex items-center justify-between mb-sm">
          <h3 className="ultron-heading h3" style={{ color: 'var(--color-accent-primary)' }}>
            MEMORY CORE
          </h3>
          <button
            onClick={onNewConversation}
            className="ultron-button primary text-xs"
          >
            NEW
          </button>
        </div>
        
        {/* Search */}
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="ultron-input w-full mb-sm text-sm"
        />
        
        {/* Sort Options */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="ultron-input w-full text-sm"
        >
          <option value="updated">Last Updated</option>
          <option value="created">Date Created</option>
          <option value="title">Title</option>
        </select>
      </div>
      
      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto ultron-scroll">
        {filteredConversations.length === 0 ? (
          <div className="p-md text-center text-slate-400">
            {searchTerm ? 'No conversations found' : 'No conversations yet'}
          </div>
        ) : (
          <div className="space-y-xs p-sm">
            {filteredConversations.map(conversation => {
              const isActive = currentConversation?.id === conversation.id
              
              return (
                <div
                  key={conversation.id}
                  className={`ultron-panel p-sm cursor-pointer transition-all hover:scale-105 group ${
                    isActive ? 'active glow-border' : ''
                  }`}
                  onClick={() => onConversationSelect(conversation)}
                >
                  <div className="flex items-start justify-between mb-xs">
                    <h4 className="text-sm font-medium truncate flex-1 pr-sm">
                      {conversation.title}
                    </h4>
                    {isActive && (
                      <div className="status-indicator online flex-shrink-0" />
                    )}
                  </div>
                  
                  <div className="text-xs text-slate-400 mb-xs">
                    {conversation.model} • {conversation.messages.length} messages
                  </div>
                  
                  <div className="text-xs text-slate-500 mb-xs leading-relaxed">
                    {getMessagePreview(conversation.messages)}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      {formatDate(conversation.updated_at)}
                    </span>
                    
                    {/* Action buttons (shown on hover) */}
                    <div className="flex gap-xs opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          exportConversation(conversation)
                        }}
                        className="text-xs text-slate-400 hover:text-cyan-400"
                        title="Export"
                      >
                        ⤓
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowDeleteConfirm(conversation.id)
                        }}
                        className="text-xs text-slate-400 hover:text-red-400"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
      
      {/* Stats Footer */}
      <div className="p-sm border-t border-slate-700">
        <div className="text-xs text-slate-400">
          {filteredConversations.length} of {conversations.length} conversations
        </div>
        {currentConversation && (
          <div className="text-xs mt-xs" style={{ color: 'var(--color-accent-primary)' }}>
            Active: {currentConversation.title}
          </div>
        )}
      </div>
      
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="ultron-panel p-md m-md max-w-sm">
            <h4 className="ultron-heading h4 mb-sm text-red-400">CONFIRM DELETE</h4>
            <p className="text-sm text-slate-300 mb-md">
              Are you sure you want to delete this conversation? This action cannot be undone.
            </p>
            <div className="flex gap-sm">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="ultron-button flex-1"
              >
                CANCEL
              </button>
              <button
                onClick={() => deleteConversation(showDeleteConfirm)}
                className="ultron-button danger flex-1"
              >
                DELETE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
