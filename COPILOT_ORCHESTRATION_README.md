# ULTRON Agent - Copilot Dynamic Orchestration

## Overview

The ULTRON Agent now includes a sophisticated Copilot orchestration system that enables GitHub Copilot Chat to analyze the project using NVIDIA Maverick via NIM and provide comprehensive enhancement recommendations.

## How It Works

1. **Trigger Command**: Use `run dynamic executor` in GitHub Copilot Chat
2. **Dynamic Execution**: Copilot executes `tools/dynamic_code_executor.py`
3. **Maverick Analysis**: Contacts NVIDIA Maverick via NIM for project analysis
4. **Response Processing**: Saves Maverick's response to `/logs/maverick_response_<timestamp>.txt`
5. **Copilot Analysis**: GitHub Copilot analyzes the response and adds its own recommendations
6. **Combined Report**: Presents structured analysis with implementation roadmap

## Setup Requirements

### Environment Variables

```bash
# For NVIDIA NIM API access
export NVIDIA_NIM_API_KEY="your-api-key"
export NVIDIA_NIM_BASE_URL="https://api.nvidia.com/v1"
export NIM_MAVERICK_MODEL="maverick"

# Alternative: Local NIM installation
# Ensure nim-cli is available in PATH
```

### Dependencies

```bash
pip install requests openai nvidia-nim
```

## GitHub MCP Server Integration

The Copilot orchestration flow can optionally call into the GitHub MCP server so Copilot Chat can inspect repositories, issues, PRs, and projects through the Model Context Protocol.

### Remote GitHub MCP (GitHub-hosted)

1. Generate a classic GitHub Personal Access Token (PAT) with `repo` (read) scope; store it in `.env` using the keys added to `.env.example`.
2. Set `GITHUB_MCP_RUNTIME=remote` so diagnostics know to expect the hosted service.
3. Update `GITHUB_TOOLSETS` (e.g., `issues,pullRequests,repositories`) to match the MCP capabilities you want enabled.
4. Keep `GITHUB_READ_ONLY=true` unless you explicitly need mutation APIs.
5. Reload the workspace so Copilot Chat picks up the new environment variables.

### Local Self-Hosted MCP (Docker/NPM)

1. Clone `github/mcp-github` and run `npm install` inside the project.
2. Start the server with Docker (recommended):

   ```pwsh
   docker compose up --build
   ```

   or via `npm run start` for a node-only process.
3. Set `GITHUB_MCP_RUNTIME=local` and adjust `GITHUB_HOST` to `http://localhost:<port>`.
4. Ensure the PAT still has read-only access; the server uses it for outbound GitHub calls.
5. Keep the container running while using Copilot Chat.

### VS Code MCP Client Configuration

The repository guardrails currently block auto-generating `.vscode/mcp.json`, but you can create it manually with the following template:

```json
{
	"clients": {
		"github": {
			"type": "mcp",
			"description": "GitHub MCP Server",
			"transport": {
				"type": "sse",
				"url": "${env:GITHUB_HOST:-https://api.github.com}/mcp"
			},
			"env": {
				"GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_PERSONAL_ACCESS_TOKEN}",
				"GITHUB_TOOLSETS": "${env:GITHUB_TOOLSETS}",
				"GITHUB_READ_ONLY": "${env:GITHUB_READ_ONLY}",
				"GITHUB_DYNAMIC_TOOLSETS": "${env:GITHUB_DYNAMIC_TOOLSETS}",
				"GITHUB_DEFAULT_ORG": "${env:GITHUB_DEFAULT_ORG}"
			}
		}
	}
}
```

After saving, reload VS Code so Copilot Chat discovers the MCP endpoint.

## Usage

### In GitHub Copilot Chat

```text
run dynamic executor
```

Or directly:

```text
@githubcopilot run dynamic executor
```

### Manual Execution

```python
from tools.dynamic_code_executor import DynamicCodeExecutor

# Initialize executor
executor = DynamicCodeExecutor()

# Run full orchestration
result = executor.execute("orchestrate with maverick")
print(result)

# Execute specific code
result = executor.execute("run code print('Hello World')")
print(result)
```

## Output Structure

The orchestration produces a comprehensive report with:

### Section 1: Maverick Report

- Direct analysis from NVIDIA Maverick
- Project review and recommendations
- Latest AI tools and models suggestions

### Section 2: Copilot Recommendations

- New modules and tools to add
- Architectural improvements
- AI model upgrade suggestions
- Integration recommendations

### Section 3: Implementation Roadmap

- 90-day development plan
- Prioritized enhancement suggestions
- Automated PR generation options

## Files Created

- `tools/dynamic_code_executor.py` - Main orchestration tool
- `.github/copilot-instructions.md` - Copilot integration instructions
- `/logs/maverick_response_<timestamp>.txt` - Saved Maverick responses

## Safety Features

- **Workspace Contained**: All operations within repository boundaries
- **Timeout Protection**: Code execution limited to 30 seconds
- **Error Handling**: Comprehensive exception handling and logging
- **API Fallback**: Supports both cloud NIM and local NIM installations

## Integration Points

The system integrates with:

- **ULTRON Agent Core**: Automatic tool loading and memory access
- **NVIDIA NIM**: AI analysis via Maverick model
- **GitHub Copilot**: Enhanced analysis and recommendations
- **ULTRON Memory**: Context and learning insights storage

## Future Enhancements

- Automated PR generation for top recommendations
- Real-time collaboration features
- Enhanced model switching capabilities
- Performance monitoring integration

---

*This orchestration system enables continuous evolution of the ULTRON Agent through AI-powered analysis and recommendations.*
