export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large' | 'x-large';
  language: string;
  notifications: boolean;
  autoSave: boolean;
  defaultMode: AssistantMode;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  mode?: AssistantMode;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  url: string;
  size?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  mode?: AssistantMode;
  tags?: string[];
}

export interface Note {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
  tags?: string[];
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
  tags?: string[];
}

export interface Reminder {
  id: string;
  title: string;
  description?: string;
  dueDate: Date;
  datetime?: Date;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type AssistantMode = 'chat' | 'code' | 'creative' | 'analytical' | 'general';

export interface AssistantPersonality {
  id: string;
  name: string;
  description: string;
  avatar?: string;
  icon?: string;
  color?: string;
  systemPrompt: string;
  mode: AssistantMode;
}

export interface SearchResult {
  id: string;
  title: string;
  url: string;
  snippet: string;
  source: string;
}

