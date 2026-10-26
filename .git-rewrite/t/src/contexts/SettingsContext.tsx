import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Define the settings types
export interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  aiModel: 'default' | 'creative' | 'code' | 'productivity' | 'research';
  temperature: number;
  autoSave: boolean;
  dataCollection: boolean;
  voiceInput: boolean;
  voiceOutput: boolean;
}

// Define the action types
type SettingsAction =
  | { type: 'SET_THEME'; payload: 'light' | 'dark' | 'system' }
  | { type: 'SET_AI_MODEL'; payload: 'default' | 'creative' | 'code' | 'productivity' | 'research' }
  | { type: 'SET_TEMPERATURE'; payload: number }
  | { type: 'TOGGLE_AUTO_SAVE' }
  | { type: 'TOGGLE_DATA_COLLECTION' }
  | { type: 'TOGGLE_VOICE_INPUT' }
  | { type: 'TOGGLE_VOICE_OUTPUT' };

// Initial state
const initialState: SettingsState = {
  theme: 'system',
  aiModel: 'default',
  temperature: 0.7,
  autoSave: true,
  dataCollection: true,
  voiceInput: false,
  voiceOutput: false,
};

// Load settings from localStorage
const loadSettings = (): SettingsState => {
  try {
    const savedSettings = localStorage.getItem('aiAssistantSettings');
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings);
      // Validate the settings structure
      return {
        ...initialState,
        ...parsed,
        // Ensure temperature is within bounds
        temperature: Math.max(0, Math.min(1, parsed.temperature || 0.7)),
      };
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
  return initialState;
};

// Save settings to localStorage
const saveSettings = (settings: SettingsState) => {
  try {
    localStorage.setItem('aiAssistantSettings', JSON.stringify(settings));
  } catch (error) {
    console.error('Failed to save settings:', error);
  }
};

// Reducer function
const settingsReducer = (state: SettingsState, action: SettingsAction): SettingsState => {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'SET_AI_MODEL':
      return { ...state, aiModel: action.payload };
    case 'SET_TEMPERATURE':
      return { ...state, temperature: Math.max(0, Math.min(1, action.payload)) };
    case 'TOGGLE_AUTO_SAVE':
      return { ...state, autoSave: !state.autoSave };
    case 'TOGGLE_DATA_COLLECTION':
      return { ...state, dataCollection: !state.dataCollection };
    case 'TOGGLE_VOICE_INPUT':
      return { ...state, voiceInput: !state.voiceInput };
    case 'TOGGLE_VOICE_OUTPUT':
      return { ...state, voiceOutput: !state.voiceOutput };
    default:
      return state;
  }
};

// Create the context
const SettingsContext = createContext<{
  settings: SettingsState;
  dispatch: React.Dispatch<SettingsAction>;
} | undefined>(undefined);

// Provider component
export const SettingsProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [state, dispatch] = useReducer(settingsReducer, initialState, loadSettings);

  // Save to localStorage whenever settings change
  useEffect(() => {
    saveSettings(state);
  }, [state]);

  return (
    <SettingsContext.Provider value={{ settings: state, dispatch }}>
      {children}
    </SettingsContext.Provider>
  );
};

// Custom hook for using the settings context
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};