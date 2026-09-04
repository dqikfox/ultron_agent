# MCP Quick Reference - Amazon Q + ULTRON Agent

## 🚀 Quick Commands

### Installation
```bash
npm install -g @modelcontextprotocol/server-*
```

### Test All Servers
```bash
# Core
npx @modelcontextprotocol/server-memory
npx @modelcontextprotocol/server-sequential-thinking
npx @modelcontextprotocol/server-filesystem C:\Projects\ultron_agent

# Web
npx @browsermcp/mcp@latest
npx @modelcontextprotocol/server-puppeteer
npx @modelcontextprotocol/server-fetch

# Database
npx @modelcontextprotocol/server-sqlite avatar_game.db
npx @modelcontextprotocol/server-postgres

# Cloud
npx @modelcontextprotocol/server-aws
npx @modelcontextprotocol/server-docker

# Version Control
npx @modelcontextprotocol/server-git
npx @modelcontextprotocol/server-github

# AI/ML
npx @modelcontextprotocol/server-ollama
```

## 📋 Common Use Cases

| Task | MCP Servers Used | Example Command |
|------|------------------|-----------------|
| Code Review | filesystem, memory, sequential-thinking | "Review agent_core.py changes" |
| Deploy AWS | aws, git, filesystem | "Deploy Lambda function" |
| Query Database | sqlite | "Show top avatars by messages" |
| Test GUI | puppeteer, fetch | "Test Pokédex interface" |
| Search Docs | search, fetch | "Find FastAPI WebSocket docs" |
| Commit Changes | git, github | "Commit and create PR" |
| Model Testing | ollama, fetch | "Test llava:7b model" |
| Run Workflow | langflow | "Execute ULTRON workflow" |

## 🔑 Environment Variables

```bash
# Required
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
POSTGRES_CONNECTION_STRING=postgresql://xxx
LANGFLOW_API_KEY=sk-xxx
BRAVE_API_KEY=BSA_xxx
SLACK_BOT_TOKEN=xoxb-xxx
AWS_REGION=us-east-1
OLLAMA_HOST=http://localhost:11434
```

## 🎯 Amazon Q Prompts

### Development
- "Use filesystem to read all Python files in tools/"
- "Use sequential-thinking to analyze the architecture"
- "Use memory to remember this design decision"

### Testing
- "Use puppeteer to test the web GUI"
- "Use fetch to validate API endpoints"
- "Use sqlite to verify avatar data"

### Deployment
- "Use aws to deploy Lambda function"
- "Use docker to build and push image"
- "Use git to commit and push changes"

### Research
- "Use search to find AWS Bedrock examples"
- "Use fetch to get API documentation"
- "Use github to search similar projects"

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not found | `npm install -g @modelcontextprotocol/server-<name>` |
| Connection timeout | Check service status: `curl http://localhost:11434` |
| Permission denied | Run as Administrator (Windows) |
| Missing credentials | Add to `.env` file |

## 📊 Server Status Check

```bash
# Quick health check
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:7860/health     # LangFlow
curl http://localhost:8080/           # Web GUI
curl http://localhost:5000/health     # API Server
```

## 🎨 MCP Server Categories

### 🔧 Development (5)
- memory, sequential-thinking, filesystem, git, github

### 🌐 Web (3)
- browsermcp, puppeteer, fetch

### 🗄️ Database (2)
- sqlite, postgres

### ☁️ Cloud (2)
- aws, docker

### 🤖 AI/ML (2)
- ollama, langflow

### 🔍 Utilities (5)
- search, slack, time, inspector, python-env

## 💡 Pro Tips

1. **Combine Servers**: Use multiple MCP servers together for complex tasks
2. **Memory First**: Always use memory server to maintain context
3. **Sequential Thinking**: Use for complex analysis and debugging
4. **Test Locally**: Validate with inspector before production use
5. **Monitor Performance**: Check logs in `logs/` directory

## 🔗 Quick Links

- [Full Setup Guide](MCP_AMAZON_Q_SETUP.md)
- [MCP Documentation](https://modelcontextprotocol.io)
- [ULTRON Agent README](README.md)
- [Amazon Q Rules](.amazonq/rules/amazon_Q_Rules.md)

---

**Last Updated**: 2025-01-16
