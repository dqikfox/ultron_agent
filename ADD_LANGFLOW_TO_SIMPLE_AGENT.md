# Add LangFlow MCP Tool to Simple Agent

## Quick Steps

1. **Open LangFlow UI**: http://localhost:7860
2. **Load "Simple Agent" flow**
3. **Add Custom Component**:
   - Click "+" button
   - Select "Custom Component" 
   - Upload: `tools/langflow_mcp_tool.py`
4. **Connect it**:
   - Drag from LangflowMCPTool output → Agent "tools" input
5. **Save flow**

## Alternative: Use Python Script

Run this to add the tool programmatically:

```python
import json

# Load Simple Agent flow
with open('flows/Simple Agent.json', 'r') as f:
    flow = json.load(f)

# Add LangflowMCPTool node
langflow_node = {
    "id": "LangflowMCP-12345",
    "type": "CustomComponent",
    "data": {
        "file_path": "tools/langflow_mcp_tool.py",
        "type": "LangflowMCPTool"
    },
    "position": {"x": 1200, "y": 300}
}

flow['data']['nodes'].append(langflow_node)

# Add edge connecting to Agent
edge = {
    "id": "edge-langflow-agent",
    "source": "LangflowMCP-12345",
    "target": "Agent-ELcID",
    "sourceHandle": "output",
    "targetHandle": "tools"
}

flow['data']['edges'].append(edge)

# Save
with open('flows/Simple Agent.json', 'w') as f:
    json.dump(flow, f, indent=2)

print("✓ Added LangFlow MCP Tool to Simple Agent")
```

## What You Get

Once added, the Simple Agent can:
- Execute LangFlow workflows
- Test connections
- List available flows
- Run code analysis, GUI enhancement, security audits

## Test It

In LangFlow playground, ask the agent:
```
"List available langflow workflows"
"Test langflow connection"
"Run analyze_code workflow"
```
