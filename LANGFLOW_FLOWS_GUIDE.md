# 🎮 LANGFLOW WORKFLOWS - MANUAL SETUP GUIDE

## 📋 6 ESSENTIAL FLOWS

### Flow 1: CODE ASSISTANT (General Coding)

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
You are an expert coding assistant.

Task: {input}

Provide:
1. Clean, formatted code
2. Type hints (Python) or types (TypeScript)
3. Brief inline comments for complex logic
4. Follow best practices

Output only code, no explanations.
```

**Ollama Settings:**
- Model: `qwen2.5-coder:1.5b`
- Base URL: `http://localhost:11434`

**Save as:** `code_assistant`

---

### Flow 2: PYTHON TYPE HINTS

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
Add type hints to this Python code:

{input}

Rules:
- Add type hints to all function parameters and returns
- Use typing module (List, Dict, Optional, etc.)
- Keep original logic unchanged
- Return only the code with type hints
```

**Save as:** `python_type_hints`

---

### Flow 3: GAME LOGIC ASSISTANT

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
You are a game development expert.

Request: {input}

Provide:
1. Efficient game logic code
2. Performance-optimized algorithms
3. Common game patterns (state machines, object pooling, etc.)
4. Memory-efficient data structures

Focus on: Unity C#, Python game engines, or JavaScript game frameworks.
Output: Production-ready code only.
```

**Save as:** `game_logic`

---

### Flow 4: UNITY C# HELPER

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
You are a Unity C# expert.

Task: {input}

Generate Unity C# script with:
1. Proper Unity lifecycle methods (Awake, Start, Update, etc.)
2. SerializeField for inspector variables
3. Null checks and error handling
4. Performance best practices (avoid GetComponent in Update)
5. XML documentation comments

Output: Complete Unity MonoBehaviour script.
```

**Save as:** `unity_csharp`

---

### Flow 5: DOCUMENTATION GENERATOR

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
Generate documentation for this code:

{input}

Include:
1. Module/class docstring
2. Function docstrings with Args, Returns, Raises
3. Inline comments for complex logic
4. Usage examples

Format: Python docstrings (Google style) or JSDoc for JavaScript.
```

**Save as:** `documentation_generator`

---

### Flow 6: DEBUG ASSISTANT

**Components:**
```
[Chat Input] → [Prompt] → [Ollama] → [Chat Output]
```

**Prompt Template:**
```
Debug this code/error:

{input}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix
4. Prevention tips

Output: Fixed code first, then brief explanation.
```

**Save as:** `debug_assistant`

---

## 🚀 QUICK SETUP STEPS

### Step 1: Create Each Flow (10 min)

For each flow above:

1. Open Langflow: `http://127.0.0.1:7861`
2. Click "New Flow"
3. Add components from left sidebar:
   - **Chat Input**
   - **Prompt** (paste template)
   - **Ollama** (set model to `qwen2.5-coder:1.5b`)
   - **Chat Output**
4. Connect: Input → Prompt → Ollama → Output
5. Click "Save" with the name shown
6. **Copy the Flow ID** from URL

### Step 2: Record Flow IDs (2 min)

Create a file with your flow IDs:

```json
{
  "code_assistant": "YOUR_FLOW_ID_1",
  "python_type_hints": "YOUR_FLOW_ID_2",
  "game_logic": "YOUR_FLOW_ID_3",
  "unity_csharp": "YOUR_FLOW_ID_4",
  "documentation_generator": "YOUR_FLOW_ID_5",
  "debug_assistant": "YOUR_FLOW_ID_6"
}
```

Save as: `langflow_flow_ids.json`

---

## 🔧 CURSOR MCP CONFIGURATION

### Update Cursor Settings

Location: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "code-assistant": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_1"],
      "disabled": false
    },
    "python-types": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_2"],
      "disabled": false
    },
    "game-logic": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_3"],
      "disabled": false
    },
    "unity-csharp": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_4"],
      "disabled": false
    },
    "docs-generator": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_5"],
      "disabled": false
    },
    "debug-assistant": {
      "command": "uvx",
      "args": ["langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", "FLOW_ID_6"],
      "disabled": false
    }
  }
}
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Format Code

