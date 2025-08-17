#!/usr/bin/env python3
"""
Copilot Assistant - Real-time advice and assistance
"""

import time
import json
from copilot_monitor import copilot_monitor, get_copilot_advice

class CopilotAssistant:
    """Provides real-time assistance for GitHub Copilot usage"""
    
    def __init__(self):
        self.last_advice_time = 0
        self.advice_interval = 300  # 5 minutes
        
    def check_and_advise(self):
        """Check usage patterns and provide advice"""
        current_time = time.time()
        
        if current_time - self.last_advice_time > self.advice_interval:
            stats = get_copilot_advice()
            advice = stats.get("advice", [])
            
            if advice:
                print("\n🤖 Copilot Assistant Advice:")
                for tip in advice:
                    print(f"   {tip}")
                print()
                
            self.last_advice_time = current_time
            return advice
        
        return []
    
    def get_quick_tips(self) -> list:
        """Get quick tips for better Copilot usage"""
        return [
            "💡 Write comments describing what you want to code",
            "🎯 Use descriptive variable and function names", 
            "⚡ Press Tab to accept, Esc to reject suggestions",
            "🔄 Use Alt+] and Alt+[ to cycle through suggestions",
            "💬 Try Ctrl+I for inline chat with Copilot",
            "🚀 Use Copilot Chat for complex problem solving"
        ]
    
    def analyze_current_context(self, file_type: str = "", code_context: str = ""):
        """Analyze current coding context and provide specific advice"""
        advice = []
        
        if file_type == "python":
            advice.extend([
                "🐍 Python: Use type hints for better suggestions",
                "📝 Write docstrings for function completions"
            ])
        elif file_type == "javascript":
            advice.extend([
                "⚡ JS: Use JSDoc comments for better completions",
                "🔧 Consider async/await patterns"
            ])
        elif file_type == "typescript":
            advice.extend([
                "🔷 TS: Define interfaces for better type completions",
                "⚙️ Use generic types for flexible suggestions"
            ])
        
        return advice

# Global assistant instance
copilot_assistant = CopilotAssistant()

def show_copilot_tips():
    """Show quick Copilot tips"""
    tips = copilot_assistant.get_quick_tips()
    print("\n🤖 GitHub Copilot Quick Tips:")
    for tip in tips:
        print(f"   {tip}")
    print()

def get_contextual_advice(file_type: str = "", code_context: str = ""):
    """Get advice based on current context"""
    return copilot_assistant.analyze_current_context(file_type, code_context)

if __name__ == "__main__":
    show_copilot_tips()
    
    # Monitor and provide advice
    while True:
        try:
            copilot_assistant.check_and_advise()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nCopilot Assistant stopped")
            break