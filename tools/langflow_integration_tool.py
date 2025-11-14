"""Langflow integration tool for ULTRON Agent"""
import requests
from utils.ultron_logger import log_info, log_error

class LangflowIntegrationTool:
    name = "Langflow Integration"
    description = "Execute Langflow workflows and manage AI pipelines"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.base_url = self.config.get('langflow_url', 'http://localhost:7860')
    
    def match(self, command: str) -> bool:
        keywords = ['langflow', 'workflow', 'pipeline', 'ai flow']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            if 'run' in command.lower():
                return self._run_workflow(command)
            elif 'list' in command.lower():
                return self._list_workflows()
            else:
                return "Langflow commands: 'run workflow [name]', 'list workflows'"
        except Exception as e:
            log_error("langflow_tool", f"Error: {e}")
            return f"Langflow error: {str(e)}"
    
    def _run_workflow(self, command: str) -> str:
        """Execute a Langflow workflow"""
        workflow_name = command.split('run workflow')[-1].strip()
        log_info("langflow_tool", f"Running workflow: {workflow_name}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/run/{workflow_name}",
                json={"input": command},
                timeout=30
            )
            return f"Workflow executed: {response.json()}"
        except Exception as e:
            return f"Failed to run workflow: {str(e)}"
    
    def _list_workflows(self) -> str:
        """List available workflows"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/flows", timeout=10)
            flows = response.json()
            return f"Available workflows: {', '.join([f['name'] for f in flows])}"
        except Exception as e:
            return f"Failed to list workflows: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Workflow command"}
            }
        }
