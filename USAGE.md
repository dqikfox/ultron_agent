# ULTRON Agent Usage Guide

This comprehensive guide covers all aspects of using ULTRON Agent 3.0, from basic commands to advanced automation workflows.

## 🚀 Quick Start

### First Run

```bash
# Start ULTRON Agent with default GUI
python main.py

# Start with voice interaction
python main.py --voice

# Start web interface only
python main.py --web --port 8000

# CLI mode for scripting
ultron "What's the weather like today?"
```

### Basic Voice Commands

Once ULTRON Agent is running with voice enabled:

```
"Hello ULTRON"              # Wake up and greet
"What can you do?"          # List available capabilities
"Search the web for Python tutorials"
"Take a screenshot"
"Read this file: README.md"
"What's the current time?"
"Open the calculator"
"Send an email to john@example.com"
```

## 🖥 Interface Options

### 1. Pokédex-style GUI (Recommended)

The modern, accessible interface designed for all users:

```bash
# Launch Pokédex GUI
python pokedex_ultron_gui.py

# Or specify in config
ultron --gui pokedex
```

**Features:**
- Voice-to-text input with visual feedback
- Accessibility features for disabled users
- Dark/light theme support
- Real-time system monitoring
- File drag-and-drop support
- Multi-tab workflow management

### 2. Web Interface

Browser-based interface for remote access:

```bash
# Start web server
python web_gui_server.py

# Or using uvicorn directly
uvicorn agent_core:app --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000`

**Features:**
- RESTful API endpoints
- WebSocket real-time communication
- Mobile-responsive design
- Multi-user support with authentication
- API documentation at `/docs`

### 3. Command Line Interface

For automation and scripting:

```bash
# Single command
ultron "translate 'hello world' to Spanish"

# Interactive mode
ultron --interactive

# Batch processing
ultron --batch commands.txt

# Output formatting
ultron "system status" --format json
ultron "system status" --format table
```

## 🎤 Voice Interaction

### Voice Commands

ULTRON Agent supports natural language voice commands:

#### System Control
```
"Show system status"
"Monitor CPU usage"
"Check disk space"
"List running processes"
"Take a screenshot"
"Lock the screen"
"Shut down computer in 10 minutes"
```

#### File Operations
```
"Open file explorer"
"Create new folder called Projects"
"Find files containing 'ultron' in Documents"
"Copy file backup.zip to USB drive"
"Delete temporary files"
"Backup my Documents folder"
```

#### Web and Search
```
"Search Wikipedia for artificial intelligence"
"Open YouTube and search for Python tutorials"
"Check the weather in New York"
"What's trending on Reddit?"
"Send a tweet: Just installed ULTRON Agent!"
"Download this video: [URL]"
```

#### Communication
```
"Send email to john@example.com with subject 'Meeting tomorrow'"
"Create a calendar event for 3 PM meeting"
"Set reminder for 2 hours: Call dentist"
"Send SMS to +1234567890: Running late"
```

### Voice Configuration

Configure voice settings in `ultron_config.json`:

```json
{
  "voice": {
    "enabled": true,
    "engine": "enhanced",
    "language": "en-US",
    "wake_word": "ultron",
    "confidence_threshold": 0.7,
    "timeout": 5,
    "continuous_listening": false,
    "noise_reduction": true,
    "speech_to_text": {
      "provider": "openai",
      "model": "whisper-1"
    },
    "text_to_speech": {
      "provider": "elevenlabs",
      "voice_id": "default",
      "speed": 1.0,
      "pitch": 0.0
    }
  }
}
```

## 🔧 Tool System

### Available Tools

#### Web Tools
```bash
# Web search
ultron "search for 'machine learning tutorials'"
ultron --tool web_search --query "Python best practices"

# Web scraping
ultron "scrape data from https://example.com"
ultron --tool web_scraper --url "https://news.ycombinator.com"

# API requests
ultron "make GET request to https://api.github.com/users/octocat"
```

#### File Tools
```bash
# File reading
ultron "read file config.json"
ultron --tool file_reader --path "documents/report.pdf"

# File writing
ultron "create file shopping_list.txt with items: milk, bread, eggs"

# File organization
ultron "organize downloads folder by file type"
ultron --tool file_organizer --path "~/Downloads"
```

#### System Tools
```bash
# Process management
ultron "list all Python processes"
ultron "kill process with PID 1234"

# System monitoring
ultron "show disk usage"
ultron "monitor network activity"

# Application control
ultron "open calculator"
ultron "close all browser windows"
```

