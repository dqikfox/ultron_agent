# ⚡ VS Code Task Automation - Quick Cheat Sheet

## 🎯 The Three Ways to Run Tasks

### 1️⃣ COMMAND PALETTE (Most Common)
```
Ctrl + Shift + P
→ type "Tasks"
→ select "Tasks: Run Task"
→ pick your task
→ Watch it execute
```

### 2️⃣ KEYBOARD SHORTCUTS (Fastest)
```
Ctrl + Shift + B  = Run Default Build Task
Ctrl + Shift + T  = Run Default Test Task
```

### 3️⃣ TERMINAL / STATUS BAR
```
Bottom-left corner → Click terminal icon
→ Select task from dropdown
```

---

## 📋 Available Tasks (Just Press Ctrl+Shift+P)

| Task | Command | Time | Memory | Use When |
|------|---------|------|--------|----------|
| 🚀 **Test Ollama Models** | `ollama ls` | 1s | None | Verify models available |
| ⚡ **Syntax Check** | qwen2.5-coder:1.5b | 50ms | 397MB | Quick code check |
| 🔍 **Logic Verify** | gpt-oss:20b-cloud | 1-2s | ☁️ Cloud | Algorithm check |
| 🛡️ **Security Review** | qwen2.5vl:3b | 200ms | 3.2GB | Security patterns |
| ✅ **Run Pytest** | `pytest tests/` | Variable | Low | Run all tests |
| 🌐 **Start Web GUI** | `web_gui_server.py` | - | Low | Open GUI |
| 📡 **Start API** | `api_server.py` | - | Low | Start API |

---

## 🔥 For A2-A6 Workflow

### Quick Workflow
```
1. Amazon Q creates template (30 min) → saves A2_TEMPLATE.py
2. You press: Ctrl+Shift+P → "Syntax Check" (50ms)
3. You press: Ctrl+Shift+P → "Logic Verify" (1-2s)
4. You press: Ctrl+Shift+P → "Security Review" (200ms)
5. Review merged report (5 min)
6. You press: Ctrl+Shift+T → pytest (Variable)
7. All tests pass ✅ → A2 DONE

Total: ~2-3 hours (vs 3-4 hours sequential)
```

---

## 💡 Lightest Possible Review (Ultra-Minimalist)

If you want the ABSOLUTE LIGHTEST approach:

```
Task 1: Syntax Only
  Model: qwen2.5-coder:1.5b (397 MB)
  Time: ~50ms
  Memory: Minimal
  Use: Quick validation
```

**This takes 1 minute and uses almost no resources.**

---

## 📊 Resource Comparison

### What We Optimized For You

| Approach | Memory Peak | Time/Task | Notes |
|----------|------------|-----------|-------|
| Original | 10+ GB | 3-4 hours | Slow, heavy |
| **Lightweight ✅** | **3.6 GB** | **2 hours** | Balanced |
| **Ultra-Light** | **397 MB** | **1-2 min** | Syntax only |

---

## 🚀 Pro Tips

### Custom Keyboard Shortcuts
Add to `.vscode/keybindings.json`:
```json
[
  {
    "key": "ctrl+alt+1",
    "command": "workbench.action.tasks.runTask",
    "args": "⚡ Quick Syntax Check (qwen2.5-coder:1.5b)"
  },
  {
    "key": "ctrl+alt+2",
    "command": "workbench.action.tasks.runTask",
    "args": "🛡️ Security Review (qwen2.5vl:3b)"
  }
]
```

Then: `Ctrl+Alt+1` = Instant syntax check

### Run on File Save
Install "Run on Save" extension, then:
```json
{
  "runOnSave.commands": [
    {
      "match": ".*_TEMPLATE\\.py$",
      "command": "bash ./scripts/run_lightweight_reviews.ps1"
    }
  ]
}
```

Auto-runs review every time you save template

---

## 🔍 Finding Tasks

**Lost? Here's how to find any task:**

```
Ctrl+Shift+P → type "task"
Shows:
  - Tasks: Run Task
  - Tasks: Run Build Task
  - Tasks: Run Test Task
  - Tasks: Terminate Task
  - Tasks: Show Running Tasks
```

---

## ⚡ Ultra-Fast Workflow

### For People Who Want SPEED

```
1. Save your Python file
2. Ctrl+Alt+1 (syntax check)
3. Ctrl+Alt+2 (security review)
4. Done in 1 minute ✅
```

Using only **qwen2.5-coder:1.5b** + **qwen2.5vl:3b**
Total memory: **3.6 GB peak**
Time: **~1 minute**

---

## 🆘 Troubleshooting

**Q: Task doesn't appear?**
```
Ctrl+Shift+P → "Reload Window" → Reload
```

**Q: Task fails to run?**
```
Make sure: Ctrl+Shift+P → "Test Ollama Models" first
If that fails: Ollama not running
```

**Q: Want to see task output?**
```
View → Terminal (Ctrl+`)
Or click terminal icon in status bar
```

**Q: Can I run multiple tasks?**
```
Yes! Use "dependsOn" in tasks.json
Or run them one after another manually
```

---

## 📖 Full Documentation

For complete setup details, see: `VS_CODE_TASKS_SETUP.md`

For workflow details, see: `OPTIMIZED_A2_A6_PLAN_LIGHTWEIGHT.md`

---

## ✨ TL;DR (Too Long; Didn't Read)

```
Press: Ctrl + Shift + P
Type: Tasks
Pick: Any task
Done ✅

Default shortcuts:
  Ctrl+Shift+B = Build/Run
  Ctrl+Shift+T = Test

That's it! 🚀
```

---

*Cheat sheet for hands-free VS Code automation*
*Generated: November 4, 2025*
