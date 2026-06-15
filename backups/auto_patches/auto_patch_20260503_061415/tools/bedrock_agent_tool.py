#!/usr/bin/env python3
"""Bedrock Agent Tool for ULTRON Agent"""

from tools.tool_interface import ToolInterface
from bedrock_ultron_agent import UltronAgentManager
from utils.ultron_logger import log_info, log_error

class BedrockAgentTool(ToolInterface):
    """Bedrock Agent integration tool for ULTRON"""

    @property
    def name(self) -> str:
        return "Bedrock Agent Tool"

    @property
    def description(self) -> str:
        return "Deploy and manage ULTRON Bedrock Agent for autonomous operations"

    def match(self, command: str) -> bool:
        keywords = ["bedrock agent", "deploy agent", "ultron agent", "autonomous", "evolve", "maintain"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            manager = UltronAgentManager()
            
            if "deploy" in cmd_lower or "create" in cmd_lower:
                return self._deploy_agent(manager)
            elif "status" in cmd_lower:
                return self._get_status(manager)
            elif "interact" in cmd_lower or "ask" in cmd_lower:
                return self._interact_with_agent(manager, command)
            elif "autonomous" in cmd_lower:
                return self._start_autonomous(manager)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("bedrock_agent_tool", f"Error: {e}")
            return f"Bedrock Agent error: {e}"

    def _deploy_agent(self, manager):
        """Deploy ULTRON Bedrock Agent"""
        
        result = manager.deploy_ultron_agent()
        
        status = result.get("deployment_status", "unknown")
        
        if status == "success":
            agent_info = result.get("agent_info", {})
            capabilities = len(agent_info.get("capabilities", []))
            
            return f"🤖 ULTRON Bedrock Agent Deployed\n" + \
                   f"Agent ID: {agent_info.get('agent_id', 'N/A')}\n" + \
                   f"Alias ID: {agent_info.get('agent_alias_id', 'N/A')}\n" + \
                   f"Capabilities: {capabilities} autonomous functions\n" + \
                   f"Status: ✅ Operational and ready for autonomous operations"
        else:
            error = result.get("error", "Unknown deployment error")
            return f"❌ Deployment Failed: {error}"

    def _get_status(self, manager):
        """Get agent status"""
        
        status = manager.get_ultron_status()
        
        if "error" in status:
            return f"❌ Status Error: {status.get('message', 'Unknown error')}"
        
        agent_status = status.get("status", "unknown")
        agent_name = status.get("agent_name", "N/A")
        model = status.get("foundation_model", "N/A")
        
        return f"🤖 ULTRON Bedrock Agent Status\n" + \
               f"Name: {agent_name}\n" + \
               f"Status: {agent_status}\n" + \
               f"Model: {model}\n" + \
               f"Agent ID: {status.get('agent_id', 'N/A')}\n" + \
               f"Alias ID: {status.get('alias_id', 'N/A')}"

    def _interact_with_agent(self, manager, command):
        """Interact with ULTRON agent"""
        
        # Extract message from command
        message = command.replace("interact", "").replace("ask", "").strip()
        if not message:
            message = "Analyze current ULTRON project status and recommend improvements"
        
        result = manager.interact_with_ultron(message)
        
        if "error" in result:
            return f"❌ Interaction Error: {result['error']}"
        
        response = result.get("response", "No response")
        session_id = result.get("session_id", "N/A")
        
        return f"🤖 ULTRON Agent Response\n" + \
               f"Session: {session_id}\n" + \
               f"Response: {response[:300]}...\n" + \
               f"Status: ✅ Interaction completed"

    def _start_autonomous(self, manager):
        """Start autonomous operations"""
        
        result = manager.bedrock_agent.start_autonomous_operations()
        
        operations = result.get("operations_completed", 0)
        session_id = result.get("autonomous_session", "N/A")
        
        return f"🤖 Autonomous Operations Started\n" + \
               f"Session ID: {session_id}\n" + \
               f"Operations Initiated: {operations}\n" + \
               f"Status: ✅ ULTRON is now operating autonomously\n" + \
               f"Capabilities: Building, maintaining, and evolving project"

    def _show_help(self):
        """Show Bedrock Agent help"""
        
        return """🤖 ULTRON Bedrock Agent Commands:

🚀 Deployment:
• "deploy bedrock agent" - Deploy ULTRON Bedrock Agent
• "create ultron agent" - Create autonomous ULTRON agent

📊 Management:
• "bedrock agent status" - Check agent status
• "ultron agent status" - Get current agent information

💬 Interaction:
• "interact with ultron [message]" - Communicate with agent
• "ask ultron [question]" - Query the autonomous agent

🤖 Autonomous Operations:
• "start autonomous operations" - Begin autonomous mode
• "autonomous maintenance" - Start maintenance operations

🎯 Capabilities:
• Project health analysis and monitoring
• Autonomous code generation and improvement
• System architecture optimization
• Performance monitoring and enhancement
• Security vulnerability detection
• Feature development and integration
• Learning from interactions
• Evolutionary system adaptation

💡 Example Usage:
• "deploy bedrock agent"
• "ask ultron to analyze project performance"
• "start autonomous operations"
• "interact with ultron about system improvements"

🔧 Agent Features:
• Claude 3 Sonnet foundation model
• Custom action groups for project management
• Autonomous decision making authority
• Continuous learning and evolution
• Real-time system monitoring
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "bedrock_agent_tool",
            "description": "Deploy and manage ULTRON Bedrock Agent for autonomous operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Bedrock Agent command to execute"
                    }
                },
                "required": ["command"]
            }
        }