"""Fully Automated Orchestration - Amazon Q → Ollama API → Results"""
import requests
import json
from pathlib import Path

class AutoOrchestrator:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.task_queue_file = "task_queue.json"
    
    def send_to_model(self, prompt: str, model: str = "qwen2.5-coder:7b") -> str:
        """Send prompt directly to Ollama API"""
        url = f"{self.ollama_url}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False}
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json().get("response", "")
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def execute_task(self, task: dict) -> dict:
        """Execute a single task"""
        print(f"\n{'='*70}")
        print(f"TASK #{task['id']}: {task['task']}")
        print(f"Model: {task['model']}")
        print(f"{'='*70}\n")
        
        response = self.send_to_model(task['prompt'], task['model'])
        
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()
        
        return {
            "task_id": task['id'],
            "status": "completed",
            "code": code
        }
    
    def run(self):
        """Execute all pending tasks"""
        # Load task queue
        with open(self.task_queue_file, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        pending = [t for t in queue['tasks'] if t['status'] == 'pending']
        
        if not pending:
            print("No pending tasks.")
            return
        
        print(f"Found {len(pending)} pending task(s)")
        
        for task in pending:
            result = self.execute_task(task)
            
            if 'output_file' in task:
                output_file = task['output_file']
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['code'])
                print(f"[OK] Saved to {output_file}\n")
            
            task['status'] = 'completed'
            queue['completed'].append(result)
        
        # Update queue
        with open(self.task_queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"[OK] ALL TASKS COMPLETED")
        print(f"{'='*70}")

if __name__ == "__main__":
    orchestrator = AutoOrchestrator()
    orchestrator.run()
