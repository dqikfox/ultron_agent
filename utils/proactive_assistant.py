"""
Proactive Assistant - Suggests actions based on context
"""
from utils.ultron_logger import log_info, log_ai_decision
from typing import Dict, List, Any, Optional
import asyncio

class ProactiveAssistant:
    """Analyzes context and suggests proactive actions"""
    
    def __init__(self, brain, tools, memory):
        self.brain = brain
        self.tools = tools
        self.memory = memory
        self.suggestion_cooldown = 300  # 5 minutes between suggestions
        self.last_suggestion_time = 0
    
    async def analyze_context_and_suggest(self) -> Optional[Dict[str, Any]]:
        """Analyze current context and suggest actions"""
        import time
        
        # Check cooldown
        if time.time() - self.last_suggestion_time < self.suggestion_cooldown:
            return None
        
        suggestions = []
        
        # Check memory for patterns
        if self.memory:
            recent = self.memory.get_recent_context(limit=10)
            if len(recent) > 5:
                suggestions.append({
                    "type": "memory_analysis",
                    "action": "analyze_conversation_patterns",
                    "reason": f"Found {len(recent)} recent interactions - can identify patterns"
                })
        
        # Check tool usage
        if self.tools:
            tool_count = len(self.tools)
            suggestions.append({
                "type": "tool_discovery",
                "action": "list_available_tools",
                "reason": f"{tool_count} tools available - explore capabilities"
            })
        
        # Suggest project analysis
        suggestions.append({
            "type": "project_health",
            "action": "analyze_project_structure",
            "reason": "Regular project health checks recommended"
        })
        
        if suggestions:
            self.last_suggestion_time = time.time()
            log_ai_decision("proactive_assistant", 
                          f"Generated {len(suggestions)} suggestions",
                          "proactive_assistant",
                          confidence_score=0.8)
            return {
                "suggestions": suggestions,
                "timestamp": time.time()
            }
        
        return None
    
    async def execute_suggestion(self, suggestion: Dict[str, Any]) -> str:
        """Execute a proactive suggestion"""
        action = suggestion.get("action")
        
        if action == "analyze_conversation_patterns":
            return await self._analyze_patterns()
        elif action == "list_available_tools":
            return self._list_tools()
        elif action == "analyze_project_structure":
            return await self._analyze_project()
        
        return "Unknown suggestion action"
    
    async def _analyze_patterns(self) -> str:
        """Analyze conversation patterns"""
        if not self.memory:
            return "Memory not available"
        
        recent = self.memory.get_recent_context(limit=20)
        if not recent:
            return "No conversation history"
        
        # Use brain to analyze
        prompt = f"Analyze these {len(recent)} recent interactions and identify patterns or insights"
        return await self.brain.direct_chat(prompt)
    
    def _list_tools(self) -> str:
        """List available tools with descriptions"""
        if not self.tools:
            return "No tools loaded"
        
        tool_list = []
        for name, tool in list(self.tools.items())[:10]:  # First 10
            desc = getattr(tool, 'description', 'No description')
            tool_list.append(f"• {name}: {desc}")
        
        return f"Available tools ({len(self.tools)} total):\n" + "\n".join(tool_list)
    
    async def _analyze_project(self) -> str:
        """Analyze project structure"""
        if not self.brain:
            return "Brain not available"
        
        prompt = "Analyze the ultron_agent project structure and suggest improvements"
        return await self.brain.direct_chat(prompt)
