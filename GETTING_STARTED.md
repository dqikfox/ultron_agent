# Getting Started with ULTRON Agent 3.0

## Prerequisites

### Required
- **Python 3.8+**: Core runtime environment
- **Ollama**: Local LLM backend for AI capabilities
  - Download: https://ollama.ai/download
  - Or install via: `winget install Ollama.Ollama`
- **Git**: Version control

### Optional
- **Node.js >= 18.x**: For frontend development (if modifying GUI)
- **VS Code**: Recommended IDE with AI extensions
- **FFmpeg**: For voice/audio features
- **Tesseract OCR**: For vision/text extraction features

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent
```

### Step 2: Install Python Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or using conda (if preferred)
conda create -n ultron python=3.10
conda activate ultron
pip install -r requirements.txt
```

### Step 3: Install Ollama
```bash
# Windows (PowerShell)
winget install Ollama.Ollama

# Or download installer from https://ollama.ai/download
```

### Step 4: Pull AI Model
```bash
# Pull the default model (llava:7b - multimodal, vision-enabled)
ollama pull llava:7b

# Or pull alternative models
ollama pull llama3.1
ollama pull qwen3-coder:480b-cloud
```

## Configuration

### Basic Configuration

1. **Copy Configuration Template** (if exists):
   ```bash
   cp ultron_config.json.example ultron_config.json
   ```

2. **Edit Configuration** (`ultron_config.json`):
   ```json
   {
     "llm_model": "llava:7b",
     "ollama_base_url": "http://localhost:11434",
     "voice_enabled": false,
     "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
   }
   ```

3. **Set Environment Variables** (for API keys):
   ```powershell
   # Windows PowerShell
   $env:ELEVENLABS_APIKEY = "your-key-here"
   $env:OPENAI_API_KEY = "your-key-here"  # If using OpenAI fallback

   # Or add to system environment variables permanently
   ```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `llm_model` | `dolphin3:latest` | Primary AI model to use |
| `ollama_base_url` | `http://localhost:11434` | Ollama service endpoint |
| `voice_enabled` | `false` | Enable voice features |
| `elevenlabs_api_key` | `USE_ENV_ELEVENLABS_APIKEY` | ElevenLabs API key (optional) |
| `web_gui_port` | `8080` | Web GUI server port |
| `frontend_port` | `5175` | Frontend UI port |

## Running ULTRON Agent

### Recommended: Master Launcher (with Health Checks)

```bash
# Windows
.\run.bat

# This performs:
# 1. Process cleanup (kills old instances)
# 2. Pre-flight checks (files, Python, etc.)
# 3. Ollama service startup/verification
# 4. 5 automated health tests
# 5. Web GUI & Frontend UI launch
```


**What the Health Checks Do**:
- ✅ Test 1: Service availability (Ollama responding)
- ✅ Test 2: Model availability (dolphin3:latest loaded)
- ✅ Test 3: Text generation (basic inference)
- ✅ Test 4: Chat API (conversational interface)
- ✅ Test 5: Context retention (multi-turn memory)

If any test fails, you'll see:
```
[WARN] ⚠️  Some tests failed. System may not work correctly.
[PROMPT] Press Y to continue anyway, or any other key to exit...
```

### Alternative: Development Mode (No Health Checks)

```bash
# Minimal startup
python main.py

# Web GUI only
python web_gui_server.py

# Frontend UI only
python frontend_server.py --port 5175
```

### Standalone Health Tests

```bash
# Run comprehensive tests manually
.\test_ollama_communication.ps1

# Expected output:
# [TEST 1/5] Checking Ollama service availability...
# [SUCCESS] ✅ Test 1 PASSED - Ollama service responding
# ... (5 tests total)
# [TEST SUMMARY] Tests Passed: 5/5 | Tests Failed: 0/5
```

## Accessing the Interfaces

### Web Interfaces

1. **Primary Web GUI** (Pokédex-style retro interface):
   - URL: http://localhost:8080
   - Features: Console, System Monitor, Vision, Tasks, Files, Settings
   - Technology: HTML5 + CSS3 + JavaScript

