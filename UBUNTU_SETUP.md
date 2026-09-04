# ULTRON Agent 3.0 - Ubuntu Setup Guide

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the automated setup script
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh

# Activate virtual environment
source venv/bin/activate

# Start ULTRON
./run.sh
```

### Manual Setup

If you prefer manual installation:

## Prerequisites

### 1. System Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: 8GB minimum (16GB recommended for AI models)
- **Storage**: 10GB free space
- **Python**: 3.8 or higher

### 2. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install Python and build tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    curl \
    wget \
    git \
    lsof \
    portaudio19-dev
```

### 3. Install Ollama (AI Backend)

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Or start manually if systemd not available
ollama serve &
```

### 4. Download AI Model

```bash
# Pull the default model (llava:7b - 4.7GB)
ollama pull llava:7b

# Optional: Pull fallback model
ollama pull deepseek-r1:14b

# Verify models
ollama list
```

## Project Setup

### 1. Clone Repository (if not already done)

```bash
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes depending on your internet connection.

### 4. Configure Environment

```bash
# Copy config template (if exists)
cp ultron_config.json.example ultron_config.json 2>/dev/null || true

# Edit configuration
nano ultron_config.json
```

**Key Configuration Items**:
- API keys (use `USE_ENV_*` placeholders for security)
- Voice settings (if using voice features)
- Model preferences

### 5. Create Required Directories

```bash
# Create log and cache directories
mkdir -p logs cache/voice cache/web_search screenshots
```

## Running ULTRON Agent

### Method 1: Using Launch Script (Recommended)

```bash
# Make script executable
chmod +x run.sh

# Run ULTRON
./run.sh
```

This will:
- ✅ Check all dependencies
- ✅ Start Ollama if not running
- ✅ Launch Web GUI (port 8080)
- ✅ Launch API Server (port 5000)
- ✅ Open browser automatically
- ✅ Perform health checks

### Method 2: Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run main agent
python3 main.py
```

### Method 3: Individual Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Web GUI
source venv/bin/activate
python3 web_gui_server.py

# Terminal 3: Start API Server
source venv/bin/activate
python3 api_server.py
```

## Accessing the Interface

Once running, access the Web GUI at:

**🌐 http://localhost:8080**

Other endpoints:
- API Server: http://localhost:5000
- Ollama Backend: http://localhost:11434

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8080
sudo lsof -i :8080

# Kill the process if needed
sudo kill -9 <PID>

# Or use different ports in ultron_config.json
```

### Ollama Not Starting

```bash
# Check Ollama status
systemctl status ollama

# View Ollama logs
journalctl -u ollama -f

# Manual start
ollama serve
```

### Python Dependencies Issues

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Or upgrade specific packages
pip install --upgrade <package-name>
```

### Permission Issues

```bash
# Make scripts executable
chmod +x run.sh setup_ubuntu.sh

# Fix log directory permissions
chmod -R 755 logs/
```

### Missing Audio Dependencies (for voice features)

```bash
# Install PortAudio
sudo apt-get install portaudio19-dev

# Install ALSA utilities
sudo apt-get install alsa-utils

# Test audio
aplay -l
```

## Service Management

### Start Services

```bash
./run.sh
```

### Stop Services

Press `Ctrl+C` in the terminal running `run.sh`

Or manually:

```bash
# Kill all ULTRON processes
pkill -f "web_gui_server.py"
pkill -f "api_server.py"

# Optionally stop Ollama
sudo systemctl stop ollama
```

### Auto-Start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/ultron.service
```

Add:

```ini
[Unit]
Description=ULTRON Agent 3.0
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/ultron_agent
ExecStart=/path/to/ultron_agent/run.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ultron.service
sudo systemctl start ultron.service
```

## Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest --maxfail=1 --strict-markers

# Run specific test categories
pytest -m unit
pytest -m integration
```

## Logs and Debugging

### Log Locations

- **Startup Log**: `ultron.log`
- **Web GUI**: `logs/web_gui.log`
- **API Server**: `logs/api_server.log`
- **AI Activity**: `logs/ai_activities.log`
- **File Operations**: `logs/file_changes.log`

### View Live Logs

```bash
# Web GUI logs
tail -f logs/web_gui.log

# API Server logs
tail -f logs/api_server.log

# All logs
tail -f logs/*.log
```

## Environment Variables

For sensitive configuration (recommended):

```bash
# Add to ~/.bashrc or ~/.zshrc
export ELEVENLABS_APIKEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"

# Reload shell
source ~/.bashrc
```

Then in `ultron_config.json`:

```json
{
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY",
  "anthropic_api_key": "USE_ENV_ANTHROPIC_API_KEY"
}
```

## Performance Tips

### Optimize Ollama

```bash
# Use GPU acceleration (if NVIDIA GPU available)
# Install CUDA toolkit first, then:
ollama run llava:7b --gpu

# Limit CPU usage
taskset -c 0-3 ollama serve
```

### Python Virtual Environment

Always activate before running:

```bash
source venv/bin/activate
```

### Memory Management

For systems with limited RAM, use lighter models:

```bash
ollama pull tinyllama
# Update ultron_config.json to use tinyllama
```

## Uninstallation

```bash
# Stop services
./run.sh  # Then Ctrl+C

# Remove virtual environment
deactivate
rm -rf venv/

# Remove Ollama (optional)
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama

# Remove project directory
cd ..
rm -rf ultron_agent/
```

## Additional Resources

- **Documentation Hub**: See `DOCUMENTATION_HUB.md`
- **System Architecture**: See `SYSTEM_ARCHITECTURE.md`
- **Voice Setup**: See `VOICE_MICROPHONE_DOCUMENTATION.md`
- **MCP Integration**: See `MCP_INTEGRATION_GUIDE.md`

## Getting Help

1. Check logs in `logs/` directory
2. Review documentation in project root
3. Open an issue on GitHub
4. Check Ollama status: `ollama list` and `systemctl status ollama`

## Quick Reference

```bash
# Setup (one-time)
./setup_ubuntu.sh

# Daily use
source venv/bin/activate
./run.sh

# Stop
Ctrl+C

# View logs
tail -f logs/*.log

# Test
pytest
```
