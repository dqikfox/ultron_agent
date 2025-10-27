# ULTRON Agent - Tools & Services Reference

## Overview

ULTRON Agent has multiple integrated tools and services that Continue.dev should be aware of when providing development assistance.

## 🔍 Diagnostics System (NEW - Unity Cloud-Style)

**Status**: ✅ Fully Implemented
**Port**: 5001
**Dashboard**: http://localhost:5001

ULTRON now includes comprehensive diagnostics inspired by Unity Cloud:

**Core Features**:
- ✅ Real-time crash reporting with full stack traces
- ✅ Performance telemetry (CPU, memory, disk, services)
- ✅ Web dashboard with auto-refresh
- ✅ AWS CloudWatch integration for oasis_app
- ✅ Automatic error tracking via decorators
- ✅ Historical data export

**Quick Usage**:
```python
from diagnostics import diagnostic_wrapper, track_metric, report_crash

@diagnostic_wrapper("component_name", track_performance=True)
async def my_function():
    # Automatic crash reporting + performance tracking
    pass

track_metric("brain", "tokens_processed", 1024, "tokens")
crash_id = report_crash("tool", exception, severity="critical")
```

**Start Dashboard**:
```powershell
.\scripts\start_diagnostics.ps1
# Or: python -m diagnostics.diagnostics_dashboard
```

**AWS CloudWatch Integration**:
- Namespace: `ULTRON/Diagnostics`
- Log Group: `/ultron/oasis_app/diagnostics`
- Region: us-west-2
- Alarms: HighCrashRate (>10/hr), HighCPU (>90%), HighMemory (>85%)

**Files**:
- `diagnostics/diagnostics_core.py` - Core tracking
- `diagnostics/diagnostics_dashboard.py` - Web UI (Flask)
- `diagnostics/cloudwatch_integration.py` - AWS sync
- `diagnostics/__init__.py` - Decorators and helpers
- `DIAGNOSTICS_SETUP.md` - Complete documentation

## MCP (Model Context Protocol) Servers

ULTRON integrates with MCP servers defined in `mcp.json` and accessible through `tools/mcp_integration_tool.py`.

### Browser Automation (browsermcp)
**Command**: `npx @browsermcp/mcp@latest`
**Port**: Chrome/Edge automation
**Usage**:
```
"browser: go to google.com"
"browser: search for 'ULTRON Agent'"
"browser: take screenshot"
"browser: click button with text 'Submit'"
```

### GitHub Operations (github)
**Command**: `npx @anthropic-ai/mcp-server-github`
**Requires**: `GITHUB_PERSONAL_ACCESS_TOKEN`
**Usage**:
```
"github: list my issues"
"github: create issue 'Bug in voice system' in dqikfox/ultron_agent"
"github: list commits in main branch"
"github: create PR 'feat: new tool' from branch feature"
```

### Filesystem Access (filesystem)
**Command**: `npx @anthropic-ai/mcp-server-filesystem`
**Scope**: Workspace-scoped access
**Usage**:
```
"filesystem: read agent_core.py"
"filesystem: list tools directory"
"filesystem: search for 'voice_enabled' in config"
```

### Database Operations (postgres)
**Command**: `npx @anthropic-ai/mcp-server-postgres`
**Requires**: `POSTGRES_CONNECTION_STRING`
**Usage**:
```
"database: SELECT * FROM users LIMIT 10"
"database: show tables"
"database: describe table agents"
```

### Puppeteer (Advanced Browser Control)
**Command**: `npx @modelcontextprotocol/server-puppeteer`
**Usage**: Headless browser automation for testing

## ULTRON Built-in Tools

### 1. Dynamic Code Executor
**File**: `tools/dynamic_code_executor.py`
**Purpose**: Sandboxed Python code execution
**Usage**:
```python
# Execute arbitrary Python code safely
executor = DynamicCodeExecutor()
result = executor.execute("import sys; print(sys.version)")
```

### 2. PyAutoGUI Tool
**File**: `tools/pyautogui_tool.py`
**Purpose**: System automation (mouse, keyboard)
**Usage**:
```
"move mouse to 100, 100"
"click at 500, 300"
"type 'Hello World'"
"press enter"
```

### 3. Web Scraping Tool
**File**: `tools/web_scraping_tool.py`
**Purpose**: Extract data from websites
**Usage**:
```python
scraper = WebScrapingTool()
data = scraper.execute("scrape https://example.com")
```

