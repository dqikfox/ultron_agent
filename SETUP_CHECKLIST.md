# ULTRON Agent 3.0 - Setup Checklist

**Purpose**: Step-by-step setup guide for new installations
**Last Updated**: October 24, 2025
**Difficulty**: Beginner-Friendly

---

## Pre-Installation Requirements

### System Requirements

- [ ] **Operating System**: Windows 10/11, Linux, or macOS
- [ ] **Python**: Version 3.8 or higher
  ```powershell
  python --version
  # Expected: Python 3.8.x or higher
  ```
- [ ] **Disk Space**: Minimum 5GB free (for Ollama models)
- [ ] **RAM**: Minimum 8GB (16GB recommended for larger models)
- [ ] **Internet**: Required for API services (ElevenLabs, Ollama model downloads)

### Browser Requirements (for GUI)

- [ ] **Supported Browsers**:
  - Chrome 90+ (recommended)
  - Edge 90+
  - Safari 14+
  - Firefox 88+
- [ ] **Microphone**: Required for voice input
- [ ] **Speakers/Headphones**: Required for voice output

---

## Installation Steps

### Step 1: Install Ollama

**Purpose**: Local LLM backend for AI reasoning

**Windows**:
```powershell
# Download installer from https://ollama.ai/download
# Run installer and follow prompts
```

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify Installation**:
```powershell
ollama --version
# Expected: ollama version 0.x.x
```

- [ ] Ollama installed successfully
- [ ] Ollama version verified

---

### Step 2: Pull Required Models

**Download AI Models**:
```powershell
# Primary model (recommended)
ollama pull llava:7b

# Alternative models (optional)
ollama pull llama3.1
ollama pull deepseek-r1:14b
ollama pull qwen3-coder:480b-cloud
```

**Verify Models**:
```powershell
ollama list
# Expected: llava:7b in list
```

- [ ] `llava:7b` model downloaded
- [ ] Models verified with `ollama list`

**Note**: First pull may take 10-30 minutes depending on internet speed

---

### Step 3: Clone Repository

```powershell
# Navigate to your projects directory
cd C:\Projects

# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git

# Navigate to project
cd ultron_agent
```

- [ ] Repository cloned successfully
- [ ] Inside `ultron_agent` directory

---

### Step 4: Install Python Dependencies

```powershell
# Install required packages
pip install -r requirements.txt

# If requirements.txt is missing, install core packages:
pip install flask aiohttp SpeechRecognition pyautogui pytest asyncio
```

**Verify Installation**:
```powershell
python -c "import flask; import aiohttp; print('Dependencies OK')"
# Expected: Dependencies OK
```

- [ ] Python packages installed
- [ ] Dependencies verified

---

### Step 5: Configure Environment Variables

**Required for Voice Features**:

**Option A: PowerShell (Session-Only)**
```powershell
$env:ELEVENLABS_APIKEY = "sk-your-api-key-here"
```

**Option B: PowerShell (Persistent)**
```powershell
[System.Environment]::SetEnvironmentVariable('ELEVENLABS_APIKEY', 'sk-your-api-key', 'User')
```

**Option C: Batch File (Session-Only)**
```batch
set ELEVENLABS_APIKEY=sk-your-api-key-here
```

**Get ElevenLabs API Key**:
1. Visit https://elevenlabs.io/
2. Sign up for account (free tier available)
3. Navigate to Profile → API Keys
4. Copy your API key

**Verify Configuration**:
```powershell
echo $env:ELEVENLABS_APIKEY
# Expected: Your API key
```

- [ ] ElevenLabs API key obtained
- [ ] Environment variable set
- [ ] Variable verified

**Note**: Voice features will use local fallback (pyttsx3) if API key not set

---

### Step 6: Verify Configuration File

**Check `ultron_config.json`**:
```powershell
# Validate JSON syntax
python -c "import json; config = json.load(open('ultron_config.json')); print('Config OK')"
```

**Expected Output**: `Config OK`

**Key Settings to Review**:
```json
{
  "llm_model": "llava:7b",
  "ollama_base_url": "http://localhost:11434",
  "voice_enabled": true,
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
}
```

- [ ] `ultron_config.json` exists
- [ ] JSON syntax valid
- [ ] `llm_model` set to `llava:7b`
- [ ] `elevenlabs_api_key` uses `USE_ENV_` pattern

---

### Step 7: Test Ollama Connection

```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

**Expected Response**: JSON list of available models

- [ ] Ollama service running
- [ ] Connection successful

---

### Step 8: Run First-Time Startup

**Full System Startup**:
```powershell
.\run.bat
```

**What Happens**:
1. Starts Ollama service (if not running)
2. Runs 5 health checks:
   - Service availability
   - Model availability
   - Text generation
   - Chat API
   - Context retention
3. Starts API Server (port 5000)
4. Starts Web GUI (port 8080)
5. Opens browser automatically

**Expected Terminal Output**:
```
[TEST] Ollama Service Availability... PASSED
[TEST] Model Availability (llava:7b)... PASSED
[TEST] Text Generation Test... PASSED
[TEST] Chat API Test... PASSED
[TEST] Context Retention Test... PASSED
[TEST] Summary: Passed=5 Failed=0

