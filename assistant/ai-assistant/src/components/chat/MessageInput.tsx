import React, { useState, useRef, useEffect } from 'react';
import { useApp, assistantPersonalities } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { 
  Send, 
  Paperclip, 
  Mic, 
  Square,
  X,
  FileText,
  Image as ImageIcon
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { v4 as uuidv4 } from 'uuid';

export default function MessageInput() {
  const { state, addMessage, dispatch, createNewConversation } = useApp();
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { currentMode, isTyping } = state;
  const personality = assistantPersonalities.find(p => p.id === currentMode);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const simulateAIResponse = async (userMessage: string) => {
    dispatch({ type: 'SET_TYPING', payload: true });
    
    // Simulate thinking time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    // Generate contextual response based on mode and content
    let response = '';
    
    if (currentMode === 'creative') {
      response = `I'd love to help you with that creative project! Here are some ideas:\n\n• **Brainstorming approach**: Let's think outside the box and explore unconventional angles\n• **Structure suggestion**: Consider a three-act approach with a compelling hook\n• **Style recommendations**: Mix descriptive language with dynamic dialogue\n\nWhat specific aspect would you like to dive deeper into?`;
    } else if (currentMode === 'technical') {
      response = `Let me help you with that technical question. Here's my analysis:\n\n\`\`\`\n// Example solution approach\nfunction handleRequest(input) {\n  // Process the input\n  return processedResult;\n}\n\`\`\`\n\n**Key considerations:**\n- Performance optimization\n- Error handling\n- Scalability factors\n\nWould you like me to elaborate on any of these points?`;
    } else if (currentMode === 'productivity') {
      response = `Great question! Here's a structured approach to boost your productivity:\n\n**📋 Action Items:**\n1. Break down your goal into smaller, manageable tasks\n2. Set specific deadlines for each milestone\n3. Use the Pomodoro Technique for focused work sessions\n\n**⏰ Time Management:**\n- Prioritize tasks using the Eisenhower Matrix\n- Block time for deep work\n- Schedule regular breaks\n\nWhat's your biggest productivity challenge right now?`;
    } else if (currentMode === 'research') {
      response = `Excellent research question! Let me provide you with a comprehensive analysis:\n\n**📊 Key Findings:**\n- Primary sources suggest multiple perspectives on this topic\n- Recent studies indicate emerging trends in this field\n- Cross-referencing data reveals interesting correlations\n\n**🔍 Methodology:**\n1. Literature review of peer-reviewed sources\n2. Data analysis from reputable databases\n3. Expert opinion synthesis\n\n**📚 Recommended next steps:**\n- Explore specific case studies\n- Review additional primary sources\n- Consider alternative viewpoints\n\nWould you like me to focus on any particular aspect?`;
    } else {
      // General mode
      response = `I understand you're asking about "${userMessage.substring(0, 50)}${userMessage.length > 50 ? '...' : ''}". Let me help you with that!\n\nBased on your question, here are some key points to consider:\n\n• **Context**: Understanding the background is important\n• **Options**: There are several approaches we could take\n• **Recommendations**: I'd suggest starting with the most straightforward solution\n\nIs there a specific aspect you'd like me to focus on or explain in more detail?`;
    }
    
    dispatch({ type: 'SET_TYPING', payload: false });
    addMessage(response, 'assistant');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() && attachments.length === 0) return;
    
    // Create new conversation if none exists
    if (!state.currentConversationId) {
      createNewConversation(currentMode);
    }

    // Process attachments
    const processedAttachments = attachments.map(file => ({
      id: uuidv4(),
      name: file.name,
      type: file.type,
      size: file.size,
      url: URL.createObjectURL(file),
      uploadedAt: new Date()
    }));

    // Add user message
    addMessage(input.trim(), 'user', processedAttachments);
    
    // Clear input
    const messageContent = input.trim();
    setInput('');
    setAttachments([]);
    
    // Simulate AI response
    await simulateAIResponse(messageContent);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments(prev => [...prev, ...files]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const startRecording = () => {
    setIsRecording(true);
    // Simulate recording - in a real app, implement voice recording
    setTimeout(() => {
      setIsRecording(false);
      setInput(prev => prev + "This is a simulated voice input. ");
    }, 2000);
  };

  return (
    <div className="space-y-3">
      {/* Current Mode Indicator */}
      {personality && (
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <span>{personality.icon}</span>
            <span className="text-xs">{personality.name} Mode</span>
          </Badge>
          <span className="text-xs text-muted-foreground">
            {personality.description}
          </span>
        </div>
      )}

      {/* Attachments */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-2 bg-muted rounded-lg"
            >
              {file.type.startsWith('image/') ? (
                <ImageIcon className="h-4 w-4" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              <span className="text-sm truncate max-w-32">{file.name}</span>
              <Button
                variant="ghost"
                size="icon"
                className="h-5 w-5"
                onClick={() => removeAttachment(index)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Message ${personality?.name || 'AI Assistant'}...`}
            className={cn(
              "min-h-[60px] max-h-[200px] resize-none pr-32",
              "focus-visible:ring-1 focus-visible:ring-ring"
            )}
            disabled={isTyping}
          />
          
          {/* Input Actions */}
          <div className="absolute bottom-3 right-3 flex items-center gap-1">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileUpload}
              accept="image/*,.pdf,.txt,.doc,.docx"
              className="hidden"
            />
            
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => fileInputRef.current?.click()}
              disabled={isTyping}
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className={cn(
                "h-8 w-8",
                isRecording && "text-red-500 animate-pulse"
              )}
              onClick={startRecording}
              disabled={isTyping || isRecording}
            >
              {isRecording ? (
                <Square className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </Button>
            
            <Button
              type="submit"
              size="icon"
              className="h-8 w-8"
              disabled={(!input.trim() && attachments.length === 0) || isTyping}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Input Help */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            Press Enter to send, Shift+Enter for new line
          </span>
          <span>
            {input.length}/4000
          </span>
        </div>
      </form>
    </div>
  );
}
