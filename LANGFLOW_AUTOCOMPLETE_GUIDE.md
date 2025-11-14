# 🌊 LangFlow Autocomplete Integration for Continue.dev

**Project**: ULTRON Agent 3.0
**Purpose**: Connect LangFlow workflows to Continue.dev for enhanced autocomplete
**Date**: November 4, 2025
**Status**: ✅ Ready to Configure

---

## 📊 Current Status

| Component | Status | Location |
|-----------|--------|----------|
| LangFlow Server | ✅ Enabled | `http://127.0.0.1:7861` |
| Continue.dev Config | ✅ Set up | `.continue/config.json` |
| LangFlow Flow | ⏳ To Create | LangFlow UI |
| Integration | ⏳ To Connect | Continue API settings |

---

## 🎯 Why LangFlow for Autocomplete?

### Benefits
- **Chain multiple models** in single autocomplete flow
- **Add custom logic** (syntax checking, security validation)
- **Memory & context** handling
- **Rate limiting** and caching
- **Custom evaluation** of suggestions

### Example Flow
```
User types code
    ↓
LangFlow receives prompt
    ↓
Model 1: Check syntax (fast)
    ↓
Model 2: Generate completion (accuracy)
    ↓
Model 3: Security check (validation)
    ↓
Return best suggestion to Continue.dev
```

---

## 🚀 Quick Setup (10 Minutes)

### Step 1: Start LangFlow Server

```powershell
# Option A: Via Python pip
pip install langflow
langflow run

# Option B: Via Docker
docker run -p 7861:7861 langflowai/langflow

# Option C: Check if already running
curl http://127.0.0.1:7861/

# Expected: HTML page loads (LangFlow UI)
```

**Verify**: Open browser to `http://127.0.0.1:7861/` - Should see LangFlow UI

### Step 2: Create New Flow in LangFlow

1. Open http://127.0.0.1:7861/
2. Click **"New Project"** → Name it `ULTRON Autocomplete`
3. In the canvas, add these components:

**A. Input Node**
- Name: `code_context`
- Type: String

**B. Model Node (Ollama)**
- Provider: Ollama
- Model: `qwen2.5-coder:1.5b`
- Prompt:
```
Complete this code based on context:

PREFIX:
{prefix}

SUFFIX:
{suffix}

FILEPATH: {filepath}

Complete the code snippet. Return ONLY the completion, no explanation.
```

**C. Output Node**
- Name: `completion`
- Input: Connected to Model output

### Step 3: Save & Deploy Flow

1. Click **"Save"** button (top right)
2. Note the **Flow ID** shown in URL or settings
3. Click **"Deploy"** to make it accessible via API

### Step 4: Get Flow API Endpoint

The endpoint will be:
```
http://127.0.0.1:7861/api/v1/run/{FLOW_ID}
```

---

## 🔧 Configure Continue.dev to Use LangFlow

### Option A: LangFlow Model Provider

Edit `.continue/config.json`:

```json
{
  "models": [
    {
      "name": "LangFlow Autocomplete",
      "provider": "ollama",
      "model": "qwen2.5-coder:1.5b",
      "roles": ["autocomplete"],
      "autocompleteOptions": {
        "disable": false,
        "maxPromptTokens": 512,
        "debounceDelay": 100,
        "modelTimeout": 150,
        "maxSuffixPercentage": 0.2,
        "prefixPercentage": 0.3
      }
    }
  ]
}
```

### Option B: Custom LangFlow Integration

For more control, use a custom completion handler. Create `.continue/langflow_autocomplete.py`:

```python
# .continue/langflow_autocomplete.py
import requests
import json
from typing import Optional

class LangFlowAutocomplete:
    def __init__(self, flow_id: str, base_url: str = "http://127.0.0.1:7861"):
        self.flow_id = flow_id
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/run/{flow_id}"

    async def get_completion(
        self,
        prefix: str,
        suffix: str,
        filepath: str
    ) -> Optional[str]:
        """Get code completion from LangFlow"""

        payload = {
            "input_value": {
                "prefix": prefix,
                "suffix": suffix,
                "filepath": filepath
            },
            "output_type": "chat"
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=2.0  # Fast timeout for autocomplete
            )

            if response.status_code == 200:
                data = response.json()
                # Extract completion from LangFlow output
                completion = data.get("output", {}).get("message", "")
                return completion.strip()

            return None

        except Exception as e:
            print(f"LangFlow error: {e}")
            return None

# Usage
langflow = LangFlowAutocomplete(flow_id="your-flow-id-here")
completion = await langflow.get_completion(
    prefix="def hello(",
    suffix=":\n    pass",
    filepath="test.py"
)
```

---

## 🔗 Connect LangFlow to Continue.dev

### Method 1: Via Environment Variable

```powershell
# PowerShell
$env:LANGFLOW_FLOW_ID = "your-flow-id-here"
$env:LANGFLOW_BASE_URL = "http://127.0.0.1:7861"

# Verify
Write-Host $env:LANGFLOW_FLOW_ID
```

### Method 2: Via Continue Config

Add to `.continue/config.json`:

```json
{
  "experimental": {
    "langflow": {
      "enabled": true,
      "flowId": "your-flow-id-here",
      "baseUrl": "http://127.0.0.1:7861",
      "timeout": 2000
    }
  }
}
```

### Method 3: Via Ultron Config

Add to `ultron_config.json`:

```json
{
  "langflow_enabled": true,
  "langflow_flow_id": "your-flow-id-here",
  "langflow_host": "127.0.0.1",
  "langflow_port": 7861,
  "langflow_api_url": "http://127.0.0.1:7861",
  "langflow_autocomplete_enabled": true,
  "langflow_autocomplete_flow_id": "autocomplete-flow-id"
}
```

