#!/usr/bin/env python3
"""
AI Consultant Router - Automatically routes questions to the most appropriate AI persona
"""

from tools.base import Tool
from tools.ai_agent_personas import AIAgentPersonas
from utils.ultron_logger import log_info, log_error, log_ai_decision
import re

class AIConsultantRouter(Tool):
    name = "ai_consultant_router"
    description = "Automatically routes questions to the most appropriate AI persona based on content analysis"
    
    def __init__(self):
        self.personas = AIAgentPersonas()
        self.routing_keywords = {
            "architect": [
                "design", "architecture", "system", "structure", "framework", "pattern",
                "scalability", "microservices", "api design", "database design", "infrastructure"
            ],
            "debugger": [
                "error", "bug", "debug", "troubleshoot", "fix", "broken", "issue", "problem",
                "exception", "crash", "failure", "not working", "investigate"
            ],
            "optimizer": [
                "optimize", "performance", "speed", "slow", "memory", "cpu", "efficiency",
                "bottleneck", "profiling", "cache", "faster", "resource usage"
            ],
            "security": [
                "security", "vulnerability", "authentication", "authorization", "encryption",
                "secure", "attack", "threat", "penetration", "audit", "compliance", "privacy"
            ],
            "teacher": [
                "explain", "how", "what", "why", "learn", "understand", "tutorial", "guide",
                "teach", "concept", "basics", "fundamentals", "introduction"
            ],
            "innovator": [
                "creative", "innovative", "new approach", "alternative", "brainstorm", "idea",
                "novel", "experimental", "cutting edge", "breakthrough", "disruptive"
            ],
            "analyst": [
                "analyze", "data", "metrics", "statistics", "report", "insights", "trends",
                "patterns", "dashboard", "visualization", "business intelligence"
            ],
            "automator": [
                "automate", "script", "workflow", "process", "repetitive", "batch", "schedule",
                "pipeline", "ci/cd", "deployment", "orchestration", "integration"
            ]
        }
    
    def match(self, command: str) -> bool:
        keywords = ["consult", "ask ai", "ai help", "expert", "advisor", "consultant"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, **kwargs):
        try:
            command = kwargs.get('command', '')
            
            if not command or len(command) < 10:
                return self._show_consultant_help()
            
            # Analyze question and route to appropriate persona
            best_persona = self._analyze_and_route(command)
            
            if best_persona:
                # Create consultation with the selected persona
                consult_command = f"ask {best_persona} about {command}"
                result = self.personas._consult_agent(consult_command, {'command': consult_command})
                
                # Add routing information
                persona_data = self.personas.agents[best_persona]
                routing_info = f"\n\n🎯 **Auto-Routed to {persona_data['emoji']} {persona_data['name']}**\n"
                routing_info += f"*Selected based on question analysis and expertise match*"
                
                log_ai_decision("ai_consultant_router", f"Routed question to {best_persona}", ai_model="routing_algorithm")
                return result + routing_info
            else:
                return self._show_available_consultants(command)
                
        except Exception as e:
            log_error("ai_consultant_router", f"Routing failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _analyze_and_route(self, question: str) -> str:
        """Analyze question content and route to best persona"""
        question_lower = question.lower()
        
        # Score each persona based on keyword matches
        persona_scores = {}
        
        for persona, keywords in self.routing_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in question_lower:
                    # Weight longer keywords more heavily
                    score += len(keyword.split())
            
            if score > 0:
                persona_scores[persona] = score
        
        # Additional context-based scoring
        persona_scores = self._apply_context_scoring(question_lower, persona_scores)
        
        # Return the highest scoring persona
        if persona_scores:
            best_persona = max(persona_scores, key=persona_scores.get)
            log_info("ai_consultant_router", f"Question analysis scores: {persona_scores}")
            return best_persona
        
        return None
    
    def _apply_context_scoring(self, question: str, scores: dict) -> dict:
        """Apply additional context-based scoring"""
        
        # Question patterns that indicate specific personas
        patterns = {
            "architect": [
                r"how to (design|structure|organize)",
                r"best practices for (system|architecture)",
                r"(microservices|monolith|api) design"
            ],
            "debugger": [
                r"(error|exception|bug).*(fix|solve|debug)",
                r"why (is|does).*(not work|fail|crash)",
                r"troubleshoot.*problem"
            ],
            "optimizer": [
                r"make.*(faster|efficient|better performance)",
                r"(slow|performance).*(issue|problem)",
                r"optimize.*(code|query|algorithm)"
            ],
            "security": [
                r"(secure|protect|vulnerability).*(assessment|review)",
                r"(authentication|authorization).*(implement|design)",
                r"security.*(best practices|audit)"
            ],
            "teacher": [
                r"(explain|teach|show).*(how to|what is)",
                r"(understand|learn).*(concept|basics)",
                r"(tutorial|guide).*(for|on)"
            ],
            "innovator": [
                r"(creative|innovative|new).*(solution|approach|idea)",
                r"(alternative|different).*(way|method|approach)",
                r"(brainstorm|ideate).*(solutions|approaches)"
            ],
            "analyst": [
                r"(analyze|examine).*(data|metrics|performance)",
                r"(insights|patterns).*(from|in).*(data|logs)",
                r"(dashboard|report).*(showing|displaying)"
            ],
            "automator": [
                r"(automate|script).*(process|task|workflow)",
                r"(repetitive|manual).*(task|process)",
                r"(ci/cd|pipeline|deployment).*(automation|setup)"
            ]
        }
        
        for persona, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, question):
                    scores[persona] = scores.get(persona, 0) + 3  # Bonus for pattern match
        
        return scores
    
    def _show_consultant_help(self) -> str:
        """Show help for the AI consultant router"""
        result = "🎯 **AI Consultant Router**\n\n"
        result += "I automatically route your questions to the most appropriate AI expert!\n\n"
        
        result += "**How it works:**\n"
        result += "1. Analyze your question content\n"
        result += "2. Match keywords and patterns\n"
        result += "3. Route to the best-suited AI persona\n"
        result += "4. Provide expert consultation\n\n"
        
        result += "**Example Questions:**\n"
        result += "• 'How do I design a scalable microservices architecture?' → 🏗️ Architect\n"
        result += "• 'My authentication is throwing errors' → 🔍 Detective\n"
        result += "• 'This database query is too slow' → ⚡ Optimizer\n"
        result += "• 'Security review for my API endpoints' → 🛡️ Guardian\n"
        result += "• 'Explain how async/await works' → 📚 Mentor\n\n"
        
        result += "**Usage:** Just ask your question naturally, and I'll route it to the right expert!\n"
        
        return result
    
    def _show_available_consultants(self, question: str) -> str:
        """Show available consultants when routing fails"""
        result = f"🤔 **Question Analysis**\n\n"
        result += f"Your question: *{question}*\n\n"
        result += "I couldn't automatically determine the best consultant. Here are your options:\n\n"
        
        for agent_key, agent_data in self.personas.agents.items():
            result += f"{agent_data['emoji']} **{agent_data['name']}** - {agent_data['specialty']}\n"
        
        result += "\n**Manual Selection:**\n"
        result += f"• Type: 'ask [persona] about {question}'\n"
        result += f"• Or use emoji: '🏗️ {question}'\n"
        
        return result
    
    @staticmethod
    def schema():
        return {
            "name": "ai_consultant_router",
            "description": "Automatically routes questions to the most appropriate AI persona based on intelligent content analysis",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Question or problem to route to appropriate AI consultant"
                }
            }
        }