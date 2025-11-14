# MCP Servers for Amazon Q - ULTRON Agent Enhancement

## Overview

This configuration adds 15+ MCP (Model Context Protocol) servers to enhance Amazon Q's capabilities when working with the ULTRON Agent project. These servers provide specialized tools for development, debugging, deployment, and system management.

## Quick Start

```bash
# Install MCP servers globally
npm install -g @modelcontextprotocol/server-*

# Verify installation
npx @modelcontextprotocol/server-inspector --version
```

## MCP Servers Configured

### 🔧 Core Development Tools

#### 1. **Memory Server**
- **Purpose**: Persistent context across sessions
- **Use Cases**: Remember project decisions, track changes, maintain conversation history
- **Command**: `npx @modelcontextprotocol/server-memory`

#### 2. **Sequential Thinking**
- **Purpose**: Enhanced reasoning with step-by-step analysis
- **Use Cases**: Complex debugging, architecture decisions, multi-step refactoring
- **Command**: `npx @modelcontextprotocol/server-sequential-thinking`

#### 3. **Filesystem Server**
- **Purpose**: Direct workspace file access
- **Use Cases**: Read/write files, directory traversal, file search
- **Scope**: `${workspaceFolder}` (ULTRON Agent root)

### 🌐 Web & Browser Automation

#### 4. **Browser MCP**
- **Purpose**: Browser automation and control
- **Use Cases**: Test web GUI, automate workflows, scrape documentation
- **Command**: `npx @browsermcp/mcp@latest`

#### 5. **Puppeteer Server**
- **Purpose**: Headless browser automation
- **Use Cases**: Screenshot testing, PDF generation, web scraping
- **Command**: `npx @modelcontextprotocol/server-puppeteer`

#### 6. **Fetch Server**
- **Purpose**: HTTP requests and API testing
- **Use Cases**: Test REST endpoints, validate API responses, debug integrations
- **Command**: `npx @modelcontextprotocol/server-fetch`

### 🗄️ Database & Storage

#### 7. **SQLite Server**
- **Purpose**: Avatar game database access
- **Database**: `avatar_game.db`
- **Use Cases**: Query conversations, manage avatars, analyze game data
- **Command**: `npx @modelcontextprotocol/server-sqlite avatar_game.db`

#### 8. **PostgreSQL Server**
- **Purpose**: Production database integration
- **Use Cases**: Supabase integration, data migration, analytics
- **Requires**: `POSTGRES_CONNECTION_STRING` environment variable

### ☁️ Cloud & Infrastructure

#### 9. **AWS Server**
- **Purpose**: AWS services integration
- **Services**: Bedrock, Lambda, S3, Polly, Secrets Manager
- **Region**: `us-east-1` (configurable)
- **Use Cases**: Deploy functions, manage storage, AI model access

#### 10. **Docker Server**
- **Purpose**: Container management
- **Use Cases**: Build images, manage containers, orchestrate services
- **Command**: `npx @modelcontextprotocol/server-docker`

### 🔄 Version Control & Collaboration

#### 11. **Git Server**
- **Purpose**: Git operations and repository management
- **Use Cases**: Commit changes, branch management, merge conflicts
- **Command**: `npx @modelcontextprotocol/server-git`

#### 12. **GitHub Server**
- **Purpose**: GitHub API integration
- **Use Cases**: Create issues, manage PRs, review code, CI/CD
- **Requires**: `GITHUB_PERSONAL_ACCESS_TOKEN`

#### 13. **Slack Server**
- **Purpose**: Team communication integration
- **Use Cases**: Send notifications, create channels, post updates
- **Requires**: `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`

### 🤖 AI & ML Integration

#### 14. **Ollama Server**
- **Purpose**: Local AI model management
- **Host**: `http://localhost:11434`
- **Use Cases**: Model switching, inference testing, performance monitoring
- **Models**: llava:7b, qwen3-coder, deepseek-r1

#### 15. **LangFlow Server**
- **Purpose**: Workflow automation and flow execution
- **Port**: 7860
- **Use Cases**: Execute AI workflows, manage flows, test integrations
- **Requires**: LangFlow API key and project ID

### 🔍 Utilities

#### 16. **Search Server (Brave)**
- **Purpose**: Web search for documentation and solutions
- **Use Cases**: Find API docs, research solutions, discover libraries
- **Requires**: `BRAVE_API_KEY`

#### 17. **Time Server**
- **Purpose**: Time and timezone utilities
- **Use Cases**: Timestamp generation, timezone conversion, scheduling

#### 18. **Inspector Server**
- **Purpose**: MCP server introspection
- **Use Cases**: Debug MCP connections, test tools, validate configurations

#### 19. **Python Environment Server**
- **Purpose**: Python environment introspection
- **Use Cases**: Check packages, manage dependencies, validate imports
- **PYTHONPATH**: `${workspaceFolder}`

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# GitHub Integration
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# PostgreSQL (Supabase)
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/ultron_db

