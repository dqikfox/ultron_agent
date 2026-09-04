import React from 'react'
import { User, Bot, Info, Clock, Cpu } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  model?: string
  tokens?: number
  responseTime?: number
}

interface ChatMessageProps {
  message: Message
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const isAssistant = message.role === 'assistant'

  const getIcon = () => {
    if (isUser) return <User className="w-5 h-5" />
    if (isSystem) return <Info className="w-5 h-5" />
    return <Bot className="w-5 h-5" />
  }

  const getAvatarBg = () => {
    if (isUser) return 'bg-blue-600'
    if (isSystem) return 'bg-yellow-600'
    return 'bg-red-600'
  }

  const getMessageBg = () => {
    if (isUser) return 'glass'
    if (isSystem) return 'bg-yellow-900/20 border-yellow-500/30'
    return 'glass-intense'
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    })
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message Header */}
        <div className={`flex items-center space-x-2 mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && (
            <div className={`w-8 h-8 rounded-full ${getAvatarBg()} flex items-center justify-center glow-subtle`}>
              {getIcon()}
            </div>
          )}
          
          <div className={`text-sm font-orbitron ${isUser ? 'text-right' : 'text-left'}`}>
            <span className={`${isUser ? 'text-blue-400' : isSystem ? 'text-yellow-400' : 'text-red-400'}`}>
              {isUser ? 'You' : isSystem ? 'System' : message.model || 'Assistant'}
            </span>
            <span className="text-gray-500 ml-2">
              {formatTime(message.timestamp)}
            </span>
          </div>
          
          {isUser && (
            <div className={`w-8 h-8 rounded-full ${getAvatarBg()} flex items-center justify-center glow-subtle`}>
              {getIcon()}
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className={`${getMessageBg()} border rounded-lg p-4 ${isUser ? 'border-blue-500/30' : 'border-red-500/30'}`}>
          {isAssistant ? (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || '')
                    const isCodeBlock = match && className
                    return isCodeBlock ? (
                      <SyntaxHighlighter
                        style={atomDark}
                        language={match[1]}
                        PreTag="div"
                        className="rounded-md"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className="bg-gray-800 px-1 py-0.5 rounded text-red-400" {...props}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="font-roboto whitespace-pre-wrap">
              {message.content}
            </div>
          )}
        </div>

        {/* Message Metadata */}
        {isAssistant && (message.tokens || message.responseTime) && (
          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 font-roboto">
            {message.responseTime && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{message.responseTime}ms</span>
              </div>
            )}
            {message.tokens && (
              <div className="flex items-center space-x-1">
                <Cpu className="w-3 h-3" />
                <span>{message.tokens} tokens</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}