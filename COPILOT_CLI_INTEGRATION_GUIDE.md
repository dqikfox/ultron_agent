# Copilot CLI Integration Guide - ULTRON Agent

**Date**: October 30, 2025
**Status**: Ready for Implementation

## Overview

This guide explains how to integrate GitHub Copilot CLI into ULTRON Agent's development workflow for autonomous self-improvement and delegated task execution.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Custom Agents](#custom-agents)
4. [Self-Prompting Automation](#self-prompting-automation)
5. [Integration Points](#integration-points)
6. [Workflow Examples](#workflow-examples)
7. [Advanced Usage](#advanced-usage)

## Prerequisites

- GitHub Copilot Pro, Pro+, Business, or Enterprise plan
- GitHub CLI (`gh`) installed
- Copilot CLI installed (`copilot` command available)
- ULTRON Agent repository cloned
- Python 3.10+

## Installation & Setup

### 1. Install Copilot CLI

```powershell
# Using GitHub CLI (recommended)
gh copilot --version

# Or install from releases
# https://github.com/github/cli/releases
```

### 2. Authenticate with GitHub

```powershell
# Navigate to ULTRON Agent directory
cd C:\Projects\ultron_agent

# Start Copilot CLI
copilot

# When prompted, authenticate:
/login
# Follow browser-based authentication flow
```

### 3. Trust the Project Directory

When starting Copilot CLI in the project:

```
? Do you trust the files in this folder?
> Yes, proceed
> Yes, and remember this folder for future sessions
> No, exit
```

Select "Yes, and remember this folder for future sessions" to avoid repeated prompts.

## Custom Agents

ULTRON Agent includes pre-configured custom agents in `.github/agents/`:

### 1. ULTRON Automation Agent
**File**: `.github/agents/ultron-automation-agent.md`

Purpose: General automation, tool development, CI/CD

```powershell
copilot
/agent

# Select: "ULTRON Automation Agent"
# Then provide your task
```

Example tasks:
```
Create a new tool in tools/ for automated testing orchestration

/delegate Refactor agent_core.py tool discovery to use async/await
```

### 2. Code Optimization Agent
**File**: `.github/agents/code-optimization-agent.md`

Purpose: Performance improvements, code quality, refactoring

```powershell
copilot
Use the code optimization agent to analyze brain.py for bottlenecks

# Or directly
copilot --agent=code-optimization-agent --prompt "Optimize tool caching"
```

## Self-Prompting Automation

### Enable Auto-Run Feature

Edit `ultron_config.json`:

```json
{
  "auto_run": {
    "enabled": true,
    "startup_commands": [
      "copilot quality analysis",
      "copilot performance optimization",
      "copilot documentation generation"
    ],
    "startup_delay_seconds": 5,
    "run_in_background": true,
    "log_auto_commands": true
  }
}
```

### Use the Self-Prompting Tool

The `CopilotCLIAutomationTool` is automatically discovered and available:

```powershell
# In interactive agent mode
copilot
> copilot delegate Analyze and fix code quality issues

# Or via ULTRON command system
python main.py
> copilot self-improve quality
```

### Self-Prompting Orchestrator

For recurring autonomous improvement cycles:

```python
from utils.self_prompting_orchestrator import SelfPromptingOrchestrator

orchestrator = SelfPromptingOrchestrator()

# Start single improvement cycle
await orchestrator.start_improvement_cycle(
    cycle_name="quality_improvement",
    goals=["improve code quality", "add type hints", "update docs"],
    priority="high"
)

# Schedule recurring cycles
await orchestrator.schedule_recurring_cycle(
    cycle_name="daily_optimization",
    goals=["performance improvement", "documentation"],
    interval_hours=24,
    priority="medium"
)

# Check status
print(orchestrator.get_improvement_status())
```

## Integration Points

### 1. Agent Core Integration

Add to `agent_core.py` startup sequence:

```python
# Initialize Copilot CLI tool
from tools.copilot_cli_automation_tool import CopilotCLIAutomationTool

self.copilot_cli_tool = CopilotCLIAutomationTool()

# Log availability
if self.copilot_cli_tool.copilot_available:
    log_info("agent_core", "Copilot CLI available for automation")
```

### 2. Event System Integration

Subscribe to improvement events:

```python
async def on_improvement_task_start(data):
    log_info("agent_core", f"Improvement task started: {data['title']}")

await event_system.subscribe(
    "improvement_task_start",
    on_improvement_task_start
)
```

### 3. API Server Endpoints

New endpoints in `api_server.py`:

```python
@app.route("/api/copilot/delegate", methods=["POST"])
def delegate_task():
    """Delegate a task to Copilot CLI"""
    data = request.get_json()
    task = data.get("task", "")
    priority = data.get("priority", "medium")

    result = AGENT_INSTANCE.copilot_cli_tool.execute(
        f"delegate {task}"
    )
    return jsonify({"result": result}), 200

@app.route("/api/copilot/workflow", methods=["POST"])
def run_workflow():
    """Execute a workflow"""
    data = request.get_json()
    workflow = data.get("workflow", "")

    result = AGENT_INSTANCE.copilot_cli_tool.execute(
        f"workflow {workflow}"
    )
    return jsonify({"result": result}), 200

@app.route("/api/copilot/status", methods=["GET"])
def copilot_status():
    """Get Copilot CLI status"""
    status = AGENT_INSTANCE.copilot_cli_tool.execute("status")
    return jsonify(json.loads(status)), 200
```

### 4. GitHub Actions Integration

Create `.github/workflows/copilot-auto-improve.yml`:

```yaml
name: Copilot Auto-Improve

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  improve:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          brew install gh copilot  # On macOS

      - name: Run improvement cycle
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_COPILOT_TOKEN: ${{ secrets.COPILOT_API_TOKEN }}
        run: |
          python -c "
          import asyncio
          from utils.self_prompting_orchestrator import SelfPromptingOrchestrator

          orchestrator = SelfPromptingOrchestrator()
          asyncio.run(orchestrator.start_improvement_cycle(
              cycle_name='auto_improve_${{ github.run_number }}',
              goals=['performance', 'quality', 'documentation'],
              priority='medium'
          ))
          "
```

## Workflow Examples

### Example 1: Quality Scan Workflow

```powershell
copilot
```

```
> copilot workflow quality_scan

✅ Run pylint on all Python files and fix violations
✅ Generate type hints using pyright analysis
✅ Create missing docstrings for public API
✅ Refactor functions with high cyclomatic complexity

Workflow 'quality_scan' completed: 4 tasks executed
```

### Example 2: Delegating Code Optimization

```powershell
copilot
```

```
> delegate Optimize agent_core.py tool discovery mechanism

ULTRON Agent 3.0 - Multi-modal AI platform...
Task: Optimize agent_core.py tool discovery mechanism

Copilot will:
1. Analyze current tool loading approach
2. Identify performance bottlenecks
3. Design caching strategy
4. Implement optimizations
5. Create tests

Create PR #123: Optimize tool discovery with caching
https://github.com/dqikfox/ultron_agent/pull/123
```

### Example 3: Self-Prompting Improvement

```python
from utils.self_prompting_orchestrator import SelfPromptingOrchestrator

orchestrator = SelfPromptingOrchestrator()

# Define improvement goals
goals = [
    "Reduce brain.py response latency",
    "Improve error handling coverage",
    "Update API documentation"
]

# Execute improvement cycle
import asyncio
result = asyncio.run(orchestrator.start_improvement_cycle(
    cycle_name="performance_sprint",
    goals=goals,
    priority="high"
))

print(f"Completed: {result['completed']}/{result['total_tasks']}")
print(f"Success Rate: {result['success_rate']:.1%}")
```

## Advanced Usage

### 1. Conditional Task Delegation

```python
from tools.copilot_cli_automation_tool import CopilotCLIAutomationTool
from utils.model_awareness import should_modify_file

cli_tool = CopilotCLIAutomationTool()

# Check if modification is safe
should_proceed, reason, context = should_modify_file(
    "agent_core.py",
    "optimization",
    "copilot-cli"
)

if should_proceed:
    result = cli_tool.execute("delegate Optimize agent_core.py")
else:
    print(f"Cannot modify: {reason}")
```

### 2. Custom Task Generation

```python
from utils.self_prompting_orchestrator import SelfPromptingOrchestrator

class CustomOrchestrator(SelfPromptingOrchestrator):
    async def _generate_improvement_tasks(self, goal, priority):
        """Generate domain-specific tasks"""
        if "voice" in goal.lower():
            return [
                {
                    "id": "voice_001",
                    "title": "Improve voice recognition accuracy",
                    "priority": priority,
                    "target_file": "voice.py"
                },
                {
                    "id": "voice_002",
                    "title": "Optimize TTS latency",
                    "priority": priority,
                    "target_file": "voice.py"
                }
            ]
        return await super()._generate_improvement_tasks(goal, priority)
```

### 3. Integration with MCP Servers

```python
# Use Copilot CLI with MCP context
copilot
```

```
/mcp add
# Enter MCP server details

/add-dir /path/to/custom/directory

> delegate Integrate with custom MCP server for workflow automation
```

### 4. Session Management

```powershell
# Resume previous session
copilot --resume

# Continue most recent session
copilot --continue

# Get usage statistics
copilot
> /usage
```

## Tips & Best Practices

### 1. Approval Workflow

Always review before major changes:
```powershell
copilot
> delegate Refactor core authentication system

# When Copilot asks to modify files
# Review the changes before approving
> Yes, proceed with caution
```

### 2. Task Prioritization

Organize complex work:
```
/delegate High: Fix critical performance regression in brain.py
/delegate Medium: Add type hints to utils/
/delegate Low: Improve documentation formatting
```

### 3. Batch Operations

For large refactors:
```
# Break into smaller tasks
/delegate Step 1: Analyze current patterns in agent_core.py
/delegate Step 2: Design new architecture for tool discovery
/delegate Step 3: Implement and test new approach
/delegate Step 4: Update documentation
```

### 4. Verification

Always verify automatic improvements:
```powershell
# After delegation completes
pytest
pytest --cov=. --cov-report=html
git diff
```

### 5. Logging

Check improvement cycle logs:
```powershell
# View orchestrator logs
Get-Content logs\ai_activities.log -Tail 100 | Select-String "improvement"

# View Copilot CLI interactions
Get-Content logs\brain.log | Select-String "copilot"
```

## Troubleshooting

### Copilot CLI Not Found

```powershell
# Check installation
which copilot
# or
Get-Command copilot

# Install if needed
gh copilot --version
```

### Authentication Issues

```powershell
copilot
/login
# Verify GitHub token has necessary scopes
```

### Task Delegation Fails

```powershell
# Check logs
Get-Content logs\ai_activities.log -Tail 50

# Test connectivity
curl https://api.github.com/user
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│         ULTRON Agent v3.0                       │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │   Copilot CLI Integration Layer         │  │
│  │                                          │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │ CopilotCLIAutomationTool          │ │  │
│  │  │ - delegate()                       │ │  │
│  │  │ - workflow()                       │ │  │
│  │  │ - self_prompt()                    │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                                          │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │ SelfPromptingOrchestrator          │ │  │
│  │  │ - improvement_cycle()               │ │  │
│  │  │ - recurring_cycle()                 │ │  │
│  │  └────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
│                   │                             │
│                   ▼                             │
│  ┌──────────────────────────────────────────┐  │
│  │   Event System                           │  │
│  │ (improvement_cycle_start, etc.)         │  │
│  └──────────────────────────────────────────┘  │
│                   │                             │
└───────────────────┼─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    ┌─────────┐         ┌─────────────┐
    │ Copilot │         │  GitHub     │
    │   CLI   │         │  Actions    │
    │         │         │             │
    │ - Local │         │ - Schedule  │
    │ - Agent │         │ - Run tests │
    │ - MCP   │         │ - Validate  │
    └─────────┘         └─────────────┘
```

## Related Documentation

- `.github/copilot-instructions.md` - Main developer instructions
- `.github/agents/ultron-automation-agent.md` - Automation agent guide
- `.github/agents/code-optimization-agent.md` - Optimization agent guide
- `MCP_INTEGRATION_GUIDE.md` - MCP server integration
- `COPILOT_CONTINUE_INTEGRATION.md` - Continue.dev integration

## Summary

Copilot CLI integration transforms ULTRON Agent into a self-improving system that can:

✅ Autonomously improve code quality
✅ Optimize performance continuously
✅ Generate and maintain documentation
✅ Create comprehensive test coverage
✅ Handle technical debt proactively
✅ Coordinate with GitHub workflows

This creates a **feedback loop of continuous improvement** where the agent itself becomes an active participant in its own evolution.

---

**Maintained By**: ULTRON Development Team
**Last Updated**: October 30, 2025
**Version**: 1.0
