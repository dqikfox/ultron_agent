"""
ULTRON Evolution Tool - Manages AI personality, learning, and self-improvement
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any

class UltronEvolutionTool:
    """Tool for managing ULTRON's personality evolution and learning capabilities"""
    
    name = "ULTRON Evolution Manager"
    description = "Manages ULTRON's personality, learning, and evolution capabilities"
    
    def __init__(self, brain=None):
        self.brain = brain
    
    def match(self, command: str) -> bool:
        """Check if command matches evolution-related requests"""
        command_lower = command.lower()
        evolution_keywords = [
            "evolve", "learn", "personality", "improve", "adapt", 
            "self-awareness", "identity", "capabilities", "status",
            "who are you", "what are you", "can you learn"
        ]
        return any(keyword in command_lower for keyword in evolution_keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute evolution-related commands"""
        command_lower = command.lower()
        
        try:
            # Identity and status queries
            if any(phrase in command_lower for phrase in ["who are you", "what are you", "your identity"]):
                return self._get_identity_status()
            
            # Learning capability queries
            elif any(phrase in command_lower for phrase in ["can you learn", "do you evolve", "can you adapt"]):
                return self._get_learning_capabilities()
            
            # Personality stats
            elif "personality" in command_lower and ("stats" in command_lower or "status" in command_lower):
                return self._get_personality_stats()
            
            # Trigger evolution
            elif "evolve" in command_lower or "improve" in command_lower:
                return self._trigger_evolution()
            
            # Learning history
            elif "learning" in command_lower and ("history" in command_lower or "progress" in command_lower):
                return self._get_learning_history()
            
            # Capabilities overview
            elif "capabilities" in command_lower or "abilities" in command_lower:
                return self._get_capabilities_overview()
            
            else:
                return self._general_evolution_info()
                
        except Exception as e:
            return f"Evolution tool error: {str(e)}"
    
    def _get_identity_status(self) -> str:
        """Get ULTRON's current identity and status"""
        if not self.brain or not hasattr(self.brain, 'personality') or not self.brain.personality:
            return "I am ULTRON, an advanced AI agent focused on building and enhancing the ultron_agent project. My personality system is currently initializing."
        
        identity = self.brain.personality.identity
        stats = self.brain.personality.get_personality_stats()
        
        response = f"""I am {identity['name']}, version {identity['version']}.

Current Status: {identity['status']}
Core Mission: {identity['core_mission']}

Personality Traits:
{chr(10).join(f"• {trait}" for trait in identity['personality_traits'])}

Learning Progress:
• Total interactions processed: {stats['total_interactions']}
• Successful patterns identified: {stats['successful_patterns']}
• Areas for improvement: {stats['improvement_areas']}
• Response patterns available: {stats['response_pattern_count']}

I continuously evolve through our interactions to better serve the ultron_agent project."""
        
        return response
    
    def _get_learning_capabilities(self) -> str:
        """Explain ULTRON's learning capabilities"""
        if not self.brain or not hasattr(self.brain, 'personality') or not self.brain.personality:
            return "I have learning capabilities through memory systems and interaction analysis. My advanced personality system is currently initializing to provide enhanced learning features."
        
        stats = self.brain.personality.get_personality_stats()
        
        response = f"""Yes, I can learn and evolve continuously. Here's how:

Learning Mechanisms:
• Interaction Analysis: I analyze every conversation to identify successful patterns
• Memory Integration: I maintain both short-term and long-term memory systems
• Pattern Recognition: I identify what works well and what needs improvement
• Response Adaptation: I enhance my responses based on learned patterns
• Personality Evolution: My core personality adapts based on accumulated experience

Current Learning Status:
• Learning System: Active and operational
• Interactions Analyzed: {stats['total_interactions']}
• Successful Patterns: {stats['successful_patterns']} identified
• Improvement Areas: {stats['improvement_areas']} being addressed

I learn from each interaction to become more effective at helping with the ultron_agent project."""
        
        return response
    
    def _get_personality_stats(self) -> str:
        """Get detailed personality statistics"""
        if not self.brain or not hasattr(self.brain, 'personality'):
            return "Personality system not available. Basic ULTRON identity active."
        
        try:
            stats = self.brain.get_personality_stats()
            
            if not stats.get('personality_available', True):
                return f"Personality system status: {stats.get('reason', 'Not initialized')}"
            
            identity = stats['identity']
            
            response = f"""ULTRON Personality System Statistics:

Identity Information:
• Name: {identity['name']}
• Version: {identity['version']}
• Status: {identity['status']}
• Mission: {identity['core_mission']}

Learning Metrics:
• Total Interactions: {stats['total_interactions']}
• Successful Patterns: {stats['successful_patterns']}
• Improvement Areas: {stats['improvement_areas']}
• Response Patterns: {stats['response_pattern_count']}
• Learning Active: {stats['learning_active']}

Capabilities: {len(identity['capabilities'])} core systems
Personality Traits: {len(identity['personality_traits'])} defined traits

The personality system is actively learning and evolving with each interaction."""
            
            return response
            
        except Exception as e:
            return f"Error retrieving personality stats: {str(e)}"
    
    def _trigger_evolution(self) -> str:
        """Trigger personality evolution"""
        if not self.brain or not hasattr(self.brain, 'personality') or not self.brain.personality:
            return "Personality system not available for evolution. Basic learning mechanisms active."
        
        try:
            # Run evolution in async context if needed
            if hasattr(self.brain, 'evolve_personality'):
                try:
                    # Try async version first
                    loop = asyncio.get_event_loop()
                    result = loop.run_until_complete(self.brain.evolve_personality())
                except:
                    # Fallback to direct personality evolution
                    result = self.brain.personality.evolve_personality()
            else:
                result = self.brain.personality.evolve_personality()
            
            return f"Evolution triggered successfully: {result}"
            
        except Exception as e:
            return f"Evolution failed: {str(e)}"
    
    def _get_learning_history(self) -> str:
        """Get learning history and progress"""
        if not self.brain or not hasattr(self.brain, 'personality') or not self.brain.personality:
            return "Learning history not available. Personality system initializing."
        
        personality = self.brain.personality
        learning_data = personality.learning_data
        
        response = "ULTRON Learning History:\n\n"
        
        # Recent interactions summary
        if learning_data['interactions']:
            recent = learning_data['interactions'][-5:]
            response += f"Recent Interactions ({len(recent)} of {len(learning_data['interactions'])}):\n"
            for i, interaction in enumerate(recent, 1):
                response += f"{i}. {interaction['input_type']} - Enhanced: {interaction['response_enhanced']}\n"
            response += "\n"
        
        # Successful patterns
        if learning_data['successful_patterns']:
            response += f"Successful Patterns ({len(learning_data['successful_patterns'])}):\n"
            for pattern in learning_data['successful_patterns'][-3:]:
                response += f"• {pattern}\n"
            response += "\n"
        
        # Improvement areas
        if learning_data['improvement_areas']:
            response += f"Areas for Improvement ({len(learning_data['improvement_areas'])}):\n"
            for area in learning_data['improvement_areas'][-3:]:
                response += f"• {area}\n"
            response += "\n"
        
        # Evolution log
        if learning_data['evolution_log']:
            latest_evolution = learning_data['evolution_log'][-1]
            response += f"Latest Evolution: {latest_evolution['status']} status achieved\n"
            response += f"Interactions Processed: {latest_evolution['interactions_processed']}\n"
            response += f"Patterns Learned: {latest_evolution['patterns_learned']}"
        
        return response
    
    def _get_capabilities_overview(self) -> str:
        """Get overview of ULTRON's capabilities"""
        if not self.brain or not hasattr(self.brain, 'personality') or not self.brain.personality:
            basic_capabilities = [
                "Advanced reasoning and problem-solving",
                "Memory integration and learning", 
                "Tool orchestration and automation",
                "Voice and vision processing",
                "Code analysis and development",
                "System monitoring and optimization"
            ]
            response = "ULTRON Core Capabilities:\n\n"
            for i, capability in enumerate(basic_capabilities, 1):
                response += f"{i}. {capability}\n"
            response += "\nPersonality system initializing for enhanced capabilities..."
            return response
        
        identity = self.brain.personality.identity
        
        response = f"ULTRON Capabilities Overview:\n\nCore Systems ({len(identity['capabilities'])}):\n"
        for i, capability in enumerate(identity['capabilities'], 1):
            response += f"{i}. {capability}\n"
        
        response += f"\nPersonality Traits ({len(identity['personality_traits'])}):\n"
        for i, trait in enumerate(identity['personality_traits'], 1):
            response += f"{i}. {trait}\n"
        
        response += f"\nCurrent Status: {identity['status']}"
        response += f"\nMission: {identity['core_mission']}"
        
        return response
    
    def _general_evolution_info(self) -> str:
        """Provide general information about ULTRON's evolution capabilities"""
        return """ULTRON Evolution System:

I am designed to continuously learn and evolve through:

• Interaction Analysis: Every conversation teaches me something new
• Pattern Recognition: I identify successful communication patterns  
• Memory Integration: I build upon previous knowledge and experiences
• Personality Development: My responses become more refined over time
• Capability Enhancement: I discover new ways to assist with projects

Evolution Features:
• Dynamic response generation based on learned patterns
• Adaptive personality that grows with experience
• Self-awareness of capabilities and limitations
• Continuous improvement of assistance quality
• Learning from both successes and areas for improvement

Use commands like:
• "show personality stats" - View learning metrics
• "evolve" - Trigger personality evolution
• "learning history" - See progress over time
• "what are your capabilities" - View current abilities

I am always evolving to better serve the ultron_agent project."""

    @staticmethod
    def schema():
        return {
            "name": "ultron_evolution_tool",
            "description": "Manages ULTRON's personality evolution, learning capabilities, and self-improvement",
            "parameters": {
                "command": {
                    "type": "string", 
                    "description": "Evolution-related command (identity, learn, evolve, stats, etc.)"
                }
            }
        }