#### Communication Tools
```bash
# Email
ultron "compose email to team@company.com about project update"

# Calendar
ultron "schedule meeting for tomorrow at 2 PM with John and Sarah"

# Notifications
ultron "remind me in 30 minutes to take a break"
```

### Creating Custom Commands

Create custom command aliases in `ultron_config.json`:

```json
{
  "commands": {
    "daily_report": {
      "description": "Generate daily system report",
      "actions": [
        "system status",
        "disk usage",
        "running processes",
        "recent log entries"
      ]
    },
    "backup_work": {
      "description": "Backup work files",
      "actions": [
        "backup ~/Documents to ~/Backups/work_backup_$(date)",
        "compress backup folder",
        "verify backup integrity"
      ]
    }
  }
}
```

Use custom commands:
```bash
ultron daily_report
ultron backup_work
```

## 📊 API Usage

### REST API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Send Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current time?"}'
```

#### System Status
```bash
curl http://localhost:8000/status
```

#### Tool Execution
```bash
curl -X POST http://localhost:8000/tools/web_search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python tutorials"}'
```

### WebSocket API

Connect to real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to ULTRON Agent');
    
    // Send a message
    ws.send(JSON.stringify({
        type: 'query',
        message: 'Hello ULTRON'
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Response:', response);
};
```

### Python API

Use ULTRON Agent programmatically:

```python
from ultron_agent import UltronAgent
import asyncio

async def main():
    # Initialize agent
    agent = UltronAgent()
    
    # Send query
    response = await agent.process_query("What's the weather like?")
    print(response)
    
    # Use specific tool
    result = await agent.execute_tool("web_search", query="Python news")
    print(result)
    
    # System operations
    status = await agent.get_system_status()
    print(f"CPU: {status['cpu_percent']}%")
    print(f"Memory: {status['memory_percent']}%")

# Run async function
asyncio.run(main())
```

## 🔍 Advanced Features

### Multi-Model AI Integration

Switch between different AI models:

```bash
# Use specific model
ultron "What is machine learning?" --model gpt-4

# Compare responses from multiple models
ultron "Explain quantum computing" --compare-models

# Set default model
ultron config set models.default gpt-4
```

Configure models in `ultron_config.json`:

```json
{
  "models": {
    "default": "ollama",
    "fallback_chain": ["ollama", "openai", "anthropic"],
    "ollama": {
      "enabled": true,
      "host": "http://localhost:11434",
      "models": ["llama3.2:latest", "codellama:latest"]
    },
    "openai": {
      "enabled": true,
      "models": ["gpt-4o", "gpt-4o-mini"],
      "temperature": 0.7
    }
  }
}
```

### Workflow Automation

Create complex workflows:

```yaml
# workflows/daily_routine.yaml
name: "Daily Morning Routine"
description: "Automated morning tasks"
trigger:
  type: "schedule"
  time: "08:00"

steps:
  - name: "Weather Check"
    tool: "weather"
    params:
      location: "New York"
  
  - name: "News Summary"
    tool: "web_search"
    params:
      query: "today's tech news"
      summarize: true
  
  - name: "Calendar Review"
    tool: "calendar"
    action: "today_events"
  
  - name: "Send Summary"
    tool: "email"
    params:
      to: "me@example.com"
      subject: "Daily Brief"
      content: "{{ weather.summary }} {{ news.summary }} {{ calendar.events }}"
```

Execute workflows:
```bash
# Run specific workflow
ultron --workflow daily_routine

# List available workflows
ultron --list-workflows

# Create new workflow interactively
ultron --create-workflow
```

### Plugin Development

Create custom plugins:

```python
# plugins/my_plugin.py
from ultron_agent.tools.base_tool import BaseTool
from typing import Dict, Any

class MyCustomTool(BaseTool):
    """Custom tool for specific functionality."""
    
    @staticmethod
    def match(user_input: str) -> bool:
        """Check if this tool should handle the input."""
        return any(keyword in user_input.lower() 
                  for keyword in ["my tool", "custom function"])
    
    @staticmethod
    async def execute(**kwargs) -> Dict[str, Any]:
        """Execute the tool's functionality."""
        # Your custom logic here
        result = "Custom tool executed successfully"
        
        return {
            "success": True,
            "result": result,
            "data": kwargs
        }
    
    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return JSON schema for API documentation."""
        return {
            "name": "my_custom_tool",
            "description": "Performs custom functionality",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input parameter"
                    }
                },
                "required": ["input"]
            }
        }
```

Register the plugin:
```python
# In your ultron_config.json
{
  "plugins": {
    "enabled": ["my_plugin"],
    "paths": ["./plugins"]
  }
}
```

