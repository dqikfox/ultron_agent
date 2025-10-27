# GitHub Copilot & AI Assistant Integration

## Multi-AI Assistant Coordination

ULTRON Agent works alongside multiple AI assistants in VS Code. This document explains how Continue.dev, GitHub Copilot, and other AI tools coordinate for maximum productivity.

## Active AI Assistants in ULTRON

### 1. GitHub Copilot
**Purpose**: Real-time code suggestions and completions
**Triggers**: Automatically as you type
**Best For**:
- Inline code completion
- Function implementation suggestions
- Boilerplate code generation
- Common patterns and idioms

**Usage**:
```python
# Type a comment and Copilot suggests implementation
# Calculate Fibonacci sequence

# Copilot suggests:
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 2. Continue.dev (This Extension)
**Purpose**: Context-aware AI assistance with codebase knowledge
**Triggers**: Manual (Ctrl+I) or selection-based
**Best For**:
- Understanding ULTRON architecture
- Refactoring with project context
- Debugging with access to logs and terminal
- Following ULTRON coding standards

**Usage**:
```
Press Ctrl+I and ask:
"How do I add a new tool to ULTRON?"
"Refactor this to use async/await"
"Debug this Ollama connection issue"
```

### 3. Amazon Q (CodeWhisperer)
**Purpose**: AWS-optimized code generation
**Best For**:
- AWS service integration
- Security scanning
- Enterprise code patterns

### 4. Sixth AI
**Purpose**: Advanced inline completions
**Best For**:
- Multi-line predictions
- Context-aware suggestions

### 5. Pochi/Tabby
**Purpose**: MCP-enabled AI assistant
**Best For**:
- Model Context Protocol operations
- Tool coordination

## Integration Strategy

### When to Use Each Assistant

#### Use GitHub Copilot When:
- ✅ Writing new functions (let it suggest implementation)
- ✅ Creating test cases (fast boilerplate)
- ✅ Implementing common patterns (API endpoints, error handling)
- ✅ Writing docstrings and comments
- ✅ Converting comments to code

#### Use Continue.dev When:
- ✅ Need ULTRON-specific context (service ports, architecture)
- ✅ Following coding standards (mandatory logging, model awareness)
- ✅ Understanding existing code (references rules and docs)
- ✅ Complex refactoring (understands project structure)
- ✅ Debugging issues (access to logs, terminal, git diff)
- ✅ API design (references internal.docs standards)

#### Use Amazon Q When:
- ✅ AWS integration code
- ✅ Security vulnerability scanning
- ✅ Cloud architecture questions

## Coordination Patterns

### Pattern 1: Copilot → Continue.dev
```python
# 1. Copilot generates initial code
def process_voice_command(command: str):
    # Copilot suggests basic implementation
    result = parse_command(command)
    return result

# 2. Select code → Ctrl+I → "Refactor to follow ULTRON standards"
# Continue.dev adds:
# - Logging via utils.ultron_logger
# - Model awareness check
# - Event system integration
# - Error handling

from utils.ultron_logger import log_info, log_error
from utils.event_system import get_event_system

async def process_voice_command(command: str) -> str:
    """Process voice command through ULTRON system."""
    log_info("voice_processor", f"Processing: {command}")

    try:
        event_system = get_event_system()
        await event_system.emit("voice_command_start", {"command": command})

        result = await parse_command(command)

        await event_system.emit("voice_command_complete", {"result": result})
        return result
    except Exception as e:
        log_error("voice_processor", f"Error: {e}", exception=e)
        raise
```

### Pattern 2: Continue.dev → Copilot
```python
# 1. Ask Continue.dev: "Show me the pattern for a new tool"
# Continue.dev provides ULTRON-specific template

# 2. Start implementing with template
# Copilot fills in implementation details

class MyNewTool(ToolInterface):
    # Copilot suggests property implementations
    @property
    def name(self) -> str:
        return "My New Tool"

    # Copilot suggests match logic
    def match(self, command: str) -> bool:
        keywords = ["my", "new", "tool"]
        return any(kw in command.lower() for kw in keywords)
