import React, { useState } from 'react';
import { Message } from '../../types';
import { assistantPersonalities } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { 
  Copy, 
  ThumbsUp, 
  ThumbsDown, 
  MoreHorizontal,
  User,
  Bot,
  FileText,
  Image as ImageIcon,
  Download
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { format } from 'date-fns';
import { cn } from '../../lib/utils';

interface MessageBubbleProps {
  message: Message;
  isLast: boolean;
}

export default function MessageBubble({ message, isLast }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const { role, content, timestamp, mode, attachments } = message;
  
  const personality = assistantPersonalities.find(p => p.id === mode);
  const isUser = role === 'user';

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const downloadAttachment = (attachment: any) => {
    const link = document.createElement('a');
    link.href = attachment.url;
    link.download = attachment.name;
    link.click();
  };

  return (
    <div className={cn(
      "flex gap-4 group",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar */}
      <Avatar className={cn(
        "flex-shrink-0",
        isUser ? "order-2" : "order-1"
      )}>
        <AvatarFallback className={cn(
          isUser 
            ? "bg-primary text-primary-foreground" 
            : personality?.color || "bg-secondary"
        )}>
          {isUser ? (
            <User className="h-4 w-4" />
          ) : (
            <span className="text-sm">{personality?.icon || '🤖'}</span>
          )}
        </AvatarFallback>
      </Avatar>

      {/* Message Content */}
      <div className={cn(
        "flex-1 min-w-0 max-w-[80%]",
        isUser ? "flex flex-col items-end" : "flex flex-col items-start"
      )}>
        {/* Header */}
        <div className={cn(
          "flex items-center gap-2 mb-1",
          isUser ? "flex-row-reverse" : "flex-row"
        )}>
          <span className="font-medium text-sm">
            {isUser ? 'You' : personality?.name || 'Assistant'}
          </span>
          {mode && !isUser && (
            <Badge variant="outline" className="text-xs">
              {personality?.icon} {personality?.name}
            </Badge>
          )}
          <span className="text-xs text-muted-foreground">
            {format(timestamp, 'HH:mm')}
          </span>
        </div>

        {/* Attachments */}
        {attachments && attachments.length > 0 && (
          <div className="mb-3 space-y-2">
            {attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center gap-2 p-2 rounded-lg border bg-muted/50"
              >
                {attachment.type.startsWith('image/') ? (
                  <ImageIcon className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <FileText className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="text-sm truncate flex-1">{attachment.name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => downloadAttachment(attachment)}
                >
                  <Download className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        )}

        {/* Message Bubble */}
        <div className={cn(
          "relative rounded-2xl px-4 py-3 max-w-full",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-muted border"
        )}>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            {isUser ? (
              <p className="whitespace-pre-wrap break-words m-0">{content}</p>
            ) : (
              <div className="[&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-2 last:mb-0">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-2 last:mb-0">{children}</ol>,
                  code: ({ children, className }) => {
                    const isBlock = className?.includes('language-');
                    if (isBlock) {
                      return (
                        <pre className="bg-muted p-2 rounded mt-2 mb-2 overflow-x-auto">
                          <code>{children}</code>
                        </pre>
                      );
                    }
                    return (
                      <code className="bg-muted px-1 py-0.5 rounded text-sm">
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {content}
              </ReactMarkdown>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {!isUser && (
          <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={copyToClipboard}
            >
              <Copy className="h-3 w-3" />
            </Button>
            
            {copied && (
              <span className="text-xs text-green-600 dark:text-green-400">
                Copied!
              </span>
            )}

            <Button variant="ghost" size="icon" className="h-7 w-7">
              <ThumbsUp className="h-3 w-3" />
            </Button>
            
            <Button variant="ghost" size="icon" className="h-7 w-7">
              <ThumbsDown className="h-3 w-3" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7">
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={copyToClipboard}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy message
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Bot className="h-4 w-4 mr-2" />
                  Regenerate response
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>
    </div>
  );
}
