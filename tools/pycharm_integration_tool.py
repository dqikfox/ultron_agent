"""PyCharm Integration Tool - Open projects, files, and execute IDE commands"""
import subprocess
import os
from pathlib import Path

class PyCharmIntegrationTool:
    name = "PyCharm Integration"
    description = "Open PyCharm IDE, projects, and files"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
        self.pycharm_path = r"C:\Program Files\JetBrains\PyCharm 2025.2.1.1\bin\pycharm64.exe"
    
    def match(self, command: str) -> bool:
        keywords = ['pycharm', 'ide', 'open project', 'edit code']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        cmd_lower = command.lower()
        
        try:
            # Open current project
            if 'open project' in cmd_lower or 'open pycharm' in cmd_lower:
                project_path = os.getcwd()
                subprocess.Popen([self.pycharm_path, project_path])
                return f"✅ Opening PyCharm with project: {project_path}"
            
            # Open specific file
            if 'open file' in cmd_lower or 'edit' in cmd_lower:
                # Extract filename from command
                words = command.split()
                for word in words:
                    if word.endswith('.py') or word.endswith('.json'):
                        file_path = Path(word)
                        if file_path.exists():
                            subprocess.Popen([self.pycharm_path, str(file_path)])
                            return f"✅ Opening {file_path} in PyCharm"
                return "❌ No valid file found in command"
            
            # Default: open PyCharm
            subprocess.Popen([self.pycharm_path])
            return "✅ PyCharm launched"
            
        except Exception as e:
            return f"❌ PyCharm error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Command to execute"}
            }
        }
