# ULTRON Agent Common Tasks

## Development Tasks

### Adding New Tools
```python
# 1. Create tool in tools/ directory
class NewTool:
    name = "new_tool"
    description = "Tool functionality description"
    
    def match(self, command: str) -> bool:
        return "keyword" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        from utils.ultron_logger import log_info, log_error
        try:
            log_info("new_tool", f"Executing: {command}")
            # Implementation
            return "Success"
        except Exception as e:
            log_error("new_tool", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def schema():
        return {
            "name": "new_tool",
            "description": "Tool description",
            "parameters": {}
        }

# 2. Tool is automatically discovered by agent_core.py
```

### Configuring New AI Models
```yaml
# Add to .continue/config.yaml
models:
  - name: New Model
    provider: ollama
    model: model-name:tag
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit
      - apply
```

### Adding MCP Servers
```yaml
# Add to .continue/config.yaml mcpServers section
mcpServers:
  - name: new-server
    command: npx
    args: ["-y", "@company/mcp-server-name"]
    env:
      API_KEY: ${NEW_SERVER_API_KEY}
```

## System Administration Tasks

### Health Check and Diagnostics
```bash
# Run comprehensive system test
python test_enhanced_system.py

# Check MCP connections
python mcp_diagnostic.py

# Validate Ollama integration
.\test_ollama_communication.ps1

# Start system with health checks
.\run.bat
```

### Service Management
```bash
# Start individual services
python main.py                    # Core agent
python web_gui_server.py          # GUI (port 8080)
python api_server.py              # API (port 5000)
python gui_ocr_integration.py     # Enhanced API (port 5001)

# Check service status
Get-NetTCPConnection -LocalPort 8080,5000,5001,11434
```

### Configuration Updates
```python
# Update ultron_config.json
{
  "llm_model": "new-model:latest",
  "voice_provider": "elevenlabs",
  "api_keys": {
    "new_service": "${NEW_SERVICE_API_KEY}"
  }
}

# Reload configuration (automatic in most services)
```

## User Interaction Tasks

### Voice Command Processing
```python
# Natural language commands ULTRON understands
commands = [
    "hey ultron open chrome and search for cars",
    "take a screenshot and read the text",
    "open notepad and remember this conversation",
    "show me what we searched for recently",
    "help with MCP integration"
]

# Voice system automatically processes these through:
# 1. Speech recognition (ElevenLabs/Web Speech API)
# 2. Intent parsing (WindowsSystemTool._parse_intent)
# 3. Command execution (appropriate tool)
# 4. Response synthesis (voice_manager.speak)
```

### GUI Operations
```javascript
// Enhanced ULTRON GUI operations
const gui = new EnhancedUltronGUI();

// Voice control
gui.toggleVoiceListening();

// System commands
await gui.executeSystemCommand("open calculator");

// Browser automation
await gui.executeBrowserCommand("navigate to google.com");

// Documentation queries
await gui.executeDocsQuery("help with Continue integration");
```

## Integration Tasks

### Amazon Q Integration
```python
# Amazon Q understands ULTRON patterns and provides:
# - Code suggestions for tool development
# - Error detection and fixes
# - Security vulnerability scanning
# - Documentation generation

# Example: Amazon Q suggests improvements for this pattern
class ToolWithAmazonQIntegration:
    def execute(self, command: str) -> str:
        # Amazon Q suggests proper error handling
        try:
            result = self._process_command(command)
            # Amazon Q suggests logging best practices
            log_info("tool", f"Command executed: {command}")
            return result
        except Exception as e:
            # Amazon Q suggests comprehensive error handling
            log_error("tool", f"Command failed: {str(e)}")
            return f"Error: {str(e)}"
```

### Continue Extension Tasks
```python
# Use Continue's context providers
# @codebase - Analyze entire ULTRON codebase
# @docs - Access Continue and ULTRON documentation
# @terminal - Include terminal output in context
# @problems - Include VS Code problems/errors

# Example Continue chat:
# "Using @codebase, help me add a new tool for file management"
# "With @docs context, explain how to configure MCP servers"
```

### MCP Server Operations
```python
# Browser automation via MCP
browser_commands = [
    "navigate to https://example.com",
    "click button with text 'Submit'",
    "fill input[name='search'] with 'query'",
    "take screenshot of current page"
]

# GitHub operations via MCP
github_commands = [
    "list repositories",
    "create issue with title 'Bug Report'",
    "get commits for repository 'ultron_agent'"
]
```

## Troubleshooting Tasks

### Common Issues and Solutions
```python
# Issue: Port conflicts
# Solution: Use run.bat which automatically kills conflicting processes

# Issue: Ollama not responding
# Solution: Restart Ollama service
subprocess.run(["ollama", "serve"], check=True)

# Issue: Voice system not working
# Solution: Check ElevenLabs API key and fallback to pyttsx3
voice_manager = get_voice_manager()
voice_manager.test_voice_system()

# Issue: GUI not loading
# Solution: Check if web server is running on correct port
curl http://localhost:8080/

# Issue: Tools not loading
# Solution: Check tools/ directory and agent_core.py logs
```

### Log Analysis
```python
# Check centralized logs
log_files = [
    "logs/agent_core.log",
    "logs/brain.log", 
    "logs/voice.log",
    "logs/ai_activities.log",
    "logs/file_changes.log"
]

# Analyze recent errors
for log_file in log_files:
    with open(log_file, 'r') as f:
        recent_logs = f.readlines()[-50:]  # Last 50 lines
        errors = [line for line in recent_logs if "ERROR" in line]
```

## Performance Optimization Tasks

### Memory Management
```python
# Monitor memory usage
import psutil
memory_percent = psutil.virtual_memory().percent
if memory_percent > 80:
    # Implement cleanup or restart services
    pass

# Optimize tool loading
# Tools are loaded dynamically to reduce startup memory
```

### Service Optimization
```python
# Use async patterns for I/O operations
async def optimized_operation():
    tasks = [
        asyncio.create_task(service1.process()),
        asyncio.create_task(service2.process()),
        asyncio.create_task(service3.process())
    ]
    results = await asyncio.gather(*tasks)
    return results

# Implement caching for frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_operation(param):
    # Expensive operation
    return result
```

## Backup and Recovery Tasks

### Configuration Backup
```bash
# Backup critical configuration files
copy ultron_config.json ultron_config.backup.json
copy .continue\config.yaml .continue\config.backup.yaml
copy .vscode\settings.json .vscode\settings.backup.json
```

### Data Recovery
```python
# Recover conversation history from memory database
import sqlite3
conn = sqlite3.connect("memory/context.db")
conversations = conn.execute("SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 100").fetchall()

# Recover logs from centralized logging
import json
with open("logs/ai_activities.log", 'r') as f:
    activities = [json.loads(line) for line in f if line.strip()]
```

These common tasks provide a comprehensive guide for working with ULTRON Agent in development, administration, and troubleshooting scenarios.