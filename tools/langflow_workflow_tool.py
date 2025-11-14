"""
Langflow Workflow Integration Tool for ULTRON Agent
Enables visual workflow creation and execution within ULTRON system.

Author: ULTRON Agent + Copilot + Amazon Q Collaboration
Date: November 1, 2025
Status: PHASE 2B - Initial Implementation
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.event_system import get_event_system


class LangflowClient:
    """Interface to communicate with Langflow service"""

    def __init__(self, base_url: str = "http://localhost:7860",
                 api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = 30

    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows"""
        try:
            # Mock response - in production would call Langflow API
            workflows = [
                {
                    "id": "data-processing",
                    "name": "Data Processing Pipeline",
                    "version": "1.0",
                    "description": "ETL pipeline for data transformation"
                },
                {
                    "id": "api-integration",
                    "name": "API Integration",
                    "version": "1.0",
                    "description": "Connect and call external APIs"
                },
                {
                    "id": "code-generation",
                    "name": "Code Generation",
                    "version": "1.0",
                    "description": "Generate code from specifications"
                },
                {
                    "id": "analysis",
                    "name": "Analysis Workflow",
                    "version": "1.0",
                    "description": "Data analysis and reporting"
                },
                {
                    "id": "monitoring",
                    "name": "Monitoring Pipeline",
                    "version": "1.0",
                    "description": "System monitoring and alerting"
                }
            ]

            log_info("langflow_client", f"Retrieved {len(workflows)} workflows")
            return workflows
        except Exception as e:
            log_error("langflow_client", f"Error getting workflows: {e}")
            return []

    async def execute_workflow(self, workflow_id: str,
                              inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with given inputs"""
        try:
            log_info("langflow_client", f"Executing workflow: {workflow_id}")

            # Mock execution - in production would call Langflow API
            result = {
                "workflow_id": workflow_id,
                "status": "success",
                "execution_time": "2.45s",
                "output": {
                    "message": f"Workflow {workflow_id} executed successfully",
                    "processed_items": len(inputs),
                    "timestamp": datetime.now().isoformat()
                }
            }

            log_ai_decision(
                "langflow_client",
                f"Workflow executed: {workflow_id}",
                ai_model="langflow",
                confidence_score=0.95
            )

            return result
        except Exception as e:
            log_error("langflow_client", f"Error executing workflow: {e}")
            return {"status": "error", "error": str(e)}

    async def get_workflow_template(self, template_id: str
                                   ) -> Dict[str, Any]:
        """Get workflow template definition"""
        try:
            templates = {
                "data-processing": {
                    "name": "Data Processing Pipeline",
                    "nodes": [
                        {"id": "input", "type": "input",
                         "name": "Input Data"},
                        {"id": "transform", "type": "tool",
                         "name": "Transform"},
                        {"id": "output", "type": "output",
                         "name": "Output"}
                    ]
                },
                "api-integration": {
                    "name": "API Integration",
                    "nodes": [
                        {"id": "request", "type": "api",
                         "name": "API Request"},
                        {"id": "parse", "type": "parser",
                         "name": "Parse Response"},
                        {"id": "output", "type": "output",
                         "name": "Output"}
                    ]
                },
                "code-generation": {
                    "name": "Code Generation",
                    "nodes": [
                        {"id": "spec", "type": "input",
                         "name": "Code Specification"},
                        {"id": "generate", "type": "ai",
                         "name": "Generate Code"},
                        {"id": "output", "type": "output",
                         "name": "Generated Code"}
                    ]
                },
                "analysis": {
                    "name": "Analysis Workflow",
                    "nodes": [
                        {"id": "input", "type": "input",
                         "name": "Input Data"},
                        {"id": "analyze", "type": "analyzer",
                         "name": "Analyze"},
                        {"id": "report", "type": "reporter",
                         "name": "Generate Report"},
                        {"id": "output", "type": "output",
                         "name": "Output Report"}
                    ]
                },
                "monitoring": {
                    "name": "Monitoring Pipeline",
                    "nodes": [
                        {"id": "monitor", "type": "monitor",
                         "name": "Monitor System"},
                        {"id": "alert", "type": "alerter",
                         "name": "Generate Alerts"},
                        {"id": "output", "type": "output",
                         "name": "Alert Output"}
                    ]
                }
            }

            return templates.get(template_id, {})
        except Exception as e:
            log_error("langflow_client",
                     f"Error getting template: {e}")
            return {}


class WorkflowRegistry:
    """Manages workflow templates and instances"""

    def __init__(self):
        self.templates: Dict[str, Dict] = {}
        self.instances: Dict[str, Dict] = {}
        self.execution_history: List[Dict] = []

    def add_template(self, template_id: str,
                    template_def: Dict[str, Any]):
        """Register a workflow template"""
        self.templates[template_id] = {
            **template_def,
            "registered_at": datetime.now().isoformat()
        }
        log_info("workflow_registry",
                f"Registered template: {template_id}")

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get workflow template"""
        return self.templates.get(template_id)

    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return list(self.templates.values())

    def create_instance(self, instance_id: str,
                       template_id: str) -> bool:
        """Create workflow instance from template"""
        if template_id not in self.templates:
            return False

        self.instances[instance_id] = {
            "template_id": template_id,
            "created_at": datetime.now().isoformat(),
            "status": "ready",
            "executions": 0
        }
        log_info("workflow_registry",
                f"Created instance: {instance_id}")
        return True

    def record_execution(self, instance_id: str, result: Dict):
        """Record workflow execution"""
        self.execution_history.append({
            "instance_id": instance_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        if instance_id in self.instances:
            self.instances[instance_id]["executions"] += 1
            self.instances[instance_id]["last_execution"] = (
                datetime.now().isoformat()
            )


class LangflowWorkflowTool(ToolInterface):
    """Langflow Workflow integration for ULTRON Agent

    Enables:
    - Visual workflow creation in Langflow
    - Workflow execution from ULTRON
    - 5 pre-built templates
    - Execution history tracking
    """

    def __init__(self):
        self.langflow_client = LangflowClient()
        self.workflow_registry = WorkflowRegistry()
        self.event_system = get_event_system()

        log_info("langflow_workflow", "Tool initialized")

    @property
    def name(self) -> str:
        return "Langflow Workflow Integration"

    @property
    def description(self) -> str:
        return (
            "Execute Langflow workflows in ULTRON - "
            "5 templates available"
        )

    def match(self, command: str) -> bool:
        """Check if command matches Langflow integration"""
        keywords = [
            "workflow", "langflow", "run workflow",
            "execute workflow", "create workflow",
            "show workflows"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute Langflow workflow command"""
        try:
            command_lower = command.lower()

            if "run" in command_lower or "execute" in command_lower:
                return self._handle_execute_workflow(command, **kwargs)
            elif "list" in command_lower or "show" in command_lower:
                return self._handle_list_workflows(command, **kwargs)
            elif "create" in command_lower:
                return self._handle_create_instance(command, **kwargs)
            elif "template" in command_lower:
                return self._handle_template_info(command, **kwargs)
            elif "history" in command_lower:
                return self._handle_execution_history(command, **kwargs)
            else:
                return f"Unknown workflow command: {command}"

        except Exception as e:
            error_msg = f"Workflow error: {e}"
            log_error("langflow_workflow", error_msg)
            return error_msg

    def _handle_execute_workflow(self, command: str,
                                **kwargs) -> str:
        """Execute a workflow"""
        try:
            workflow_name = self._extract_workflow_name(command)
            if not workflow_name:
                return "No workflow specified. Usage: run workflow [name]"

            # Map friendly names to IDs
            workflow_map = {
                "data processing": "data-processing",
                "api integration": "api-integration",
                "code generation": "code-generation",
                "analysis": "analysis",
                "monitoring": "monitoring"
            }

            workflow_id = None
            for key, val in workflow_map.items():
                if key in workflow_name.lower():
                    workflow_id = val
                    break

            if not workflow_id:
                return f"Unknown workflow: {workflow_name}"

            # Extract inputs
            inputs = self._extract_inputs(command)

            # Execute
            result = asyncio.run(
                self.langflow_client.execute_workflow(
                    workflow_id, inputs
                )
            )

            # Record execution
            instance_id = (
                f"{workflow_id}_{int(datetime.now().timestamp())}"
            )
            self.workflow_registry.record_execution(
                instance_id, result
            )

            output = f"✓ Workflow: {workflow_name}\n"
            output += f"  Status: {result['status']}\n"
            output += f"  Time: {result.get('execution_time', 'N/A')}\n"
            if result['status'] == 'success':
                output += f"  Result: {result['output'].get('message', '')}"

            return output

        except Exception as e:
            return f"Error executing workflow: {e}"

    def _handle_list_workflows(self, command: str,
                              **kwargs) -> str:
        """List available workflows"""
        try:
            workflows = asyncio.run(
                self.langflow_client.get_workflows()
            )

            if not workflows:
                return "No workflows available"

            result = "Available Workflows:\n\n"
            for i, workflow in enumerate(workflows, 1):
                result += f"{i}. {workflow['name']}\n"
                result += f"   ID: {workflow['id']}\n"
                result += f"   {workflow['description']}\n"

            return result

        except Exception as e:
            return f"Error listing workflows: {e}"

    def _handle_create_instance(self, command: str,
                               **kwargs) -> str:
        """Create workflow instance"""
        try:
            template_name = self._extract_workflow_name(command)
            if not template_name:
                return (
                    "No template specified. "
                    "Usage: create workflow [template_name]"
                )

            template_map = {
                "data processing": "data-processing",
                "api integration": "api-integration",
                "code generation": "code-generation",
                "analysis": "analysis",
                "monitoring": "monitoring"
            }

            template_id = None
            for key, val in template_map.items():
                if key in template_name.lower():
                    template_id = val
                    break

            if not template_id:
                return f"Unknown template: {template_name}"

            instance_id = f"instance_{int(datetime.now().timestamp())}"
            success = self.workflow_registry.create_instance(
                instance_id, template_id
            )

            if success:
                result = f"✓ Instance created: {instance_id}\n"
                result += f"  Template: {template_name}\n"
                result += f"  Status: Ready for execution"
                return result
            else:
                return f"Failed to create instance for template: {template_id}"

        except Exception as e:
            return f"Error creating instance: {e}"

    def _handle_template_info(self, command: str,
                             **kwargs) -> str:
        """Get template information"""
        try:
            template_name = self._extract_workflow_name(command)
            if not template_name:
                return (
                    "No template specified. "
                    "Usage: template info [template_name]"
                )

            template_map = {
                "data processing": "data-processing",
                "api integration": "api-integration",
                "code generation": "code-generation",
                "analysis": "analysis",
                "monitoring": "monitoring"
            }

            template_id = None
            for key, val in template_map.items():
                if key in template_name.lower():
                    template_id = val
                    break

            if not template_id:
                return f"Unknown template: {template_name}"

            template = asyncio.run(
                self.langflow_client.get_workflow_template(
                    template_id
                )
            )

            if not template:
                return f"No template found: {template_id}"

            result = f"Template: {template.get('name', 'Unknown')}\n"
            result += f"Nodes: {len(template.get('nodes', []))}\n\n"

            for node in template.get('nodes', []):
                result += f"  • {node['name']} ({node['type']})\n"

            return result

        except Exception as e:
            return f"Error getting template info: {e}"

    def _handle_execution_history(self, command: str,
                                 **kwargs) -> str:
        """Show execution history"""
        if not self.workflow_registry.execution_history:
            return "No execution history available"

        result = "Execution History:\n\n"
        for entry in self.workflow_registry.execution_history[-10:]:
            result += f"Instance: {entry['instance_id']}\n"
            result += f"  Status: {entry['result'].get('status', 'N/A')}\n"
            result += f"  Time: {entry['timestamp']}\n\n"

        return result

    @staticmethod
    def _extract_workflow_name(command: str) -> Optional[str]:
        """Extract workflow name from command"""
        # Look for quoted name
        quoted_match = re.search(
            r'["\']([^"\']+)["\']', command
        )
        if quoted_match:
            return quoted_match.group(1)

        # Look for name after workflow keyword
        name_match = re.search(
            r'(?:workflow|template)\s+(?:named\s+)?(?:")?'
            r'([a-z\s]+)(?:")?',
            command, re.IGNORECASE
        )
        if name_match:
            return name_match.group(1).strip()

        return None

    @staticmethod
    def _extract_inputs(command: str) -> Dict[str, Any]:
        """Extract workflow inputs from command"""
        inputs = {}

        # Look for JSON inputs
        json_match = re.search(r'with\s+({.*?})', command)
        if json_match:
            try:
                inputs = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return inputs

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for OpenAI-compatible calling"""
        return {
            "name": "langflow_workflow",
            "description": (
                "Execute Langflow workflows - "
                "5 pre-built templates available"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Workflow command: "
                            "run, list, create, template, history"
                        )
                    }
                },
                "required": ["command"]
            }
        }
