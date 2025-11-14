# 🤖 Continue Extension - Local Ollama Models Guide

**Status**: ✅ CONFIGURED
**Date**: January 16, 2025

---

## 🚀 Quick Start

### Available Models (Priority Order)

1. **Qwen 2.5 Coder 7B** (PRIMARY) - Best for coding
2. **DeepSeek R1 14B** - Best for reasoning/architecture
3. **Qwen 3 Coder 480B Cloud** - Advanced coding tasks
4. **Devstral** - Specialized development
5. **Mistral Small 3.2** - Fast responses
6. **Llava 7B** - Vision/image analysis

### Keyboard Shortcuts

- `Ctrl+L` - Open Continue chat
- `Ctrl+I` - Inline edit with AI
- `Tab` - Accept autocomplete suggestion
- `Ctrl+Shift+R` - Refactor selection
- `Ctrl+Shift+L` - Explain code

---

## 💡 Usage Examples

### 1. Code Generation
```
Ctrl+L → Type: "Create a Python function to parse JSON with error handling"
Model: Qwen 2.5 Coder 7B (auto-selected)
```

### 2. Code Explanation
```
Select code → Ctrl+Shift+L
Model: DeepSeek R1 14B (reasoning)
```

### 3. Refactoring
```
Select code → Ctrl+I → Type: "Refactor to use async/await"
Model: Qwen 2.5 Coder 7B
```

### 4. Architecture Discussion
```
Ctrl+L → Type: "How should I structure this microservice?"
Model: DeepSeek R1 14B (reasoning)
```

### 5. Bug Fixing
```
Select buggy code → Ctrl+I → Type: "Fix this bug"
Model: Qwen 2.5 Coder 7B
```

---

## 🎯 Model Selection Guide

| Task | Best Model | Why |
|------|------------|-----|
| **Python/JS coding** | Qwen 2.5 Coder 7B | Optimized for code |
| **Architecture design** | DeepSeek R1 14B | Strong reasoning |
| **Complex algorithms** | Qwen 3 Coder 480B | Highest capability |
| **Quick fixes** | Mistral Small 3.2 | Fast responses |
| **Image analysis** | Llava 7B | Vision support |
| **Specialized dev** | Devstral | Dev-focused |

---

## ⚡ Autocomplete Configuration

**Model**: Qwen 2.5 Coder 1.5B (ultra-fast)
**Trigger**: Automatic as you type
**Delay**: 200ms
**Timeout**: 100ms

### Tips
- Pause typing for 200ms to trigger
- Press `Tab` to accept
- Press `Esc` to dismiss
- Works in all file types

---

## 🔧 Advanced Features

### Context Providers
- `@diff` - Git changes
- `@codebase` - Search entire project
- `@terminal` - Terminal output
- `@folder` - Specific folder
- `@file` - Specific file
- `@docs` - Documentation

### Slash Commands
- `/analyze` - Analyze ULTRON patterns
- `/test` - Generate tests
- `/docs` - Generate documentation
- `/refactor` - Refactor code

### Example with Context
```
Ctrl+L → Type: "@codebase How does the voice system work?"
Model: DeepSeek R1 14B (searches all files)
```

---

## 🎨 ULTRON-Specific Commands

### 1. Create New Tool
```
/analyze @file tools/example_tool.py
"Create a new tool following ULTRON patterns"
```

### 2. Add Logging
```
Select function → Ctrl+I
"Add centralized logging with ultron_logger"
```

### 3. Add Model Awareness
```
Select file operation → Ctrl+I
"Add model awareness check before modification"
```

### 4. Generate Tests
```
/test @file brain.py
"Generate pytest tests for this component"
```

---

## 📊 Performance Tips

### Fast Responses
- Use **Mistral Small 3.2** for quick questions
- Use **Qwen 2.5 Coder 1.5B** for autocomplete
- Keep context small with specific `@file` references

### Best Quality
- Use **DeepSeek R1 14B** for architecture
- Use **Qwen 3 Coder 480B** for complex code
- Provide full context with `@codebase`

### Balance
- Use **Qwen 2.5 Coder 7B** (default) for most tasks
- Good speed + quality balance
- 4096 token context window

---

## 🔍 Troubleshooting

### Model Not Responding
```powershell
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
Stop-Process -Name "ollama" -Force
ollama serve
```

### Slow Autocomplete
```yaml
# Edit .continue/config.yaml
tabAutocompleteOptions:
  debounceDelay: 300  # Increase delay
  modelTimeout: 200   # Increase timeout
```

### Wrong Model Selected
```
Ctrl+L → Click model dropdown → Select preferred model
```

---

## 🎯 Best Practices

### DO
✅ Use specific context (`@file`, `@folder`)
✅ Start with Qwen 2.5 Coder 7B
✅ Switch to DeepSeek R1 for reasoning
✅ Use autocomplete for repetitive code
✅ Provide clear, specific prompts

### DON'T
❌ Use `@codebase` for simple questions
❌ Use 480B model for trivial tasks
❌ Ignore autocomplete suggestions
❌ Use vision models for text tasks
❌ Provide vague prompts

---

## 📈 Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| Qwen 2.5 Coder 1.5B | 1GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Autocomplete |
| Qwen 2.5 Coder 7B | 5GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | General coding |
| DeepSeek R1 14B | 9GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Reasoning |
| Qwen 3 Coder 480B | Cloud | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks |
| Mistral Small 3.2 | 15GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Fast responses |
| Devstral | 14GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Specialized dev |

---

## 🚀 Next Steps

1. **Test Configuration**:
   ```
   Ctrl+L → Type: "Hello, test local model"
   ```

2. **Try Autocomplete**:
   - Open any Python file
   - Start typing a function
   - Wait for suggestions

3. **Use Context**:
   ```
   Ctrl+L → Type: "@codebase Explain the brain.py architecture"
   ```

4. **Switch Models**:
   - Click model dropdown in Continue chat
   - Try different models for same task
   - Find your preferred model

---

## 📞 Support

- **Continue Docs**: https://docs.continue.dev
- **Ollama Docs**: https://ollama.ai/docs
- **ULTRON Docs**: See `.github/copilot-instructions.md`

---

**Status**: ✅ READY TO USE
**Configuration**: `.continue/config.yaml`
**Models**: 6 local + 1 cloud fallback
