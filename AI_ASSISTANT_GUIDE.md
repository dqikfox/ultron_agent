# 🤖 ULTRON AI Assistant - Complete Guide

## Overview

ULTRON AI Assistant is an advanced, voice-enabled AI system that can interact with your Ubuntu system through:

- ✅ **Voice Chat** - Speak naturally and get spoken responses
- ✅ **File System Access** - Read, write, and manage files safely
- ✅ **Command Execution** - Run terminal commands with safety checks
- ✅ **AI Reasoning** - Powered by Ollama LLM (llava:7b)
- ✅ **Natural Language** - Conversational interaction

## Quick Start

### Text Mode (Easiest)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the assistant
python3 ultron_ai_assistant.py
```

### Voice Mode (Requires microphone)

```bash
# Install audio dependencies first
sudo apt-get install portaudio19-dev python3-pyaudio

# Reinstall voice packages
pip install pyaudio SpeechRecognition pyttsx3

# Run with voice
python3 ultron_ai_assistant.py --voice
```

## Features & Commands

### 1. File System Operations

**Read Files:**
```
You: read file ultron_config.json
ULTRON: [Shows file contents]

You: show me README.md
ULTRON: [Displays README]
```

**List Directories:**
```
You: list directory .
ULTRON: [Shows current directory contents]

You: show files in Documents
ULTRON: [Lists ~/Documents]
```

**Write Files:**
```python
# Programmatic access:
assistant.filesystem.write_file("test.txt", "Hello World")
```

### 2. Command Execution

**Safe Commands:**
```
You: run ls -la
ULTRON: [Shows directory listing]

You: execute whoami
ULTRON: [Shows current user]

You: run python3 --version
ULTRON: [Shows Python version]
```

**System Information:**
```
You: run df -h        # Disk usage
You: run free -h      # Memory usage
You: run uptime       # System uptime
You: run ps aux       # Running processes
```

### 3. AI Conversation

**General Questions:**
```
You: What is Python?
ULTRON: [AI-generated explanation]

You: How do I create a virtual environment?
ULTRON: [Step-by-step guide]

You: Explain async/await in Python
ULTRON: [Detailed explanation]
```

### 4. Voice Interaction

With `--voice` flag:
- Speak naturally into your microphone
- ULTRON will respond verbally
- Say "goodbye", "exit", or "quit" to stop

## Safety Features

### File System Protection

- ✅ **Restricted Paths** - Only access allowed directories:
  - `~/Documents`
  - `~/Downloads`
  - `~/projects`
  - Current directory

- ✅ **File Size Limits** - Max 10MB per file
- ✅ **Path Validation** - Prevents directory traversal attacks

### Command Execution Safety

- ✅ **Whitelist System** - Only safe commands allowed by default
- ✅ **Dangerous Pattern Detection** - Blocks destructive commands:
  - `rm -rf /`
  - `dd if=`
  - `mkfs`, `fdisk`
  - System-critical operations

- ✅ **Timeout Protection** - Commands timeout after 30 seconds
- ✅ **Confirmation Required** - Unknown commands require approval

### Example Safety Checks

```bash
# SAFE ✅
run ls -la
run python3 script.py
run git status

# BLOCKED ❌
run rm -rf /
run dd if=/dev/zero of=/dev/sda
run chmod 777 /etc

# REQUIRES CONFIRMATION ⚠️
run sudo apt install package  # Unknown command
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            ULTRON AI Assistant                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ Voice Input  │  │  Text Input  │               │
│  │ (Microphone) │  │  (Keyboard)  │               │
│  └──────┬───────┘  └──────┬───────┘               │
│         │                   │                        │
│         └────────┬──────────┘                       │
│                  │                                   │
│         ┌────────▼─────────┐                       │
│         │  Command Router  │                        │
│         └────────┬─────────┘                       │
│                  │                                   │
│     ┌────────────┼────────────┐                    │
│     │            │             │                     │
│  ┌──▼───┐  ┌────▼────┐  ┌────▼────┐               │
│  │ AI   │  │  File   │  │ Command │               │
│  │ Brain│  │ System  │  │ Executor│               │
│  │      │  │ Manager │  │         │               │
│  └──┬───┘  └────┬────┘  └────┬────┘               │
│     │           │              │                     │
│     │     ┌─────▼──────────────▼───┐               │
│     │     │   Ollama (LLM Backend) │               │
│     │     │   llava:7b Model       │               │
│     │     └────────────────────────┘               │
│     │                                                │
│  ┌──▼────────────┐                                 │
│  │ Voice Output  │                                  │
│  │ (TTS Engine)  │                                  │
│  └───────────────┘                                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Advanced Usage

