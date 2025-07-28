from .base import Tool
import logging
import subprocess
import tempfile
import os

class CodeExecutionTool(Tool):
    def __init__(self):
        self.name = "CodeExecutionTool"
        self.description = "Execute Python code snippets safely in a sandbox."
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "run python" in cmd or "execute code" in cmd

    def execute(self, command: str) -> str:
        code = command.replace("run python", "").replace("execute code", "").strip()
        if not code:
            return "No code provided."
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
                f.write(code.encode())
                temp_file = f.name
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            os.remove(temp_file)
            output = result.stdout or result.stderr
            logging.info(f"Code executed: {output}")
            return output
        except Exception as e:
            logging.error(f"Code execution error: {e}")
            return f"Error: {e}"