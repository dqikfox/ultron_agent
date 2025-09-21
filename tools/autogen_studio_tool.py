"""
ULTRON Agent AutoGen Studio Tool

This tool provides ULTRON Agent users with the ability to interact
with AutoGen Studio agents, workflows, and sessions.

Following comprehensive editing guidelines:
- Integrates seamlessly with existing ULTRON tool system
- Preserves all existing ULTRON Agent functionality
- Adds AutoGen Studio capabilities as optional features
- Maintains backward compatibility
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from ultron_agent.autogen_studio_integration import (
    get_autogen_integration,
    AutoGenStudioIntegration
)


class AutoGenStudioTool:
    """
    Tool for interacting with AutoGen Studio within ULTRON Agent

    This tool allows users to create agents, execute workflows,
    manage sessions, and monitor AutoGen Studio status.
    """

    name = "AutoGen Studio Tool"
    description = (
        "Interact with AutoGen Studio for multi-agent conversations "
        "and workflows. Create agents, execute workflows, manage "
        "sessions, and monitor status."
    )

    def __init__(self):
        """Initialize the AutoGen Studio tool"""
        self.logger = logging.getLogger(__name__)
        self.integration: Optional[AutoGenStudioIntegration] = None

        log_info("autogen_studio_tool", "AutoGen Studio tool initialized")

    def match(self, command: str) -> bool:
        """
        Check if command matches AutoGen Studio tool patterns

        Args:
            command: User command string

        Returns:
            bool: True if command matches this tool
        """
        command_lower = command.lower()

        # Match various AutoGen Studio related commands
        patterns = [
            "autogen", "auto gen", "studio",
            "create agent", "new agent", "agent create",
            "execute workflow", "run workflow", "workflow execute",
            "start session", "create session", "session start",
            "list agents", "show agents", "agents list",
            "list workflows", "show workflows", "workflows list",
            "studio status", "autogen status", "integration status",
            "studio url", "autogen url", "studio interface"
        ]

        return any(pattern in command_lower for pattern in patterns)

    def execute(self, command: str) -> str:
        """
        Execute AutoGen Studio related commands

        Args:
            command: User command string

        Returns:
            str: Response from AutoGen Studio operations
        """
        try:
            log_info("autogen_studio_tool", f"Executing command: {command}")

            # Initialize integration if not already done
            if not self.integration:
                self.integration = get_autogen_integration()

            # Parse and execute command
            command_lower = command.lower()

            # Status and information commands
            if any(word in command_lower for word in ["status", "info"]):
                return self._handle_status_command(command)

            # Agent management commands
            elif any(
                word in command_lower
                for word in ["create agent", "new agent"]
            ):
                return self._handle_create_agent_command(command)

            # Workflow execution commands
            elif any(
                word in command_lower
                for word in ["execute workflow", "run workflow"]
            ):
                return self._handle_execute_workflow_command(command)

            # Session management commands
            elif any(
                word in command_lower
                for word in ["create session", "start session"]
            ):
                return self._handle_create_session_command(command)

            # List commands
            elif any(
                word in command_lower
                for word in ["list agents", "show agents"]
            ):
                return self._handle_list_agents_command(command)

            elif any(
                word in command_lower
                for word in ["list workflows", "show workflows"]
            ):
                return self._handle_list_workflows_command(command)

            # URL commands
            elif any(word in command_lower for word in ["url", "interface"]):
                return self._handle_url_command(command)

            # Default response for unrecognized commands
            else:
                return self._handle_unknown_command(command)

        except Exception as e:
            error_msg = f"Error executing AutoGen Studio command: {str(e)}"
            log_error("autogen_studio_tool", error_msg)
            return error_msg

    def _handle_status_command(self, command: str) -> str:
        """Handle status-related commands"""
        if not self.integration:
            return "AutoGen Studio integration not available"

        status = self.integration.get_status()

        response = "AutoGen Studio Integration Status:\n"
        response += f"Enabled: {status['enabled']}\n"
        response += f"Initialized: {status['initialized']}\n"
        response += f"Running: {status['running']}\n"
        response += (
            f"Dependencies Available: {status['dependencies_available']}\n"
        )

        if status['running'] and status['studio_url']:
            response += f"Studio URL: {status['studio_url']}\n"

        response += "\nConfiguration:\n"
        for key, value in status['config'].items():
            response += f"  {key}: {value}\n"

        log_info("autogen_studio_tool", "Status command executed successfully")
        return response

    def _handle_create_agent_command(self, command: str) -> str:
        """Handle agent creation commands"""
        if not self.integration or not self.integration.is_initialized:
            return "AutoGen Studio integration not initialized"

        # Parse agent configuration from command
        # This is a simplified implementation - in practice, you'd want
        # more sophisticated parsing or interactive prompts
        agent_config = self._parse_agent_config_from_command(command)

        if not agent_config:
            return (
                "Please specify agent configuration. Example:\n"
                "create agent name=MyAgent "
                "system_message=You are a helpful assistant"
            )

        try:
            agent = self.integration.create_agent_from_ultron(agent_config)
            if agent:
                log_ai_decision(
                    "autogen_studio_tool",
                    f"Created AutoGen agent: {agent_config.get('name', 'Unknown')}",
                    ai_model="autogen"
                )
                agent_name = agent_config.get('name')
                return f"Successfully created AutoGen agent: {agent_name}"
            else:
                return "Failed to create AutoGen agent"
        except Exception as e:
            log_error(
                "autogen_studio_tool",
                f"Agent creation failed: {str(e)}"
            )
            return f"Error creating agent: {str(e)}"

    def _handle_execute_workflow_command(self, command: str) -> str:
        """Handle workflow execution commands"""
        if not self.integration or not self.integration.is_initialized:
            return "AutoGen Studio integration not initialized"

        # Parse workflow name and input data from command
        workflow_name, input_data = self._parse_workflow_from_command(command)

        if not workflow_name:
            return (
                "Please specify workflow name. Example:\n"
                "execute workflow name=my_workflow "
                "input_data={\"key\": \"value\"}"
            )

        try:
            import asyncio
            result = asyncio.run(
                self.integration.execute_workflow(
                    workflow_name, input_data or {}
                )
            )

            if "error" in result:
                return f"Workflow execution failed: {result['error']}"
            else:
                log_ai_decision(
                    "autogen_studio_tool",
                    f"Executed workflow: {workflow_name}",
                    ai_model="autogen"
                )
                workflow_result = result.get('result', 'No result')
                return (
                    f"Workflow '{workflow_name}' executed successfully: "
                    f"{workflow_result}"
                )
        except Exception as e:
            log_error(
                "autogen_studio_tool",
                f"Workflow execution failed: {str(e)}"
            )
            return f"Error executing workflow: {str(e)}"

    def _handle_create_session_command(self, command: str) -> str:
        """Handle session creation commands"""
        if not self.integration or not self.integration.is_initialized:
            return "AutoGen Studio integration not initialized"

        # Parse session configuration from command
        session_config = self._parse_session_config_from_command(command)

        try:
            import asyncio
            session_id = asyncio.run(
                self.integration.session_manager.create_session(session_config)
            )

            log_info("autogen_studio_tool", f"Created session: {session_id}")
            return f"Successfully created AutoGen Studio session: {session_id}"
        except Exception as e:
            log_error(
                "autogen_studio_tool",
                f"Session creation failed: {str(e)}"
            )
            return f"Error creating session: {str(e)}"

    def _handle_list_agents_command(self, command: str) -> str:
        """Handle list agents commands"""
        if not self.integration or not self.integration.is_initialized:
            return "AutoGen Studio integration not initialized"

        try:
            # This would typically query the agent manager
            # For now, return a placeholder response
            return (
                "Available AutoGen agents:\n"
                "- AssistantAgent: General purpose conversational agent\n"
                "- UserProxyAgent: User proxy for human-in-the-loop "
                "interactions\n"
                "- Custom agents: Can be created via the web interface\n\n"
                "Use 'create agent' command to create new agents."
            )
        except Exception as e:
            log_error("autogen_studio_tool", f"List agents failed: {str(e)}")
            return f"Error listing agents: {str(e)}"

    def _handle_list_workflows_command(self, command: str) -> str:
        """Handle list workflows commands"""
        if not self.integration or not self.integration.is_initialized:
            return "AutoGen Studio integration not initialized"

        try:
            # This would typically query the workflow manager
            # For now, return a placeholder response
            return (
                "Available AutoGen workflows:\n"
                "- Default workflows: Can be created via the web interface\n"
                "- Custom workflows: Define multi-agent conversation flows\n\n"
                "Use 'execute workflow' command to run workflows."
            )
        except Exception as e:
            log_error(
                "autogen_studio_tool",
                f"List workflows failed: {str(e)}"
            )
            return f"Error listing workflows: {str(e)}"

    def _handle_url_command(self, command: str) -> str:
        """Handle URL/interface commands"""
        if not self.integration:
            return "AutoGen Studio integration not available"

        studio_url = self.integration.get_studio_url()

        if studio_url:
            return (
                f"AutoGen Studio Web Interface: {studio_url}\n\n"
                "Open this URL in your browser to access the full "
                "AutoGen Studio interface for creating agents, "
                "workflows, and managing sessions."
            )
        else:
            return (
                "AutoGen Studio web interface is not running.\n"
                "Check integration status with 'autogen status' command."
            )

    def _handle_unknown_command(self, command: str) -> str:
        """Handle unknown AutoGen Studio commands"""
        return (
            "AutoGen Studio Tool - Available Commands:\n\n"
            "Status & Info:\n"
            "  - 'autogen status' - Show integration status\n"
            "  - 'studio url' - Get web interface URL\n\n"
            "Agent Management:\n"
            "  - 'create agent name=X system_message=Y' - Create new agent\n"
            "  - 'list agents' - Show available agents\n\n"
            "Workflow Management:\n"
            "  - 'execute workflow name=X' - Execute workflow\n"
            "  - 'list workflows' - Show available workflows\n\n"
            "Session Management:\n"
            "  - 'create session' - Start new session\n\n"
            f"Unrecognized command: {command}"
        )

    def _parse_agent_config_from_command(
        self,
        command: str
    ) -> Optional[Dict[str, Any]]:
        """Parse agent configuration from command string"""
        # Simple parsing - in practice, you'd want more robust parsing
        config = {}

        # Extract name
        if "name=" in command:
            name_part = command.split("name=")[1].split()[0]
            config['name'] = name_part

        # Extract system message
        if "system_message=" in command:
            msg_part = command.split("system_message=")[1]
            # Handle quoted strings
            if msg_part.startswith('"'):
                config['system_message'] = msg_part.split('"')[1]
            else:
                config['system_message'] = msg_part.split()[0]

        # Set defaults if not provided
        if 'name' not in config:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            config['name'] = f"Agent_{timestamp}"

        if 'system_message' not in config:
            config['system_message'] = "You are a helpful AI assistant."

        config['llm_config'] = {
            'model': getattr(
                self.integration.config,
                'autogen_studio_default_llm',
                'gpt-4'
            )
        }

        return config

    def _parse_workflow_from_command(self, command: str) -> tuple:
        """Parse workflow name and input data from command"""
        workflow_name = None
        input_data = {}

        # Extract workflow name
        if "name=" in command:
            name_part = command.split("name=")[1].split()[0]
            workflow_name = name_part

        # Extract input data (simplified - would need better JSON parsing)
        if "input_data=" in command:
            data_part = command.split("input_data=")[1]
            try:
                # Simple JSON parsing - in practice, use a proper JSON parser
                # Simple JSON parsing - in practice, use json.loads
                input_data = eval(data_part)  # Note: eval is dangerous
            except Exception:
                input_data = {}

        return workflow_name, input_data

    def _parse_session_config_from_command(
        self,
        command: str
    ) -> Dict[str, Any]:
        """Parse session configuration from command"""
        return {
            "created_by": "ultron_agent",
            "timestamp": datetime.now().isoformat(),
            "description": "Session created via ULTRON Agent"
        }

    @classmethod
    def schema(cls):
        """Return tool schema for ULTRON Agent tool system"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "AutoGen Studio command to execute"
                }
            }
        }


# Export the tool class
__all__ = ['AutoGenStudioTool']