```

### Pattern 3: Multi-Assistant Review
```python
# 1. Write initial code (with Copilot)
# 2. Ask Continue.dev: "Review this code"
# 3. Amazon Q: Security scan
# 4. Final manual review
```

## GitHub Copilot Specific Integration

### Access GitHub Resources
Continue.dev can interact with GitHub through MCP:

```yaml
# Already configured in config.yaml:
mcpServers:
  - name: github
    command: npx
    args: ["-y", "@anthropic-ai/mcp-server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN}
```

**Usage in Continue.dev**:
```
"Search ULTRON GitHub issues for voice system bugs"
"Show me recent commits to agent_core.py"
"List open PRs in ultron_agent repository"
"Create GitHub issue for new feature: X"
```

### GitHub CLI Integration
Continue.dev understands GitHub CLI commands:

```bash
# Search code across repositories
gh search code --owner dqikfox "voice_enabled"

# List issues
gh issue list --repo dqikfox/ultron_agent --label bug

# Create PR
gh pr create --title "feat: Add new tool" --body "Description"

# View PR
gh pr view 123
```

## ULTRON-Specific Copilot Patterns

### Tool Development
```python
# Type comment: "Create tool for system monitoring"
# Copilot suggests structure, Continue.dev adds ULTRON patterns

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info  # Continue.dev adds this

class SystemMonitorTool(ToolInterface):
    # Copilot generates, Continue.dev ensures standards
```

### API Endpoints
```python
# Type: "Create Flask endpoint for tool status"
# Copilot generates Flask code
@app.route("/api/tools/status", methods=["GET"])
def tool_status():
    # Continue.dev adds: error handling, logging, ULTRON patterns
    if not AGENT_INSTANCE:
        return jsonify({"error": "Agent not initialized"}), 500
```

### Event Handling
```python
# Copilot generates event subscription
# Continue.dev adds ULTRON event system patterns
async def handle_command(data):
    # Copilot suggests implementation
    # Continue.dev ensures logging and error handling
```

## Best Practices

### 1. Let Each Assistant Do What It's Best At
```
Copilot: Fast code generation, common patterns
Continue.dev: ULTRON architecture, standards, refactoring
Amazon Q: AWS and security
```

### 2. Review AI-Generated Code
```
1. Let Copilot generate initial code
2. Use Continue.dev to review for ULTRON standards
3. Manual check for business logic
```

### 3. Use Comments to Guide Copilot
```python
# Good comment for Copilot:
# "Create async function to query Ollama at localhost:11434"

# Copilot generates better code with context:
async def query_ollama(prompt: str, model: str = "llava:7b"):
    # Implementation follows
```

### 4. Use Continue.dev for Complex Queries
```
Bad: Ask Copilot in comments for architecture advice
Good: Ctrl+I → Ask Continue.dev about ULTRON patterns
```

### 5. Combine Strengths
```
1. Copilot: Generate function skeleton
2. Continue.dev: "Refactor to follow ULTRON standards"
3. Copilot: Fill implementation details
4. Continue.dev: "Review for errors and improvements"
```

## Keyboard Shortcuts

### GitHub Copilot
- `Tab` - Accept suggestion
- `Esc` - Dismiss suggestion
- `Alt+]` - Next suggestion
- `Alt+[` - Previous suggestion
- `Ctrl+Enter` - Open Copilot panel

### Continue.dev
- `Ctrl+I` - Open agent mode
- `Ctrl+L` - Add to context
- `Ctrl+Shift+R` - Refactor selection
- `Ctrl+Shift+M` - Open chat panel

### Multi-Select Workflow
```
1. Write code with Copilot (Tab to accept)
2. Select code block
3. Ctrl+I → "Refactor for ULTRON standards"
4. Tab through Continue.dev suggestions
5. Repeat as needed
```

## GitHub Integration Features

### Repository Operations
```
Continue.dev can now:
- Search code across repositories
- View and create issues
- List and create PRs
- View commit history
- Clone repositories
- Read file contents
```

### Example Workflows

#### Bug Investigation
```
You: "Search for voice_enabled in ULTRON repository"
Continue.dev: Uses GitHub MCP to search code
Continue.dev: Shows relevant files with context
You: Select code → "Explain this implementation"
```

#### Feature Development
```
1. Copilot generates initial code
2. Continue.dev: "Create GitHub issue for this feature"
3. Continue.dev: Issue created with context
4. Develop feature with both assistants
5. Continue.dev: "Create PR for this feature"
```

#### Code Review
```
You: "Show me recent changes to brain.py"
Continue.dev: Uses GitHub MCP to fetch commits
Continue.dev: Displays git diff with explanations
You: "Review these changes for issues"
Continue.dev: Analyzes with ULTRON context
```

## Conflict Resolution

### When Assistants Disagree

**Copilot suggests**: Simple implementation
**Continue.dev suggests**: ULTRON-compliant implementation

**Resolution**: Use Continue.dev's suggestion (follows project standards)

**Example**:
```python
# Copilot suggests:
def log(msg):
    print(msg)

# Continue.dev suggests:
from utils.ultron_logger import log_info
log_info("component", msg)

# Use Continue.dev's version (follows ULTRON standards)
```

### Priority Order
```
1. ULTRON coding standards (Continue.dev)
2. Python best practices (Copilot/Continue.dev)
3. Performance optimization (Continue.dev with context)
4. Security (Amazon Q)
```

## Productivity Tips

### 1. Use Copilot for Speed
Let Copilot generate first draft quickly

### 2. Use Continue.dev for Quality
Refactor with ULTRON context for maintainability

### 3. Leverage GitHub MCP
Access repository data without leaving editor

### 4. Combine Context
- Copilot learns from your code
- Continue.dev learns from rules and docs
- Together they understand your intent better

### 5. Iterate Efficiently
```
Draft (Copilot) → Review (Continue.dev) →
Refine (Copilot) → Validate (Continue.dev)
```

## Environment Setup

### Required Extensions
- ✅ GitHub Copilot
- ✅ Continue.dev (this extension)
- ✅ Amazon Q (optional)
- ✅ GitLens (enhanced git integration)

### Environment Variables
```powershell
# For GitHub MCP integration
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_your_token"

# For ULTRON services
$env:ELEVENLABS_APIKEY = "your_key"
$env:POSTGRES_CONNECTION_STRING = "postgresql://..."
```

### VS Code Settings
```json
{
  "github.copilot.enable": true,
  "continue.enableTabAutocomplete": true,
  "continue.enableCodeLens": true,
  "github.copilot.inlineSuggest.enable": true,
  "editor.inlineSuggest.enabled": true,
  "editor.quickSuggestions": {
    "comments": true,
    "strings": true,
    "other": true
  }
}
```

## Summary

### GitHub Copilot
- Fast code generation
- Inline suggestions
- Common patterns

### Continue.dev
- ULTRON architecture awareness
- Project standards enforcement
- Complex refactoring
- GitHub integration via MCP
- Access to logs, terminal, git

### Together
- Copilot generates → Continue.dev refines
- Speed + Quality
- Pattern + Context
- Individual + Team Standards

**Use both assistants strategically for maximum productivity!** 🚀
