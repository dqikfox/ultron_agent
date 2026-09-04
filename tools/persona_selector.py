#!/usr/bin/env python3
"""
Persona Selector - Quick access interface for AI agent personas
"""

from tools.base import Tool
from tools.ai_agent_personas import AIAgentPersonas
from utils.ultron_logger import log_info, log_error
import json

class PersonaSelector(Tool):
    name = "persona_selector"
    description = "Quick access interface for AI agent personas"
    
    def __init__(self):
        self.personas = AIAgentPersonas()
        self.quick_commands = {
            "🏗️": "architect",
            "🔍": "debugger", 
            "⚡": "optimizer",
            "🛡️": "security",
            "📚": "teacher",
            "💡": "innovator",
            "📊": "analyst",
            "🤖": "automator"
        }
    
    def match(self, command: str) -> bool:
        keywords = ["persona", "agent", "help", "consult", "ask"]
        emoji_match = any(emoji in command for emoji in self.quick_commands.keys())
        return any(keyword in command.lower() for keyword in keywords) or emoji_match
    
    def execute(self, **kwargs):
        try:
            command = kwargs.get('command', '').lower()
            
            # Quick emoji selection
            for emoji, agent_key in self.quick_commands.items():
                if emoji in command:
                    return self._quick_consult(agent_key, command)
            
            # Show persona menu
            if any(word in command for word in ['menu', 'select', 'choose', 'help']):
                return self._show_persona_menu()
            
            # Delegate to main personas tool
            return self.personas.execute(**kwargs)
            
        except Exception as e:
            log_error("persona_selector", f"Execution failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _show_persona_menu(self) -> str:
        """Show interactive persona selection menu"""
        result = "🎭 **AI Persona Selector**\n\n"
        result += "Choose your AI assistant by typing the emoji or name:\n\n"
        
        personas_data = self.personas.agents
        
        for emoji, agent_key in self.quick_commands.items():
            agent = personas_data[agent_key]
            result += f"{emoji} **{agent['name']}** - {agent['specialty']}\n"
        
        result += "\n**Quick Commands:**\n"
        result += "• Type emoji + your question: '🏗️ design a microservices architecture'\n"
        result += "• Use name: 'ask architect about system design'\n"
        result += "• Get help: 'persona help' or 'agent menu'\n"
        
        result += "\n**Example Consultations:**\n"
        result += "• 🔍 'debug this authentication error'\n"
        result += "• ⚡ 'optimize this database query'\n"
        result += "• 🛡️ 'security review for API endpoints'\n"
        result += "• 📚 'explain async/await in Python'\n"
        
        log_info("persona_selector", "Displayed persona selection menu")
        return result
    
    def _quick_consult(self, agent_key: str, command: str) -> str:
        """Quick consultation with an agent using emoji"""
        # Extract question after emoji
        for emoji in self.quick_commands.keys():
            if emoji in command:
                question = command.replace(emoji, '').strip()
                break
        
        if not question or len(question) < 3:
            agent = self.personas.agents[agent_key]
            return f"{agent['emoji']} **{agent['name']}** is ready to help!\n\nPlease provide your question after the emoji.\nExample: '{agent['emoji']} how do I optimize database queries?'"
        
        # Create consultation command
        consult_command = f"ask {agent_key} about {question}"
        return self.personas._consult_agent(consult_command, {'command': consult_command})
    
    @staticmethod
    def schema():
        return {
            "name": "persona_selector",
            "description": "Quick access interface for AI agent personas with emoji shortcuts",
            "parameters": {
                "command": {
                    "type": "string", 
                    "description": "Command with emoji or persona name"
                }
            }
        }