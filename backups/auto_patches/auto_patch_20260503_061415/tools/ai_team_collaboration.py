#!/usr/bin/env python3
"""
AI Team Collaboration - Multiple personas working together on complex problems
"""

from tools.base import Tool
from tools.ai_agent_personas import AIAgentPersonas
from utils.ultron_logger import log_info, log_error, log_ai_decision
import json

class AITeamCollaboration(Tool):
    name = "ai_team_collaboration"
    description = "Multiple AI personas collaborating on complex problems"
    
    def __init__(self):
        self.personas = AIAgentPersonas()
        self.collaboration_templates = {
            "full_stack_development": {
                "name": "Full Stack Development Team",
                "personas": ["architect", "security", "optimizer", "debugger"],
                "description": "Complete application development with architecture, security, performance, and debugging",
                "workflow": [
                    ("architect", "System design and architecture planning"),
                    ("security", "Security requirements and threat modeling"),
                    ("optimizer", "Performance considerations and optimization strategy"),
                    ("debugger", "Testing strategy and error handling approach")
                ]
            },
            "problem_solving": {
                "name": "Problem Solving Task Force",
                "personas": ["analyst", "innovator", "debugger", "teacher"],
                "description": "Comprehensive problem analysis and solution development",
                "workflow": [
                    ("analyst", "Problem analysis and data gathering"),
                    ("innovator", "Creative solution brainstorming"),
                    ("debugger", "Solution validation and risk assessment"),
                    ("teacher", "Implementation guidance and knowledge transfer")
                ]
            },
            "system_optimization": {
                "name": "System Optimization Squad",
                "personas": ["analyst", "optimizer", "architect", "automator"],
                "description": "Complete system performance analysis and optimization",
                "workflow": [
                    ("analyst", "Performance metrics analysis and bottleneck identification"),
                    ("optimizer", "Optimization strategies and implementation"),
                    ("architect", "Architectural improvements and scalability"),
                    ("automator", "Automation opportunities and workflow optimization")
                ]
            },
            "security_audit": {
                "name": "Security Audit Team",
                "personas": ["security", "analyst", "debugger", "architect"],
                "description": "Comprehensive security assessment and hardening",
                "workflow": [
                    ("security", "Threat modeling and vulnerability assessment"),
                    ("analyst", "Security metrics and compliance analysis"),
                    ("debugger", "Penetration testing and vulnerability validation"),
                    ("architect", "Secure architecture recommendations")
                ]
            },
            "learning_project": {
                "name": "Learning & Development Team",
                "personas": ["teacher", "innovator", "analyst", "automator"],
                "description": "Educational content creation and skill development",
                "workflow": [
                    ("teacher", "Learning objectives and curriculum design"),
                    ("innovator", "Creative teaching methods and engagement strategies"),
                    ("analyst", "Learning progress tracking and assessment"),
                    ("automator", "Automated learning tools and workflow setup")
                ]
            }
        }
    
    def match(self, command: str) -> bool:
        keywords = ["team", "collaborate", "multiple", "together", "group", "squad", "task force"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, **kwargs):
        try:
            command = kwargs.get('command', '').lower()
            
            # Show available teams
            if any(word in command for word in ['list', 'show', 'teams', 'available']):
                return self._list_collaboration_teams()
            
            # Execute specific team collaboration
            for team_key, team_data in self.collaboration_templates.items():
                if team_key.replace('_', ' ') in command or any(word in command for word in team_key.split('_')):
                    return self._execute_team_collaboration(team_key, kwargs.get('problem', command))
            
            # Custom team collaboration
            if 'custom' in command or 'specific' in command:
                return self._custom_team_collaboration(command, kwargs)
            
            return self._list_collaboration_teams()
            
        except Exception as e:
            log_error("ai_team_collaboration", f"Collaboration failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _list_collaboration_teams(self) -> str:
        """List all available collaboration teams"""
        result = "👥 **AI Team Collaboration**\n\n"
        result += "Available specialized teams for complex problem solving:\n\n"
        
        for team_key, team_data in self.collaboration_templates.items():
            result += f"🎯 **{team_data['name']}**\n"
            result += f"   Description: {team_data['description']}\n"
            result += f"   Team: "
            
            team_members = []
            for persona_key in team_data['personas']:
                persona = self.personas.agents[persona_key]
                team_members.append(f"{persona['emoji']} {persona['name']}")
            result += " + ".join(team_members) + "\n\n"
        
        result += "**Usage Examples:**\n"
        result += "• 'team full stack development for e-commerce platform'\n"
        result += "• 'problem solving team for authentication issues'\n"
        result += "• 'security audit team for API endpoints'\n"
        result += "• 'system optimization squad for database performance'\n\n"
        
        result += "**Custom Teams:**\n"
        result += "• 'custom team with architect, security, optimizer for [problem]'\n"
        
        log_info("ai_team_collaboration", "Listed all collaboration teams")
        return result
    
    def _execute_team_collaboration(self, team_key: str, problem: str) -> str:
        """Execute a team collaboration on a specific problem"""
        if team_key not in self.collaboration_templates:
            return f"Team '{team_key}' not found"
        
        team = self.collaboration_templates[team_key]
        
        result = f"👥 **{team['name']} Collaboration**\n\n"
        result += f"**Problem:** {problem}\n\n"
        result += f"**Team Approach:** {team['description']}\n\n"
        
        # Execute each persona's contribution in workflow order
        for i, (persona_key, task_description) in enumerate(team['workflow'], 1):
            persona = self.personas.agents[persona_key]
            
            result += f"## {i}. {persona['emoji']} {persona['name']} - {task_description}\n\n"
            
            # Get persona-specific analysis
            persona_response = self._get_persona_contribution(persona_key, problem, task_description)
            result += persona_response + "\n\n"
        
        # Add collaboration summary
        result += self._generate_collaboration_summary(team_key, problem)
        
        log_ai_decision("ai_team_collaboration", f"Executed {team_key} collaboration for: {problem[:50]}...", ai_model="team_collaboration")
        return result
    
    def _get_persona_contribution(self, persona_key: str, problem: str, task: str) -> str:
        """Get a specific persona's contribution to the team effort"""
        persona = self.personas.agents[persona_key]
        
        # Create focused consultation
        focused_question = f"{task} for: {problem}"
        consult_command = f"ask {persona_key} about {focused_question}"
        
        # Get the persona's guidance (simplified version)
        if persona_key == "architect":
            return self.personas._architect_guidance(focused_question)
        elif persona_key == "debugger":
            return self.personas._debugger_guidance(focused_question)
        elif persona_key == "optimizer":
            return self.personas._optimizer_guidance(focused_question)
        elif persona_key == "security":
            return self.personas._security_guidance(focused_question)
        elif persona_key == "teacher":
            return self.personas._teacher_guidance(focused_question)
        elif persona_key == "innovator":
            return self.personas._innovator_guidance(focused_question)
        elif persona_key == "analyst":
            return self.personas._analyst_guidance(focused_question)
        elif persona_key == "automator":
            return self.personas._automator_guidance(focused_question)
        
        return f"**{persona['prompt_prefix']}**\n\nFocusing on: {task}"
    
    def _generate_collaboration_summary(self, team_key: str, problem: str) -> str:
        """Generate a summary of the team collaboration"""
        team = self.collaboration_templates[team_key]
        
        result = "## 🎯 Team Collaboration Summary\n\n"
        result += f"**Problem Addressed:** {problem}\n\n"
        result += f"**Team Composition:** {len(team['personas'])} specialized AI personas\n\n"
        
        result += "**Integrated Approach:**\n"
        for i, (persona_key, task) in enumerate(team['workflow'], 1):
            persona = self.personas.agents[persona_key]
            result += f"{i}. {persona['emoji']} {task}\n"
        
        result += "\n**Next Steps:**\n"
        result += "1. Review each persona's recommendations\n"
        result += "2. Integrate insights into a comprehensive solution\n"
        result += "3. Prioritize actions based on impact and feasibility\n"
        result += "4. Implement solutions with appropriate testing and validation\n\n"
        
        result += "**Follow-up:** Consult individual personas for detailed implementation guidance."
        
        return result
    
    def _custom_team_collaboration(self, command: str, kwargs: dict) -> str:
        """Handle custom team collaboration requests"""
        result = "🛠️ **Custom Team Collaboration**\n\n"
        result += "To create a custom team, specify:\n\n"
        result += "**Format:** 'custom team with [persona1], [persona2], [persona3] for [problem]'\n\n"
        
        result += "**Available Personas:**\n"
        for persona_key, persona_data in self.personas.agents.items():
            result += f"• {persona_data['emoji']} {persona_key} - {persona_data['specialty']}\n"
        
        result += "\n**Example:**\n"
        result += "'custom team with architect, security, teacher for building a secure learning platform'\n"
        
        return result
    
    @staticmethod
    def schema():
        return {
            "name": "ai_team_collaboration",
            "description": "Multiple AI personas collaborating on complex problems with specialized team compositions",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Team collaboration request or problem description"
                },
                "problem": {
                    "type": "string",
                    "description": "Specific problem or project for team collaboration"
                }
            }
        }