import React from 'react'
import { Bot } from 'lucide-react'

interface TypingIndicatorProps {
  model: string
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ model }) => {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%]">
        {/* Header */}
        <div className="flex items-center space-x-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center glow-subtle pulse-red">
            <Bot className="w-5 h-5" />
          </div>
          <div className="text-sm font-orbitron">
            <span className="text-red-400">{model}</span>
            <span className="text-gray-500 ml-2">is thinking...</span>
          </div>
        </div>

        {/* Typing Animation */}
        <div className="glass-intense border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-gray-400 text-sm font-roboto ml-2">Processing...</span>
          </div>
          
          {/* Scanning line effect */}
          <div className="mt-3 h-0.5 bg-gradient-to-r from-transparent via-red-500 to-transparent scan-line" />
        </div>
      </div>
    </div>
  )
}