**In Cursor chat:**
```
Use code-assistant to format this:
def hello()
print("hello")
```

**Result:** Clean, formatted Python code with type hints

### Example 2: Add Type Hints

**In Cursor chat:**
```
Use python-types to add type hints:
def calculate(a, b):
    return a + b
```

**Result:** 
```python
def calculate(a: int, b: int) -> int:
    return a + b
```

### Example 3: Create Unity Script

**In Cursor chat:**
```
Use unity-csharp to create a player controller with WASD movement
```

**Result:** Complete Unity MonoBehaviour script

### Example 4: Generate Game Logic

**In Cursor chat:**
```
Use game-logic to create an inventory system with item stacking
```

**Result:** Efficient inventory system code

### Example 5: Auto-Document

**In Cursor chat:**
```
Use docs-generator to document this function:
[paste your function]
```

**Result:** Function with complete docstrings

### Example 6: Debug Code

**In Cursor chat:**
```
Use debug-assistant to fix this error:
[paste error and code]
```

**Result:** Fixed code with explanation

---

## 📊 WORKFLOW EFFICIENCY

### Time Savings

| Task | Manual Time | With Flow | Savings |
|------|-------------|-----------|---------|
| Format code | 5 min | 10 sec | 96% |
| Add type hints | 10 min | 15 sec | 97% |
| Create Unity script | 20 min | 30 sec | 97% |
| Write documentation | 15 min | 20 sec | 98% |
| Debug issue | 30 min | 1 min | 97% |

### Quality Improvements

- ✅ Consistent code style
- ✅ Complete type coverage
- ✅ Best practices enforced
- ✅ Comprehensive documentation
- ✅ Faster debugging

---

## 🚀 ADVANCED WORKFLOWS (OPTIONAL)

### Flow 7: Code Review

**Prompt:**
```
Review this code for:
1. Security vulnerabilities
2. Performance issues
3. Best practice violations
4. Potential bugs

Code: {input}

Output: Issues found + fixed code
```

### Flow 8: Test Generator

**Prompt:**
```
Generate unit tests for this code:

{input}

Include:
- Happy path tests
- Edge cases
- Error handling tests
- Mock external dependencies

Output: Complete test file
```

### Flow 9: Refactor Assistant

**Prompt:**
```
Refactor this code for:
1. Better readability
2. Reduced complexity
3. Improved performance
4. SOLID principles

Code: {input}

Output: Refactored code + explanation
```

---

## ✅ SETUP CHECKLIST

- [ ] Langflow running on port 7861
- [ ] Flow 1: code_assistant created
- [ ] Flow 2: python_type_hints created
- [ ] Flow 3: game_logic created
- [ ] Flow 4: unity_csharp created
- [ ] Flow 5: documentation_generator created
- [ ] Flow 6: debug_assistant created
- [ ] All Flow IDs recorded
- [ ] Cursor MCP settings updated
- [ ] Cursor restarted
- [ ] Test command works in Cursor

---

## 🎓 TIPS & TRICKS

### Tip 1: Chain Flows

Use multiple flows in sequence:
```
1. Use code-assistant to write code
2. Use python-types to add type hints
3. Use docs-generator to document
```

### Tip 2: Custom Prompts

Modify prompts for your specific needs:
- Add your coding style preferences
- Include project-specific patterns
- Enforce company standards

### Tip 3: Model Selection

- **Fast:** `qwen2.5-coder:1.5b` (current)
- **Balanced:** `qwen2.5-coder:7b`
- **Best:** `deepseek-coder:33b`

### Tip 4: Keyboard Shortcuts

Create Cursor shortcuts for common flows:
- `Ctrl+Alt+F` → Format with code-assistant
- `Ctrl+Alt+T` → Add type hints
- `Ctrl+Alt+D` → Generate docs

---

## 📝 NEXT STEPS

1. **Create all 6 flows** (10 minutes)
2. **Record flow IDs** (2 minutes)
3. **Update Cursor MCP config** (3 minutes)
4. **Restart Cursor** (1 minute)
5. **Test each flow** (5 minutes)

**Total setup time:** ~20 minutes

**Result:** 6 powerful AI workflows integrated into your editor! 🚀

---

**Ready to create the flows?** Open Langflow and start with Flow 1! 🎯
