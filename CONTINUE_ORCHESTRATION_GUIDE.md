# 🎭 Continue Orchestration Guide - Local Model Workflows

**Purpose**: Use Continue extension to orchestrate local Ollama models for automated workflows

---

## 🎯 How It Works

**Amazon Q** (me) provides:
- Task requirements
- Context and analysis
- Quality standards
- Verification criteria

**Your Local Models** (via Continue) execute:
- Code generation
- File modifications
- Testing and verification
- Documentation updates

---

## 🚀 Quick Start

### Method 1: Using Prompts (Recommended)

1. **Press `Ctrl+L`** in VS Code
2. **Type**: `@prompt orchestration_workflow`
3. **Add task**: "Create a new tool for [purpose]"
4. **Let model execute** following the workflow

### Method 2: Direct Task Assignment

1. **Press `Ctrl+L`**
2. **Type**: `@prompt task_executor`
3. **Paste Amazon Q's requirements**
4. **Model executes systematically**

### Method 3: Context-Aware Execution

1. **Press `Ctrl+L`**
2. **Type**: `@codebase @file brain.py`
3. **Add task**: "Add new method to handle [feature]"
4. **Model has full context**

---

## 💡 Example Workflows

### Workflow 1: Create New Tool

**Amazon Q provides**:
```
TASK: Create a weather lookup tool
REQUIREMENTS:
- Tool name: weather_tool
- API: OpenWeatherMap
- Commands: "weather in [city]", "forecast for [city]"
- Include error handling and logging
```

**You execute in Continue**:
```
Ctrl+L → Type:

@prompt orchestration_workflow Create weather_tool with these requirements:
- Match commands: "weather in [city]"
- Use OpenWeatherMap API
- Include ultron_logger
- Add error handling
- Follow ToolInterface pattern
```

**Local model executes**:
- Creates `tools/weather_tool.py`
- Implements match() and execute()
- Adds logging and error handling
- Provides test commands

---

### Workflow 2: Fix Bug

**Amazon Q identifies**:
```
BUG: brain.py line 145 - tools not executing
FIX: Add _execute_matching_tools() call before LLM query
```

**You execute in Continue**:
```
Ctrl+L → Type:

@file brain.py Fix bug at line 145:
- Add _execute_matching_tools() method
- Call it before LLM query
- Ensure tools execute BEFORE AI response
```

**Local model executes**:
- Reads brain.py
- Adds the method
- Integrates into workflow
- Tests the fix

---

### Workflow 3: Refactor Code

**Amazon Q suggests**:
```
REFACTOR: voice_manager.py
- Add type hints
- Improve error handling
- Add centralized logging
- Simplify fallback logic
```

**You execute in Continue**:
```
Ctrl+L → Type:

@file voice_manager.py Refactor following ULTRON patterns:
- Add type hints to all methods
- Use ultron_logger instead of print
- Improve try-except blocks
- Maintain existing functionality
```

**Local model executes**:
- Analyzes current code
- Adds improvements incrementally
- Preserves functionality
- Documents changes

---

## 🎨 Advanced Orchestration

### Multi-Step Workflow

**Step 1: Amazon Q Plans**
```
PROJECT: Add sentiment analysis to avatar game
STEPS:
1. Create sentiment_tool.py
2. Integrate with avatar_game_server.py
3. Update GUI to show sentiment
4. Add tests
```

**Step 2: You Orchestrate**
```
# Task 1
Ctrl+L → @prompt task_executor
Create sentiment_tool.py with AWS Comprehend integration

# Task 2
Ctrl+L → @file avatar_game_server.py
Integrate sentiment_tool into message handler

# Task 3
Ctrl+L → @file gui/ultron_enhanced/web/ultron_avatar_game_ultimate.html
Add sentiment display to chat interface

# Task 4
Ctrl+L → Create pytest tests for sentiment_tool
```

**Step 3: Models Execute**
- Each task completed systematically
- Changes verified at each step
- Integration tested
- Documentation updated

---

## 🔧 Orchestration Patterns

### Pattern 1: Sequential Execution
```
Task 1 → Verify → Task 2 → Verify → Task 3 → Verify
```

### Pattern 2: Parallel Analysis
```
Model 1: Analyze architecture
Model 2: Review code quality
Model 3: Check security
→ Combine insights → Execute fixes
```

### Pattern 3: Iterative Refinement
```
Draft 1 → Review → Draft 2 → Review → Final → Deploy
```

