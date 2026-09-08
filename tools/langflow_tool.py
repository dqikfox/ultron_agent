"""
ULTRON Agent Langflow Integration Tool

This tool provides ULTRON Agent users with the ability to interact
with Langflow workflows and manage flow execution.

Following comprehensive editing guidelines:
- Integrates seamlessly with existing ULTRON tool system
- Preserves all existing ULTRON Agent functionality
- Adds Langflow capabilities as optional features
- Maintains backward compatibility
"""

import logging
import requests
import json
from typing import Dict, Any, Optional, List

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from ultron_agent.config import UltronConfig


class LangflowTool:
    """
    Tool for interacting with Langflow within ULTRON Agent

    This tool allows users to execute Langflow workflows, manage
    flow configurations, and monitor execution status.
    """

    name = "Langflow Tool"
    description = (
        "Interact with Langflow for workflow execution and management. "
        "Execute flows, manage configurations, and monitor status."
    )

    def __init__(self, config: Optional[UltronConfig] = None):
        """Initialize the Langflow tool"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.base_url = None
        self.session = requests.Session()
        self.session.timeout = 30  # 30 second timeout

        # Initialize from config if available
        if self.config:
            self.base_url = getattr(
                self.config, 'langflow_api_url', 'http://127.0.0.1:7861'
            )
        else:
            self.base_url = 'http://127.0.0.1:7861'

        log_info(
            "langflow_tool",
            f"Langflow tool initialized with URL: {self.base_url}"
        )

    def match(self, command: str) -> bool:
        """
        Check if command matches Langflow tool patterns

        Args:
            command: User command string

        Returns:
            bool: True if command matches this tool
        """
        command_lower = command.lower()

        # Match various Langflow related commands
        patterns = [
            "langflow", "flow", "workflow",
            "execute flow", "run flow", "flow execute",
            "list flows", "show flows", "flows list",
            "flow status", "langflow status", "flow info",
            "create flow", "new flow", "flow create",
            "delete flow", "remove flow", "flow delete"
        ]

        return any(pattern in command_lower for pattern in patterns)

    def execute(self, command: str) -> str:
        """
        Execute Langflow related commands

        Args:
            command: User command string

        Returns:
            str: Response from Langflow operations
        """
        try:
            log_info("langflow_tool", f"Executing command: {command}")

            # Parse and execute command
            command_lower = command.lower()

            # Status and information commands
            if any(word in command_lower for word in ["status", "info"]):
                return self._handle_status_command(command)

            # Flow execution commands
            elif any(
                word in command_lower
                for word in ["execute flow", "run flow"]
            ):
                return self._handle_execute_flow_command(command)

            # Flow management commands
            elif any(
                word in command_lower
                for word in ["list flows", "show flows"]
            ):
                return self._handle_list_flows_command(command)

            elif any(
                word in command_lower
                for word in ["create flow", "new flow"]
            ):
                return self._handle_create_flow_command(command)

            elif any(
                word in command_lower
                for word in ["delete flow", "remove flow"]
            ):
                return self._handle_delete_flow_command(command)

            # Default response for unrecognized commands
            else:
                return self._handle_unknown_command(command)

        except Exception as e:
            error_msg = f"Error executing Langflow command: {str(e)}"
            log_error("langflow_tool", error_msg)
            return error_msg

    def _handle_status_command(self, command: str) -> str:
        """Handle status-related commands"""
        try:
            # Test connection to Langflow
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                status_info = {
                    "status": "running",
                    "url": self.base_url,
                    "response_time": f"{response.elapsed.total_seconds():.2f}s"
                }
            else:
                status_info = {
                    "status": "error",
                    "url": self.base_url,
                    "error": f"HTTP {response.status_code}"
                }

        except requests.exceptions.RequestException as e:
            status_info = {
                "status": "unreachable",
                "url": self.base_url,
                "error": str(e)
            }

        response = "Langflow Integration Status:\n"
        response += f"Status: {status_info['status']}\n"
        response += f"URL: {status_info['url']}\n"

        if 'response_time' in status_info:
            response += f"Response Time: {status_info['response_time']}\n"

        if 'error' in status_info:
            response += f"Error: {status_info['error']}\n"

        log_info(
            "langflow_tool",
            f"Status check completed: {status_info['status']}"
        )
        return response

    def _handle_execute_flow_command(self, command: str) -> str:
        """Handle flow execution commands"""
        # Parse flow name and input data from command
        flow_id, input_data = self._parse_flow_execution_from_command(command)

        if not flow_id:
            return (
                "Please specify flow ID. Example:\n"
                "execute flow id=my_flow_id "
                "input_data={\"key\": \"value\"}"
            )

        try:
            # Execute the flow
            result = self._execute_langflow_flow(flow_id, input_data)

            if "error" in result:
                return f"Flow execution failed: {result['error']}"
            else:
                log_ai_decision(
                    "langflow_tool",
                    f"Executed Langflow: {flow_id}",
                    ai_model="langflow"
                )
                flow_result = result.get('result', 'No result')
                return (
                    f"Flow '{flow_id}' executed successfully: "
                    f"{flow_result}"
                )
        except Exception as e:
            log_error(
                "langflow_tool",
                f"Flow execution failed: {str(e)}"
            )
            return f"Error executing flow: {str(e)}"

    def _handle_list_flows_command(self, command: str) -> str:
        """Handle list flows commands"""
        try:
            flows = self._get_langflow_flows()

            if not flows:
                return "No flows found or unable to connect to Langflow."

            response = "Available Langflow Flows:\n\n"
            for flow in flows:
                response += f"ID: {flow.get('id', 'N/A')}\n"
                response += f"Name: {flow.get('name', 'N/A')}\n"
                response += f"Description: {flow.get('description', 'N/A')}\n"
                response += f"Status: {flow.get('status', 'N/A')}\n"
                response += "---\n"

            return response

        except Exception as e:
            log_error("langflow_tool", f"List flows failed: {str(e)}")
            return f"Error listing flows: {str(e)}"

    def _handle_create_flow_command(self, command: str) -> str:
        """Handle flow creation commands"""
        # Parse flow configuration from command
        flow_config = self._parse_flow_config_from_command(command)

        if not flow_config:
            return (
                "Please specify flow configuration. Example:\n"
                "create flow name=MyFlow "
                "description=A sample flow"
            )

        try:
            result = self._create_langflow_flow(flow_config)

            if "error" in result:
                return f"Flow creation failed: {result['error']}"
            else:
                flow_id = result.get('id')
                log_ai_decision(
                    "langflow_tool",
                    f"Created Langflow: {flow_config.get('name', 'Unknown')}",
                    ai_model="langflow"
                )
                return f"Successfully created flow: {flow_id}"
        except Exception as e:
            log_error(
                "langflow_tool",
                f"Flow creation failed: {str(e)}"
            )
            return f"Error creating flow: {str(e)}"

    def _handle_delete_flow_command(self, command: str) -> str:
        """Handle flow deletion commands"""
        flow_id = self._parse_flow_id_from_command(command)

        if not flow_id:
            return "Please specify flow ID. Example: delete flow id=my_flow_id"

        try:
            result = self._delete_langflow_flow(flow_id)

            if "error" in result:
                return f"Flow deletion failed: {result['error']}"
            else:
                log_ai_decision(
                    "langflow_tool",
                    f"Deleted Langflow: {flow_id}",
                    ai_model="langflow"
                )
                return f"Successfully deleted flow: {flow_id}"
        except Exception as e:
            log_error(
                "langflow_tool",
                f"Flow deletion failed: {str(e)}"
            )
            return f"Error deleting flow: {str(e)}"

    def _handle_unknown_command(self, command: str) -> str:
        """Handle unknown Langflow commands"""
        return (
            "Langflow Tool - Available Commands:\n\n"
            "Status & Info:\n"
            "  - 'langflow status' - Show integration status\n\n"
            "Flow Management:\n"
            "  - 'execute flow id=X' - Execute flow by ID\n"
            "  - 'list flows' - Show available flows\n"
            "  - 'create flow name=X description=Y' - Create new flow\n"
            "  - 'delete flow id=X' - Delete flow by ID\n\n"
            f"Unrecognized command: {command}"
        )

    def _execute_langflow_flow(
        self, flow_id: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a Langflow workflow"""
        try:
            url = f"{self.base_url}/api/v1/flow/{flow_id}/execute"

            payload = {
                "input_data": input_data,
                "tweaks": {}
            }

            response = self.session.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                return {"result": response.json()}
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def _get_langflow_flows(self) -> List[Dict[str, Any]]:
        """Get list of available flows"""
        try:
            url = f"{self.base_url}/api/v1/flows"
            response = self.session.get(url)

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(
                    f"Failed to get flows: HTTP {response.status_code}"
                )
                return []

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get flows: {str(e)}")
            return []

    def _create_langflow_flow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Langflow workflow"""
        try:
            url = f"{self.base_url}/api/v1/flows"

            payload = {
                "name": config.get("name", "New Flow"),
                "description": config.get("description", ""),
                "data": config.get("data", {})
            }

            response = self.session.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def _delete_langflow_flow(self, flow_id: str) -> Dict[str, Any]:
        """Delete a Langflow workflow"""
        try:
            url = f"{self.base_url}/api/v1/flow/{flow_id}"
            response = self.session.delete(url)

            if response.status_code == 204:
                return {"success": True}
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def _parse_flow_execution_from_command(self, command: str) -> tuple:
        """Parse flow ID and input data from command"""
        flow_id = None
        input_data = {}

        # Extract flow ID
        if "id=" in command:
            id_part = command.split("id=")[1].split()[0]
            flow_id = id_part

        # Extract input data
        if "input_data=" in command:
            data_part = command.split("input_data=")[1]
            try:
                input_data = json.loads(data_part)
            except json.JSONDecodeError:
                input_data = {}

        return flow_id, input_data

    def _parse_flow_config_from_command(
        self, command: str
    ) -> Optional[Dict[str, Any]]:
        """Parse flow configuration from command string"""
        config = {}

        # Extract name
        if "name=" in command:
            name_part = command.split("name=")[1].split()[0]
            config['name'] = name_part

        # Extract description
        if "description=" in command:
            desc_part = command.split("description=")[1]
            if desc_part.startswith('"'):
                config['description'] = desc_part.split('"')[1]
            else:
                config['description'] = desc_part.split()[0]

        return config if config else None

    def _parse_flow_id_from_command(self, command: str) -> Optional[str]:
        """Parse flow ID from command"""
        if "id=" in command:
            id_part = command.split("id=")[1].split()[0]
            return id_part
        return None

    @classmethod
    def schema(cls):
        """Return tool schema for ULTRON Agent tool system"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Langflow command to execute"
                }
            }
        }


# Export the tool class
__all__ = ['LangflowTool']
