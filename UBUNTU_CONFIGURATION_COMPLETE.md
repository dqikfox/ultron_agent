# Ubuntu Configuration Complete ✅

## What Was Configured

Your ULTRON Agent 3.0 project is now fully configured for Ubuntu Linux!

### Files Created

1. **`run.sh`** - Main launcher script for Ubuntu
   - Automated service startup
   - Health checks for all components
   - Clean shutdown handling
   - Browser auto-launch

2. **`setup_ubuntu.sh`** - One-time setup script
   - Installs system dependencies
   - Installs Ollama AI backend
   - Downloads AI models
   - Creates virtual environment
   - Installs Python packages

3. **`verify_setup.sh`** - System verification tool
   - Checks all prerequisites
   - Verifies port availability
   - Validates configuration

4. **`UBUNTU_SETUP.md`** - Comprehensive setup guide
   - Detailed installation instructions
   - Troubleshooting section
   - Service management guide
   - Performance optimization tips

5. **`QUICKSTART_UBUNTU.md`** - Quick reference
   - One-command setup
   - Common commands
   - Daily usage patterns

### Updated Files

1. **`.github/copilot-instructions.md`**
   - Added Ubuntu-specific startup information
   - Virtual environment activation guidance
   - Cross-platform launcher documentation

2. **`README.md`**
   - Added Ubuntu quick start section
   - Links to Ubuntu documentation

## System Status

Based on verification:

✅ **Python 3.12.3** - Installed and ready
✅ **pip3** - Available
✅ **Ollama 0.13.1** - Installed and running
✅ **llava:7b model** - Downloaded (4.7GB)
✅ **Ports 8080, 5000** - Available
✅ **Configuration** - ultron_config.json exists
⚠️ **Virtual environment** - Needs to be created (run setup script)

## Next Steps

### Option 1: Quick Start (Recommended)

```bash
# Run automated setup
./setup_ubuntu.sh

# Activate virtual environment
source venv/bin/activate

# Start ULTRON
./run.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start ULTRON
./run.sh
```

## Usage

### Daily Usage Pattern

```bash
# 1. Navigate to project
cd ~/projects/ultron_agent

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start ULTRON
./run.sh

# 4. Access Web GUI
# Browser opens automatically to http://localhost:8080
```

### Stopping Services

Press `Ctrl+C` in the terminal running `./run.sh`

## Key Differences from Windows

| Aspect | Windows | Ubuntu |
|--------|---------|--------|
| **Launcher** | `run.bat` | `./run.sh` |
| **Setup** | Manual | `./setup_ubuntu.sh` |
| **Python** | `python` | `python3` |
| **Venv Activation** | `venv\Scripts\activate` | `source venv/bin/activate` |
| **Ollama Install** | MSI installer | `curl | sh` |
| **Service Management** | Task Manager | `systemctl` or `pkill` |
| **Browser Launch** | Direct | `xdg-open` |

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ULTRON Agent 3.0 (Ubuntu)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  run.sh                                                      │
│    ├── Checks dependencies                                  │
│    ├── Starts Ollama (if needed)                            │
│    ├── Launches web_gui_server.py → Port 8080               │
│    ├── Launches api_server.py → Port 5000                   │
│    └── Opens browser                                         │
│                                                              │
│  Services:                                                   │
│    • Ollama Backend (localhost:11434)                        │
│    • Web GUI (localhost:8080)                                │
│    • API Server (localhost:5000)                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

1. **"Permission denied" when running scripts**
   ```bash
   chmod +x run.sh setup_ubuntu.sh verify_setup.sh
   ```

2. **Port 8080 already in use**
   ```bash
   sudo lsof -i :8080
   sudo kill -9 <PID>
   ```

3. **Module not found errors**
   ```bash
   source venv/bin/activate  # Make sure venv is activated!
   pip install -r requirements.txt
   ```

4. **Ollama not responding**
   ```bash
   sudo systemctl restart ollama
   # Or manually: ollama serve &
   ```

### Log Locations

- **Startup**: `ultron.log`
- **Web GUI**: `logs/web_gui.log`
- **API Server**: `logs/api_server.log`
- **AI Activity**: `logs/ai_activities.log`

View live logs:
```bash
tail -f logs/*.log
```

## Documentation

- **Quick Start**: `QUICKSTART_UBUNTU.md`
- **Detailed Setup**: `UBUNTU_SETUP.md`
- **Architecture**: `SYSTEM_ARCHITECTURE.md`
- **Developer Guide**: `.github/copilot-instructions.md`

## Environment Variables (Optional)

For better security, set API keys as environment variables:

```bash
# Add to ~/.bashrc
export ELEVENLABS_APIKEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Reload
source ~/.bashrc
```

Then in `ultron_config.json`:
```json
{
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
}
```

## Performance Tips

### For Low-Memory Systems

Use a lighter model:
```bash
ollama pull tinyllama
# Update ultron_config.json: "llm_model": "tinyllama"
```

### For Better Performance

If you have an NVIDIA GPU:
```bash
# Ollama automatically uses GPU if available
nvidia-smi  # Check GPU status
```

## What's Different?

The Ubuntu configuration maintains **100% feature parity** with Windows:

- ✅ Same architecture
- ✅ Same services
- ✅ Same ports
- ✅ Same configuration
- ✅ Same capabilities

Only the launcher scripts differ to accommodate OS-specific commands.

## Getting Help

1. Run verification: `./verify_setup.sh`
2. Check logs in `logs/` directory
3. Review `UBUNTU_SETUP.md` for detailed troubleshooting
4. Ensure virtual environment is activated: `source venv/bin/activate`

---

**Ready to start?** Run `./setup_ubuntu.sh` now! 🚀
