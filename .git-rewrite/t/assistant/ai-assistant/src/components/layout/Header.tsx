import React from 'react';
import { useApp, assistantPersonalities } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { 
  Menu, 
  Settings, 
  Download, 
  Sun, 
  Moon, 
  Monitor,
  Sparkles
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { useTheme } from 'next-themes';

export default function Header() {
  const { state, dispatch } = useApp();
  const { theme, setTheme } = useTheme();
  const { currentMode, sidebarOpen } = state;

  const currentPersonality = assistantPersonalities.find(p => p.id === currentMode);

  const exportConversation = () => {
    const conversation = state.conversations.find(c => c.id === state.currentConversationId);
    if (!conversation) return;

    const content = conversation.messages
      .map(msg => `**${msg.role.toUpperCase()}**: ${msg.content}`)
      .join('\n\n');
    
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${conversation.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAllData = () => {
    const data = {
      conversations: state.conversations,
      notes: state.notes,
      tasks: state.tasks,
      reminders: state.reminders,
      settings: state.settings,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_assistant_backup_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      {/* Left Section */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
        >
          <Menu className="h-5 w-5" />
        </Button>
        
        {currentPersonality && (
          <div className="flex items-center gap-2">
            <span className="text-2xl">{currentPersonality.icon}</span>
            <div>
              <h1 className="font-semibold text-lg">{currentPersonality.name}</h1>
              <p className="text-sm text-muted-foreground">{currentPersonality.description}</p>
            </div>
          </div>
        )}
      </div>

      {/* Center Section - AI Mode Selector */}
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-muted-foreground" />
        <Select
          value={currentMode}
          onValueChange={(value) => dispatch({ type: 'SET_CURRENT_MODE', payload: value as any })}
        >
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {assistantPersonalities.map((personality) => (
              <SelectItem key={personality.id} value={personality.id}>
                <div className="flex items-center gap-2">
                  <span>{personality.icon}</span>
                  <span>{personality.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Export Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Download className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={exportConversation}>
              Export Current Conversation
            </DropdownMenuItem>
            <DropdownMenuItem onClick={exportAllData}>
              Export All Data
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme Toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme("light")}>
              <Sun className="mr-2 h-4 w-4" />
              Light
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")}>
              <Moon className="mr-2 h-4 w-4" />
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")}>
              <Monitor className="mr-2 h-4 w-4" />
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Settings */}
        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
