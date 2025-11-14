"""Jupyter Integration Tool - Launch notebooks and execute code"""
import subprocess
import os
from pathlib import Path

class JupyterIntegrationTool:
    name = "Jupyter Integration"
    description = "Launch Jupyter notebooks and execute Python code interactively"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['jupyter', 'notebook', 'lab', 'ipynb']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        cmd_lower = command.lower()
        
        try:
            # Launch JupyterLab
            if 'lab' in cmd_lower:
                subprocess.Popen(['jupyter', 'lab'], cwd=os.getcwd())
                return f"✅ JupyterLab starting at http://localhost:8888"
            
            # Launch Jupyter Notebook
            if 'notebook' in cmd_lower:
                subprocess.Popen(['jupyter', 'notebook'], cwd=os.getcwd())
                return f"✅ Jupyter Notebook starting at http://localhost:8888"
            
            # Open specific notebook
            if '.ipynb' in cmd_lower:
                words = command.split()
                for word in words:
                    if word.endswith('.ipynb'):
                        file_path = Path(word)
                        if file_path.exists():
                            subprocess.Popen(['jupyter', 'notebook', str(file_path)])
                            return f"✅ Opening {file_path} in Jupyter"
                return "❌ Notebook file not found"
            
            # Default: launch notebook
            subprocess.Popen(['jupyter', 'notebook'], cwd=os.getcwd())
            return "✅ Jupyter Notebook launched"
            
        except Exception as e:
            return f"❌ Jupyter error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Jupyter command"}
            }
        }
