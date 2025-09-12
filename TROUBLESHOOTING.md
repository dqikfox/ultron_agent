# ULTRON Agent Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ULTRON Agent 3.0.

## 🔍 Quick Diagnostic Tools

### Built-in Diagnostics

```bash
# Run comprehensive system check
python main.py --diagnose

# Test specific components
python main.py --test-voice
python main.py --test-api
python main.py --test-models

# Check configuration
ultron config validate

# System status
ultron system status
```

### Log Analysis

```bash
# View recent logs
tail -f logs/ultron.log
tail -f logs/error.log

# Search logs for errors
grep "ERROR" logs/ultron.log
grep "Exception" logs/error.log

# View startup logs
cat logs/startup.log
```

## 🚨 Common Issues and Solutions

### 1. Installation Issues

#### Python Version Problems

**Symptoms:**
- `SyntaxError: invalid syntax` on startup
- `ModuleNotFoundError` for built-in modules
- Type hint errors

**Solutions:**
```bash
# Check Python version (must be 3.10+)
python --version

# If version is too old, install newer Python
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Windows
# Download from python.org or use Chocolatey
choco install python

# macOS
brew install python@3.11
```

#### Dependency Installation Failures

**Symptoms:**
- `pip install` fails with compilation errors
- Missing system libraries
- `PyAudio` installation fails

**Solutions:**

**Linux:**
```bash
# Install build dependencies
sudo apt install build-essential python3-dev portaudio19-dev

# For CentOS/RHEL
sudo dnf install gcc gcc-c++ python3-devel portaudio-devel

# Reinstall problematic packages
pip uninstall pyaudio
sudo apt install python3-pyaudio
```

**Windows:**
```powershell
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or use pre-compiled wheels
pip install https://github.com/intxcc/pyaudio_portaudio/raw/master/pyaudio-0.2.11-cp311-cp311-win_amd64.whl
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install

# Install portaudio
brew install portaudio

# Reinstall pyaudio
pip uninstall pyaudio
pip install pyaudio
```

### 2. Configuration Issues

#### API Key Problems

**Symptoms:**
- `Authentication failed` errors
- `API key not found` warnings
- `Invalid API key` messages

**Solutions:**
```bash
# Check if .env file exists and has correct format
cat .env

# Verify API key format (no quotes, no spaces)
# Correct:   OPENAI_API_KEY=sk-abcd1234...
# Incorrect: OPENAI_API_KEY="sk-abcd1234..."
# Incorrect: OPENAI_API_KEY = sk-abcd1234...

# Test API key validity
ultron test api --service openai
ultron test api --service anthropic

# Regenerate API keys if needed
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/
```

#### Configuration File Errors

**Symptoms:**
- `JSON decode error` on startup
- `Configuration validation failed`
- Default settings not loading

**Solutions:**
```bash
# Validate JSON format
python -m json.tool ultron_config.json

# Reset to default configuration
cp ultron_config.json.example ultron_config.json

# Check file permissions
chmod 644 ultron_config.json

# Validate configuration
ultron config validate --verbose
```

### 3. Voice System Issues

#### Microphone Not Working

**Symptoms:**
- "No microphone detected"
- Voice commands not recognized
- Audio input errors

**Solutions:**

**Check Permissions:**
```bash
# Linux: Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again

# macOS: Check System Preferences > Security & Privacy > Microphone
# Windows: Check Settings > Privacy > Microphone
```

**Test Audio System:**
```bash
# Test microphone
ultron --test-microphone

# List audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)}') for i in range(p.get_device_count())]"

# Configure specific device
# In ultron_config.json:
{
  "voice": {
    "input_device_index": 1,  # Use device index from list above
    "sample_rate": 16000
  }
}
```

#### Text-to-Speech Problems

**Symptoms:**
- No audio output
- Robotic or garbled speech
- TTS service errors

**Solutions:**
```bash
# Test TTS engines
ultron --test-tts --engine pyttsx3
ultron --test-tts --engine elevenlabs
ultron --test-tts --engine openai

# Check system audio
# Linux
pulseaudio --check
# If not running: pulseaudio --start

# Test with different voice settings
# In ultron_config.json:
{
  "voice": {
    "text_to_speech": {
      "provider": "pyttsx3",  # Try different providers
      "rate": 150,            # Slower speech
      "volume": 0.9
    }
  }
}
```

### 4. GUI Issues

#### GUI Won't Start

