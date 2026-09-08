import React from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  MessageSquare, 
  Upload, 
  Search, 
  StickyNote, 
  CheckSquare, 
  Bell,
  Settings,
  Home
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface NavigationProps {
  onNavigate: (view: string) => void;
  currentView: string;
  notificationCounts?: {
    tasks: number;
    reminders: number;
    notes: number;
  };
}

export default function Navigation({ onNavigate, currentView, notificationCounts }: NavigationProps) {
  const navigationItems = [
    {
      id: 'chat',
      label: 'Chat',
      icon: MessageSquare,
      description: 'AI Assistant Chat'
    },
    {
      id: 'files',
      label: 'Files',
      icon: Upload,
      description: 'File Processing'
    },
    {
      id: 'search',
      label: 'Search',
      icon: Search,
      description: 'Web Search'
    },
    {
      id: 'notes',
      label: 'Notes',
      icon: StickyNote,
      description: 'Notes Manager',
      count: notificationCounts?.notes
    },
    {
      id: 'tasks',
      label: 'Tasks',
      icon: CheckSquare,
      description: 'Task Manager',
      count: notificationCounts?.tasks
    },
    {
      id: 'reminders',
      label: 'Reminders',
      icon: Bell,
      description: 'Reminders',
      count: notificationCounts?.reminders
    }
  ];

  return (
    <div className="space-y-2">
      {/* Primary Navigation */}
      <div className="space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start gap-3 h-auto py-3 px-3",
                isActive && "bg-secondary"
              )}
              onClick={() => onNavigate(item.id)}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              <div className="flex-1 text-left">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs text-muted-foreground">{item.description}</div>
              </div>
              {item.count && item.count > 0 && (
                <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
                  {item.count > 99 ? '99+' : item.count}
                </Badge>
              )}
            </Button>
          );
        })}
      </div>

      {/* Divider */}
      <div className="border-t my-4" />

      {/* Secondary Navigation */}
      <div className="space-y-1">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 h-auto py-3 px-3"
          onClick={() => onNavigate('settings')}
        >
          <Settings className="h-5 w-5 flex-shrink-0" />
          <div className="flex-1 text-left">
            <div className="font-medium">Settings</div>
            <div className="text-xs text-muted-foreground">Preferences & Config</div>
          </div>
        </Button>
      </div>

      {/* Footer Info */}
      <div className="pt-4 text-center">
        <div className="text-xs text-muted-foreground space-y-1">
          <p>AI Assistant v1.0</p>
          <p>Built with React & TypeScript</p>
        </div>
      </div>
    </div>
  );
}
