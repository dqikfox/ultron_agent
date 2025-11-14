# 🌐 Browser MCP Server Guide for ULTRON Agent

**Status:** ✅ Already Configured and Ready to Use
**Date:** October 25, 2025

---

## 📋 What is Browser MCP?

The Browser MCP server (`@browsermcp/mcp`) provides browser automation capabilities to ULTRON Agent through the Model Context Protocol. It enables:

- 🌐 **Web Navigation** - Visit URLs and browse websites
- 🖱️ **Element Interaction** - Click buttons, fill forms, extract data
- 📸 **Screenshots** - Capture page screenshots
- 📄 **Content Extraction** - Get page content, parse HTML
- 🔍 **Web Scraping** - Extract structured data from websites
- ⚡ **Automation** - Automate repetitive browser tasks

Documentation: https://docs.browsermcp.io/

---

## ✅ Current Configuration

Your `mcp.json` already has Browser MCP configured:

```json
{
  "browsermcp": {
    "type": "stdio",
    "command": "npx",
    "args": ["@browsermcp/mcp@latest"],
    "description": "Browser automation and control through MCP",
    "env": {}
  }
}
```

**Integration:** Accessible through `tools/mcp_integration_tool.py`
**Auto-loaded:** Yes, when ULTRON Agent starts

---

## 🚀 How to Use Browser MCP

### Method 1: Through ULTRON Voice/Chat Commands

Simply ask ULTRON naturally:

```
"Open a browser and navigate to github.com"
"Click the login button on the page"
"Extract all links from the current page"
"Take a screenshot of the dashboard"
"Fill in the search box with 'Python tutorials'"
```

ULTRON's MCP integration tool will automatically:
1. Detect browser-related keywords
2. Start the Browser MCP server if needed
3. Execute the browser automation command
4. Return results to you

### Method 2: Direct MCP Commands

You can also use explicit MCP commands:

```
"List MCP servers"
"Start MCP browsermcp"
"Stop MCP browsermcp"
"MCP status"
```

### Method 3: Programmatic Usage

From Python code or tools:

```python
from tools.mcp_integration_tool import MCPIntegrationTool

mcp = MCPIntegrationTool()

# Start Browser MCP server
result = mcp.execute("start mcp browsermcp")

# Use browser automation
result = mcp.execute("browser navigate to https://example.com")

# Stop server when done
result = mcp.execute("stop mcp browsermcp")
```

---

## 🛠️ Available Browser Commands

Based on Browser MCP documentation:

### Navigation
- `"Navigate to [URL]"`
- `"Go to [URL]"`
- `"Open [URL] in browser"`

### Interaction
- `"Click [element]"`
- `"Type [text] into [field]"`
- `"Fill [field] with [value]"`
- `"Submit form"`

### Content Extraction
- `"Get page content"`
- `"Extract text from [selector]"`
- `"Get all links"`
- `"Parse table data"`

### Screenshots
- `"Take screenshot"`
- `"Capture page"`
- `"Screenshot [element]"`

### Advanced
- `"Wait for [element]"`
- `"Scroll to [position]"`
- `"Execute JavaScript: [code]"`

---

## 📊 Testing Browser MCP

### Quick Test Script

Create a test file to verify Browser MCP works:

```python
# test_browser_mcp.py
from tools.mcp_integration_tool import MCPIntegrationTool

def test_browser_mcp():
    """Test Browser MCP server integration"""
    mcp = MCPIntegrationTool()

    # 1. Check server status
    print("=== MCP Server Status ===")
    print(mcp.execute("list mcp servers"))

    # 2. Start Browser MCP
    print("\n=== Starting Browser MCP ===")
    print(mcp.execute("start mcp browsermcp"))

    # 3. Test browser automation
    print("\n=== Testing Browser Automation ===")
    print(mcp.execute("browser navigate to https://example.com"))

    # 4. Stop server
    print("\n=== Stopping Browser MCP ===")
    print(mcp.execute("stop mcp browsermcp"))

if __name__ == "__main__":
    test_browser_mcp()
```

Run it:
```powershell
python test_browser_mcp.py
```

### Via ULTRON Chat/Voice

Start ULTRON and try these commands:

1. **Check Status:**
   ```
   "Show me MCP server status"
   ```

2. **Start Browser MCP:**
   ```
   "Start the browser MCP server"
   ```

3. **Test Navigation:**
   ```
   "Open example.com in the browser"
   ```

4. **Extract Content:**
   ```
   "Get the page title and main heading"
   ```

---

## 🔧 Configuration Options

### Basic Setup (Current)
```json
{
  "browsermcp": {
    "type": "stdio",
    "command": "npx",
    "args": ["@browsermcp/mcp@latest"],
    "env": {}
  }
}
```

