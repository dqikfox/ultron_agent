# MCP Integration for GitHub Copilot & Codex

This guide extends the existing Model Context Protocol setup so GitHub Copilot (or any MCP-compatible client) can reach the ULTRON toolchain, including the Codex agent, Browser MCP, Inspector, and other servers defined in `mcp.json`.

## 1. Prerequisites

- GitHub Copilot Chat extension **v0.19.0+** with MCP support enabled (Settings → Extensions → GitHub Copilot Chat → Experimental → “Enable Model Context Protocol”).
- Node.js 18+ (needed for the npm-based MCP servers).
- `npx` available on your PATH.
- The ULTRON repository cloned at `C:\Projects\ultron_agent` (adjust paths if different).

## 2. Update `mcp.json`

`mcp.json` already lists the core servers and now includes the Inspector server:

```jsonc
{
  "servers": {
    "browsermcp": { "command": "npx", "args": ["@browsermcp/mcp@latest"] },
    "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"] },
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"] },
    "postgres": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-postgres"] },
    "puppeteer": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-puppeteer"] },
    "inspector": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-inspector"] }
  }
}
```

The Inspector server lets you introspect active MCP tools (`list_tools`, `list_resources`, and inspect prompts). It is lightweight and uses stdio, so Copilot can connect to it automatically once configured.

## 3. Wire Copilot/Codex to the MCP servers

Create or update `C:\Users\<you>\.codex\config.toml` (or the Codex CLI location noted in the [docs](https://github.com/openai/codex/blob/main/docs/config.md#mcp-integration)). Add the MCP server list so Codex exposes the same servers back to Copilot:

```toml
[[mcp_servers]]
name = "browsermcp"
type = "stdio"
command = "npx"
args = ["@browsermcp/mcp@latest"]

[[mcp_servers]]
name = "github"
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "${input:github-token}" }

[[mcp_servers]]
name = "filesystem"
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]

[[mcp_servers]]
name = "postgres"
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres"]
env = { POSTGRES_CONNECTION_STRING = "${input:postgres-url}" }

[[mcp_servers]]
name = "puppeteer"
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-puppeteer"]

[[mcp_servers]]
name = "inspector"
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-inspector"]
```

> **Tip:** Keep `mcp.json` and the Codex config aligned so that starting a server through ULTRON or through Copilot yields the same behaviour.

## 4. Connect GitHub Copilot Chat

1. Open VS Code → GitHub Copilot Chat view.
2. Run `@settings` and confirm MCP support is enabled.
3. Use the command palette → “GitHub Copilot: Restart Model Context Protocol Servers” to reload the config.
4. In any chat, access a server:  
   - `@browsermcp navigate to https://example.com`  
   - `@inspector list_tools`  
   - `@github search issues --query "repo:owner/project is:open label:bug"`

Copilot will spawn the MCP servers listed in the Codex config, allowing you to interact with ULTRON’s capabilities directly from the chat window.

## 5. Using Codex as an MCP server

When Codex CLI runs with the configuration above, GitHub Copilot treats it as the MCP host. Any custom tools (including ULTRON’s `MCPIntegrationTool`) remain available:

- Start/stop servers with natural language: “Start MCP inspector” or “List MCP status”.
- Inspect server resources via `@inspector describe tool browsermcp`.
- Combine Copilot and ULTRON automation by referencing the same `mcp.json`.

## 6. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `command not found: npx` | Install Node.js (https://nodejs.org) and restart VS Code. |
| `permission denied` or `Cannot find module` | Run `npm install -g @browsermcp/mcp @modelcontextprotocol/server-inspector` or rerun with `npx -y`. |
| Copilot does not list MCP servers | Confirm `config.toml` is in the Codex config directory, then “GitHub Copilot: Restart Model Context Protocol Servers”. |
| Inspector shows no tools | Make sure the server you want to inspect is running; list active servers with ULTRON (`list mcp servers`) or via Copilot `@inspector list_servers`. |

With this setup, GitHub Copilot can reach the same MCP ecosystem that ULTRON uses, including the new Inspector server for introspection and debugging.
