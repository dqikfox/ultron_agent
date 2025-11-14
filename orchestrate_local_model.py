"""Direct orchestration of local Ollama models - Amazon Q to Local AI"""
import requests
import json

def send_task_to_model(task: str, model: str = "qwen2.5-coder:7b") -> str:
    """Send task directly to local Ollama model"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": task,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# DEMO TASK: Create hello_tool
task = """You are working on the ULTRON Agent project. Create a new tool file.

TASK: Create tools/hello_tool.py

REQUIREMENTS:
- Class name: HelloTool
- Match method: Return True if command contains "hello" or "hi"
- Execute method: Return friendly greeting, extract name if provided
- Use: from utils.ultron_logger import log_info, log_error
- Include: schema() classmethod
- Pattern: Follow ToolInterface (match, execute, schema methods)

EXAMPLE:
Command: "hello John"
Response: "Hello John! How can I help you today?"

Generate ONLY the Python code, no explanations."""

print("Sending task to local model (qwen2.5-coder:7b)...")
print("=" * 70)

response = send_task_to_model(task)

print("\nMODEL RESPONSE:")
print("=" * 70)
print(response)
print("=" * 70)

# Save response to file
with open("tools/hello_tool.py", "w") as f:
    # Extract code if wrapped in markdown
    if "```python" in response:
        code = response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        code = response.split("```")[1].split("```")[0].strip()
    else:
        code = response.strip()
    
    f.write(code)

print("\n✅ Code saved to tools/hello_tool.py")
print("\nTest with:")
print("  python -c \"from tools.hello_tool import HelloTool; t=HelloTool(); print(t.execute('hello John'))\"")