---

## 🧪 Test LangFlow Autocomplete

### Test 1: Direct API Call

```powershell
# Replace YOUR_FLOW_ID with actual ID
$flowId = "YOUR_FLOW_ID"
$body = @{
    "input_value" = @{
        "prefix" = "def hello("
        "suffix" = ":\n    pass"
        "filepath" = "test.py"
    }
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://127.0.0.1:7861/api/v1/run/$flowId" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

**Expected Response**:
```json
{
  "output": {
    "message": "): # Complete function body here",
    "type": "string"
  }
}
```

### Test 2: In VS Code

1. Open any `.py` file
2. Type: `def my_func(`
3. Wait 100-200ms
4. Should see suggestion

### Test 3: Check Logs

```
VS Code → Output → Continue
# Should see log entries like:
# "Requesting LangFlow autocomplete: def my_func("
# "LangFlow response: ): # ..."
```

---

## 🎨 Advanced: Multi-Model LangFlow Flow

Create a complex flow combining multiple models:

```
Input (code context)
    ↓
    ├→ Model 1 (syntax check)
    │   └→ Output A
    ├→ Model 2 (completion)
    │   └→ Output B
    └→ Model 3 (security check)
        └→ Output C
    ↓
Combiner (merge results)
    ↓
Output (best suggestion)
```

**LangFlow Setup**:

1. Add 3 Model nodes:
   - Model 1: `qwen2.5-coder:1.5b` (syntax)
   - Model 2: `deepseek-r1:8b` (logic)
   - Model 3: `qwen2.5-coder:7b` (security)

2. Add Combiner logic:
   ```
   Select suggestion from Model 2
   If Model 3 approves (security check)
   If Model 1 confirms (syntax ok)
   Return suggestion
   ```

3. Use Custom Code node:
   ```python
   def select_best_suggestion(syntax_ok, security_ok, completion):
       if syntax_ok and security_ok:
           return completion
       else:
           return None  # No suggestion if fails checks
   ```

---

## 📋 Configuration Checklist

- [ ] LangFlow server running (`http://127.0.0.1:7861/` loads)
- [ ] New project created in LangFlow UI
- [ ] Flow components added (Input, Model, Output)
- [ ] Flow saved and deployed
- [ ] Flow ID copied from URL
- [ ] `.continue/config.json` updated with model settings
- [ ] `ultron_config.json` updated with LangFlow settings
- [ ] Environment variables set (`LANGFLOW_FLOW_ID`)
- [ ] Direct API test successful (PowerShell test)
- [ ] VS Code autocomplete test successful

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "LangFlow not responding" | Check if server running: `curl http://127.0.0.1:7861/` |
| "Flow not found" | Verify Flow ID is correct and flow is deployed |
| "Timeout errors" | Increase `modelTimeout` in autocomplete options |
| "Empty completions" | Check LangFlow flow logic and test directly |
| "CORS errors" | LangFlow CORS usually allows localhost - check headers |
| "No suggestions appearing" | Check `.continue/logs/` for error messages |

---

## 🔒 Security Notes

- LangFlow runs locally on `127.0.0.1:7861` (not exposed to internet)
- No API key needed for local LangFlow
- If exposing LangFlow to network: add authentication
- Consider rate limiting for production

---

## 📚 Integration Points

### With Continue.dev
- Autocomplete suggestions
- Chat context enrichment
- Code analysis

### With ULTRON Agent
- Brain integration (via tools/langflow_mcp_tool.py)
- Command execution
- Memory integration

### With Web GUI
- Real-time suggestions in editor
- Flow monitoring dashboard
- Performance metrics

---

## 🎯 Success Criteria

✅ LangFlow server accessible at `http://127.0.0.1:7861/`
✅ Autocomplete flow created and deployed
✅ Continue.dev configured to use flow
✅ Direct API tests return valid completions
✅ VS Code shows suggestions when typing
✅ Suggestions appear in <200ms
✅ No timeout or CORS errors in logs

---

## 📖 Example: Complete Working Setup

### ultron_config.json
```json
{
  "langflow_enabled": true,
  "langflow_host": "127.0.0.1",
  "langflow_port": 7861,
  "langflow_api_url": "http://127.0.0.1:7861",
  "langflow_autocomplete_enabled": true,
  "langflow_autocomplete_flow_id": "abc123def456..."
}
```

### .continue/config.json
```json
{
  "models": [
    {
      "name": "LangFlow Autocomplete",
      "provider": "ollama",
      "model": "qwen2.5-coder:1.5b",
      "roles": ["autocomplete"],
      "autocompleteOptions": {
        "disable": false,
        "maxPromptTokens": 512,
        "debounceDelay": 100,
        "modelTimeout": 150,
        "onlyMyCode": true
      }
    }
  ]
}
```

### Test Command
```powershell
# PowerShell
curl -X POST http://127.0.0.1:7861/api/v1/run/abc123def456 `
  -H "Content-Type: application/json" `
  -d '{"input_value":{"prefix":"def hello(","suffix":":\n    pass","filepath":"test.py"}}'

# Expected: JSON response with suggestion
```

---

## 🔗 Resources

- **LangFlow Docs**: https://docs.langflow.org
- **LangFlow GitHub**: https://github.com/langflowai/langflow
- **Continue.dev Autocomplete**: https://docs.continue.dev/customize/deep-dives/autocomplete
- **ULTRON LangFlow Integration**: `tools/langflow_mcp_tool.py`

---

*Created: November 4, 2025*
*Effort: 10-15 minutes to configure*
*Complexity: Medium (requires creating LangFlow flow)*
