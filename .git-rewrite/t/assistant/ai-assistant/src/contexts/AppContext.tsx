import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { 
  Conversation, 
  Message, 
  AssistantMode, 
  UserSettings, 
  Note, 
  Task, 
  Reminder,
  AssistantPersonality 
} from '../types';

interface AppState {
  conversations: Conversation[];
  currentConversationId: string | null;
  settings: UserSettings;
  notes: Note[];
  tasks: Task[];
  reminders: Reminder[];
  isTyping: boolean;
  sidebarOpen: boolean;
  currentMode: AssistantMode;
}

type AppAction =
  | { type: 'SET_CONVERSATIONS'; payload: Conversation[] }
  | { type: 'ADD_CONVERSATION'; payload: Conversation }
  | { type: 'UPDATE_CONVERSATION'; payload: { id: string; updates: Partial<Conversation> } }
  | { type: 'DELETE_CONVERSATION'; payload: string }
  | { type: 'SET_CURRENT_CONVERSATION'; payload: string | null }
  | { type: 'ADD_MESSAGE'; payload: { conversationId: string; message: Message } }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<UserSettings> }
  | { type: 'ADD_NOTE'; payload: Note }
  | { type: 'UPDATE_NOTE'; payload: { id: string; updates: Partial<Note> } }
  | { type: 'DELETE_NOTE'; payload: string }
  | { type: 'ADD_TASK'; payload: Task }
  | { type: 'UPDATE_TASK'; payload: { id: string; updates: Partial<Task> } }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'ADD_REMINDER'; payload: Reminder }
  | { type: 'UPDATE_REMINDER'; payload: { id: string; updates: Partial<Reminder> } }
  | { type: 'DELETE_REMINDER'; payload: string }
  | { type: 'SET_TYPING'; payload: boolean }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_CURRENT_MODE'; payload: AssistantMode };

const initialState: AppState = {
  conversations: [],
  currentConversationId: null,
  settings: {
    theme: 'system',
    fontSize: 'medium',
    language: 'en',
    notifications: true,
    autoSave: true,
    defaultMode: 'general'
  },
  notes: [],
  tasks: [],
  reminders: [],
  isTyping: false,
  sidebarOpen: true,
  currentMode: 'general'
};

