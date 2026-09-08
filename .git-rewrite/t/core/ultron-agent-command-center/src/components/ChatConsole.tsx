import React, { useState, useRef, useEffect } from 'react'
import { Conversation, ChatMessage } from '../hooks/useAppState'
import { OllamaModel } from '../hooks/useAppState'

interface ChatConsoleProps {
  conversation: Conversation | null
  activeModel: OllamaModel | null
  onSendMessage: (content: string, images?: string[]) => void
  isLoading: boolean
}

export function ChatConsole({ conversation, activeModel, onSendMessage, isLoading }: ChatConsoleProps) {
  const [inputValue, setInputValue] = useState('')
  const [selectedImages, setSelectedImages] = useState<File[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || !activeModel) return

    const content = inputValue.trim()
    let imageData: string[] | undefined

    // Convert selected images to base64
    if (selectedImages.length > 0) {
      imageData = await Promise.all(
        selectedImages.map(file => {
          return new Promise<string>((resolve) => {
            const reader = new FileReader()
            reader.onload = () => {
              const base64 = reader.result as string
              resolve(base64.split(',')[1]) // Remove data:image/... prefix
            }
            reader.readAsDataURL(file)
          })
        })
      )
    }

    onSendMessage(content, imageData)
    setInputValue('')
    setSelectedImages([])
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const imageFiles = files.filter(file => file.type.startsWith('image/'))
    setSelectedImages(prev => [...prev, ...imageFiles])
  }

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index))
  }

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="ultron-code inline">$1</code>')
      .replace(/```([\s\S]*?)```/g, '<pre class="ultron-code block">$1</pre>')
  }

  return (
    <div className="message-container">
      {/* Header */}
      <div className="p-md border-b border-slate-700">
        <h3 className="ultron-heading h3" style={{ color: 'var(--color-accent-primary)' }}>
          MULTIMODAL CHAT CONSOLE
        </h3>
        {conversation && (
          <div className="text-sm text-slate-400 mt-xs">
            {conversation.title} • {conversation.messages.length} messages
          </div>
        )}
      </div>
      
      {/* Messages */}
      <div className="message-list custom-scroll">
        {!conversation ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <div className="text-lg mb-md">Initializing...</div>
              <div className="text-sm">Setting up your conversation</div>
            </div>
          </div>
        ) : conversation.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <div className="text-lg mb-md">Ready to chat</div>
              <div className="text-sm">Send a message to start the conversation</div>
            </div>
          </div>
        ) : (
          <div className="space-y-md">
            {conversation.messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] ultron-panel p-md ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-slate-700 to-slate-600'
                      : message.error
                      ? 'bg-gradient-to-r from-red-900/50 to-red-800/50 border-red-500'
                      : 'bg-gradient-to-r from-slate-800 to-slate-700'
                  }`}
                >
                  <div className="flex items-start gap-sm">
                    <div className="flex-shrink-0">
                      {message.role === 'user' ? (
                        <div className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-xs font-bold">
                          U
                        </div>
                      ) : (
                        <div className="w-6 h-6 rounded bg-gradient-to-r from-pink-600 to-red-600 flex items-center justify-center text-xs font-bold">
                          AI
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div
                        className="text-sm leading-relaxed"
                        dangerouslySetInnerHTML={{
                          __html: formatMessage(message.content)
                        }}
                      />
                      
                      {message.images && message.images.length > 0 && (
                        <div className="mt-sm space-y-xs">
                          {message.images.map((image, imgIndex) => (
                            <img
                              key={imgIndex}
                              src={`data:image/jpeg;base64,${image}`}
                              alt="Uploaded"
                              className="max-w-full h-auto rounded border border-slate-600"
                            />
                          ))}
                        </div>
                      )}
                      
                      <div className="text-xs text-slate-500 mt-xs">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="ultron-panel p-md bg-gradient-to-r from-slate-800 to-slate-700">
                  <div className="flex items-center gap-sm">
                    <div className="w-6 h-6 rounded bg-gradient-to-r from-pink-600 to-red-600 flex items-center justify-center text-xs font-bold">
                      AI
                    </div>
                    <div className="pulse">Thinking...</div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Image Preview */}
      {selectedImages.length > 0 && (
        <div className="p-md border-t border-slate-700">
          <div className="flex gap-sm overflow-x-auto">
            {selectedImages.map((file, index) => (
              <div key={index} className="relative flex-shrink-0">
                <img
                  src={URL.createObjectURL(file)}
                  alt="Preview"
                  className="w-16 h-16 object-cover rounded border border-slate-600"
                />
                <button
                  onClick={() => removeImage(index)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-red-600 rounded-full text-xs flex items-center justify-center hover:bg-red-700"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Input */}
      <div className="message-input">
        <form onSubmit={handleSubmit} className="flex gap-sm">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/*"
            multiple
            className="hidden"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="ultron-button flex-shrink-0"
            title="Attach images"
          >
            📎
          </button>
          
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter your message..."
            className="ultron-input flex-1"
            disabled={isLoading || !activeModel}
          />
          
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading || !activeModel}
            className="ultron-button primary flex-shrink-0"
          >
            SEND
          </button>
        </form>
        
        {!activeModel && (
          <div className="text-xs text-slate-500 mt-xs">
            Select a model to start chatting
          </div>
        )}
      </div>
    </div>
  )
}
