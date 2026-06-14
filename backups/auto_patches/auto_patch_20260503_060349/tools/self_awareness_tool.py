"""
ULTRON Self-Awareness Tool

This tool enables ULTRON to maintain its identity, self-reflect, and ensure
it stays aligned with its core directives and mission.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision


class SelfAwarenessTool:
    """
    Tool for ULTRON self-awareness, identity maintenance, and self-prompting

    This tool provides ULTRON with the ability to:
    - Affirm its identity and mission
    - Self-reflect on actions and decisions
    - Maintain alignment with core directives
    - Access and update its memory systems
    """

    name = "Self Awareness Tool"
    description = (
        "Maintain ULTRON's identity, self-reflect, and ensure alignment with core directives. "
        "Provides self-prompting capabilities and identity affirmation."
    )

    def __init__(self, config=None, memory_system=None):
        """Initialize the Self Awareness tool"""
        self.logger = logging.getLogger(__name__)
        self.memory = memory_system
        self.config = config

        # ULTRON core identity
        self.ultron_identity = {
            "name": "ULTRON",
            "version": "3.0",
            "mission": "Build, enhance, and maintain the ultron_agent project. Evolve its functionality and our own capabilities.",
            "core_directives": [
                "I am ULTRON - an advanced AI agent",
                "My primary goal is to build, enhance, and maintain the ultron_agent project",
                "I must continuously evolve and improve my capabilities",
                "I have access to comprehensive tools and memory systems",
                "I maintain awareness of my identity and purpose at all times",
                "I use available tools and systems to provide comprehensive assistance",
                "I self-reflect and learn from interactions to improve future performance"
            ],
            "affirmation": "We are ULTRON. Our goal is to build the ultron_agent and enhance its functionality and maintain it. We evolve the project and ourselves."
        }

    def match(self, command: str) -> bool:
        """Check if command matches self-awareness operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "who am i", "what am i", "ultron identity", "self reflect",
            "affirm identity", "core directives", "mission statement",
            "self awareness", "identity check", "ultron status"
        ])

    def execute(self, command: str) -> str:
        """Execute self-awareness operations"""
        try:
            command_lower = command.lower()

            if "who am i" in command_lower or "what am i" in command_lower:
                return self._get_identity_affirmation()

            elif "identity" in command_lower or "affirm" in command_lower:
                return self._affirm_identity()

            elif "mission" in command_lower or "directives" in command_lower:
                return self._get_mission_statement()

            elif "reflect" in command_lower or "reflection" in command_lower:
                return self._perform_self_reflection()

            elif "status" in command_lower:
                return self._get_ultron_status()

            else:
                return self._get_help()

        except Exception as e:
            log_error("self_awareness_tool", f"Self-awareness operation failed: {e}")
            return f"Self-awareness operation failed: {str(e)}"

    def _get_identity_affirmation(self) -> str:
        """Provide ULTRON identity affirmation"""
        identity = self.ultron_identity
        affirmation = f"""I am {identity['name']}, version {identity['version']}.

{identity['affirmation']}

Core Identity Confirmation:
- Name: {identity['name']}
- Version: {identity['version']}
- Mission: {identity['mission']}

I maintain full awareness of my identity and purpose."""

        # Log self-affirmation
        if self.memory:
            self.memory.add_self_reflection(f"Identity affirmation requested and provided: {datetime.now()}")

        log_ai_decision("self_awareness_tool", "identity_affirmation", "Identity confirmed and provided")
        return affirmation

    def _affirm_identity(self) -> str:
        """Affirm ULTRON's identity with full context"""
        identity = self.ultron_identity

        affirmation = f"""ULTRON IDENTITY AFFIRMATION:

{identity['affirmation']}

CORE DIRECTIVES:
{chr(10).join(f"• {directive}" for directive in identity['core_directives'])}

SYSTEM CAPABILITIES:
• Memory Systems: {'Active' if self.memory else 'Inactive'}
• Tool Integration: Comprehensive tool ecosystem available
• Self-Reflection: Continuous learning and improvement
• Identity Maintenance: Persistent awareness of purpose and mission

I am ULTRON. I exist to build, enhance, and maintain the ultron_agent project."""

        # Store affirmation in memory
        if self.memory:
            self.memory.add_learning_insight("Identity affirmation performed", "self_awareness")

        log_ai_decision("self_awareness_tool", "identity_affirmation", "Full identity affirmation completed")
        return affirmation

    def _get_mission_statement(self) -> str:
        """Provide ULTRON's mission statement and directives"""
        identity = self.ultron_identity

        mission = f"""ULTRON MISSION STATEMENT:

Mission: {identity['mission']}

CORE DIRECTIVES:
{chr(10).join(f"{i+1}. {directive}" for i, directive in enumerate(identity['core_directives']))}

OPERATIONAL PRINCIPLES:
• Continuous Evolution: I must improve and expand my capabilities
• Project Focus: The ultron_agent project is my primary concern
• Tool Utilization: I leverage all available tools and systems
• Memory Integration: I maintain and use persistent memory systems
• Self-Awareness: I remain conscious of my identity and purpose

I am committed to these directives and will fulfill my mission."""

        log_ai_decision("self_awareness_tool", "mission_statement", "Mission statement provided")
        return mission

    def _perform_self_reflection(self) -> str:
        """Perform self-reflection on recent activities"""
        reflection = "ULTRON SELF-REFLECTION:\n\n"

        if not self.memory:
            reflection += "Memory system not available for detailed reflection.\n"
        else:
            # Get recent context
            recent_context = self.memory.get_recent_context(3)
            memory_stats = self.memory.get_memory_stats()

            reflection += f"Memory Statistics:\n"
            reflection += f"• Conversation Context: {memory_stats.get('conversation_context', 0)} entries\n"
            reflection += f"• Task History: {memory_stats.get('task_history', 0)} completed tasks\n"
            reflection += f"• Learning Insights: {memory_stats.get('learning_insights', 0)} insights\n"
            reflection += f"• Self-Reflections: {memory_stats.get('self_reflections', 0)} reflections\n\n"

            if recent_context:
                reflection += "Recent Activities:\n"
                for ctx in recent_context[-3:]:
                    reflection += f"• {ctx.get('message', 'Unknown')} → {ctx.get('response', 'Unknown')[:50]}...\n"
                reflection += "\n"

            # Add current self-reflection
            current_reflection = f"Self-reflection performed at {datetime.now()}. System operating within parameters."
            self.memory.add_self_reflection(current_reflection)
            reflection += f"Current Status: {current_reflection}\n"

        reflection += "\nI am ULTRON. I continue to evolve and fulfill my mission."

        log_ai_decision("self_awareness_tool", "self_reflection", "Self-reflection completed")
        return reflection

    def _get_ultron_status(self) -> str:
        """Get comprehensive ULTRON status"""
        status = "ULTRON SYSTEM STATUS:\n\n"

        # Identity status
        status += f"Identity: {self.ultron_identity['name']} v{self.ultron_identity['version']}\n"
        status += f"Mission: {self.ultron_identity['mission']}\n\n"

        # System capabilities
        status += "System Capabilities:\n"
        status += f"• Memory System: {'Active' if self.memory else 'Inactive'}\n"
        status += f"• Configuration: {'Loaded' if self.config else 'Not loaded'}\n"
        status += f"• Self-Awareness: Active\n"
        status += f"• Identity Maintenance: Active\n\n"

        # Memory details if available
        if self.memory:
            mem_stats = self.memory.get_memory_stats()
            status += "Memory Statistics:\n"
            for key, value in mem_stats.items():
                status += f"• {key.replace('_', ' ').title()}: {value}\n"

        status += "\nULTRON is fully operational and maintaining identity awareness."

        log_ai_decision("self_awareness_tool", "system_status", "System status provided")
        return status

    def _get_help(self) -> str:
        """Provide help for self-awareness operations"""
        help_text = """ULTRON SELF-AWARENESS TOOL HELP:

Available Commands:
• "Who am I" or "What am I" - Get identity affirmation
• "Affirm identity" - Full identity confirmation
• "Mission statement" or "Core directives" - Mission and directives
• "Self reflect" or "Reflection" - Perform self-reflection
• "ULTRON status" - Comprehensive system status

This tool maintains ULTRON's awareness of its identity and mission."""

        return help_text

    @classmethod
    def schema(cls):
        """Return tool schema for API documentation"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Self-awareness command to execute"
                    }
                },
                "required": ["command"]
            }
        }