---

## 📋 Task Templates

### Template: New Feature
```
@prompt orchestration_workflow

FEATURE: [Feature name]
PURPOSE: [What it does]
INTEGRATION: [Where it fits]
REQUIREMENTS:
- [Requirement 1]
- [Requirement 2]
PATTERNS:
- Use ultron_logger
- Follow ToolInterface
- Include error handling
```

### Template: Bug Fix
```
@file [affected_file]

BUG: [Description]
LOCATION: Line [number]
ROOT CAUSE: [Cause]
FIX: [Solution]
VERIFY: [Test command]
```

### Template: Code Review
```
@file [file_to_review]

REVIEW FOR:
- ULTRON patterns compliance
- Error handling completeness
- Logging usage
- Type hints
- Documentation
PROVIDE: Specific improvements with line numbers
```

---

## 🎯 Model Selection for Tasks

| Task Type | Best Model | Why |
|-----------|------------|-----|
| **Code Generation** | Qwen 2.5 Coder 7B | Optimized for coding |
| **Architecture** | DeepSeek R1 14B | Strong reasoning |
| **Quick Fixes** | Mistral Small 3.2 | Fast responses |
| **Complex Logic** | Qwen 3 Coder 480B | Highest capability |
| **Code Review** | DeepSeek R1 14B | Analytical |
| **Documentation** | Qwen 2.5 Coder 7B | Clear explanations |

**Switch models**: Click dropdown in Continue chat

---

## ✅ Quality Checklist

After each task, verify:
- [ ] Code follows ULTRON patterns
- [ ] Logging added (ultron_logger)
- [ ] Error handling included
- [ ] Type hints present
- [ ] Documentation updated
- [ ] No existing functionality broken
- [ ] Tests pass (if applicable)

---

## 🚀 Real-World Example

**Scenario**: Amazon Q identifies that tools aren't executing in brain.py

### Step 1: Amazon Q Analysis
```
ISSUE: Tools mentioned but not executed
FILE: brain.py
SOLUTION: Add _execute_matching_tools() method
INTEGRATION: Call before LLM query
```

### Step 2: You Orchestrate
```
Ctrl+L in VS Code

@file brain.py

Task: Fix tool execution bug

Add this method:
def _execute_matching_tools(self, command: str) -> str:
    results = []
    for tool in self.tools:
        if tool.match(command):
            result = tool.execute(command)
            results.append(result)
    return "\n".join(results) if results else ""

Then call it in direct_chat() before ollama query.
```

### Step 3: Model Executes
- Reads brain.py
- Adds the method
- Integrates into workflow
- Provides test command

### Step 4: Verification
```
Test: "open chrome and search for cars"
Expected: Chrome opens, then AI responds
Result: ✅ Works!
```

---

## 📊 Orchestration Metrics

Track your orchestration success:
- **Tasks Completed**: Count successful executions
- **Time Saved**: Compare manual vs automated
- **Quality Score**: Code review ratings
- **Error Rate**: Bugs introduced vs fixed

---

## 🎓 Best Practices

### DO
✅ Provide clear, specific tasks
✅ Use @file and @codebase for context
✅ Verify after each change
✅ Use appropriate model for task
✅ Follow ULTRON patterns
✅ Test before committing

### DON'T
❌ Give vague instructions
❌ Skip verification steps
❌ Use wrong model for task
❌ Ignore existing patterns
❌ Make untested changes
❌ Remove functionality without asking

---

## 🔄 Feedback Loop

1. **Amazon Q** → Provides task and requirements
2. **You** → Orchestrate via Continue
3. **Local Model** → Executes task
4. **You** → Verify results
5. **Amazon Q** → Reviews and approves
6. **Repeat** → Next task

---

## 📚 Resources

- **Prompts**: `.continue/prompts/orchestration_workflow.md`
- **Task Executor**: `.continue/prompts/task_executor.md`
- **Continue Docs**: `CONTINUE_LOCAL_MODELS_GUIDE.md`
- **ULTRON Patterns**: `.github/copilot-instructions.md`

---

## 🎉 Ready to Orchestrate!

**Your local models are ready to execute workflows through Continue.**

**Next**: Try the first example workflow above!

---

**Status**: ✅ ORCHESTRATION FRAMEWORK READY
**Models**: 6 local + 1 cloud configured
**Prompts**: 2 workflow prompts created
**Documentation**: Complete
