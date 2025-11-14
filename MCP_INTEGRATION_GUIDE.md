# MCP Integration Guide for ULTRON Agent 3.0

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that allows AI agents like ULTRON to use external tools and services through a unified interface. This significantly extends ULTRON's capabilities beyond its built-in tools.

## 🎯 Why Add MCP to ULTRON?

### Current State
ULTRON Agent has powerful built-in tools (PyAutoGUI, OCR, web scraping, GitHub Models, etc.) but each tool requires custom integration code.

### With MCP Integration
- **Unified Interface**: All external tools use the same MCP protocol
- **Dynamic Discovery**: MCP servers auto-discover and register tools
- **No Code Changes**: Add new capabilities by just updating `mcp.json`
- **Ecosystem Access**: Use any MCP-compatible server from the community
- **Browser Automation**: Control Chrome/Edge through Browser MCP
- **Cross-Platform**: Works with Cursor, Claude Desktop, VS Code, and more

## 📦 Included MCP Servers

ULTRON Agent comes pre-configured with 5 powerful MCP servers:

### 1. **Browser MCP** (`browsermcp`)
- **Purpose**: Automate Chrome/Edge browser interactions
- **Capabilities**:
  - Navigate to URLs
  - Click elements
  - Fill forms
  - Extract data
  - Take screenshots
  - Execute JavaScript
- **Example Commands**:
  - "Go to google.com and search for 'ULTRON Agent'"
  - "Click the first result"
  - "Fill the form with my name and email"

### 2. **GitHub MCP** (`github`)
- **Purpose**: GitHub repository management and operations
- **Capabilities**:
  - List repositories
  - Create/close issues
  - Manage pull requests
  - Read file contents
  - Search code
  - List commits
- **Example Commands**:
  - "List my GitHub issues"
  - "Create a new issue in ultron_agent repo"
  - "Show pull requests for this repository"

### 3. **Filesystem MCP** (`filesystem`)
- **Purpose**: Local filesystem access with security boundaries
- **Capabilities**:
  - Read files
  - Write files
  - List directories
  - Search files
  - Move/copy files
- **Scope**: Limited to ULTRON Agent workspace for security
- **Example Commands**:
  - "Read the contents of agent_core.py"
  - "List all Python files in tools directory"
  - "Search for 'TODO' comments in the codebase"

### 4. **Postgres MCP** (`postgres`)
- **Purpose**: PostgreSQL database integration
- **Capabilities**:
  - Execute SQL queries
  - Read table schemas
  - Insert/update/delete records
  - Database migrations
- **Example Commands**:
  - "Query the users table"
  - "Show database schema"
  - "Insert a new record into logs table"

### 5. **Puppeteer MCP** (`puppeteer`)
- **Purpose**: Headless browser automation (advanced)
- **Capabilities**:
  - Full browser control
  - Network interception
  - PDF generation
  - Performance profiling
- **Example Commands**:
  - "Generate PDF of webpage"
  - "Run performance audit on website"
  - "Intercept network requests"

## 🚀 Quick Start

### Step 1: Install Node.js (if not already installed)
MCP servers run through Node.js:
```powershell
# Check if Node.js is installed
node --version

# If not installed, download from: https://nodejs.org/
```

### Step 2: Configure MCP Servers
The `mcp.json` file is already configured at the project root. You may need to add API keys:

```json
{
  "servers": {
    "browsermcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```

### Step 3: Install Browser MCP Extension
For browser automation, install the Chrome extension:
1. Open Chrome/Edge
2. Go to Chrome Web Store
3. Search "Browser MCP"
4. Click "Add to Chrome"
5. Extension will show "Connected" status

### Step 4: Start Using MCP in ULTRON

#### Option A: Through VS Code (Recommended)
1. Open ULTRON Agent workspace in VS Code
2. Press `Ctrl+Alt+I` to open Copilot Chat
3. MCP servers auto-discover from `mcp.json`
4. Use MCP tools with `#` prefix or in agent mode

**Example VS Code Usage**:
```
User: #browser Go to google.com and search for "ULTRON Agent"
Copilot: [Invokes browsermcp tool, navigates browser, executes search]
```

#### Option B: Through ULTRON Agent Directly
Add MCP integration to your ULTRON commands:

