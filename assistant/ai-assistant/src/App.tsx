"import React, { useState } from 'react';
import { ThemeProvider } from 'next-themes';
import { AppProvider } from './contexts/AppContext';
import MainLayout from './components/layout/MainLayout';
import ChatInterface from './components/chat/ChatInterface';
import FileProcessor from './components/features/FileProcessor';
import WebSearch from './components/features/WebSearch';
import NotesManager from './components/productivity/NotesManager';
import TaskManager from './components/productivity/TaskManager';
import SettingsPanel from './components/settings/SettingsPanel';
import { Toaster } from './components/ui/toaster';
import './index.css';

function App() {
  const [currentView, setCurrentView] = useState('chat');

  const handleNavigate = (view: string) => {
    setCurrentView(view);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'chat':
        return <ChatInterface />;
      case 'files':
        return <FileProcessor />;
      case 'search':
        return <WebSearch />;
      case 'notes':
        return <NotesManager />;
      case 'tasks':
        return <TaskManager />;
      case 'reminders':
        return (
          <div className=\"flex items-center justify-center h-full\">
            <div className=\"text-center\">
              <h2 className=\"text-2xl font-bold mb-4\">Reminders</h2>
              <p className=\"text-muted-foreground\">Coming soon...</p>
            </div>
          </div>
        );
      case 'settings':
        return <SettingsPanel />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <ThemeProvider attribute=\"class\" defaultTheme=\"system\" enableSystem>
      <AppProvider>
        <div className=\"min-h-screen bg-background text-foreground\">
          <MainLayout
            currentView={currentView}
            onNavigate={handleNavigate}
          >
            {renderCurrentView()}
          </MainLayout>
          <Toaster />
        </div>
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;"