### 4. OpenAI Tools
**File**: `tools/openai_tools.py`
**Purpose**: OpenAI API integration
**Usage**:
```python
# Generate text, embeddings, completions
openai_tool = OpenAITool()
response = openai_tool.execute("generate: Write a poem")
```

### 5. Mobile Web Interface
**File**: `tools/mobile_web_interface_tool.py`
**Purpose**: Mobile-optimized web UI
**Port**: 8001
**Usage**: Access via `http://localhost:8001`

### 6. MCP Integration Tool
**File**: `tools/mcp_integration_tool.py`
**Purpose**: Central MCP server manager
**Commands**:
```
"list mcp servers"
"start mcp browsermcp"
"start all mcp servers"
"stop mcp github"
"browser: go to google.com"
"github: list issues"
"filesystem: read main.py"
```

## ULTRON Services

### 1. API Server (Flask)
**File**: `api_server.py`
**Port**: 5000
**Endpoints**:
- `GET /health` - Health check
- `POST /command` - Execute command
- `GET /api/tools` - List available tools
- `POST /api/tools/execute` - Execute specific tool
- `POST /api/model/switch` - Switch AI model

**Usage**:
```powershell
# Health check
curl http://localhost:5000/health

# Execute command
curl -X POST http://localhost:5000/command `
  -H "Content-Type: application/json" `
  -d '{"command": "list tools"}'

# Switch model
curl -X POST http://localhost:5000/api/model/switch `
  -H "Content-Type: application/json" `
  -d '{"model": "llama3.1"}'
```

### 2. Web GUI Server
**File**: `web_gui_server.py`
**Port**: 8080
**Purpose**: Primary Pokédex-style GUI
**Access**: `http://localhost:8080`
**Features**:
- Voice control interface
- Command input/output
- Real-time status
- System monitoring

### 3. Avatar Server
**File**: `Avatar/avatar_server.py`
**Port**: 8090
**Purpose**: 3D avatar visualization
**Access**: `http://localhost:8090/ultron_simple_viewer.html`
**Features**:
- 3D model viewer (GLB format)
- Animation support
- Camera controls

### 4. Ollama Service
**Service**: External (Ollama)
**Port**: 11434
**Purpose**: Local LLM inference
**Endpoints**:
- `GET /api/tags` - List models
- `POST /api/generate` - Generate text
- `POST /api/chat` - Chat completion
**Models**:
- `llava:7b` (default, multimodal)
- `llama3.1` (fast)
- `deepseek-r1:14b` (reasoning)
- `qwen3-coder:480b-cloud` (coding)

**Usage**:
```powershell
# List models
curl http://localhost:11434/api/tags

# Generate text
curl -X POST http://localhost:11434/api/generate `
  -H "Content-Type: application/json" `
  -d '{"model": "llava:7b", "prompt": "Hello", "stream": false}'
```

### 5. AI Chat Server
**File**: `nvidia_enhanced_ultron.py`
**Port**: 8000
**Purpose**: Enhanced AI chat with NVIDIA NIM
**Usage**: Advanced AI interactions

## Service Dependencies

### Startup Order
```
1. Ollama (port 11434) - Must start first
2. API Server (port 5000) - Core services
3. Web GUI (port 8080) - User interface
4. Avatar Server (port 8090) - Optional visualization
5. AI Chat (port 8000) - Optional enhancement
```

### Health Check Sequence
```
run.bat performs:
1. Service Availability Check
2. Model Availability Check (llava:7b)
3. Text Generation Test
4. Chat API Test
5. Context Retention Test
```

## Tool Discovery System

### Auto-Discovery
ULTRON automatically discovers tools in `tools/` directory:

```python
# tools/my_new_tool.py
from tools.tool_interface import ToolInterface

class MyNewTool(ToolInterface):
    @property
    def name(self) -> str:
        return "My New Tool"

    def match(self, command: str) -> bool:
        return "mynew" in command.lower()

    def execute(self, command: str, **kwargs) -> str:
        return "Tool executed"

    @classmethod
    def schema(cls) -> dict:
        return {...}
```

**Restart Required**: After adding new tools, restart agent:
```powershell
python main.py
```

## Integration with Continue.dev

### Using Tools in Continue.dev

