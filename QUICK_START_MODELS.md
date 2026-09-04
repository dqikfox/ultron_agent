# 🚀 QUICK START: Install Upgraded Models (5 Minutes)

**Your System**: 65GB RAM + NVIDIA RTX 3050
**Goal**: Get better models running TODAY
**Time**: 5-10 minutes total

---

## Step 1: Stop Current Ollama (30 seconds)

```powershell
# PowerShell - Kill Ollama process
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
```

---

## Step 2: Start Optimized Ollama (2 minutes)

```powershell
# Create ollama_optimized.bat in your project root
# Copy this:

@echo off
REM Optimized Ollama startup for RTX 3050 + 65GB RAM
setlocal enabledelayedexpansion

REM Use both GPU and CPU cores
set OLLAMA_NUM_PARALLEL=2
set OLLAMA_NUM_THREAD=12
set OLLAMA_GPU_MEMORY=3964000000

REM Start Ollama
echo [Ollama] Starting with optimizations...
echo [Ollama] GPU Parallel: 2, CPU Threads: 12, GPU Memory: 3.96GB
ollama serve

pause
```

Then run it:
```powershell
.\ollama_optimized.bat
```

---

## Step 3: Pull Recommended Models (3-5 minutes)

**Open a NEW PowerShell window** (keep ollama_optimized.bat running):

```powershell
# Pull each model one at a time
echo "[1/4] Installing Mistral (general chat)..."
ollama pull mistral:latest

echo "[2/4] Installing DeepSeek Coder (code generation)..."
ollama pull deepseek-coder:33b-instruct

echo "[3/4] Installing DeepSeek R1 (reasoning)..."
ollama pull deepseek-r1:8b

echo "[4/4] Installing Qwen2.5 Coder (already done?)..."
ollama pull qwen2.5-coder:7b

echo "[DONE] All models installed!"
ollama list
```

**Install times**:
- Mistral: ~2 min (4.1GB)
- DeepSeek Coder: ~5 min (20GB)
- DeepSeek R1: ~2 min (4.8GB)
- Qwen: ~1 min (already have it)
- **Total: ~10 minutes** (can run while you do other things)

---

## Step 4: Verify Installation (1 minute)

```powershell
# Should show all 4 models
ollama list

# Should output:
# NAME                              SIZE      ID
# mistral:latest                    4.1GB     2ae6f3fb8b23
# deepseek-coder:33b-instruct      20GB      7e7c8e8e8e8e
# deepseek-r1:8b                    4.8GB     a1a1a1a1a1a1
# qwen2.5-coder:7b                  4.7GB     b2b2b2b2b2b2
```

---

## Step 5: Update Continue.dev Config (1 minute)

Edit `.continue/config.json`:

Replace the models section with:

```jsonc
"models": [
  {
    "name": "Mistral (Chat)",
    "provider": "ollama",
    "model": "mistral:latest",
    "roles": ["chat"]
  },
  {
    "name": "DeepSeek Coder (Code Gen)",
    "provider": "ollama",
    "model": "deepseek-coder:33b-instruct",
    "roles": ["chat", "edit"]
  },
  {
    "name": "DeepSeek R1 (Reasoning)",
    "provider": "ollama",
    "model": "deepseek-r1:8b",
    "roles": ["chat"]
  },
  {
    "name": "Qwen2.5 Coder (Autocomplete)",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b",
    "roles": ["autocomplete"],
    "autocompleteOptions": {
      "disable": false,
      "modelTimeout": 200
    }
  }
]
```

Then restart VS Code.

---

## ✅ You're Done!

Now you can:

1. **Use Continue.dev** with much better models
2. **Run parallel code reviews** (3 models simultaneously)
3. **Complete A2-A6 tasks** in half the time
4. **Switch between models** with `/model` command in Continue.dev

---

## 🧪 Quick Test

In VS Code, open Continue.dev and try:

```
/model mistral
"Explain how rate limiting works in Python"

# Then:
/model deepseek-coder:33b-instruct
"Generate a rate limiting decorator"

# Then:
/model deepseek-r1:8b
"What security issues could this have?"
```

Each model will give you different perspectives on the same problem.

---

## 📊 Memory Usage

Monitor your system while running:

```powershell
# PowerShell script to monitor
while($true) {
  $mem = (Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory/1MB/1024
  $used = 65 - $mem
  Write-Host "RAM: ${used}GB / 65GB used | Free: ${mem}GB" -ForegroundColor Cyan
  Start-Sleep 2
}
```

**Expected**:
- Idle: ~5GB used
- 1 model running: ~20-25GB used
- 2 models running: ~35-45GB used
- 3 models running: ~55-65GB used

---

## ⚡ Performance Tips

1. **Autocomplete is instant** - Use qwen2.5-coder:7b (already configured)
2. **Code generation** - Switch to deepseek-coder:33b (chat command or config)
3. **Complex logic** - Use deepseek-r1:8b for reasoning
4. **Batch heavy tasks** - Run during off-peak times if needed

---

## 📚 See Also

- `MODEL_OPTIMIZATION_65GB_RTX3050.md` - Full optimization guide
- `EXECUTIVE_SUMMARY_AMAZON_Q.md` - A2-A6 workflow
- `.continue/config.json` - Your configuration

---

**Status**: Ready to upgrade 🚀
**Next Step**: Run `ollama pull mistral:latest` in 30 seconds
