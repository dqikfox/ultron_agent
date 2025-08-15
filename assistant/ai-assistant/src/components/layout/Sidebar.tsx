import React, { useState } from 'react';
import { useApp, assistantPersonalities } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import Navigation from './Navigation';
import {
  Plus,
  MessageSquare,
  Search,
  Trash2,
  StickyNote,
  CheckSquare,
  Bell,
  Calendar,
  Archive
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { format } from 'date-fns';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

export default function Sidebar({ currentView, onNavigate }: SidebarProps) {
  const { state, dispatch, createNewConversation } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  
  const { conversations, currentConversationId, notes, tasks, reminders } = state;

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.messages.some(msg => 
      msg.content.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const pendingTasks = tasks.filter(task => !task.completed);
  const upcomingReminders = reminders
    .filter(reminder => !reminder.completed && reminder.datetime > new Date())
    .sort((a, b) => a.datetime.getTime() - b.datetime.getTime())
    .slice(0, 5);

  const notificationCounts = {
    tasks: tasks.filter(task => !task.completed).length,
    reminders: reminders.filter(reminder => !reminder.completed && reminder.datetime > new Date()).length,
    notes: notes.length
  };

  return (
    <div className="flex flex-col h-full bg-muted/40">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <h2 className="font-semibold text-lg">AI Assistant</h2>
        </div>
        
        {currentView === 'chat' && (
          <Button 
            onClick={() => createNewConversation()}
            className="w-full"
            size="sm"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        )}
      </div>

      {/* Navigation */}
      <div className="p-4 border-b">
        <Navigation 
          currentView={currentView}
          onNavigate={onNavigate}
          notificationCounts={notificationCounts}
        />
      </div>

      {/* Content Tabs - Only show for chat view */}
      {currentView === 'chat' && (
        <Tabs defaultValue="chats" className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-4 mx-4 mt-2">
            <TabsTrigger value="chats" className="text-xs">
              <MessageSquare className="h-3 w-3 mr-1" />
              Chats
            </TabsTrigger>
            <TabsTrigger value="notes" className="text-xs">
              <StickyNote className="h-3 w-3 mr-1" />
              Notes
            </TabsTrigger>
            <TabsTrigger value="tasks" className="text-xs">
              <CheckSquare className="h-3 w-3 mr-1" />
              Tasks
            </TabsTrigger>
            <TabsTrigger value="reminders" className="text-xs">
              <Bell className="h-3 w-3 mr-1" />
              Alerts
            </TabsTrigger>
          </TabsList>

        {/* Chats Tab */}
        <TabsContent value="chats" className="flex-1 flex flex-col px-4 mt-2">
          <div className="relative mb-3">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          <ScrollArea className="flex-1">
            <div className="space-y-2">
              {filteredConversations.map((conversation) => {
                const personality = assistantPersonalities.find(p => p.id === conversation.mode);
                const isActive = conversation.id === currentConversationId;
                const lastMessage = conversation.messages[conversation.messages.length - 1];
                
                return (
                  <div
                    key={conversation.id}
                    onClick={() => dispatch({ type: 'SET_CURRENT_CONVERSATION', payload: conversation.id })}
                    className={cn(
                      "p-3 rounded-lg cursor-pointer border transition-colors group",
                      isActive 
                        ? "bg-primary/10 border-primary/20" 
                        : "hover:bg-muted border-transparent"
                    )}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <h3 className="font-medium text-sm truncate flex-1">
                        {conversation.title}
                      </h3>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          dispatch({ type: 'DELETE_CONVERSATION', payload: conversation.id });
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center gap-2 mb-2">
                      {personality && (
                        <Badge variant="secondary" className="text-xs">
                          {personality.icon} {personality.name}
                        </Badge>
                      )}
                    </div>
                    
                    {lastMessage && (
                      <p className="text-xs text-muted-foreground truncate mb-1">
                        {lastMessage.content}
                      </p>
                    )}
                    
                    <p className="text-xs text-muted-foreground">
                      {format(conversation.updatedAt, 'MMM d, HH:mm')}
                    </p>
                  </div>
                );
              })}
              
              {filteredConversations.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No conversations found</p>
                  {searchQuery && (
                    <p className="text-xs">Try a different search term</p>
                  )}
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Notes Tab */}
        <TabsContent value="notes" className="flex-1 flex flex-col px-4 mt-2">
          <ScrollArea className="flex-1">
            <div className="space-y-2">
              {notes.slice(0, 10).map((note) => (
                <div
                  key={note.id}
                  className="p-3 rounded-lg border hover:bg-muted cursor-pointer"
                >
                  <h3 className="font-medium text-sm truncate mb-1">
                    {note.title}
                  </h3>
                  <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                    {note.content}
                  </p>
                  <div className="flex flex-wrap gap-1 mb-1">
                    {note.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {format(note.updatedAt, 'MMM d')}
                  </p>
                </div>
              ))}
              
              {notes.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <StickyNote className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No notes yet</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="flex-1 flex flex-col px-4 mt-2">
          <ScrollArea className="flex-1">
            <div className="space-y-2">
              {pendingTasks.slice(0, 10).map((task) => (
                <div
                  key={task.id}
                  className="p-3 rounded-lg border hover:bg-muted cursor-pointer"
                >
                  <div className="flex items-start gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-4 w-4 mt-0.5"
                      onClick={() => dispatch({ 
                        type: 'UPDATE_TASK', 
                        payload: { id: task.id, updates: { completed: true } }
                      })}
                    >
                      <CheckSquare className="h-3 w-3" />
                    </Button>
                    <div className="flex-1">
                      <h3 className="font-medium text-sm">
                        {task.title}
                      </h3>
                      {task.description && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {task.description}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        <Badge 
                          variant={task.priority === 'high' ? 'destructive' : 
                                  task.priority === 'medium' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {task.priority}
                        </Badge>
                        {task.dueDate && (
                          <span className="text-xs text-muted-foreground">
                            Due {format(task.dueDate, 'MMM d')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {pendingTasks.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <CheckSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No pending tasks</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Reminders Tab */}
        <TabsContent value="reminders" className="flex-1 flex flex-col px-4 mt-2">
          <ScrollArea className="flex-1">
            <div className="space-y-2">
              {upcomingReminders.map((reminder) => (
                <div
                  key={reminder.id}
                  className="p-3 rounded-lg border hover:bg-muted cursor-pointer"
                >
                  <h3 className="font-medium text-sm mb-1">
                    {reminder.title}
                  </h3>
                  {reminder.description && (
                    <p className="text-xs text-muted-foreground mb-2">
                      {reminder.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2">
                    <Calendar className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      {format(reminder.datetime, 'MMM d, HH:mm')}
                    </span>
                  </div>
                </div>
              ))}
              
              {upcomingReminders.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No upcoming reminders</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
      )}
    </div>
  );
}
