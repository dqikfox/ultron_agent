"""AI Agent Orchestration and Workflow Management Tool"""

import asyncio
from typing import Any, Dict, List

from core.advanced_models import models_manager
from core.agent_orchestrator import orchestrator
from core.workflow_engine import workflow_engine
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_error, log_info


class OrchestrationTool(ToolInterface):
    """AI Agent Orchestration and Workflow Management Tool"""

    @property
    def name(self) -> str:
        return "AI Orchestration"

    @property
    def description(self) -> str:
        return (
            "Multi-agent orchestration, advanced models, and "
            "workflow automation"
        )

    def match(self, command: str) -> bool:
        """Check if command matches orchestration operations"""
        keywords: List[str] = [
            "orchestrate", "delegate", "workflow", "multi agent",
            "advanced ai", "route model", "automate", "agents"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute orchestration operation"""
        log_info("orchestration_tool", f"Processing: {command}")

        try:
            cmd_lower: str = command.lower()
            if "delegate" in cmd_lower or "orchestrate" in cmd_lower:
                return asyncio.run(self._delegate_task(command))
            elif "workflow" in cmd_lower or "automate" in cmd_lower:
                return asyncio.run(self._execute_workflow(command))
            elif "route" in cmd_lower or "advanced" in cmd_lower:
                return asyncio.run(self._route_to_model(command))
            else:
                return self._show_status()
        except Exception as e:
            log_error("orchestration_tool", f"Error: {e}")
            return f"❌ Orchestration error: {str(e)}"

    async def _delegate_task(self, command: str) -> str:
        """Delegate task to appropriate agent"""
        task_type: str = self._extract_task_type(command)
        task: Dict[str, Any] = {
            "type": task_type,
            "description": command,
            "priority": "normal"
        }

        result: Any = await orchestrator.delegate_task(task)
        return f"🤖 Task Delegation:\n{result}"

    async def _execute_workflow(self, command: str) -> str:
        """Execute or trigger workflow"""
        cmd_lower: str = command.lower()
        if "code review" in cmd_lower:
            workflow_result: Any = (
                await workflow_engine.trigger_workflow(
                    "code_changed", {"file_path": "current"}
                )
            )
            return workflow_result
        elif "deploy" in cmd_lower:
            workflow_result = await workflow_engine.trigger_workflow(
                "deploy_requested", {"environment": "staging"}
            )
            return workflow_result
        else:
            workflow_result = await workflow_engine.trigger_workflow(
                "general", {}
            )
            return workflow_result

    async def _route_to_model(self, command: str) -> str:
        """Route to advanced AI model"""
        task_type: str = self._extract_task_type(command)
        prompt: str = self._extract_prompt(command)

        result: Any = await models_manager.route_to_best_model(
            task_type, prompt
        )
        return f"🧠 Advanced AI Response:\n{result}"

    def _extract_task_type(self, command: str) -> str:
        """Extract task type from command"""
        cmd_lower: str = command.lower()
        coding_keywords: List[str] = ["code", "debug", "program"]
        reasoning_keywords: List[str] = ["analyze", "reason", "think"]
        vision_keywords: List[str] = ["image", "vision", "see"]

        if any(word in cmd_lower for word in coding_keywords):
            return "coding"
        elif any(word in cmd_lower for word in reasoning_keywords):
            return "reasoning"
        elif any(word in cmd_lower for word in vision_keywords):
            return "vision"
        else:
            return "general"

    def _extract_prompt(self, command: str) -> str:
        """Extract prompt from command"""
        prefixes: List[str] = ["route", "advanced", "ask", "tell"]
        prompt: str = command.lower()
        for prefix in prefixes:
            if prompt.startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        return prompt if prompt else command

    def _show_status(self) -> str:
        """Show orchestration status"""
        agent_count: int = len(orchestrator.agents)
        workflow_count: int = len(workflow_engine.workflows)
        model_types: int = len(models_manager.models)

        status_msg: str = f"""🤖 AI Orchestration Status:

👥 Agents: {agent_count} registered
🔄 Workflows: {workflow_count} available
🧠 Model Types: {model_types} categories

Available Commands:
• "orchestrate code review task"
• "delegate image analysis to vision agent"
• "workflow automate deployment"
• "route advanced reasoning question"
• "advanced ai explain quantum computing"
"""
        return status_msg

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "ai_orchestration",
            "description": (
                "Multi-agent orchestration and workflow automation"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Orchestration action"
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Type of task"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Task description"
                    }
                },
                "required": ["action"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> OrchestrationTool:
    """Required function for tool loader"""
    return OrchestrationTool()
