"""FastAPI Integration - Launch and manage FastAPI apps"""
import subprocess
from pathlib import Path

class FastAPIIntegrationTool:
    name = "FastAPI Integration"
    description = "Launch FastAPI applications and API servers"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        return any(k in command.lower() for k in ['fastapi', 'api server', 'uvicorn'])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            # Find FastAPI app file
            for filename in ['main.py', 'app.py', 'api.py']:
                if Path(filename).exists():
                    subprocess.Popen(['uvicorn', f'{filename[:-3]}:app', '--reload'])
                    return f"✅ FastAPI running: {filename} at http://localhost:8000"
            return "❌ No FastAPI app found (main.py, app.py, or api.py)"
        except Exception as e:
            return f"❌ FastAPI error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {"name": cls.name, "description": cls.description}