**Symptoms:**
- `tkinter not found` errors
- GUI window doesn't appear
- Display-related errors

**Solutions:**

**Linux:**
```bash
# Install GUI dependencies
sudo apt install python3-tk python3-tkinter

# Check display environment
echo $DISPLAY

# For remote/headless systems
export DISPLAY=:0  # or use X11 forwarding
```

**Windows:**
```powershell
# Reinstall Python with tkinter
# Download from python.org, ensure "tcl/tk and IDLE" is selected

# Or repair installation
python -m ensurepip --upgrade
```

**macOS:**
```bash
# Install tkinter
brew install python-tk

# For macOS Big Sur and later, may need:
/Applications/Python\ 3.x/Install\ Certificates.command
```

#### GUI Performance Issues

**Symptoms:**
- Slow/laggy interface
- High CPU usage
- Memory leaks

**Solutions:**
```bash
# Reduce GUI complexity
# In ultron_config.json:
{
  "gui": {
    "theme": "light",           # Lighter theme
    "animations": false,        # Disable animations
    "update_interval": 1000,    # Slower updates
    "accessibility_mode": true  # Optimized rendering
  }
}

# Monitor resource usage
ultron --monitor-resources

# Clear GUI cache
rm -rf ~/.ultron/gui_cache/
```

### 5. API and Networking Issues

#### Connection Timeouts

**Symptoms:**
- `Request timeout` errors
- `Connection refused` messages
- Slow API responses

**Solutions:**
```bash
# Check network connectivity
ping api.openai.com
ping api.anthropic.com

# Test with increased timeouts
# In ultron_config.json:
{
  "api": {
    "timeout": 60,              # Increase from default 30
    "retry_attempts": 3,
    "retry_delay": 2
  }
}

# Check firewall settings
# Linux
sudo ufw status
# Windows
netsh advfirewall firewall show rule name=all
```

#### Rate Limiting

**Symptoms:**
- `Rate limit exceeded` errors
- `Too many requests` messages
- Temporary API blocks

**Solutions:**
```bash
# Check rate limits
ultron api status --service openai

# Configure rate limiting
# In ultron_config.json:
{
  "api": {
    "rate_limiting": {
      "requests_per_minute": 50,
      "tokens_per_minute": 40000,
      "backoff_strategy": "exponential"
    }
  }
}

# Use multiple API keys for load balancing
# In .env:
OPENAI_API_KEY_1=sk-key1...
OPENAI_API_KEY_2=sk-key2...
```

### 6. Model and AI Issues

#### Ollama Connection Problems

**Symptoms:**
- `Ollama server not responding`
- `Connection refused to localhost:11434`
- Model loading failures

**Solutions:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama service
ollama serve

# On Linux, create systemd service
sudo systemctl enable ollama
sudo systemctl start ollama

# Test model availability
ollama list
ollama run llama3.2:latest "Hello"

# Configure different host/port
# In ultron_config.json:
{
  "models": {
    "ollama": {
      "host": "http://localhost:11434",
      "timeout": 120
    }
  }
}
```

#### Model Loading Errors

**Symptoms:**
- `Model not found` errors
- GPU/CPU compatibility issues
- Out of memory errors

**Solutions:**
```bash
# Check available models
ollama list

# Download required models
ollama pull llama3.2:latest
ollama pull codellama:latest

# For GPU issues
# Check CUDA installation
nvidia-smi
# Install appropriate CUDA version

# For memory issues, use smaller models
ollama pull llama3.2:1b  # Smaller variant

# Configure model settings
# In ultron_config.json:
{
  "models": {
    "ollama": {
      "model": "llama3.2:1b",  # Use smaller model
      "context_length": 2048,  # Reduce context
      "num_gpu": 0            # Force CPU if needed
    }
  }
}
```

### 7. Performance Issues

#### High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors
- Process killed by OS

**Solutions:**
```bash
# Monitor memory usage
ultron --monitor-memory

# Clear caches
ultron cache clear

# Reduce memory usage
# In ultron_config.json:
{
  "performance": {
    "max_memory_usage": "2GB",
    "cache_size_limit": "500MB",
    "model_offload": true
  }
}

# Use swap file (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Slow Response Times

**Symptoms:**
- Long delays for responses
- Timeouts on queries
- UI freezing

