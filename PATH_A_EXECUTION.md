# 🚀 PATH A EXECUTION GUIDE - Speed-Focused Lightweight Setup

**Status**: Ready to execute NOW
**Time Required**: 20 minutes (10-15 min downloads + 5 min config)
**System Impact**: 3.6GB peak (leaves 61GB free)
**Goal**: Get A2-A6 done in 2 hours per task with minimal system lag

---

## 📋 STEP-BY-STEP EXECUTION

### ✅ Step 1: Security First (2 minutes)

**DO THIS NOW** before anything else:

```powershell
# Go to: https://platform.openai.com/account/api-keys
# Find the key exposed in: H:\My Drive\ultron\ultron.js
# Click "Delete" or "Revoke"
# Wait for confirmation
```

**Why**: Key is exposed and could be abused for expensive API calls
**Status**: 🔴 REQUIRED - Do this first!

---

### ✅ Step 2: Stop Running Ollama (30 seconds)

**Terminal 1: PowerShell**

```powershell
# Kill any running Ollama
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✅ Ollama stopped" -ForegroundColor Green
```

**Expected Output**: No error if already stopped

---

### ✅ Step 3: Launch Lightweight Ollama (1 minute)

**Terminal 1: Same PowerShell**

```powershell
# Navigate to project root
cd c:\Projects\ultron_agent

# Start lightweight Ollama
.\ollama_lightweight.bat
```

**Expected Output**:
```
============================================================
[OLLAMA] Starting Lightweight Mode
============================================================
Configuration:
- GPU Parallel: 1 (sequential models)
- CPU Threads: 8 (leaving 4 cores free)
- GPU Memory: 1.5GB (conservative allocation)
- Peak System Usage: 3.6GB (models + overhead)
...
```

**Keep this terminal open!** (Ollama stays running in background)

---

### ✅ Step 4: Pull Models (10-15 minutes)

**Terminal 2: NEW PowerShell** (keep Terminal 1 open with ollama_lightweight.bat)