export const assistantPersonalities: AssistantPersonality[] = [
  {
    id: 'general',
    name: 'General Assistant',
    description: 'Helpful and knowledgeable for everyday tasks',
    icon: '🤖',
    color: 'bg-blue-500',
    systemPrompt: 'You are a helpful and knowledgeable AI assistant.'
  },
  {
    id: 'creative',
    name: 'Creative Writer',
    description: 'Specialized in creative writing and brainstorming',
    icon: '✨',
    color: 'bg-purple-500',
    systemPrompt: 'You are a creative AI assistant specialized in writing, storytelling, and creative ideation.'
  },
  {
    id: 'technical',
    name: 'Code Assistant',
    description: 'Expert in programming and technical solutions',
    icon: '💻',
    color: 'bg-green-500',
    systemPrompt: 'You are a technical AI assistant specialized in programming, software development, and technical problem-solving.'
  },
  {
    id: 'productivity',
    name: 'Productivity Coach',
    description: 'Focused on organization and efficiency',
    icon: '📊',
    color: 'bg-orange-500',
    systemPrompt: 'You are a productivity-focused AI assistant specialized in organization, time management, and efficiency optimization.'
  },
  {
    id: 'research',
    name: 'Research Helper',
    description: 'Expert in research and information analysis',
    icon: '🔍',
    color: 'bg-indigo-500',
    systemPrompt: 'You are a research-focused AI assistant specialized in information gathering, analysis, and academic support.'
  }
];

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CONVERSATIONS':
      return { ...state, conversations: action.payload };
    
    case 'ADD_CONVERSATION':
      return { 
        ...state, 
        conversations: [action.payload, ...state.conversations],
        currentConversationId: action.payload.id
      };
    
    case 'UPDATE_CONVERSATION':
      return {
        ...state,
        conversations: state.conversations.map(conv =>
          conv.id === action.payload.id 
            ? { ...conv, ...action.payload.updates, updatedAt: new Date() }
            : conv
        )
      };
    
    case 'DELETE_CONVERSATION':
      const filteredConversations = state.conversations.filter(conv => conv.id !== action.payload);
      return {
        ...state,
        conversations: filteredConversations,
        currentConversationId: state.currentConversationId === action.payload 
          ? filteredConversations[0]?.id || null 
          : state.currentConversationId
      };
    
    case 'SET_CURRENT_CONVERSATION':
      return { ...state, currentConversationId: action.payload };
    
    case 'ADD_MESSAGE':
      return {
        ...state,
        conversations: state.conversations.map(conv =>
          conv.id === action.payload.conversationId
            ? { 
                ...conv, 
                messages: [...conv.messages, action.payload.message],
                updatedAt: new Date()
              }
            : conv
        )
      };
    
    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };
    
    case 'ADD_NOTE':
      return { ...state, notes: [action.payload, ...state.notes] };
    
    case 'UPDATE_NOTE':
      return {
        ...state,
        notes: state.notes.map(note =>
          note.id === action.payload.id 
            ? { ...note, ...action.payload.updates, updatedAt: new Date() }
            : note
        )
      };
    
    case 'DELETE_NOTE':
      return { ...state, notes: state.notes.filter(note => note.id !== action.payload) };
    
    case 'ADD_TASK':
      return { ...state, tasks: [action.payload, ...state.tasks] };
    
    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id 
            ? { ...task, ...action.payload.updates, updatedAt: new Date() }
            : task
        )
      };
    
    case 'DELETE_TASK':
      return { ...state, tasks: state.tasks.filter(task => task.id !== action.payload) };
    
    case 'ADD_REMINDER':
      return { ...state, reminders: [action.payload, ...state.reminders] };
    
    case 'UPDATE_REMINDER':
      return {
        ...state,
        reminders: state.reminders.map(reminder =>
          reminder.id === action.payload.id 
            ? { ...reminder, ...action.payload.updates }
            : reminder
        )
      };
    
    case 'DELETE_REMINDER':
      return { ...state, reminders: state.reminders.filter(reminder => reminder.id !== action.payload) };
    
    case 'SET_TYPING':
      return { ...state, isTyping: action.payload };
    
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };
    
    case 'SET_CURRENT_MODE':
      return { ...state, currentMode: action.payload };
    
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  createNewConversation: (mode?: AssistantMode) => void;
  addMessage: (content: string, role: 'user' | 'assistant', attachments?: any[]) => void;
  getCurrentConversation: () => Conversation | undefined;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Load data from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem('ai-assistant-data');
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        if (parsed.conversations) {
          dispatch({ type: 'SET_CONVERSATIONS', payload: parsed.conversations });
        }
        if (parsed.settings) {
          dispatch({ type: 'UPDATE_SETTINGS', payload: parsed.settings });
        }
        if (parsed.notes) {
          parsed.notes.forEach((note: Note) => dispatch({ type: 'ADD_NOTE', payload: note }));
        }
        if (parsed.tasks) {
          parsed.tasks.forEach((task: Task) => dispatch({ type: 'ADD_TASK', payload: task }));
        }
        if (parsed.reminders) {
          parsed.reminders.forEach((reminder: Reminder) => dispatch({ type: 'ADD_REMINDER', payload: reminder }));
        }
      } catch (error) {
        console.error('Error loading saved data:', error);
      }
    }
  }, []);

  // Save data to localStorage whenever state changes
  useEffect(() => {
    const dataToSave = {
      conversations: state.conversations,
      settings: state.settings,
      notes: state.notes,
      tasks: state.tasks,
      reminders: state.reminders
    };
    localStorage.setItem('ai-assistant-data', JSON.stringify(dataToSave));
  }, [state.conversations, state.settings, state.notes, state.tasks, state.reminders]);

  const createNewConversation = (mode: AssistantMode = 'general') => {
    const newConversation: Conversation = {
      id: uuidv4(),
      title: 'New Conversation',
      messages: [],
      mode,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    dispatch({ type: 'ADD_CONVERSATION', payload: newConversation });
    dispatch({ type: 'SET_CURRENT_MODE', payload: mode });
  };

  const addMessage = (content: string, role: 'user' | 'assistant', attachments?: any[]) => {
    if (!state.currentConversationId) {
      createNewConversation(state.currentMode);
      return;
    }

    const message: Message = {
      id: uuidv4(),
      content,
      role,
      timestamp: new Date(),
      mode: state.currentMode,
      attachments
    };

    dispatch({ 
      type: 'ADD_MESSAGE', 
      payload: { conversationId: state.currentConversationId, message } 
    });

    // Update conversation title based on first user message
    const conversation = state.conversations.find(c => c.id === state.currentConversationId);
    if (conversation && conversation.messages.length === 0 && role === 'user') {
      const title = content.length > 50 ? content.substring(0, 50) + '...' : content;
      dispatch({ 
        type: 'UPDATE_CONVERSATION', 
        payload: { id: state.currentConversationId, updates: { title } } 
      });
    }
  };

  const getCurrentConversation = () => {
    return state.conversations.find(conv => conv.id === state.currentConversationId);
  };

  return (
    <AppContext.Provider value={{
      state,
      dispatch,
      createNewConversation,
      addMessage,
      getCurrentConversation
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
