import React from 'react';
import { useApp, assistantPersonalities } from '../../contexts/AppContext';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { cn } from '../../lib/utils';

export default function TypingIndicator() {
  const { state } = useApp();
  const { currentMode } = state;
  
  const personality = assistantPersonalities.find(p => p.id === currentMode);

  return (
    <div className="flex gap-4 group">
      {/* Avatar */}
      <Avatar className="flex-shrink-0">
        <AvatarFallback className={personality?.color || "bg-secondary"}>
          <span className="text-sm">{personality?.icon || '🤖'}</span>
        </AvatarFallback>
      </Avatar>

      {/* Typing Bubble */}
      <div className="flex flex-col items-start">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm">
            {personality?.name || 'Assistant'}
          </span>
          <span className="text-xs text-muted-foreground">
            is typing...
          </span>
        </div>
        
        <div className="bg-muted border rounded-2xl px-4 py-3">
          <div className="flex items-center gap-1">
            <div className={cn(
              "w-2 h-2 bg-muted-foreground rounded-full animate-bounce",
              "[animation-delay:-0.3s]"
            )} />
            <div className={cn(
              "w-2 h-2 bg-muted-foreground rounded-full animate-bounce",
              "[animation-delay:-0.15s]"
            )} />
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
          </div>
        </div>
      </div>
    </div>
  );
}