## 📊 Monitoring and Logging

### System Monitoring

View real-time system metrics:

```bash
# System dashboard
ultron --dashboard

# Specific metrics
ultron system cpu
ultron system memory
ultron system disk
ultron system network
```

### Logging Configuration

Configure logging in `ultron_config.json`:

```json
{
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "console_enabled": true,
    "files": {
      "main": "logs/ultron.log",
      "error": "logs/error.log",
      "access": "logs/access.log"
    },
    "rotation": {
      "max_size": "10MB",
      "backup_count": 5
    },
    "formatters": {
      "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      "simple": "%(levelname)s: %(message)s"
    }
  }
}
```

### Performance Analytics

```bash
# Performance report
ultron --performance-report

# Resource usage over time
ultron --resource-history --hours 24

# Query performance analysis
ultron --query-analytics
```

## 🛡 Security and Privacy

### API Key Management

Securely manage API keys:

```bash
# Encrypt stored keys
ultron config encrypt-keys

# Rotate API key
ultron config rotate-key openai

# List configured services
ultron config list-services
```

### Privacy Settings

Configure privacy preferences:

```json
{
  "privacy": {
    "data_collection": false,
    "local_processing_preferred": true,
    "anonymize_logs": true,
    "retain_conversations": false,
    "cloud_backup": false
  }
}
```

### Access Control

Set up user authentication:

```bash
# Create user
ultron user create admin --role administrator

# Set permissions
ultron user permissions admin --allow "system,tools,config"

# Enable authentication
ultron config set security.authentication.enabled true
```

## 🔧 Troubleshooting

### Common Issues

#### Voice Not Working
```bash
# Test audio system
ultron --test-audio

# Check microphone permissions
ultron --check-permissions

# Reset voice configuration
ultron voice reset
```

#### Slow Response Times
```bash
# Check system resources
ultron system status

# Clear cache
ultron cache clear

# Optimize performance
ultron optimize --auto
```

#### API Errors
```bash
# Test API connectivity
ultron test api

# Validate API keys
ultron config validate

# Check rate limits
ultron api status
```

### Debug Mode

Enable detailed debugging:

```bash
# Start with debug logging
python main.py --debug --log-level DEBUG

# Trace specific operations
ultron "search for python" --trace

# Generate diagnostic report
ultron --diagnose --output report.json
```

### Recovery Options

```bash
# Reset to default configuration
ultron config reset

# Restore from backup
ultron config restore backup_20241215.json

# Factory reset (keeps user data)
ultron factory-reset --keep-data
```

## 📚 Examples and Use Cases

### Personal Assistant
```bash
# Morning routine
ultron "good morning" # Triggers weather, news, calendar

# Task management
ultron "add task: Buy groceries for dinner party"
ultron "what's on my todo list?"
ultron "mark task complete: Buy groceries"

# Smart reminders
ultron "remind me to call mom when I get home"
```

### Development Assistant
```bash
# Code analysis
ultron "analyze this Python file for bugs"
ultron "suggest improvements for function get_data()"

# Documentation
ultron "generate docstrings for my_module.py"
ultron "create README for my project"

# Git operations
ultron "commit changes with message: Add new feature"
ultron "create pull request for feature branch"
```

### Business Automation
```bash
# Report generation
ultron "generate weekly sales report"
ultron "create presentation from data.csv"

# Communication
ultron "schedule meeting with team for project review"
ultron "send status update to stakeholders"

# Data processing
ultron "analyze customer feedback from reviews.xlsx"
ultron "export filtered data to new spreadsheet"
```

### Research Assistant
```bash
# Information gathering
ultron "research latest developments in quantum computing"
ultron "summarize this research paper: paper.pdf"

# Fact checking
ultron "verify these statistics about renewable energy"
ultron "find sources for climate change data"

# Citation management
ultron "format these references in APA style"
ultron "create bibliography from my research notes"
```

## 🚀 Advanced Tips

### Performance Optimization
- Use local models for faster responses
- Enable caching for repeated queries
- Configure appropriate timeout values
- Monitor resource usage regularly

### Customization
- Create custom voice commands
- Develop domain-specific tools
- Set up automated workflows
- Personalize the interface

### Integration
- Connect with existing tools and services
- Use API endpoints for external applications
- Set up webhook notifications
- Create dashboard integrations

---

**Ready to unlock the full potential of ULTRON Agent!** 🤖

For more advanced topics, see the [API Documentation](docs/API.md) and [Developer Guide](Contributing.md).