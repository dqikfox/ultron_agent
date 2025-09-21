export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large' | 'x-large';
  language: string;
  notifications: boolean;
  autoSave: boolean;
  defaultMode: AssistantMode;
}

