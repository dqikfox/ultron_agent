# Copilot CLI Self-Prompting Quick Start

**Get ULTRON Agent autonomously improving itself in 5 minutes.**

## 1. Install & Authenticate (1 minute)

```powershell
# Verify Copilot CLI is installed
copilot --version

# If not installed, use GitHub CLI
gh copilot --version

# Navigate to project
cd C:\Projects\ultron_agent

# Start Copilot CLI
copilot
```

When prompted for trust:
```
? Do you trust the files in this folder?
YES, and remember this folder
```

## 2. Authenticate (1 minute)

In Copilot CLI prompt:
```
/login
# Follow browser authentication
```

## 3. Try an Automation Agent (2 minutes)

```
/agent
# Select: ULTRON Automation Agent
```

Example delegations:

**Quick Analysis:**
```
/delegate Analyze agent_core.py for code quality issues
```

**Tool Creation:**
```
/delegate Create a new tool for performance profiling
```

**Documentation:**
```
/delegate Generate API documentation for api_server.py
```

## 4. Enable Self-Prompting (1 minute)

Edit `ultron_config.json`:

```json
{
  "auto_run": {
    "enabled": true,
    "startup_commands": [
      "copilot self-improve quality"
    ]
  }
}
```

Start ULTRON:
```powershell
python main.py
```

The system will autonomously delegate improvement tasks.

---

## Key Commands

| Command | Purpose |
|---------|---------|
| `copilot` | Start interactive CLI |
| `/login` | Authenticate |
| `/agent` | Select custom agent |
| `/delegate <task>` | Hand off work to Copilot |
| `/workflow <name>` | Run multi-step workflow |
| `/usage` | View token usage |
| `?` | Show help |

## Available Workflows

- **quality_scan** - Code quality improvements
- **optimization** - Performance optimization
- **documentation** - Documentation generation
- **testing** - Testing improvements

## Example Automation

### Scenario: Autonomous Daily Improvement

```powershell
# 1. Start Copilot
copilot

# 2. Schedule daily improvement
/delegate Schedule daily code quality improvements at 2 AM UTC

# 3. Track progress
/usage

# 4. Exit
exit
```

### Scenario: Performance Sprint

```
/agent
# Select: Code Optimization Agent

/delegate Optimize brain.py response time by 30%

/delegate Implement caching for tool discovery

/delegate Profile startup performance
```

## Next Steps

📚 **Read Full Guide**: `COPILOT_CLI_INTEGRATION_GUIDE.md`
🔧 **Custom Agents**: `.github/agents/`
🤖 **Orchestrator API**: `utils/self_prompting_orchestrator.py`
🔗 **Integration Points**: `tools/copilot_cli_automation_tool.py`

---

**Status**: ✅ Ready to use
**Date**: October 30, 2025