```python
# In agent_core.py or brain.py
from tools.mcp_integration_tool import MCPIntegrationTool

# Initialize MCP tool
mcp_tool = MCPIntegrationTool()

# Check available MCP servers
result = mcp_tool.execute("list mcp servers")
print(result)

# Start Browser MCP
result = mcp_tool.execute("start mcp browsermcp")
print(result)

# Execute browser automation
result = mcp_tool.execute("browser: go to google.com and search for ULTRON")
print(result)
```

#### Option C: Through ULTRON GUI
In the ULTRON web GUI (port 8080):
1. Type command: "list mcp servers"
2. Type command: "start mcp browsermcp"
3. Type command: "browser automate: search google for ULTRON"

## 📝 Configuration Details

### Environment Variables (Sensitive Data)
For servers requiring API keys, use environment variables:

```powershell
# Windows PowerShell
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_your_token_here"
$env:POSTGRES_CONNECTION_STRING = "postgresql://user:pass@localhost:5432/ultron"

# Add to system environment permanently via Windows Settings
```

### Input Variables (Interactive Prompts)
Alternatively, MCP can prompt for credentials when first starting a server:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github-token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```

When you start the GitHub MCP server, you'll be prompted:
```
? GitHub Personal Access Token: [hidden input]
```

## 🎮 Usage Examples

### Browser Automation
```python
# Start Browser MCP
mcp_tool.execute("start mcp browsermcp")

# Navigate and interact
mcp_tool.execute("browser: go to github.com/dqikfox/ultron_agent")
mcp_tool.execute("browser: click the 'Star' button")
mcp_tool.execute("browser: take screenshot")
```

### GitHub Operations
```python
# Start GitHub MCP (requires PAT token)
mcp_tool.execute("start mcp github")

# List issues
mcp_tool.execute("github: list issues in ultron_agent")

# Create new issue
mcp_tool.execute("github: create issue 'Add MCP integration' in ultron_agent")
```

### Filesystem Access
```python
# Start Filesystem MCP
mcp_tool.execute("start mcp filesystem")

# Read file
mcp_tool.execute("filesystem: read agent_core.py")

# List directory
mcp_tool.execute("filesystem: list tools directory")
```

### Database Queries
```python
# Start Postgres MCP (requires connection string)
mcp_tool.execute("start mcp postgres")

# Query database
mcp_tool.execute("database: SELECT * FROM users LIMIT 10")

# Show schema
mcp_tool.execute("database: show schema for users table")
```

## 🔧 Advanced Configuration

### Custom MCP Server
Add your own MCP server to `mcp.json`:

```json
{
  "servers": {
    "myCustomServer": {
      "type": "stdio",
      "command": "node",
      "args": ["C:/Projects/my-mcp-server/index.js"],
      "description": "My custom MCP server",
      "env": {
        "API_KEY": "${input:my-api-key}"
      }
    }
  }
}
```

### HTTP/SSE MCP Servers
For remote MCP servers:

```json
{
  "servers": {
    "remoteServer": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${input:api-token}"
      }
    }
  }
}
```

### Development Mode with Auto-Restart
For developing custom MCP servers:

```json
{
  "servers": {
    "myServer": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "dev": {
        "watch": "**/*.js",
        "debug": true
      }
    }
  }
}
```

## 🔒 Security Considerations

### Trust and Approval
- **Review Server Config**: Always review `mcp.json` before starting servers
- **Verify Publishers**: Only use MCP servers from trusted sources
- **Approve Tool Invocations**: VS Code prompts before executing MCP tools
- **Scope Limitations**: Filesystem MCP is scoped to workspace only

### Best Practices
1. **Use Input Variables**: Never hardcode API keys in `mcp.json`
2. **Environment Variables**: Store credentials in environment, not config
3. **Review Logs**: Check MCP output logs for suspicious activity
4. **Principle of Least Privilege**: Only grant necessary permissions
5. **Regular Updates**: Keep MCP servers updated with `npx` latest flag

## 🐛 Troubleshooting

### MCP Server Won't Start
**Symptom**: Server listed as "Stopped" after start command

**Solutions**:
1. Check Node.js is installed: `node --version`
2. Verify `mcp.json` syntax is valid JSON
3. Check terminal output for error messages
4. Try manual start: `npx @browsermcp/mcp@latest`

### Browser MCP Not Working
**Symptom**: Browser automation commands fail

**Solutions**:
1. Install Browser MCP Chrome extension
2. Check extension shows "Connected" status
3. Verify Chrome/Edge is running
4. Restart browser after installing extension

### GitHub MCP Authentication Fails
**Symptom**: "Authentication required" error

**Solutions**:
1. Create GitHub Personal Access Token: https://github.com/settings/tokens
2. Add to environment: `$env:GITHUB_PERSONAL_ACCESS_TOKEN = "your_token"`
3. Ensure token has required permissions (repo, read:user)
4. Restart ULTRON Agent after setting environment variable

### VS Code MCP Tools Not Appearing
**Symptom**: MCP tools don't show in Copilot Chat

**Solutions**:
1. Update VS Code to latest version (1.102+)
2. Enable MCP support: Settings → `chat.mcp.access` = "all"
3. Run: `MCP: Reset Cached Tools` from Command Palette
4. Restart VS Code

### Performance Issues
**Symptom**: Slow response times with multiple MCP servers

**Solutions**:
1. Only start servers you're actively using
2. Stop unused servers: `mcp_tool.execute("stop mcp servername")`
3. Use tool sets to limit active tools (max 128 per request)
4. Enable virtual tools in settings

## 📊 Monitoring MCP Servers

### View Server Status
```python
# Python API
result = mcp_tool.execute("list mcp servers")
print(result)

