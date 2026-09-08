import React from 'react';
import { useApp, assistantPersonalities } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  MessageSquare, 
  Sparkles, 
  FileText, 
  Search,
  Lightbulb,
  Zap,
  Brain,
  Target
} from 'lucide-react';

export default function EmptyState() {
  const { state, createNewConversation, dispatch } = useApp();
  const { currentMode } = state;
  
  const currentPersonality = assistantPersonalities.find(p => p.id === currentMode);

  const suggestions = {
    general: [
      { icon: <Lightbulb className="h-4 w-4" />, text: "Explain a complex topic in simple terms", category: "Learning" },
      { icon: <FileText className="h-4 w-4" />, text: "Help me write a professional email", category: "Writing" },
      { icon: <Search className="h-4 w-4" />, text: "Research the latest trends in technology", category: "Research" },
      { icon: <Target className="h-4 w-4" />, text: "Plan my day for maximum productivity", category: "Planning" }
    ],
    creative: [
      { icon: <Sparkles className="h-4 w-4" />, text: "Write a short story about time travel", category: "Fiction" },
      { icon: <Brain className="h-4 w-4" />, text: "Brainstorm ideas for a unique business", category: "Ideation" },
      { icon: <FileText className="h-4 w-4" />, text: "Create a compelling character backstory", category: "Writing" },
      { icon: <Lightbulb className="h-4 w-4" />, text: "Generate creative solutions to a problem", category: "Problem Solving" }
    ],
    technical: [
      { icon: <Brain className="h-4 w-4" />, text: "Explain how machine learning works", category: "AI/ML" },
      { icon: <FileText className="h-4 w-4" />, text: "Write a Python function to process data", category: "Coding" },
      { icon: <Search className="h-4 w-4" />, text: "Compare different database technologies", category: "Architecture" },
      { icon: <Zap className="h-4 w-4" />, text: "Debug a performance issue in my code", category: "Debugging" }
    ],
    productivity: [
      { icon: <Target className="h-4 w-4" />, text: "Create a weekly schedule template", category: "Planning" },
      { icon: <Lightbulb className="h-4 w-4" />, text: "Suggest time management techniques", category: "Efficiency" },
      { icon: <FileText className="h-4 w-4" />, text: "Design a project management workflow", category: "Organization" },
      { icon: <Zap className="h-4 w-4" />, text: "Optimize my daily routine", category: "Habits" }
    ],
    research: [
      { icon: <Search className="h-4 w-4" />, text: "Find credible sources on climate change", category: "Environment" },
      { icon: <Brain className="h-4 w-4" />, text: "Analyze market trends in renewable energy", category: "Market Analysis" },
      { icon: <FileText className="h-4 w-4" />, text: "Summarize recent scientific publications", category: "Academic" },
      { icon: <Lightbulb className="h-4 w-4" />, text: "Compare different research methodologies", category: "Methodology" }
    ]
  };

  const currentSuggestions = suggestions[currentMode] || suggestions.general;

  const handleSuggestionClick = (suggestion: string) => {
    createNewConversation(currentMode);
    // We would add the message here, but let's create the conversation first
    setTimeout(() => {
      // This would trigger the message input with the suggestion
      const event = new CustomEvent('suggestion-clicked', { detail: suggestion });
      window.dispatchEvent(event);
    }, 100);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 max-w-4xl mx-auto">
      {/* Welcome Section */}
      <div className="text-center mb-8">
        {currentPersonality && (
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl">
              {currentPersonality.icon}
            </div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome to {currentPersonality.name}
            </h1>
            <p className="text-muted-foreground text-lg max-w-2xl">
              {currentPersonality.description}
            </p>
          </div>
        )}
      </div>

      {/* AI Mode Selector */}
      <div className="mb-8">
        <p className="text-sm text-muted-foreground mb-3 text-center">
          Choose your AI assistant mode:
        </p>
        <div className="flex flex-wrap gap-2 justify-center">
          {assistantPersonalities.map((personality) => (
            <Button
              key={personality.id}
              variant={personality.id === currentMode ? "default" : "outline"}
              size="sm"
              onClick={() => dispatch({ type: 'SET_CURRENT_MODE', payload: personality.id })}
              className="flex items-center gap-2"
            >
              <span>{personality.icon}</span>
              <span>{personality.name}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div className="w-full max-w-3xl">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          Get started with these suggestions:
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentSuggestions.map((suggestion, index) => (
            <Card 
              key={index}
              className="cursor-pointer hover:shadow-md transition-shadow border-2 hover:border-primary/20"
              onClick={() => handleSuggestionClick(suggestion.text)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="text-primary mt-1">
                    {suggestion.icon}
                  </div>
                  <div className="flex-1">
                    <Badge variant="secondary" className="text-xs mb-2">
                      {suggestion.category}
                    </Badge>
                    <p className="text-sm font-medium leading-relaxed">
                      {suggestion.text}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 flex flex-wrap gap-3 justify-center">
        <Button 
          onClick={() => createNewConversation(currentMode)}
          className="flex items-center gap-2"
        >
          <MessageSquare className="h-4 w-4" />
          Start New Chat
        </Button>
        
        <Button 
          variant="outline"
          onClick={() => {
            const input = document.querySelector('textarea');
            if (input) {
              input.focus();
            }
          }}
        >
          <FileText className="h-4 w-4 mr-2" />
          Upload File
        </Button>
      </div>

      {/* Features */}
      <div className="mt-12 text-center">
        <p className="text-sm text-muted-foreground mb-4">
          Powerful features at your fingertips:
        </p>
        <div className="flex flex-wrap gap-6 justify-center text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <FileText className="h-3 w-3" />
            File Processing
          </span>
          <span className="flex items-center gap-1">
            <Search className="h-3 w-3" />
            Web Search
          </span>
          <span className="flex items-center gap-1">
            <Brain className="h-3 w-3" />
            Multiple AI Modes
          </span>
          <span className="flex items-center gap-1">
            <Target className="h-3 w-3" />
            Productivity Tools
          </span>
        </div>
      </div>
    </div>
  );
}