#### Browser Automation
```
You (in Continue.dev chat):
"Use browser to test the ULTRON GUI at localhost:8080"

Continue.dev:
Uses browsermcp MCP server to:
1. Navigate to http://localhost:8080
2. Take screenshot
3. Report status
```

#### GitHub Operations
```
You:
"Create a GitHub issue for the voice system bug"

Continue.dev:
Uses github MCP server to:
1. Create issue in dqikfox/ultron_agent
2. Add description with context
3. Return issue URL
```

#### Filesystem Access
```
You:
"Show me all tools that use logging"

Continue.dev:
Uses filesystem MCP server to:
1. Search for "ultron_logger" in tools/
2. List matching files
3. Show usage examples
```

### Service Status Checking

```
You:
"Is Ollama running?"

Continue.dev:
Checks http://localhost:11434/api/tags
Reports: "✅ Ollama running with models: llava:7b, llama3.1"
```

```
You:
"Check all ULTRON services"

Continue.dev:
Tests ports: 5000, 8000, 8080, 8090, 11434
Reports status of each service
```

## Common Tool Patterns

### 1. Web Automation
```
"browser: go to https://internal.docs/api"
"browser: take screenshot of documentation"
"browser: search for 'authentication'"
```

### 2. Repository Management
```
"github: list open issues in ultron_agent"
"github: create PR 'feat: add new tool'"
"github: show commits since last week"
```

### 3. Code Analysis
```
"filesystem: read agent_core.py lines 1-100"
"filesystem: search for 'async def' in *.py"
"filesystem: list all Python files in tools/"
```

### 4. Database Operations
```
"database: SELECT COUNT(*) FROM users"
"database: show recent activity logs"
"database: backup user data"
```

## Tool Security

### Sandboxed Execution
- `dynamic_code_executor.py` uses restricted Python environment
- Timeouts prevent infinite loops
- Resource limits prevent memory exhaustion

### API Key Management
- Keys stored in environment variables
- `USE_ENV_*` pattern in `ultron_config.json`
- Never committed to repository

### Network Security
- 30-second timeout for all network operations
- Retry logic for transient failures
- Error sanitization in logs

## Debugging Tools

### 1. Log Analysis
```python
from utils.ultron_logger import log_info, log_error

# All tools must use centralized logging
log_info("tool_name", "Operation completed")
log_error("tool_name", "Error occurred", exception=e)
```

### 2. Event Monitoring
```python
from utils.event_system import get_event_system

event_system = get_event_system()

# Subscribe to all events
async def monitor(data):
    print(f"Event: {data}")

await event_system.subscribe("*", monitor)
```

### 3. Performance Profiling
```python
from utils.performance_profiler import profile_function

@profile_function
def slow_operation():
    # Implementation
    pass
```

## Tool Development Checklist

When creating new tools, Continue.dev should ensure:

- [ ] Inherits from `ToolInterface`
- [ ] Implements required methods: `name`, `description`, `match()`, `execute()`, `schema()`
- [ ] Uses `utils.ultron_logger` for all logging
- [ ] Handles errors gracefully with try/except
- [ ] Returns meaningful error messages
- [ ] Includes docstrings
- [ ] Follows async/await patterns if needed
- [ ] Placed in `tools/` directory for auto-discovery

## Quick Reference

### Service URLs
```
API Server:    http://localhost:5000
Web GUI:       http://localhost:8080
Avatar:        http://localhost:8090
Ollama:        http://localhost:11434
AI Chat:       http://localhost:8000
Mobile UI:     http://localhost:8001
```

### MCP Commands
```
list mcp servers
start mcp <server_name>
start all mcp servers
stop mcp <server_name>
browser: <browser_command>
github: <github_command>
filesystem: <filesystem_command>
database: <sql_query>
```

### Tool Files
```
tools/tool_interface.py          - Base class
tools/tool_loader.py             - Auto-discovery
tools/mcp_integration_tool.py    - MCP manager
tools/dynamic_code_executor.py   - Code execution
tools/pyautogui_tool.py          - System automation
tools/web_scraping_tool.py       - Web scraping
tools/openai_tools.py            - OpenAI integration
tools/mobile_web_interface_tool.py - Mobile UI
```

### Configuration Files
```
ultron_config.json  - Main configuration
mcp.json           - MCP server definitions
.continue/config.yaml - Continue.dev settings
```

**Continue.dev now has full awareness of all ULTRON tools and services!** 🛠️