### Advanced Setup (Optional)

If you need specific browser options:

```json
{
  "browsermcp": {
    "type": "stdio",
    "command": "npx",
    "args": ["@browsermcp/mcp@latest"],
    "env": {
      "BROWSER_HEADLESS": "true",
      "BROWSER_TIMEOUT": "30000",
      "BROWSER_VIEWPORT_WIDTH": "1920",
      "BROWSER_VIEWPORT_HEIGHT": "1080"
    }
  }
}
```

### Local Installation (Alternative)

If you prefer local installation instead of `npx`:

```powershell
# Install globally
npm install -g @browsermcp/mcp

# Update mcp.json to use global installation
{
  "browsermcp": {
    "type": "stdio",
    "command": "browsermcp",  # Instead of "npx"
    "args": [],
    "env": {}
  }
}
```

---

## 🔍 Troubleshooting

### Issue: "Browser MCP server not starting"

**Check 1: Node.js and npm installed**
```powershell
node --version  # Should show v16+ or higher
npm --version   # Should show 7+ or higher
```

**Check 2: Test npx directly**
```powershell
npx @browsermcp/mcp@latest --version
```

**Check 3: Check logs**
```powershell
# ULTRON logs
cat logs/mcp_integration.log

# Agent core logs
cat logs/agent_core.log
```

### Issue: "Command not recognized"

Make sure you're using the right keywords:
- ✅ "browser navigate to..."
- ✅ "open in browser..."
- ❌ "go to website..." (might not trigger MCP)

### Issue: "Server already running"

Stop the server first:
```
"Stop MCP browsermcp"
```

Then restart:
```
"Start MCP browsermcp"
```

### Issue: "Permission denied"

On Windows, you might need to allow Node.js through firewall:
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Node.js" -Direction Inbound -Program "C:\Program Files\nodejs\node.exe" -Action Allow
```

---

## 🔗 Integration with Other MCP Servers

Browser MCP works alongside other configured MCP servers:

| Server | Purpose | Status |
|--------|---------|--------|
| **browsermcp** | Browser automation | ✅ Configured |
| **github** | GitHub operations | ✅ Configured |
| **filesystem** | File operations | ✅ Configured |
| **postgres** | Database queries | ✅ Configured |
| **puppeteer** | Headless browser | ✅ Configured |

You can use them together:
```
"Use browser MCP to scrape data from the website,
then use filesystem MCP to save it to a file,
then commit it to GitHub using github MCP"
```

---

## 📚 Example Use Cases

### 1. Web Data Collection
```
"Navigate to product-page.com and extract all product names and prices"
```

### 2. Automated Testing
```
"Open the login page, fill in test credentials, click submit, and verify dashboard loads"
```

### 3. Content Monitoring
```
"Check news-site.com every hour and notify me of new articles"
```

### 4. Form Automation
```
"Fill out the contact form with my details and submit it"
```

### 5. Screenshot Documentation
```
"Take screenshots of all pages in the documentation site for the report"
```

---

## 🎯 Next Steps

1. **Test the Integration:**
   ```powershell
   # Run ULTRON
   .\run.bat

   # In ULTRON chat/voice:
   "Show MCP server status"
   "Start browser MCP"
   ```

2. **Try Basic Navigation:**
   ```
   "Open example.com in browser"
   "Get the page title"
   ```

3. **Explore Advanced Features:**
   - Form filling
   - Data extraction
   - Screenshot capture
   - JavaScript execution

4. **Read Full Documentation:**
   https://docs.browsermcp.io/

5. **Check MCP Tool Integration:**
   Review `tools/mcp_integration_tool.py` for all available methods

---

## ✅ Quick Reference

**Start Server:**
```
"Start MCP browsermcp"
```

**Navigate:**
```
"Browser navigate to [URL]"
```

**Interact:**
```
"Click [element]"
"Type [text]"
```

**Extract:**
```
"Get page content"
"Extract links"
```

**Stop Server:**
```
"Stop MCP browsermcp"
```

**Check Status:**
```
"List MCP servers"
```

---

## 🌟 Summary

**You're Already Set Up!** 🎉

- ✅ Browser MCP configured in `mcp.json`
- ✅ Integration tool ready in `tools/mcp_integration_tool.py`
- ✅ Auto-loaded when ULTRON starts
- ✅ Accessible via voice/chat/code

**Just start ULTRON and say:**
```
"Start browser MCP and navigate to github.com"
```

That's it! Browser automation is ready to go! 🚀

---

*For more details, visit: https://docs.browsermcp.io/*
*ULTRON Agent v3.1 - MCP Integration Complete*