**Solutions:**
```bash
# Enable performance profiling
ultron --profile

# Use local models for faster responses
# In ultron_config.json:
{
  "models": {
    "default": "ollama",     # Prefer local models
    "fallback_chain": ["ollama", "openai"]
  }
}

# Optimize caching
{
  "cache": {
    "enabled": true,
    "ttl": 3600,            # 1 hour cache
    "max_entries": 1000
  }
}

# Use SSD for cache storage
# Move cache to faster storage
mv ~/.ultron/cache /path/to/ssd/ultron_cache
ln -s /path/to/ssd/ultron_cache ~/.ultron/cache
```

## 🔧 Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Start with maximum debugging
python main.py --debug --log-level DEBUG --trace

# Debug specific components
ultron --debug-component voice
ultron --debug-component api
ultron --debug-component gui

# Generate debug report
ultron --debug-report --output debug_report.zip
```

### Log Analysis Tools

```bash
# Install log analysis tools
pip install loguru rich

# Analyze logs with patterns
python tools/log_analyzer.py --file logs/ultron.log --pattern ERROR

# Real-time log monitoring
python tools/log_monitor.py --tail --filter "voice,api"
```

### System Information Collection

```bash
# Collect system information for bug reports
ultron --system-info --output system_info.json

# Include in bug reports:
{
  "os": "Ubuntu 22.04",
  "python": "3.11.2",
  "ultron_version": "3.0.0",
  "dependencies": {...},
  "hardware": {...},
  "configuration": {...}
}
```

## 🛠 Recovery Procedures

### Configuration Recovery

```bash
# Backup current config
cp ultron_config.json ultron_config.json.backup

# Reset to defaults
cp ultron_config.json.example ultron_config.json

# Restore from backup
cp ultron_config.json.backup ultron_config.json

# Merge configurations
python tools/config_merger.py --base ultron_config.json.example --overlay ultron_config.json.backup
```

### Database Recovery

```bash
# Check database integrity
sqlite3 ultron.db ".schema"

# Backup database
cp ultron.db ultron.db.backup

# Repair database
sqlite3 ultron.db ".recover"

# Reset database (lose data)
rm ultron.db
python main.py --init-db
```

### Complete Reset

```bash
# Factory reset (keeps user data)
ultron factory-reset --keep-data

# Complete reset (removes everything)
ultron factory-reset --complete

# Manual cleanup
rm -rf ~/.ultron/
rm -rf logs/
rm ultron.db
cp ultron_config.json.example ultron_config.json
```

## 📞 Getting Help

### Information to Include in Bug Reports

1. **System Information:**
   - Operating system and version
   - Python version (`python --version`)
   - ULTRON Agent version
   - Hardware specifications

2. **Error Details:**
   - Complete error message
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/screen recordings

3. **Log Files:**
   - Recent logs (`tail -100 logs/ultron.log`)
   - Error logs (`tail -100 logs/error.log`)
   - Debug information (`python main.py --diagnose`)

4. **Configuration:**
   - Configuration file (redact API keys)
   - Environment variables (redact sensitive data)

### Community Resources

- **GitHub Issues**: [Report bugs](https://github.com/dqikfox/ultron_agent/issues)
- **Discussions**: [Ask questions](https://github.com/dqikfox/ultron_agent/discussions)
- **Documentation**: [Read guides](https://github.com/dqikfox/ultron_agent/tree/main/docs)
- **Wiki**: [Community knowledge base](https://github.com/dqikfox/ultron_agent/wiki)

### Professional Support

For enterprise users or complex issues:

- Priority support available
- Custom integration assistance
- Training and consultation services

Contact: support@ultron-agent.com

## 🔍 FAQ

### Q: ULTRON Agent starts but doesn't respond to voice commands
**A:** Check microphone permissions, test with `ultron --test-voice`, and verify wake word configuration.

### Q: Getting "No module named 'ultron_agent'" error
**A:** Install in development mode: `pip install -e .` or add project path to PYTHONPATH.

### Q: GUI is very slow or unresponsive
**A:** Try different GUI mode (`ultron --gui minimal`) or disable animations in config.

### Q: API calls are failing with authentication errors
**A:** Verify API keys in `.env` file, check key format (no quotes), and test with `ultron test api`.

### Q: High CPU usage even when idle
**A:** Check for continuous listening mode, disable unnecessary monitoring, or use local models.

### Q: Models are not loading in Ollama
**A:** Ensure Ollama service is running (`ollama serve`) and models are downloaded (`ollama pull model-name`).

---

**Still having issues? Don't hesitate to reach out for help!** 🆘

The ULTRON Agent community is here to help you succeed.