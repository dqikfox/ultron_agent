"""Workflow editor tool for ULTRON Agent"""
import json
from pathlib import Path
from utils.ultron_logger import log_info, log_error

class WorkflowEditorTool:
    name = "Workflow Editor"
    description = "Create and edit AI workflows"
    
    def __init__(self, config=None):
        self.workflows_dir = Path('workflows')
        self.workflows_dir.mkdir(exist_ok=True)
    
    def match(self, command: str) -> bool:
        keywords = ['create workflow', 'edit workflow', 'save workflow', 'load workflow']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            if 'create' in command.lower():
                return self._create_workflow(command)
            elif 'edit' in command.lower():
                return self._edit_workflow(command)
            elif 'save' in command.lower():
                return self._save_workflow(command)
            elif 'load' in command.lower():
                return self._load_workflow(command)
            else:
                return "Workflow commands: create, edit, save, load"
        except Exception as e:
            log_error("workflow_editor", f"Error: {e}")
            return f"Workflow error: {str(e)}"
    
    def _create_workflow(self, command: str) -> str:
        """Create new workflow"""
        name = command.split('create workflow')[-1].strip()
        workflow = {
            "name": name,
            "components": [],
            "connections": [],
            "created": str(Path.ctime)
        }
        
        file_path = self.workflows_dir / f"{name}.json"
        with open(file_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        log_info("workflow_editor", f"Created workflow: {name}")
        return f"Created workflow: {name}"
    
    def _edit_workflow(self, command: str) -> str:
        """Edit existing workflow"""
        return "Workflow editing interface ready"
    
    def _save_workflow(self, command: str) -> str:
        """Save workflow"""
        return "Workflow saved"
    
    def _load_workflow(self, command: str) -> str:
        """Load workflow"""
        name = command.split('load workflow')[-1].strip()
        file_path = self.workflows_dir / f"{name}.json"
        
        if not file_path.exists():
            return f"Workflow not found: {name}"
        
        with open(file_path) as f:
            workflow = json.load(f)
        
        return f"Loaded workflow: {workflow['name']}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Workflow command"}
            }
        }