### Programmatic API

```python
from ultron_ai_assistant import ULTRONAssistant
import asyncio

async def example():
    assistant = ULTRONAssistant()

    # File operations
    content = await assistant.filesystem.read_file("test.txt")
    await assistant.filesystem.write_file("output.txt", "data")
    listing = await assistant.filesystem.list_directory(".")

    # Command execution
    result = await assistant.commander.execute("ls -la")

    # AI reasoning
    response = await assistant.brain.think("Explain asyncio")

    print(response)

asyncio.run(example())
```

### Custom Tool Integration

```python
# Add custom capabilities
class CustomTool:
    async def execute(self, command: str) -> str:
        # Your custom logic here
        return "Result"

# Extend the assistant
assistant = ULTRONAssistant()
assistant.custom_tool = CustomTool()
```

## Configuration

Edit `ultron_config.json` to customize:

```json
{
  "llm_model": "llava:7b",
  "ollama_base_url": "http://localhost:11434",
  "voice_enabled": true,
  "max_file_size_mb": 10,
  "command_timeout_seconds": 30
}
```

## Troubleshooting

### Voice Not Working

```bash
# Install audio dependencies
sudo apt-get install portaudio19-dev

# Install Python packages
source venv/bin/activate
pip install pyaudio SpeechRecognition pyttsx3

# Test microphone
arecord -l
```

### Ollama Not Responding

```bash
# Check Ollama status
systemctl status ollama

# Start Ollama
ollama serve &

# Test connection
curl http://localhost:11434/api/tags
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements_ubuntu.txt
```

## Examples

### Practical Workflows

**1. Code Review:**
```
You: read file mycode.py
ULTRON: [Shows code]

You: What does this code do?
ULTRON: [Explains the code]

You: Are there any issues?
ULTRON: [Provides analysis]
```

**2. File Management:**
```
You: list directory ~/Documents
ULTRON: [Shows files]

You: read file report.txt
ULTRON: [Displays content]

You: run grep "important" report.txt
ULTRON: [Shows matches]
```

**3. System Administration:**
```
You: run df -h
ULTRON: [Disk usage]

You: run free -m
ULTRON: [Memory usage]

You: What's using the most disk space?
ULTRON: [AI analysis based on command output]
```

## Security Best Practices

1. **Review Commands** - Check what the assistant wants to run
2. **Limit Access** - Keep allowed directories minimal
3. **Monitor Logs** - Check `logs/` for all activities
4. **Use Confirmations** - Don't auto-approve unknown commands
5. **Regular Updates** - Keep Ollama and dependencies updated

## Performance Tips

- **Fast Mode**: Use lighter models (`tinyllama`) for quicker responses
- **GPU Acceleration**: Ollama auto-uses NVIDIA GPUs if available
- **Memory**: Close other apps for better performance
- **Networking**: Use offline TTS (pyttsx3) for faster voice

## Comparison with Other Assistants

| Feature | ULTRON | Alexa | Google Assistant |
|---------|--------|-------|------------------|
| **Offline** | ✅ Yes | ❌ No | ❌ No |
| **File Access** | ✅ Full | ❌ No | ❌ No |
| **Command Execution** | ✅ Yes | ❌ No | ❌ No |
| **Customizable** | ✅ Fully | ❌ Limited | ❌ Limited |
| **Privacy** | ✅ Local | ⚠️ Cloud | ⚠️ Cloud |
| **Open Source** | ✅ Yes | ❌ No | ❌ No |

## Next Steps

1. **Try It**: `python3 ultron_ai_assistant.py`
2. **Enable Voice**: Install audio deps and use `--voice`
3. **Customize**: Edit code to add your own features
4. **Integrate**: Use as library in your projects
5. **Extend**: Add tools for web browsing, email, etc.

## Support

- **Logs**: Check `logs/` directory
- **Test Components**: Run `python3 test_components.py`
- **Ollama**: See [ollama.ai](https://ollama.ai)
- **Documentation**: `DOCUMENTATION_HUB.md`

---

**You now have a fully functional AI assistant that goes beyond chat!** 🚀
