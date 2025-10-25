from tools.tool_interface import ToolInterface
from core.agent_orchestrator import orchestrator
from core.advanced_models import models_manager
from core.workflow_engine import workflow_engine
from utils.ultron_logger import log_info, log_error
import asyncio

class OrchestrationTool(ToolInterface):
    """AI Agent Orchestration and Workflow Management Tool"""
    
    @property
    def name(self) -> str:
        return "AI Orchestration"
    
    @property
    def description(self) -> str:
        return "Multi-agent orchestration, advanced models, and workflow automation"
    
    def match(self, command: str) -> bool:
        keywords = [
            "orchestrate", "delegate", "workflow", "multi agent", 
            "advanced ai", "route model", "automate", "agents"
        ]
        return any(kw in command.lower() for kw in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("orchestration_tool", f"Processing: {command}")
        
        try:
            if "delegate" in command.lower() or "orchestrate" in command.lower():
                return asyncio.run(self._delegate_task(command))
            elif "workflow" in command.lower() or "automate" in command.lower():
                return asyncio.run(self._execute_workflow(command))
            elif "route" in command.lower() or "advanced" in command.lower():
                return asyncio.run(self._route_to_model(command))
            else:
                return self._show_status()
        except Exception as e:
            log_error("orchestration_tool", f"Error: {e}")
            return f"❌ Orchestration error: {str(e)}"
    
    async def _delegate_task(self, command: str) -> str:
        """Delegate task to appropriate agent"""
        task_type = self._extract_task_type(command)
        task = {
            "type": task_type,
            "description": command,
            "priority": "normal"
        }
        
        result = await orchestrator.delegate_task(task)
        return f"🤖 Task Delegation:\n{result}"
    
    async def _execute_workflow(self, command: str) -> str:
        """Execute or trigger workflow"""
        if "code review" in command.lower():
            return await workflow_engine.trigger_workflow("code_changed", {"file_path": "current"})
        elif "deploy" in command.lower():
            return await workflow_engine.trigger_workflow("deploy_requested", {"environment": "staging"})
        else:
            return await workflow_engine.trigger_workflow("general", {})
    
    async def _route_to_model(self, command: str) -> str:
        """Route to advanced AI model"""
        task_type = self._extract_task_type(command)
        prompt = self._extract_prompt(command)
        
        result = await models_manager.route_to_best_model(task_type, prompt)
        return f"🧠 Advanced AI Response:\n{result}"
    
    def _extract_task_type(self, command: str) -> str:
        """Extract task type from command"""
        if any(word in command.lower() for word in ["code", "debug", "program"]):
            return "coding"
        elif any(word in command.lower() for word in ["analyze", "reason", "think"]):
            return "reasoning"
        elif any(word in command.lower() for word in ["image", "vision", "see"]):
            return "vision"
        else:
            return "general"
    
    def _extract_prompt(self, command: str) -> str:
        """Extract prompt from command"""
        prefixes = ["route", "advanced", "ask", "tell"]
        prompt = command.lower()
        for prefix in prefixes:
            if prompt.startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        return prompt if prompt else command
    
    def _show_status(self) -> str:
        """Show orchestration status"""
        agent_count = len(orchestrator.agents)
        workflow_count = len(workflow_engine.workflows)
        model_types = len(models_manager.models)
        
        return f"""🤖 AI Orchestration Status:
        
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
    
    @classmethod
    def schema(cls):
        return {
            "name": "ai_orchestration",
            "description": "Multi-agent orchestration and workflow automation",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Orchestration action"},
                    "task_type": {"type": "string", "description": "Type of task"},
                    "prompt": {"type": "string", "description": "Task description"}
                },
                "required": ["action"]
            }
        }