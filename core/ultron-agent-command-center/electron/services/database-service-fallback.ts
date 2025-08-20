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
  id?: number
  key: string
  value: string
}

export class DatabaseService {
  private dataPath: string
  private conversations: Conversation[] = []
  private settings: Map<string, string> = new Map()

  constructor() {
    const userDataPath = app.getPath('userData')
    this.dataPath = userDataPath
  }

  async initialize(): Promise<void> {
    console.log('Database service initialized (localStorage fallback)')
    // In a real implementation, this would set up SQLite
    // For demo purposes, we're using in-memory storage
  }

  async saveConversation(conversation: Conversation): Promise<number> {
    const id = Date.now()
    const newConversation = {
      ...conversation,
      id,
      updated_at: new Date().toISOString()
    }
    
    this.conversations.unshift(newConversation)
    // Keep only last 50 conversations
    if (this.conversations.length > 50) {
      this.conversations = this.conversations.slice(0, 50)
    }
    
    return id
  }

  async loadConversations(): Promise<Conversation[]> {
    return [...this.conversations]
  }

  async updateConversation(id: number, conversation: Partial<Conversation>): Promise<void> {
    const index = this.conversations.findIndex(conv => conv.id === id)
    if (index !== -1) {
      this.conversations[index] = {
        ...this.conversations[index],
        ...conversation,
        updated_at: new Date().toISOString()
      }
    }
  }

  async deleteConversation(id: number): Promise<void> {
    this.conversations = this.conversations.filter(conv => conv.id !== id)
  }

  async saveSetting(key: string, value: string): Promise<void> {
    this.settings.set(key, value)
  }

  async getSetting(key: string): Promise<string | null> {
    return this.settings.get(key) || null
  }

  close(): void {
    console.log('Database service closed')
  }
}