Starting API Server on port 5000...
Starting Web GUI on port 8080...
Opening browser...
```

**Check Startup Logs**:
```powershell
Get-Content ultron_master_startup.log -Tail 20
```

- [ ] `run.bat` executed successfully
- [ ] All 5 health checks PASSED
- [ ] Browser opened to http://localhost:8080
- [ ] GUI loads without errors

---

### Step 9: Verify GUI Functionality

**In Browser (http://localhost:8080)**:

1. **Visual Check**:
   - [ ] Pokédex-themed interface loads
   - [ ] Start screen appears
   - [ ] Click "INITIALIZE SYSTEM" button
   - [ ] Dashboard renders

2. **Test Chat**:
   - [ ] Type message in input: "Hello ULTRON"
   - [ ] Click Send or press Enter
   - [ ] Response appears in chat window

3. **Test Voice (Optional)**:
   - [ ] Click microphone button
   - [ ] Browser prompts for microphone permission
   - [ ] Allow microphone access
   - [ ] Microphone icon turns green
   - [ ] Say "Hello ULTRON"
   - [ ] Transcript appears in chat
   - [ ] Response is spoken aloud

4. **Footer Status**:
   - [ ] Footer appears at bottom of page
   - [ ] Shows system status indicators
   - [ ] All services show "operational"

---

## Troubleshooting Common Issues

### Issue 1: "Port 8080 already in use"

**Solution**:
```powershell
# Find process using port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# Kill the process
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force

# Restart
.\run.bat
```

---

### Issue 2: "Chat backend unavailable"

**Symptoms**: Error message in GUI about backend unavailable

**Solution**:
```powershell
# 1. Check Ollama is running
curl http://localhost:11434/api/tags

# 2. If not responding, restart Ollama
Stop-Process -Name "ollama" -Force
ollama serve

# 3. Verify model loaded
ollama list | findstr "llava"

# 4. Test generation
curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d "{\"model\": \"llava:7b\", \"prompt\": \"test\", \"stream\": false}"

# 5. Restart services
.\run.bat
```

---

### Issue 3: Voice Not Working

**Solution**:
1. Check API key set: `echo $env:ELEVENLABS_APIKEY`
2. Verify browser microphone permissions
3. Check voice.py logs: `Get-Content logs\voice.log -Tail 50`
4. Test fallback: Voice should work with local TTS even without API key

**See**: `VOICE_MICROPHONE_DOCUMENTATION.md` for complete troubleshooting

---

### Issue 4: Health Checks Fail

**If any health check fails during `run.bat`**:

**Check Logs**:
```powershell
Get-Content ultron_master_startup.log
```

**Common Causes**:
- Model not downloaded: `ollama pull llava:7b`
- Ollama not running: `ollama serve`
- Network timeout: Increase timeout in `run.bat`
- Insufficient memory: Close other applications

---

## Post-Installation Verification

### Verify All Services Running

```powershell
# Check Ollama
curl http://localhost:11434/api/tags

# Check API Server
curl http://localhost:5000/health

# Check Web GUI
curl http://localhost:8080

# Check all Python processes
Get-Process python
```

- [ ] Ollama responding on port 11434
- [ ] API Server responding on port 5000
- [ ] Web GUI accessible on port 8080
- [ ] Python processes running

---

### Verify Logs Created

```powershell
# List all log files
Get-ChildItem logs\*.log

# Expected logs:
# - agent_core.log
# - brain.log
# - voice.log
# - ai_activities.log
# - file_changes.log
```

- [ ] Log directory exists
- [ ] Log files created

---

## Development Mode (Alternative Startup)

**For Development Without Web GUI**:

```powershell
# Start only the agent core
python main.py
```

**What This Does**:
- Initializes agent core
- No web services
- Command-line interface only
- Useful for debugging

- [ ] `main.py` runs successfully
- [ ] Command prompt appears

---

## Optional Setup

### VS Code Tasks

**Configure Tasks** (`.vscode/tasks.json` already exists):

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Ollama Service",
      "type": "shell",
      "command": "ollama serve"
    },
    {
      "label": "Run Ultron Assistant",
      "type": "shell",
      "command": "python ultron_assistant.py"
    }
  ]
}
```

**Run Tasks**:
- Press `Ctrl+Shift+P`
- Type "Run Task"
- Select task from list

- [ ] VS Code tasks configured
- [ ] Tasks tested

---

### Testing Framework

**Run Tests**:
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test category
pytest -m unit
```

- [ ] Tests run successfully
- [ ] No critical failures

---

## Next Steps

After successful installation:

1. **Read Documentation**:
   - [ ] `.github/copilot-instructions.md` - Developer guide
   - [ ] `VOICE_MICROPHONE_DOCUMENTATION.md` - Voice system details
   - [ ] `SYSTEM_ARCHITECTURE.md` - System architecture
   - [ ] `FIXES_SUMMARY_2025-10-24.md` - Recent fixes

2. **Customize Configuration**:
   - [ ] Review `ultron_config.json` settings
   - [ ] Set preferred AI model
   - [ ] Configure voice preferences

3. **Explore Tools**:
   - [ ] Check `tools/` directory
   - [ ] Review available tools
   - [ ] Add custom tools if needed

4. **Join Community** (if applicable):
   - [ ] GitHub issues for support
   - [ ] Contribute improvements

---

## Quick Reference

**Start System**:
```powershell
.\run.bat
```

**Stop System**:
```powershell
# Press Ctrl+C in terminal
# Or kill all processes:
Get-Process python,ollama,ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
```

**View Logs**:
```powershell
Get-Content ultron_master_startup.log -Tail 50
Get-Content logs\agent_core.log -Tail 50
```

**Test Voice**:
- Click microphone button in GUI
- Grant browser permissions
- Speak command
- Verify response

---

## Support

**If you encounter issues**:

1. Check logs: `logs/*.log`
2. Review startup log: `ultron_master_startup.log`
3. See troubleshooting docs:
   - `VOICE_MICROPHONE_DOCUMENTATION.md`
   - `SYSTEM_ARCHITECTURE.md`
4. GitHub issues: https://github.com/dqikfox/ultron_agent/issues

---

**End of Setup Checklist**

✅ = Task complete
⏸️ = Optional task
❌ = Failed (see troubleshooting)
