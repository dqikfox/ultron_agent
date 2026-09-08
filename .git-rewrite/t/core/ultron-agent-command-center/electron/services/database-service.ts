import Store from 'electron-store'
import { app } from 'electron'

export interface Conversation {
  id?: number
  title: string
  model: string
  messages: any[]
  created_at: string
  updated_at: string
}

export interface UserSettings {
  key: string
  value: string
}

export interface SecurityEvent {
  id: string
  timestamp: string
  event: string
  level: 'info' | 'warning' | 'error' | 'success'
  details?: any
}

type ConversationStore = {
  conversations: Conversation[]
}

type SecurityStore = {
  events: SecurityEvent[]
}

export class DatabaseService {
  private conversationStore: Store<ConversationStore>
  private settingsStore: Store<Record<string, string>>
  private securityStore: Store<SecurityStore>
  private conversationIdCounter: number

  constructor() {
    // Initialize electron-store instances
    this.conversationStore = new Store<ConversationStore>({
      name: 'conversations',
      defaults: {
        conversations: []
      },
      cwd: app.getPath('userData')
    })
    
    this.settingsStore = new Store<Record<string, string>>({
      name: 'settings',
      defaults: {},
      cwd: app.getPath('userData')
    })
    
    this.securityStore = new Store<SecurityStore>({
      name: 'security',
      defaults: {
        events: []
      },
      cwd: app.getPath('userData')
    })
    
    // Initialize conversation ID counter
    const conversations = this.conversationStore.get('conversations', [])
    this.conversationIdCounter = conversations.length > 0 
      ? Math.max(...conversations.map((c: Conversation) => c.id || 0)) + 1
      : 1
  }

  async initialize(): Promise<void> {
    console.log('Database service initialized with electron-store')
    console.log('Data directory:', app.getPath('userData'))
    
    // Add initial security event
    this.addSecurityEvent('System startup', 'info', { timestamp: new Date().toISOString() })
  }

  async saveConversation(conversation: Conversation): Promise<number> {
    const conversations = this.conversationStore.get('conversations', [])
    
    const id = this.conversationIdCounter++
    const newConversation: Conversation = {
      ...conversation,
      id,
      created_at: conversation.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    conversations.unshift(newConversation)
    
    // Keep only last 100 conversations
    if (conversations.length > 100) {
      conversations.splice(100)
    }
    
    this.conversationStore.set('conversations', conversations)
    
    this.addSecurityEvent(`Conversation saved: ${newConversation.title}`, 'info', {
      conversationId: id,
      model: newConversation.model,
      messageCount: newConversation.messages.length
    })
    
    return id
  }

  async loadConversations(): Promise<Conversation[]> {
    const conversations = this.conversationStore.get('conversations', [])
    return conversations.sort((a, b) => 
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  }

  async updateConversation(id: number, conversation: Partial<Conversation>): Promise<void> {
    const conversations = this.conversationStore.get('conversations', [])
    const index = conversations.findIndex(conv => conv.id === id)
    
    if (index !== -1) {
      conversations[index] = {
        ...conversations[index],
        ...conversation,
        updated_at: new Date().toISOString()
      }
      
      this.conversationStore.set('conversations', conversations)
      
      this.addSecurityEvent(`Conversation updated: ${conversations[index].title}`, 'info', {
        conversationId: id
      })
    }
  }

  async deleteConversation(id: number): Promise<void> {
    const conversations = this.conversationStore.get('conversations', [])
    const conversation = conversations.find(conv => conv.id === id)
    
    if (conversation) {
      const filteredConversations = conversations.filter(conv => conv.id !== id)
      this.conversationStore.set('conversations', filteredConversations)
      
      this.addSecurityEvent(`Conversation deleted: ${conversation.title}`, 'warning', {
        conversationId: id
      })
    }
  }

  async saveSetting(key: string, value: string): Promise<void> {
    this.settingsStore.set(key, value)
    
    this.addSecurityEvent(`Setting updated: ${key}`, 'info', {
      key,
      hasValue: !!value
    })
  }

  async getSetting(key: string): Promise<string | null> {
    return this.settingsStore.get(key) || null
  }

  async getAllSettings(): Promise<{ [key: string]: string }> {
    return this.settingsStore.store
  }

  addSecurityEvent(event: string, level: SecurityEvent['level'], details?: any): void {
    const events = this.securityStore.get('events', [])
    
    const newEvent: SecurityEvent = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      event,
      level,
      details
    }
    
    events.unshift(newEvent)
    
    // Keep only last 500 security events
    if (events.length > 500) {
      events.splice(500)
    }
    
    this.securityStore.set('events', events)
  }

  async getSecurityEvents(limit: number = 50): Promise<SecurityEvent[]> {
    const events = this.securityStore.get('events', [])
    return events.slice(0, limit)
  }

  async clearSecurityEvents(): Promise<void> {
    this.securityStore.set('events', [])
    this.addSecurityEvent('Security log cleared', 'warning')
  }

  // Statistics and analytics
  async getConversationStats(): Promise<{
    total: number
    byModel: { [model: string]: number }
    totalMessages: number
    averageMessagesPerConversation: number
  }> {
    const conversations = this.conversationStore.get('conversations', [])
    
    const byModel: { [model: string]: number } = {}
    let totalMessages = 0
    
    conversations.forEach(conv => {
      byModel[conv.model] = (byModel[conv.model] || 0) + 1
      totalMessages += conv.messages.length
    })
    
    return {
      total: conversations.length,
      byModel,
      totalMessages,
      averageMessagesPerConversation: conversations.length > 0 
        ? totalMessages / conversations.length 
        : 0
    }
  }

  // Backup and restore
  async exportData(): Promise<{
    conversations: Conversation[]
    settings: { [key: string]: string }
    securityEvents: SecurityEvent[]
    exportedAt: string
  }> {
    return {
      conversations: this.conversationStore.get('conversations', []),
      settings: this.settingsStore.store,
      securityEvents: this.securityStore.get('events', []),
      exportedAt: new Date().toISOString()
    }
  }

  async importData(data: {
    conversations?: Conversation[]
    settings?: { [key: string]: string }
    securityEvents?: SecurityEvent[]
  }): Promise<void> {
    if (data.conversations) {
      this.conversationStore.set('conversations', data.conversations)
      // Update counter
      const maxId = data.conversations.reduce((max, conv) => 
        Math.max(max, conv.id || 0), 0
      )
      this.conversationIdCounter = maxId + 1
    }
    
    if (data.settings) {
      Object.entries(data.settings).forEach(([key, value]) => {
        this.settingsStore.set(key, value)
      })
    }
    
    if (data.securityEvents) {
      this.securityStore.set('events', data.securityEvents)
    }
    
    this.addSecurityEvent('Data imported successfully', 'success', {
      conversationsImported: data.conversations?.length || 0,
      settingsImported: Object.keys(data.settings || {}).length,
      eventsImported: data.securityEvents?.length || 0
    })
  }

  close(): void {
    this.addSecurityEvent('Database service shutdown', 'info')
    console.log('Database service closed')
  }

  // Get storage paths for debugging
  getStoragePaths(): {
    conversations: string
    settings: string
    security: string
    userData: string
  } {
    return {
      conversations: this.conversationStore.path,
      settings: this.settingsStore.path,
      security: this.securityStore.path,
      userData: app.getPath('userData')
    }
  }
}
