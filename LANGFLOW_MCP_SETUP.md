# 🚀 LangFlow MCP Server Integration Setup

**Status**: Configuration in progress
**Date**: November 5, 2025
**Compatibility**: Cursor, Claude, VS Code, other MCP clients
**Documentation**: https://docs.langflow.org/mcp-server

---

## 📋 Quick Start Checklist

### Prerequisites
- [ ] LangFlow installed: `pip install langflow` (v1.0+)
- [ ] Node.js LTS installed (for MCP Inspector)
- [ ] MCP Inspector installed: `npx @modelcontextprotocol/inspector`
- [ ] LangFlow running on `http://localhost:7860`
- [ ] At least one LangFlow flow created with Chat Output component

### Configuration Steps
- [ ] Create LangFlow project with flows
- [ ] Enable MCP Server in LangFlow project
- [ ] Configure tool names and descriptions
- [ ] Set up authentication (API key recommended)
- [ ] Copy MCP server configuration
- [ ] Add to `mcp.json` in Cursor
- [ ] Test with MCP Inspector
- [ ] Verify flows appear as tools

---

## 🔧 Step 1: LangFlow Project Setup

### Start LangFlow Server
```bash
langflow run --host 127.0.0.1 --port 7860
```

### Create a New Project
1. Navigate to `http://localhost:7860`
2. Click "New Project"
3. Name it: `ULTRON_Agent_Flows`

### Create Sample Flows
Create flows with **Chat Output** components:

#### Flow 1: Code Analysis Workflow
- **Name**: `analyze_code`
- **Description**: "Analyze Python code for security, performance, and quality issues"
- **Components**:
  - Chat Input
  - LLM (OpenAI/Local)
  - Code Analysis Chain
  - Chat Output

#### Flow 2: GUI Enhancement Workflow
- **Name**: `enhance_gui`
- **Description**: "Generate GUI improvements and code for ATLAS interface"
- **Components**:
  - Chat Input
  - LLM
  - CSS/HTML Generator
  - Chat Output

#### Flow 3: Security Audit Workflow
- **Name**: `security_audit`
- **Description**: "Perform security audit on code or configuration"
- **Components**:
  - Chat Input
  - LLM
  - Security Analysis Module
  - Chat Output

---

## 🛠️ Step 2: Enable MCP Server in LangFlow

### In LangFlow UI
1. Go to **Projects page**
2. Click **MCP Server tab** for your project
3. View the **Flows/Tools section** (lists all flows as tools)
4. Click **Edit Tools** to configure which flows are exposed
5. Ensure all flows have **Chat Output** component (required)

### Configure Tool Names and Descriptions
1. Click **Edit Tools**
2. For each flow, set:
   - **Tool Name**: Clear, descriptive name (e.g., `analyze_code`)
   - **Tool Description**: Complete description of what the flow does
3. Save changes

**Example Configuration**:
```
Tool Name: analyze_code
Description: "Analyzes Python code for security vulnerabilities,
performance bottlenecks, and code quality issues. Returns detailed
findings with recommendations."

Tool Name: enhance_gui
Description: "Generates GUI improvements and HTML/CSS code for
enhancing the ATLAS interface. Supports themes, animations, and
responsive design."

Tool Name: security_audit
Description: "Performs comprehensive security audit on source code
or configuration files. Identifies risks and provides remediation steps."
```

---

## 🔐 Step 3: Configure Authentication

### In LangFlow MCP Server Settings
1. Click **Edit Auth** on MCP Server tab
2. Choose authentication method:

#### Option A: API Key (Recommended)
```
- Click "Generate API key"
- Copy the generated key
- Securely store it
- Use in MCP configuration
```

#### Option B: OAuth
```
- Configure OAuth settings
- Note credentials for clients
```

#### Option C: None
```
- Use for local development only
- Not recommended for production
```

---

## 📝 Step 4: MCP Configuration for Cursor

### Get Configuration from LangFlow
1. In LangFlow, go to **Projects > MCP Server tab**
2. Click **JSON tab**
3. Copy the code snippet

### Windows Configuration
```json
{
  "mcpServers": {
    "langflow_ultron": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--headers",
        "x-api-key YOUR_LANGFLOW_API_KEY",
        "http://localhost:7860/api/v1/mcp/project/PROJECT_ID/sse"
      ]
    }
  }
}
```

### Add to Cursor Settings
1. Open Cursor
2. Go to **Settings > MCP (scroll down)**
3. Click **Add New Global MCP Server**
4. This opens `.cursor/mcp.json`
5. Add the LangFlow configuration above
6. Save and restart Cursor

### Add to VS Code Settings
1. Create/edit `.vscode/mcp.json`
2. Add LangFlow MCP server configuration
3. Verify MCP extension recognizes it

---

## 🧪 Step 5: Testing with MCP Inspector

### Start MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```

### Inspector Web UI
- Opens at `http://localhost:6274`
- Shows MCP servers and tools

### Configure LangFlow Connection
1. In Inspector, click **Add New Server**
2. Enter connection details:
   ```
   Transport Type: STDIO
   Command: uvx
   Arguments: mcp-proxy --headers x-api-key YOUR_API_KEY http://localhost:7860/api/v1/mcp/project/PROJECT_ID/sse
   ```
3. Click **Connect**

### Verify Tools
1. Go to **Tools tab**
2. Should see your LangFlow flows listed:
   - `analyze_code`
   - `enhance_gui`
   - `security_audit`
3. Click each to see schema and test

### Test Tool Execution
1. Click a tool (e.g., `analyze_code`)
2. Enter test input:
   ```json
   {
     "message": "Analyze this Python code for security issues"
   }
   ```
3. Click **Execute**
4. View results and any errors

---

## 📊 Step 6: Integration with ULTRON Agent

