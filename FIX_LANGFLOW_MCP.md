# 🔧 FIX: LangFlow MCP Configuration

## ❌ Problem
You're using the WRONG config format. The file you showed has:
```json
{
  "mcpServers": {
    "langflow": {
      "env": {
        "LANGFLOW_API_KEY": "sk-...",
        "LANGFLOW_PROJECT_ID": "e6ecbc04..."
      }
    }
  }
}
```

This is **MISSING the `command` field** which is why you get "No valid MCP server found".

## ✅ Solution

### Option 1: Use Cursor's Input System (RECOMMENDED)

Your `mcp.json` is already correct! Just provide the values when Cursor prompts you:

1. **Restart Cursor**
2. **When prompted**, enter:
   - **LangFlow API Key**: `sk-ga49QmqHWdx4JESGXEPT5OQK6SylBm4Te_pCtwtm138`
   - **LangFlow Project ID**: `e6ecbc04-8495-41c2-b078-f9c3bec09411`

### Option 2: Hardcode Values (Quick Fix)

Edit `mcp.json` and replace the `${input:...}` placeholders:

```json
{
  "servers": {
    "langflow": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--headers",
        "x-api-key sk-ga49QmqHWdx4JESGXEPT5OQK6SylBm4Te_pCtwtm138",
        "http://localhost:7860/api/v1/mcp/project/e6ecbc04-8495-41c2-b078-f9c3bec09411/sse"
      ],
      "description": "LangFlow MCP server",
      "env": {
        "LANGFLOW_MCP_SERVER_ENABLED": "true"
      }
    }
  }
}
```

## 🎯 Quick Fix Command

Run this to update `mcp.json`:

```powershell
# Backup current config
Copy-Item mcp.json mcp.json.backup

# The mcp.json is already correct - just restart Cursor!
```

## ✅ Verify

After restart, check:
```bash
# In Cursor chat, type:
@langflow

# You should see autocomplete with workflows
```

## 📝 Notes

- The `mcp.json` file is **ALREADY CORRECT**
- Don't use `langflow_mcp_config.json` - that's the wrong format
- Cursor will prompt you for the API key and Project ID
- Or hardcode them in the `args` array as shown above

---

**TL;DR**: Your `mcp.json` is fine. Just restart Cursor and enter the values when prompted, OR hardcode them in the `args` array.