# Output:
# 📋 **MCP Servers Status**
#
# **browsermcp**
#   Status: 🟢 Running
#   Description: Browser automation and control
#   Command: npx
#   Type: stdio
#
# **github**
#   Status: ⚪ Stopped
#   ...
```

### View Server Logs
In VS Code:
1. Run: `MCP: List Servers`
2. Select server → "Show Output"
3. Review logs in Output panel

### Stop All Servers
```python
# Graceful shutdown of all MCP servers
mcp_tool.execute("stop all mcp servers")
```

## 🌐 Integration with ULTRON Components

### Brain.py Integration
```python
# In brain.py
from tools.mcp_integration_tool import MCPIntegrationTool

class Brain:
    def __init__(self):
        self.mcp_tool = MCPIntegrationTool()

    async def process_command(self, command: str):
        # Check if MCP tools can handle this
        if self.mcp_tool.match(command):
            return self.mcp_tool.execute(command)

        # Otherwise, use standard ULTRON tools
        return await self.standard_processing(command)
```

### GUI Integration
```javascript
// In app.js
async function handleMCPCommand(command) {
    const response = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: `mcp: ${command}` })
    });

    const result = await response.json();
    displayResponse(result.response);
}
```

### Voice Integration
```python
# In voice.py
async def process_voice_command(self, text: str):
    # Check for MCP keywords
    if any(kw in text.lower() for kw in ['browser', 'github', 'database']):
        result = self.mcp_tool.execute(text)
        await self.speak(result)
        return result
```

## 📚 Additional Resources

### Official Documentation
- **MCP Specification**: https://modelcontextprotocol.io/
- **VS Code MCP Guide**: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
- **Browser MCP Docs**: https://docs.browsermcp.io/

### MCP Server Registry
- **GitHub Registry**: https://github.com/mcp
- **Official Servers**: https://github.com/modelcontextprotocol/servers
- **Community Servers**: https://github.com/topics/mcp-server

### ULTRON-Specific
- **MCP Integration Tool**: `tools/mcp_integration_tool.py`
- **Configuration File**: `mcp.json`
- **Logging**: Check `logs/mcp_integration.log`

## 🎉 Next Steps

1. ✅ **MCP Configuration Created**: `mcp.json` is ready
2. ✅ **Integration Tool Added**: `tools/mcp_integration_tool.py`
3. ⏳ **Test MCP Servers**: Start with Browser MCP
4. ⏳ **Add Custom Servers**: Extend with your own MCP servers
5. ⏳ **GUI Integration**: Add MCP controls to web GUI

**Ready to start? Try this command in ULTRON:**
```
list mcp servers
```

---

*Last Updated: October 25, 2025*
*ULTRON Agent 3.0 - Model Context Protocol Integration*
