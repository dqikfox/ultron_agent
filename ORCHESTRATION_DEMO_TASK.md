# 🎬 Orchestration Demo Task - Try It Now!

## Quick Demo: Have Your Local Model Create a Simple Tool

### Task Overview
Create a minimal "hello_tool" to demonstrate orchestration workflow.

---

## Step-by-Step Demo

### 1. Open Continue Chat
```
Press: Ctrl+L in VS Code
```

### 2. Load Orchestration Prompt
```
Type: @prompt orchestration_workflow
```

### 3. Give This Task
```
Create a simple hello_tool that:
- Matches commands containing "hello" or "hi"
- Responds with a friendly greeting
- Includes the user's name if provided
- Uses ultron_logger for logging
- Follows ToolInterface pattern

Example commands:
- "hello"
- "hi there"
- "hello John"
```

### 4. Watch Your Model Work
Your local model (Qwen 2.5 Coder 7B) will:
1. Analyze the requirements
2. Plan the implementation
3. Generate the code
4. Provide test commands

### 5. Expected Output
The model should create something like:

```python
# tools/hello_tool.py
from utils.ultron_logger import log_info, log_error

class HelloTool:
    name = "hello_tool"
    description = "Friendly greeting tool"
    
    def match(self, command: str) -> bool:
        return any(word in command.lower() for word in ["hello", "hi"])
    
    def execute(self, command: str) -> str:
        log_info("hello_tool", f"Executing: {command}")
        
        # Extract name if provided
        words = command.split()
        name = words[-1] if len(words) > 1 else "there"
        
        return f"Hello {name}! How can I help you today?"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {}
        }
```

---

## Alternative: Direct Task Assignment

If you want more control:

### 1. Open Continue
```
Ctrl+L
```

### 2. Use Task Executor
```
@prompt task_executor

TASK: Create hello_tool
REQUIREMENTS:
- File: tools/hello_tool.py
- Match: "hello", "hi" commands
- Response: Friendly greeting
- Logging: Use ultron_logger
- Pattern: ToolInterface (match, execute, schema)
```

---

## Verification Steps

### 1. Check File Created
```
ls tools/hello_tool.py
```

### 2. Test the Tool
```python
# In Python console
from tools.hello_tool import HelloTool

tool = HelloTool()
print(tool.match("hello"))  # Should be True
print(tool.execute("hello John"))  # Should greet John
```

### 3. Verify Logging
```
# Check logs
cat logs/hello_tool.log
```

---

## Next Level: More Complex Task

Once the demo works, try:

```
@prompt orchestration_workflow

Create a calculator_tool that:
- Matches: "calculate [expression]", "math [expression]"
- Evaluates: Safe mathematical expressions
- Handles: +, -, *, /, parentheses
- Security: Blocks dangerous eval() inputs
- Logging: All calculations logged
- Errors: Graceful error messages

Examples:
- "calculate 2 + 2"
- "math (5 * 3) + 10"
- "calculate 100 / 5"
```

---

## Success Criteria

✅ Model understands the task
✅ Code follows ULTRON patterns
✅ File is created correctly
✅ Tool works as expected
✅ Logging is implemented
✅ No errors in execution

---

## Troubleshooting

### Model Doesn't Respond
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Try different model: Click dropdown, select DeepSeek R1 14B

### Code Has Errors
- Ask model to fix: "Fix the syntax error in line X"
- Provide specific feedback: "Add error handling for division by zero"

### Model Doesn't Follow Patterns
- Be more specific: "Use ultron_logger, not print()"
- Reference examples: "@file tools/example_tool.py Follow this pattern"

---

## What You're Learning

1. **Task Delegation**: How to give clear instructions to AI
2. **Orchestration**: Managing AI workflows
3. **Verification**: Checking AI output quality
4. **Iteration**: Refining AI responses
5. **Integration**: Combining AI with existing code

---

## Ready to Try?

1. Open VS Code
2. Press `Ctrl+L`
3. Type: `@prompt orchestration_workflow`
4. Paste the hello_tool task
5. Watch your local model work!

---

**Status**: 🎬 DEMO READY
**Difficulty**: Beginner
**Time**: 2-5 minutes
**Model**: Qwen 2.5 Coder 7B (recommended)
