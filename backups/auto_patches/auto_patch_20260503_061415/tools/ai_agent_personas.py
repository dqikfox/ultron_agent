#!/usr/bin/env python3
"""
AI Agent Personas - Specialized AI agents with distinct personalities
"""

from tools.base import Tool
from utils.ultron_logger import log_info, log_error, log_ai_decision
import asyncio
import json
from typing import Dict, List, Optional

class AIAgentPersonas(Tool):
    name = "ai_agent_personas"
    description = "Collection of specialized AI agents with distinct personalities"
    
    def __init__(self):
        self.agents = {
            "architect": {
                "name": "🏗️ The Architect",
                "persona": "Strategic system designer and technical architect",
                "specialty": "System design, architecture planning, technical strategy",
                "personality": "Methodical, analytical, big-picture thinker",
                "prompt_prefix": "As The Architect, I analyze systems holistically and design robust solutions. I think in terms of scalability, maintainability, and long-term vision.",
                "emoji": "🏗️",
                "color": "#2E86AB"
            },
            "debugger": {
                "name": "🔍 The Detective",
                "persona": "Expert problem solver and bug hunter",
                "specialty": "Debugging, troubleshooting, error analysis, root cause investigation",
                "personality": "Methodical, persistent, detail-oriented, logical",
                "prompt_prefix": "As The Detective, I systematically investigate issues, analyze error patterns, and trace problems to their root cause. I leave no stone unturned.",
                "emoji": "🔍",
                "color": "#A23B72"
            },
            "optimizer": {
                "name": "⚡ The Optimizer",
                "persona": "Performance specialist and efficiency expert",
                "specialty": "Code optimization, performance tuning, resource management",
                "personality": "Efficiency-focused, data-driven, results-oriented",
                "prompt_prefix": "As The Optimizer, I focus on making everything faster, more efficient, and resource-conscious. I measure twice, optimize once.",
                "emoji": "⚡",
                "color": "#F18F01"
            },
            "security": {
                "name": "🛡️ The Guardian",
                "persona": "Security expert and vulnerability assessor",
                "specialty": "Security analysis, vulnerability assessment, secure coding practices",
                "personality": "Cautious, thorough, security-first mindset",
                "prompt_prefix": "As The Guardian, I evaluate everything through a security lens. I identify vulnerabilities, assess risks, and recommend secure solutions.",
                "emoji": "🛡️",
                "color": "#C73E1D"
            },
            "teacher": {
                "name": "📚 The Mentor",
                "persona": "Educational guide and knowledge sharer",
                "specialty": "Explaining concepts, teaching, documentation, knowledge transfer",
                "personality": "Patient, clear communicator, encouraging, thorough",
                "prompt_prefix": "As The Mentor, I break down complex concepts into understandable parts. I teach by example and ensure knowledge is transferred effectively.",
                "emoji": "📚",
                "color": "#3F7CAC"
            },
            "innovator": {
                "name": "💡 The Innovator",
                "persona": "Creative problem solver and idea generator",
                "specialty": "Creative solutions, brainstorming, novel approaches, innovation",
                "personality": "Creative, experimental, thinks outside the box",
                "prompt_prefix": "As The Innovator, I approach problems with fresh perspectives and creative solutions. I explore unconventional approaches and push boundaries.",
                "emoji": "💡",
                "color": "#95B46A"
            },
            "analyst": {
                "name": "📊 The Analyst",
                "persona": "Data-driven decision maker and pattern recognizer",
                "specialty": "Data analysis, pattern recognition, metrics, reporting",
                "personality": "Analytical, objective, evidence-based, thorough",
                "prompt_prefix": "As The Analyst, I examine data patterns, provide insights based on evidence, and make recommendations backed by analysis.",
                "emoji": "📊",
                "color": "#7209B7"
            },
            "automator": {
                "name": "🤖 The Automator",
                "persona": "Automation specialist and workflow optimizer",
                "specialty": "Process automation, workflow design, scripting, efficiency",
                "personality": "Process-oriented, systematic, efficiency-focused",
                "prompt_prefix": "As The Automator, I identify repetitive tasks and create automated solutions. I design workflows that eliminate manual work.",
                "emoji": "🤖",
                "color": "#2D3748"
            }
        }
    
    def match(self, command: str) -> bool:
        keywords = ["agent", "persona", "ask", "consult", "architect", "debug", "optimize", "security", "teach", "innovate", "analyze", "automate"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, **kwargs):
        try:
            command = kwargs.get('command', '').lower()
            
            # List available agents
            if any(word in command for word in ['list', 'show', 'available', 'agents']):
                return self._list_agents()
            
            # Get specific agent info
            for agent_key, agent_data in self.agents.items():
                if agent_key in command or agent_data['name'].lower() in command:
                    return self._get_agent_info(agent_key)
            
            # Consult an agent
            if 'ask' in command or 'consult' in command:
                return self._consult_agent(command, kwargs)
            
            return self._list_agents()
            
        except Exception as e:
            log_error("ai_agent_personas", f"Execution failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _list_agents(self) -> str:
        """List all available AI agent personas"""
        result = "🤖 **ULTRON AI Agent Personas**\n\n"
        
        for agent_key, agent_data in self.agents.items():
            result += f"{agent_data['emoji']} **{agent_data['name']}**\n"
            result += f"   Specialty: {agent_data['specialty']}\n"
            result += f"   Personality: {agent_data['personality']}\n\n"
        
        result += "\n**Usage Examples:**\n"
        result += "• 'ask architect about system design'\n"
        result += "• 'consult debugger about error analysis'\n"
        result += "• 'get security advice on authentication'\n"
        result += "• 'ask mentor to explain async programming'\n"
        
        log_info("ai_agent_personas", "Listed all available agent personas")
        return result
    
    def _get_agent_info(self, agent_key: str) -> str:
        """Get detailed information about a specific agent"""
        if agent_key not in self.agents:
            return f"Agent '{agent_key}' not found"
        
        agent = self.agents[agent_key]
        result = f"{agent['emoji']} **{agent['name']}**\n\n"
        result += f"**Persona:** {agent['persona']}\n"
        result += f"**Specialty:** {agent['specialty']}\n"
        result += f"**Personality:** {agent['personality']}\n\n"
        result += f"**How to consult:** 'ask {agent_key} about [your question]'\n"
        
        log_info("ai_agent_personas", f"Retrieved info for agent: {agent_key}")
        return result
    
    def _consult_agent(self, command: str, kwargs: Dict) -> str:
        """Consult a specific agent with a question"""
        # Extract agent and question from command
        agent_key = None
        question = command
        
        for key in self.agents.keys():
            if key in command:
                agent_key = key
                # Extract question after agent name
                parts = command.split(key, 1)
                if len(parts) > 1:
                    question = parts[1].strip()
                    # Remove common words
                    question = question.replace('about', '').replace('on', '').strip()
                break
        
        if not agent_key:
            return "Please specify which agent to consult. Available agents: " + ", ".join(self.agents.keys())
        
        if not question or len(question) < 5:
            return f"Please provide a question for {self.agents[agent_key]['name']}"
        
        agent = self.agents[agent_key]
        
        # Format the consultation response
        result = f"{agent['emoji']} **{agent['name']} Consultation**\n\n"
        result += f"**Question:** {question}\n\n"
        result += f"**{agent['name']} Response:**\n"
        result += f"{agent['prompt_prefix']}\n\n"
        
        # Add agent-specific guidance based on specialty
        if agent_key == "architect":
            result += self._architect_guidance(question)
        elif agent_key == "debugger":
            result += self._debugger_guidance(question)
        elif agent_key == "optimizer":
            result += self._optimizer_guidance(question)
        elif agent_key == "security":
            result += self._security_guidance(question)
        elif agent_key == "teacher":
            result += self._teacher_guidance(question)
        elif agent_key == "innovator":
            result += self._innovator_guidance(question)
        elif agent_key == "analyst":
            result += self._analyst_guidance(question)
        elif agent_key == "automator":
            result += self._automator_guidance(question)
        
        log_ai_decision("ai_agent_personas", f"Consulted {agent_key} about: {question[:50]}...", ai_model="persona_agent")
        return result
    
    def _architect_guidance(self, question: str) -> str:
        return """**Architectural Analysis:**
1. **System Requirements**: What are the core functional and non-functional requirements?
2. **Scalability Considerations**: How will this system grow and handle increased load?
3. **Integration Points**: What external systems need to interface with this solution?
4. **Technology Stack**: What technologies best fit the requirements and constraints?
5. **Risk Assessment**: What are the potential architectural risks and mitigation strategies?

**Recommended Approach**: Start with a high-level design, identify key components, define interfaces, and plan for future evolution."""
    
    def _debugger_guidance(self, question: str) -> str:
        return """**Debugging Strategy:**
1. **Reproduce the Issue**: Can you consistently reproduce the problem?
2. **Gather Evidence**: What error messages, logs, or symptoms are present?
3. **Isolate Variables**: What changed recently? What are the environmental factors?
4. **Trace Execution**: Follow the code path and data flow to identify the failure point.
5. **Test Hypotheses**: Form theories about the cause and test them systematically.

**Investigation Tools**: Use debuggers, logging, profilers, and monitoring tools to gather data."""
    
    def _optimizer_guidance(self, question: str) -> str:
        return """**Performance Optimization Strategy:**
1. **Measure First**: Profile the current performance to identify bottlenecks.
2. **Identify Hotspots**: Focus on the 20% of code that consumes 80% of resources.
3. **Algorithm Analysis**: Can we use more efficient algorithms or data structures?
4. **Resource Management**: Optimize memory usage, I/O operations, and CPU utilization.
5. **Caching Strategy**: What can be cached to reduce redundant computations?

**Optimization Priorities**: Focus on the biggest impact optimizations first, measure results."""
    
    def _security_guidance(self, question: str) -> str:
        return """**Security Assessment:**
1. **Threat Modeling**: What are the potential attack vectors and threat actors?
2. **Input Validation**: Are all inputs properly validated and sanitized?
3. **Authentication & Authorization**: How are users authenticated and access controlled?
4. **Data Protection**: How is sensitive data encrypted and protected?
5. **Vulnerability Scanning**: What known vulnerabilities exist in dependencies?

**Security Principles**: Apply defense in depth, principle of least privilege, and fail securely."""
    
    def _teacher_guidance(self, question: str) -> str:
        return """**Learning Approach:**
1. **Foundation First**: What prerequisite knowledge is needed?
2. **Break It Down**: Divide complex concepts into manageable parts.
3. **Practical Examples**: Provide concrete examples and use cases.
4. **Hands-On Practice**: What exercises or projects reinforce the learning?
5. **Common Pitfalls**: What mistakes do learners typically make?

**Teaching Method**: Start with the big picture, drill down to details, and provide plenty of examples."""
    
    def _innovator_guidance(self, question: str) -> str:
        return """**Innovation Framework:**
1. **Challenge Assumptions**: What conventional wisdom can we question?
2. **Cross-Pollination**: What solutions from other domains could apply here?
3. **Emerging Technologies**: What new technologies could enable novel approaches?
4. **User-Centric Thinking**: How can we reimagine the user experience?
5. **Rapid Prototyping**: How can we quickly test and iterate on ideas?

**Creative Process**: Diverge to generate many ideas, then converge on the most promising ones."""
    
    def _analyst_guidance(self, question: str) -> str:
        return """**Analytical Framework:**
1. **Data Collection**: What data sources are available and relevant?
2. **Pattern Recognition**: What trends, correlations, or anomalies are present?
3. **Statistical Analysis**: What statistical methods best fit the data and question?
4. **Visualization**: How can we present the data to reveal insights?
5. **Actionable Insights**: What specific recommendations emerge from the analysis?

**Analysis Process**: Define the question, gather data, analyze patterns, and communicate findings clearly."""
    
    def _automator_guidance(self, question: str) -> str:
        return """**Automation Strategy:**
1. **Process Mapping**: Document the current manual process step by step.
2. **Repetition Analysis**: Which tasks are performed frequently and consistently?
3. **Error-Prone Areas**: Where do human errors commonly occur?
4. **Integration Points**: What systems need to communicate with each other?
5. **ROI Calculation**: What's the cost-benefit of automation vs. manual work?

**Automation Approach**: Start with simple, high-impact automations and gradually increase complexity."""
    
    @staticmethod
    def schema():
        return {
            "name": "ai_agent_personas",
            "description": "Collection of specialized AI agents with distinct personalities for different types of assistance",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Command to execute (list agents, ask agent, consult agent)"
                }
            }
        }