### Update mcp.json
Add LangFlow to `c:\Projects\ultron_agent\mcp.json`:

```json
{
  "mcpServers": {
    "langflow": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--headers",
        "x-api-key ${input:langflow-api-key}",
        "http://localhost:7860/api/v1/mcp/project/${input:langflow-project-id}/sse"
      ],
      "description": "LangFlow MCP server for ULTRON workflow automation",
      "env": {}
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "langflow-api-key",
      "description": "LangFlow API Key for authentication",
      "password": true
    },
    {
      "type": "promptString",
      "id": "langflow-project-id",
      "description": "LangFlow Project ID from MCP Server tab",
      "password": false
    }
  ]
}
```

### Test with Cursor
1. Open a file in Cursor
2. Start typing to trigger LangFlow tools
3. Cursor should offer LangFlow flows as available tools

---

## 🔌 Step 7: Python Integration

### Test LangFlow MCP via Python

```python
# test_langflow_mcp.py
import subprocess
import json
import time

def test_langflow_mcp():
    """Test LangFlow MCP connection"""

    # Configuration
    api_key = "YOUR_LANGFLOW_API_KEY"
    project_id = "YOUR_PROJECT_ID"
    langflow_url = "http://localhost:7860"

    # Build MCP proxy command
    cmd = [
        "uvx",
        "mcp-proxy",
        "--headers",
        f"x-api-key {api_key}",
        f"{langflow_url}/api/v1/mcp/project/{project_id}/sse"
    ]

    print(f"[*] Starting MCP connection to LangFlow...")
    print(f"[*] Project URL: {langflow_url}/api/v1/mcp/project/{project_id}/sse")

    try:
        # Test connection
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=5,
            text=True
        )

        if result.returncode == 0:
            print("[✓] MCP connection successful!")
            print(f"[✓] Tools available from LangFlow")
            return True
        else:
            print(f"[✗] Connection failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("[!] Connection timeout - server may be initializing")
        return False
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False

if __name__ == "__main__":
    test_langflow_mcp()
```

---

## 🐛 Troubleshooting

### LangFlow Server Not Responding
```bash
# Check if running
curl http://localhost:7860/health

# Restart
langflow run --host 127.0.0.1 --port 7860 --reload
```

### MCP Connection Failed
- Verify API key is correct
- Check Project ID matches
- Ensure LangFlow is running
- Check firewall allows localhost:7860

### No Tools Showing in Cursor
1. Verify flows have Chat Output component
2. Check tool names are descriptive
3. Restart Cursor
4. Check `.cursor/mcp.json` is valid JSON

### MCP Inspector Shows 0 Tools
- Verify flows are enabled in Edit Tools
- Check each flow has Chat Output
- Verify authentication in Edit Auth
- Try simpler test flow first

### Authentication Error
```
Error: x-api-key header not recognized
```
- Generate new API key in LangFlow
- Update mcp.json with new key
- Restart MCP connection

---

## 📚 Environment Variables (Optional)

Set in `.env` or system environment:

```bash
# Enable LangFlow MCP server
LANGFLOW_MCP_SERVER_ENABLED=true

# Enable progress notifications
LANGFLOW_MCP_SERVER_ENABLE_PROGRESS_NOTIFICATIONS=true

# Timeout for MCP operations (seconds)
LANGFLOW_MCP_SERVER_TIMEOUT=20

# Max sessions per server
LANGFLOW_MCP_MAX_SESSIONS_PER_SERVER=10
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] LangFlow running: `http://localhost:7860`
- [ ] Project created with name: `ULTRON_Agent_Flows`
- [ ] At least 3 flows created with Chat Output
- [ ] MCP Server tab shows flows as tools
- [ ] API key generated and stored securely
- [ ] mcp.json updated with LangFlow config
- [ ] MCP Inspector connects successfully
- [ ] Tools listed in MCP Inspector
- [ ] Test tool execution works
- [ ] Cursor recognizes LangFlow flows
- [ ] Tool descriptions are clear
- [ ] No errors in LangFlow logs

---

## 📊 Expected Results

### In LangFlow UI
```
Projects > MCP Server tab
├─ Flows/Tools (3 visible)
│  ├─ analyze_code
│  ├─ enhance_gui
│  └─ security_audit
├─ MCP Server tab shows JSON config
└─ Authentication set to: API Key
```

### In MCP Inspector (http://localhost:6274)
```
Tools tab
├─ analyze_code
│  └─ Available as tool
├─ enhance_gui
│  └─ Available as tool
└─ security_audit
   └─ Available as tool
```

### In Cursor
```
When typing, Cursor suggests:
├─ @langflow_analyze_code
├─ @langflow_enhance_gui
└─ @langflow_security_audit
```

---

## 🚀 Next Steps

1. **Create More Flows**: Add specialized workflows for:
   - Code generation
   - Security analysis
   - Performance optimization
   - Documentation generation
   - Testing automation

2. **Integrate with ULTRON**:
   - Add LangFlow flows to AI workflows
   - Use flows in automated pipelines
   - Combine with other MCP servers

3. **Advanced Configuration**:
   - Deploy LangFlow publicly with ngrok
   - Set up OAuth authentication
   - Add flow versioning
   - Create flow templates

4. **Monitoring**:
   - Monitor flow execution times
   - Track tool usage
   - Log errors and issues
   - Optimize performance

---

## 📞 Support & References

- **LangFlow Docs**: https://docs.langflow.org
- **MCP Protocol**: https://modelcontextprotocol.io
- **Cursor MCP**: https://docs.cursor.com/context/model-context-protocol
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector

---

**Status**: Ready for setup and testing
**Configuration Date**: November 5, 2025
**Next Review**: After initial flows created and tested
