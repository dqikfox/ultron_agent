import React, { useRef, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import EmptyState from './EmptyState';
import TypingIndicator from './TypingIndicator';

export default function ChatInterface() {
  const { state, getCurrentConversation } = useApp();
  const { currentConversationId, isTyping } = state;
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const currentConversation = getCurrentConversation();

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages, isTyping]);

  if (!currentConversation) {
    return <EmptyState />;
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <MessageList messages={currentConversation.messages} />
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <MessageInput />
        </div>
      </div>
    </div>
  );
}