# LangFlow
LANGFLOW_API_KEY=sk-your_api_key_here
LANGFLOW_PROJECT_ID=e6ecbc04-8495-41c2-b078-f9c3bec09411

# Brave Search
BRAVE_API_KEY=BSA_your_api_key_here

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_TEAM_ID=T01234567

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Ollama
OLLAMA_HOST=http://localhost:11434
```

### Testing MCP Servers

```bash
# Test memory server
npx @modelcontextprotocol/server-memory

# Test filesystem access
npx @modelcontextprotocol/server-filesystem C:\Projects\ultron_agent

# Test Ollama integration
npx @modelcontextprotocol/server-ollama

# Test Git operations
npx @modelcontextprotocol/server-git

# Test AWS integration
npx @modelcontextprotocol/server-aws
```

## Usage Examples

### Example 1: Code Review with Memory
```
Amazon Q: Review the changes in agent_core.py and remember the architectural decisions.
[Uses: filesystem, memory, sequential-thinking]
```

### Example 2: Deploy to AWS
```
Amazon Q: Deploy the latest Lambda function to AWS and update the S3 bucket.
[Uses: aws, git, filesystem]
```

### Example 3: Database Query
```
Amazon Q: Show me the top 10 avatars by conversation count from the game database.
[Uses: sqlite]
```

### Example 4: Web Testing
```
Amazon Q: Test the Pokédex GUI at localhost:8080 and take screenshots.
[Uses: puppeteer, fetch]
```

### Example 5: Documentation Search
```
Amazon Q: Search for FastAPI WebSocket documentation and best practices.
[Uses: search, fetch]
```

## Benefits for Amazon Q

### 🚀 Enhanced Capabilities
- **Persistent Memory**: Remember context across sessions
- **Direct File Access**: Read/write without manual copy-paste
- **Database Queries**: Analyze data directly
- **Cloud Operations**: Deploy and manage infrastructure
- **Web Automation**: Test and validate UIs

### 🎯 Improved Efficiency
- **Faster Development**: Direct tool access reduces manual steps
- **Better Context**: Memory server maintains project knowledge
- **Automated Testing**: Browser automation for validation
- **Integrated Workflows**: LangFlow for complex operations

### 🔒 Security & Control
- **Scoped Access**: Filesystem limited to workspace
- **Token Management**: Secure credential handling
- **Audit Trail**: All operations logged
- **Permission Control**: Fine-grained access control

## Troubleshooting

### MCP Server Not Found
```bash
# Install missing server
npm install -g @modelcontextprotocol/server-<name>

# Verify installation
npx @modelcontextprotocol/server-<name> --version
```

### Connection Timeout
```bash
# Check server status
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:7860/health     # LangFlow

# Restart services
.\run.bat  # ULTRON Agent
```

### Permission Denied
```bash
# Windows: Run as Administrator
# Linux/Mac: Check file permissions
chmod +x mcp_server_script.sh
```

## Advanced Configuration

### Custom MCP Server

Create `custom_mcp_server.py`:

```python
from mcp import Server, Tool

server = Server("ultron-custom")

@server.tool()
async def analyze_logs(log_file: str) -> dict:
    """Analyze ULTRON log files"""
    # Implementation
    return {"status": "analyzed"}

if __name__ == "__main__":
    server.run()
```

Add to `mcp.json`:

```json
{
  "custom-ultron": {
    "type": "stdio",
    "command": "python",
    "args": ["custom_mcp_server.py"],
    "description": "Custom ULTRON analysis tools"
  }
}
```

## Performance Optimization

### Lazy Loading
- MCP servers start on-demand
- Minimal memory footprint when idle
- Fast initialization (<1s per server)

### Caching
- Memory server caches context
- Filesystem server caches directory listings
- Database servers use connection pooling

### Monitoring
```bash
# Check MCP server status
npx @modelcontextprotocol/server-inspector

# Monitor resource usage
python utils/performance_monitor.py
```

## Integration with ULTRON Tools

### Tool Coordination
- MCP servers complement existing ULTRON tools
- Shared context via memory server
- Unified logging via ultron_logger
- Event system integration

### Example Workflow
1. **Amazon Q** uses `filesystem` to read code
2. **Sequential thinking** analyzes architecture
3. **Memory** stores decisions
4. **Git** commits changes
5. **GitHub** creates PR
6. **Slack** notifies team

## Next Steps

1. **Install MCP servers**: `npm install -g @modelcontextprotocol/server-*`
2. **Configure credentials**: Create `.env` file
3. **Test connections**: Run test commands
4. **Start using**: Ask Amazon Q to use MCP tools
5. **Monitor performance**: Check logs and metrics

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [ULTRON Agent Docs](README.md)
- [Amazon Q Integration](.amazonq/rules/amazon_Q_Rules.md)

---

**Status**: ✅ Production Ready  
**Last Updated**: 2025-01-16  
**Maintainer**: ULTRON Agent Team
