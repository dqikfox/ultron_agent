#!/usr/bin/env python3
"""
AI Toolkit Master Interface - Unified access to all AI persona tools
"""

from tools.base import Tool
from tools.ai_agent_personas import AIAgentPersonas
from tools.persona_selector import PersonaSelector
from tools.ai_consultant_router import AIConsultantRouter
from tools.ai_team_collaboration import AITeamCollaboration
from utils.ultron_logger import log_info, log_error, log_ai_decision

class AIToolkitMaster(Tool):
    name = "ai_toolkit_master"
    description = "Master interface for all AI persona tools and capabilities"
    
    def __init__(self):
        self.personas = AIAgentPersonas()
        self.selector = PersonaSelector()
        self.router = AIConsultantRouter()
        self.collaboration = AITeamCollaboration()
        
        self.toolkit_features = {
            "personas": {
                "name": "🎭 AI Personas",
                "description": "8 specialized AI agents with distinct personalities",
                "tool": self.personas,
                "examples": ["list agents", "ask architect about system design"]
            },
            "selector": {
                "name": "🎯 Quick Selector",
                "description": "Fast access with emoji shortcuts",
                "tool": self.selector,
                "examples": ["🏗️ design microservices", "persona menu"]
            },
            "router": {
                "name": "🧠 Smart Router",
                "description": "Automatically routes questions to best persona",
                "tool": self.router,
                "examples": ["consult about database optimization", "ai help with security"]
            },
            "collaboration": {
                "name": "👥 Team Collaboration",
                "description": "Multiple personas working together",
                "tool": self.collaboration,
                "examples": ["team full stack development", "security audit team"]
            }
        }
    
    def match(self, command: str) -> bool:
        keywords = ["ai toolkit", "persona", "agent", "consultant", "help", "ai help"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, **kwargs):
        try:
            command = kwargs.get('command', '').lower()
            
            # Show toolkit overview
            if any(word in command for word in ['toolkit', 'overview', 'help', 'menu']):
                return self._show_toolkit_overview()
            
            # Route to specific feature
            if 'team' in command or 'collaborate' in command:
                return self.collaboration.execute(**kwargs)
            elif 'route' in command or 'consult' in command or 'ai help' in command:
                return self.router.execute(**kwargs)
            elif any(emoji in command for emoji in ['🏗️', '🔍', '⚡', '🛡️', '📚', '💡', '📊', '🤖']):
                return self.selector.execute(**kwargs)
            elif 'persona' in command or 'agent' in command:
                return self.personas.execute(**kwargs)
            
            # Default: show capabilities
            return self._show_toolkit_capabilities()
            
        except Exception as e:
            log_error("ai_toolkit_master", f"Execution failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _show_toolkit_overview(self) -> str:
        """Show complete AI toolkit overview"""
        result = "🚀 **ULTRON AI Toolkit - Master Interface**\n\n"
        result += "Your comprehensive AI assistant ecosystem with specialized personas and intelligent routing.\n\n"
        
        # Feature overview
        for feature_key, feature_data in self.toolkit_features.items():
            result += f"### {feature_data['name']}\n"
            result += f"{feature_data['description']}\n\n"
            result += "**Examples:**\n"
            for example in feature_data['examples']:
                result += f"• `{example}`\n"
            result += "\n"
        
        result += "### 🎯 **Quick Start Guide**\n\n"
        result += "**1. Direct Persona Access:**\n"
        result += "• `🏗️ design a REST API architecture`\n"
        result += "• `🔍 debug this authentication error`\n"
        result += "• `⚡ optimize database query performance`\n\n"
        
        result += "**2. Smart Routing:**\n"
        result += "• `consult about microservices security`\n"
        result += "• `ai help with performance optimization`\n\n"
        
        result += "**3. Team Collaboration:**\n"
        result += "• `team full stack development for e-commerce`\n"
        result += "• `security audit team for API endpoints`\n\n"
        
        result += "**4. Browse & Select:**\n"
        result += "• `persona menu` - Interactive selection\n"
        result += "• `list agents` - View all personas\n"
        
        log_info("ai_toolkit_master", "Displayed toolkit overview")
        return result
    
    def _show_toolkit_capabilities(self) -> str:
        """Show detailed toolkit capabilities"""
        result = "🧠 **AI Toolkit Capabilities**\n\n"
        
        # Persona capabilities
        result += "### 🎭 **Available AI Personas**\n\n"
        for agent_key, agent_data in self.personas.agents.items():
            result += f"{agent_data['emoji']} **{agent_data['name']}**\n"
            result += f"   • Specialty: {agent_data['specialty']}\n"
            result += f"   • Personality: {agent_data['personality']}\n"
            result += f"   • Quick Access: `{agent_data['emoji']} [your question]`\n\n"
        
        # Collaboration teams
        result += "### 👥 **Collaboration Teams**\n\n"
        for team_key, team_data in self.collaboration.collaboration_templates.items():
            result += f"🎯 **{team_data['name']}**\n"
            result += f"   • Purpose: {team_data['description']}\n"
            result += f"   • Usage: `team {team_key.replace('_', ' ')} for [problem]`\n\n"
        
        # Advanced features
        result += "### 🚀 **Advanced Features**\n\n"
        result += "• **Smart Question Routing**: Automatically selects best persona\n"
        result += "• **Multi-Persona Collaboration**: Teams work together on complex problems\n"
        result += "• **Context-Aware Analysis**: Understands question patterns and intent\n"
        result += "• **Emoji Shortcuts**: Quick access with visual identifiers\n"
        result += "• **Integrated Logging**: All consultations tracked for learning\n\n"
        
        result += "**Try:** `ai help [your question]` for automatic routing!"
        
        return result
    
    def get_toolkit_stats(self) -> dict:
        """Get toolkit usage statistics"""
        return {
            "total_personas": len(self.personas.agents),
            "collaboration_teams": len(self.collaboration.collaboration_templates),
            "features": len(self.toolkit_features),
            "routing_keywords": sum(len(keywords) for keywords in self.router.routing_keywords.values())
        }
    
    @staticmethod
    def schema():
        return {
            "name": "ai_toolkit_master",
            "description": "Master interface providing unified access to all AI persona tools, smart routing, and team collaboration features",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Command for AI toolkit (overview, help, specific persona/team request)"
                }
            }
        }