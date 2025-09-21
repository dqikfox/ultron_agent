import React from 'react';
import { Button } from '../ui/button';
import { Plus, Settings } from 'lucide-react';

interface ChatHeaderProps {
  onNewChat: () => void;
  onShowSettings: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ onNewChat, onShowSettings }) => {
  return (
    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-100">AI Assistant</h1>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="icon"
            onClick={onShowSettings}
            className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100"
            aria-label="Settings"
          >
            <Settings className="h-5 w-5" />
          </Button>
          <Button
            onClick={onNewChat}
            className="bg-blue-600 hover:bg-blue-700 text-white"
            aria-label="New chat"
          >
            <Plus className="h-5 w-5 mr-2" />
            New Chat
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;