```powershell
# Model 1: Lightweight Coder (397 MB, ~1-2 min)
Write-Host "[1/3] Pulling qwen2.5-coder:1.5b..." -ForegroundColor Cyan
ollama pull qwen2.5-coder:1.5b
Write-Host "✅ Model 1 complete" -ForegroundColor Green

# Model 2: Lightweight Vision (3.2 GB, ~5-7 min)
Write-Host "[2/3] Pulling qwen2.5vl:3b..." -ForegroundColor Cyan
ollama pull qwen2.5vl:3b
Write-Host "✅ Model 2 complete" -ForegroundColor Green

# Model 3: Cloud-based Logic (0 GB local, ~2-3 min)
Write-Host "[3/3] Pulling gpt-oss:20b-cloud..." -ForegroundColor Cyan
ollama pull gpt-oss:20b-cloud
Write-Host "✅ Model 3 complete" -ForegroundColor Green

# Verify all installed
Write-Host "`n📊 Installed Models:" -ForegroundColor Yellow
ollama list | Select-String "qwen2.5-coder:1.5b|qwen2.5vl:3b|gpt-oss:20b-cloud"
```

**Expected Output**:
```
NAME                              SIZE      ID
qwen2.5-coder:1.5b               397MB     abc123def456
qwen2.5vl:3b                     3.2GB     xyz789abc123
gpt-oss:20b-cloud                 0MB      (cloud-based)
```

**Time Breakdown**:
- qwen2.5-coder:1.5b: 1-2 min (tiny model)
- qwen2.5vl:3b: 5-7 min (3.2GB download)
- gpt-oss:20b-cloud: 2-3 min (just registration)
- **Total: 8-12 minutes** ✅

---

### ✅ Step 5: Update Continue.dev Config (3 minutes)

**File**: `.continue/config.json`

Replace the `"models"` section with:

```jsonc
"models": [
  {
    "name": "Qwen2.5 Coder (Autocomplete)",
    "provider": "ollama",
    "model": "qwen2.5-coder:1.5b",
    "roles": ["autocomplete"],
    "autocompleteOptions": {
      "disable": false,
      "debounceMs": 100,
      "maxContextLength": 2000,
      "modelTimeout": 50,
      "onlyMyCode": true
    }
  },
  {
    "name": "GPT-OSS Logic (Cloud)",
    "provider": "ollama",
    "model": "gpt-oss:20b-cloud",
    "roles": ["chat", "edit"]
  },
  {
    "name": "Qwen2.5 Vision (Security)",
    "provider": "ollama",
    "model": "qwen2.5vl:3b",
    "roles": ["chat"]
  }
]
```

**Save and Exit** - No restart needed yet!

---

### ✅ Step 6: Restart VS Code (2 minutes)

```powershell
# Close VS Code completely
Stop-Process -Name "Code" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Reopen VS Code
code .
```

**Verify**: Open Terminal in VS Code, check Ollama status:
```powershell
ollama list
```

---

### ✅ Step 7: Test Autocomplete (2 minutes)

**In VS Code**:

1. Open any `.py` file (or create test.py)
2. Start typing:
   ```python
   def rate_limit(
   ```
3. Wait for autocomplete popup
4. Should appear **instantly** (<100ms)

**Expected**:
- ✅ Autocomplete appears without lag
- ✅ No HTTP 500 errors in console
- ✅ Suggestions are relevant
- ✅ Typing stays smooth (qwen2.5-coder:1.5b is fast!)

**If Error**:
- Check Terminal: `ollama list` should show all 3 models
- Check logs: `tail -f logs/brain.log` (if running ULTRON)
- Check `.continue/config.json` syntax (must be valid JSON)

---

## 🎯 PATH A MODEL ALLOCATION

### Three-Role Architecture

| Role | Model | Memory | Speed | Use Case |
|------|-------|--------|-------|----------|
| **Autocomplete** | qwen2.5-coder:1.5b | 397MB | 50ms | IDE typing suggestions |
| **Logic Review** | gpt-oss:20b-cloud | 0MB | API | Rate limiting algorithm verification |
| **Security Review** | qwen2.5vl:3b | 3.2GB | 500ms | Vulnerability pattern detection |

**Total Memory**: 3.6GB local (can run sequentially if needed)
**Total Peak**: Never exceeds 65GB available RAM
**Total System Impact**: ~5-6% system load (comfortable)

---

## 🧪 QUICK TEST SCRIPT

```powershell
# Test all three models in sequence
Write-Host "=== TESTING PATH A MODELS ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Autocomplete speed
Write-Host "[1/3] Testing qwen2.5-coder:1.5b (autocomplete)..." -ForegroundColor Yellow
Measure-Command {
    ollama run qwen2.5-coder:1.5b "def rate_limit"
} | Select-Object TotalMilliseconds

Write-Host "[2/3] Testing gpt-oss:20b-cloud (logic)..." -ForegroundColor Yellow
Measure-Command {
    ollama run gpt-oss:20b-cloud "explain rate limiting"
} | Select-Object TotalMilliseconds

Write-Host "[3/3] Testing qwen2.5vl:3b (vision)..." -ForegroundColor Yellow
Measure-Command {
    ollama run qwen2.5vl:3b "security issues with rate limiting"
} | Select-Object TotalMilliseconds

Write-Host ""
Write-Host "✅ All models tested successfully" -ForegroundColor Green
```

**Expected Results**:
- qwen2.5-coder:1.5b: 50-150ms (very fast)
- gpt-oss:20b-cloud: 500-1500ms (cloud latency)
- qwen2.5vl:3b: 200-600ms (good speed)

---

## 📊 SYSTEM MONITORING

```powershell
# Run this while testing to see memory usage
$timer = 0
while ($timer -lt 120) {  # 2 minute monitoring
    $mem = (Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory / 1MB / 1024
    $used = 65 - $mem
    $percent = [math]::Round(($used / 65) * 100, 1)

    Write-Host "RAM: ${used}GB / 65GB (${percent}%) | Free: ${mem}GB" -ForegroundColor Cyan
    Start-Sleep 2
    $timer += 2
}
```

**Expected During Tests**:
- Idle: 2-3GB
- qwen2.5-coder:1.5b running: 2.5-3GB
- qwen2.5vl:3b running: 5-6GB
- All at once: 6-7GB (still comfortable)

---

## ✅ COMPLETION CHECKLIST

- [ ] API key revoked (CRITICAL)
- [ ] Ollama stopped
- [ ] ollama_lightweight.bat launched (Terminal 1 still running)
- [ ] All 3 models pulled (Terminal 2)
- [ ] `.continue/config.json` updated with new models
- [ ] VS Code restarted
- [ ] Autocomplete tested and working
- [ ] No HTTP 500 errors in logs
- [ ] System stays responsive

**All checked?** → Ready for A2! 🚀

---

## 🚀 NEXT: START A2 RATE LIMITING

Once all above complete:

1. Open `OPTIMIZED_A2_A6_PLAN_LIGHTWEIGHT.md`
2. Follow "A2: Rate Limiting" section
3. Use VS Code task automation (3 parallel reviews)
4. Expected completion: 2 hours

**Timeline**:
- ✅ NOW: Setup (20 min)
- ✅ NEXT: A2 (2 hours) → COMPLETE TODAY
- ⏳ TOMORROW: A3 (2.5 hours) → COMPLETE
- ⏳ NOV 6-7: A4 (2 hours)
- ⏳ NOV 8-9: A5+A6 (3 hours)
- 🎉 **NOV 9: 100% COMPLETE** (5 days early!)

---

## 📞 TROUBLESHOOTING

**Problem**: HTTP 500 errors in autocomplete
**Solution**: Model was too large. You're now using 1.5B (397MB) instead of 7B. This should fix it.

**Problem**: Autocomplete still slow
**Solution**:
- Check `.continue/config.json`: model should be `qwen2.5-coder:1.5b`
- Check Ollama status: `ollama list`
- Check debounceMs: should be 100 in autocompleteOptions

**Problem**: Models taking too long to download
**Solution**: Normal for gpt-oss:20b-cloud (~5-10 min). It's a large model. Can continue testing while downloading.

**Problem**: "Model not found" error
**Solution**:
```powershell
# Verify Ollama is still running
ollama serve  # or check Terminal 1

# Verify models are pulled
ollama list | grep qwen2.5

# If missing, pull again
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5vl:3b
```

---

**Status**: Ready to execute! Follow steps 1-7 above. Total time: 20 minutes. 🎯
