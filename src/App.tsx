import React from 'react';
import { SettingsProvider } from './contexts/SettingsContext';
import { ChatWindow } from './components/ChatWindow';
import { ChatList } from './components/ChatList';
import { ChatHeader } from './components/ChatHeader';
import { SettingsPanel } from './components/settings/SettingsPanel';
import { useSettings } from './contexts/SettingsContext';
import { useState } from 'react';

// Mock data for conversations
const mockConversations = [
  { id: '1', title: 'Welcome to AI Assistant', timestamp: new Date(Date.now() - 86400000) },
  { id: '2', title: 'Creative Writing Ideas', timestamp: new Date(Date.now() - 172800000) },
  { id: '3', title: 'Code Optimization Tips', timestamp: new Date(Date.now() - 259200000) },
];

const App: React.FC = () => {
  const [selectedConversation, setSelectedConversation] = useState(mockConversations[0]);
  const [showSettings, setShowSettings] = useState(false);
  const { settings } = useSettings();

  return (
    <SettingsProvider>
      <div className={`flex h-screen ${settings.theme === 'dark' ? 'dark' : ''}`}>
        {/* Sidebar */}
        <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <ChatHeader 
            onNewChat={() => setSelectedConversation({ 
              id: Date.now().toString(), 
              title: 'New Conversation', 
              timestamp: new Date() 
            })}
            onShowSettings={() => setShowSettings(true)}
          />
          <ChatList 
            conversations={mockConversations} 
            selected={selectedConversation} 
            onSelect={setSelectedConversation} 
          />
        </div>
        
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {showSettings ? (
            <SettingsPanel />
          ) : (
            <ChatWindow conversation={selectedConversation} />
          )}
        </div>
      </div>
    </SettingsProvider>
  );
};

export default App;