2. **Frontend UI** (Modern interface):
   - URL: http://localhost:5175
   - Features: Chat, Status monitoring
   - Technology: Python Flask

3. **Mobile Web Interface** (Responsive):
   - URL: http://localhost:8001
   - Launch: `python tools/mobile_web_interface_tool.py`
   - Features: Command execution, mobile-optimized UI

### API Endpoints

- **Ollama Backend**: http://localhost:11434
- **API Server**: http://localhost:5000 (when `api_server.py` is running)

## First Steps After Installation

### 1. Verify Installation
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check model is available
ollama list | findstr "llava"

# Check Python packages
pip list | findstr "flask\|aiohttp\|pytest"
```

### 2. Run Health Checks
```bash
.\test_ollama_communication.ps1
```

### 3. Start the System
```bash
.\run.bat
```

### 4. Open Web GUI
- Navigate to http://localhost:8080
- Try sending a message: "Hello, who are you?"
- Check system status in the GUI

### 5. Review Logs
```bash
# Startup log with test results
Get-Content ultron_master_startup.log -Tail 50

# AI activity log
Get-Content logs\ai_activities.log -Tail 20

# Brain (AI reasoning) log
Get-Content logs\brain.log -Tail 20
```

## Common Issues & Solutions

### Issue: "Ollama service not responding"
**Solution**:
```bash
# Restart Ollama
Stop-Process -Name "ollama" -Force
ollama serve

# Or let run.bat handle it
.\run.bat
```

### Issue: "Model not found"
**Solution**:
```bash
ollama pull llava:7b
```

### Issue: "Port already in use"
**Solution**: `run.bat` now handles this automatically by killing conflicting processes. If issues persist:
```bash
# Check what's using the port
Get-NetTCPConnection -LocalPort 8080

# Kill specific process
Stop-Process -Id <PID> -Force
```

### Issue: Health tests failing
**Solution**: Check `ultron_master_startup.log` for details:
```bash
Get-Content ultron_master_startup.log | Select-String "TEST|FAIL"
```

Refer to `STARTUP_HEALTH_CHECKS.md` for detailed troubleshooting.

## Next Steps

1. **Explore Documentation**:
   - `README.md` - Full feature overview
   - `STARTUP_HEALTH_CHECKS.md` - Health check system details
   - `.github/copilot-instructions.md` - Developer guidelines
   - `COMPONENT_SPECIFICATIONS.md` - Technical specifications

2. **Try Features**:
   - Send chat messages through Web GUI
   - Upload files for AI analysis
   - Test voice features (if configured)
   - Explore tool ecosystem in `tools/` directory

3. **Customize**:
   - Modify `ultron_config.json` for your preferences
   - Add custom tools in `tools/` directory
   - Customize GUI in `gui/ultron_enhanced/web/`

4. **Development**:
   - Read `DEVELOPMENT.md` for contribution guidelines
   - Check `tests/` directory for testing framework
   - Use VS Code with AI extensions for enhanced development

## Quick Reference Commands

```bash
# Start system (recommended)
.\run.bat

# Run tests
.\test_ollama_communication.ps1

# Check logs
Get-Content ultron_master_startup.log -Tail 50

# Restart Ollama
Stop-Process -Name "ollama" -Force; ollama serve

# Check services
Get-NetTCPConnection -LocalPort 8080,5175,11434 | Format-Table -AutoSize

# Pull new model
ollama pull <model-name>

# Switch model (edit config)
# Edit ultron_config.json -> "llm_model": "new-model"
```

## Getting Help

- 📖 **Documentation**: Check `docs/` folder
- 🐛 **Issues**: GitHub Issues (if public repo)
- 💬 **Logs**: `logs/` directory for debugging
- 🔍 **Health Checks**: `ultron_master_startup.log` for startup diagnostics

---

**You're now ready to use ULTRON Agent! 🚀**
