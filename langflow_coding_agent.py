"""Langflow Coding Agent for VS Code ULTRON Integration"""
import requests
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LangflowCodingAgent:
    def __init__(self):
        self.url = "http://localhost:7860/api/v1/run/92c810b5-4829-4466-9ff1-7ad19b694435"
        self.api_key = "sk-P8RcOr7-zDErbDU1Un1cJL3l-zozgr45sazXhUcX-2U"
        self.project_root = Path("C:/Projects/ultron_agent")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
    def analyze_code(self, file_path: str, code: str) -> dict:
        """Send code to Langflow for analysis"""
        prompt = f"""Analyze this ULTRON Agent code:

File: {file_path}

Code:
```python
{code}
```

Provide:
1. Code quality assessment
2. Potential bugs
3. Performance improvements
4. Integration suggestions with ULTRON architecture
5. Refactoring recommendations"""

        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": prompt
        }
        
        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_code(self, task: str) -> dict:
        """Generate code via Langflow"""
        prompt = f"""Generate Python code for ULTRON Agent:

Task: {task}

Requirements:
- Follow ULTRON architecture patterns
- Use centralized logging (utils.ultron_logger)
- Include error handling
- Add type hints
- Integrate with existing tools

Generate complete, production-ready code."""

        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": prompt
        }
        
        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=60)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def watch_and_assist(self):
        """Watch files and provide real-time assistance"""
        class CodeHandler(FileSystemEventHandler):
            def __init__(self, agent):
                self.agent = agent
            
            def on_modified(self, event):
                if event.src_path.endswith('.py'):
                    print(f"Analyzing: {event.src_path}")
                    with open(event.src_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    result = self.agent.analyze_code(event.src_path, code)
                    print(json.dumps(result, indent=2))
        
        observer = Observer()
        observer.schedule(CodeHandler(self), str(self.project_root), recursive=True)
        observer.start()
        
        print(f"Watching {self.project_root} for changes...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    agent = LangflowCodingAgent()
    
    # Test code generation
    print("Generating game engine code...")
    result = agent.generate_code("Create GameEngine class for AI Agent Battle Arena")
    print(json.dumps(result, indent=2))
    
    # Start file watcher
    # agent.watch_and_assist()
