# MCP Quick Reference - ULTRON Agent

## 🚀 Quick Start Commands

### Check MCP Status
```
list mcp servers
mcp status
show mcp
```

### Start/Stop Servers
```
start mcp browsermcp
start mcp github
start all mcp servers
stop mcp browsermcp
stop all mcp servers
```

## 🌐 Browser Automation (browsermcp)

**Requires**: Chrome/Edge with Browser MCP extension installed

```
browser: go to google.com
browser: search for "ULTRON Agent"
browser: click the first result
browser: fill form with name "ULTRON"
browser: take screenshot
browser: scroll down
browser: click button with text "Submit"
```

## 🐙 GitHub Operations (github)

**Requires**: GitHub Personal Access Token in environment

```
github: list my issues
github: create issue "Add new feature" in ultron_agent
github: list pull requests
github: show repository ultron_agent
github: search code for "def execute"
```

## 📁 Filesystem Access (filesystem)

**Scope**: Limited to ULTRON Agent workspace

```
filesystem: read agent_core.py
filesystem: list tools directory
filesystem: search for "TODO" in codebase
filesystem: write to test.txt
filesystem: move file from src to backup
```

## 🗄️ Database Queries (postgres)

**Requires**: PostgreSQL connection string in environment

```
database: SELECT * FROM users LIMIT 10
database: show schema
database: INSERT INTO logs VALUES (...)
database: UPDATE users SET active = true
```

## 🎭 Puppeteer (puppeteer)

**Advanced**: Headless browser control

```
puppeteer: generate PDF of webpage
puppeteer: run performance audit
puppeteer: intercept network requests
puppeteer: emulate mobile device
```

## 🔧 Configuration

### Add GitHub Token
```powershell
# Windows PowerShell
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_your_token_here"
```

### Add PostgreSQL Connection
```powershell
$env:POSTGRES_CONNECTION_STRING = "postgresql://user:pass@localhost:5432/ultron"
```

### Edit MCP Config
Edit `C:\Projects\ultron_agent\mcp.json`

## 💡 Tips

1. **Agent Mode**: In VS Code Copilot Chat, tools auto-invoke in agent mode
2. **Explicit Reference**: Use `#` to explicitly reference MCP tools
3. **Tool Approval**: Review and approve tool invocations when prompted
4. **Max Tools**: Maximum 128 tools per chat request (model limit)
5. **Logs**: Check MCP output logs for debugging errors

## 🐛 Troubleshooting

### Server Won't Start
```powershell
# Check Node.js
node --version

# Manual start test
npx @browsermcp/mcp@latest
```

### Browser Extension Not Connected
1. Install: Chrome Web Store → "Browser MCP"
2. Check extension shows "Connected"
3. Restart browser

### Authentication Errors
- Verify environment variables are set
- Restart ULTRON Agent after setting env vars
- Check token permissions

---

**Full Documentation**: See `MCP_INTEGRATION_GUIDE.md` for comprehensive guide
