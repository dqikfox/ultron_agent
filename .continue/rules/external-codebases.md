# External Codebase Integration Rules

## Continue Extension Integration

### Continue Architecture Understanding
- **Purpose**: Multi-model code assistant with MCP support
- **Configuration**: `.continue/config.yaml` with model and context providers
- **MCP Servers**: GitHub, PostgreSQL, Browser, Memory, Filesystem integrations
- **Context Providers**: Codebase awareness, documentation, and real-time context

### Continue + ULTRON Integration Points
```yaml
# ULTRON-specific models in Continue config
models:
  - name: ULTRON Brain (Llava 7B)
    provider: ollama
    model: llava:7b
    apiBase: http://localhost:11434
    roles: [chat, edit, apply]

  - name: Local Agent
    provider: continue-proxy
    apiBase: http://localhost:8000
    roles: [chat, edit, apply]
```

## Amazon Q Integration Patterns

### Amazon Q Capabilities
- **Code Analysis**: Real-time error detection and suggestions
- **Security Scanning**: Vulnerability detection and remediation
- **Code Generation**: Context-aware code completion
- **Documentation**: Inline help and API documentation

### ULTRON + Amazon Q Collaboration
```python
# Amazon Q understands ULTRON patterns
class UltronTool:
    """Amazon Q recognizes this as ULTRON tool pattern"""
    def match(self, command: str) -> bool:
        # Amazon Q suggests improvements here
        return "keyword" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        # Amazon Q provides error handling suggestions
        try:
            return self._process_command(command)
        except Exception as e:
            log_error("tool", f"Error: {str(e)}")
            return f"Error: {str(e)}"
```

## GitHub Copilot Integration

### Copilot Understanding of ULTRON
- **Pattern Recognition**: Understands ULTRON's modular tool architecture
- **Code Completion**: Suggests ULTRON-specific implementations
- **Documentation**: Generates appropriate docstrings for ULTRON components
- **Testing**: Suggests test patterns for ULTRON tools and services

### ULTRON-Specific Copilot Patterns
```python
# Copilot learns from these patterns
async def ultron_async_pattern(self):
    """Copilot suggests similar async patterns"""
    try:
        result = await self.process_async_operation()
        await self.event_system.emit("operation_complete", result)
        return result
    except Exception as e:
        log_error("component", f"Async operation failed: {str(e)}")
        raise
```

## MCP Server Integrations

### Browser MCP Integration
```javascript
// Browser automation patterns ULTRON uses
const browserActions = {
    navigate: async (url) => {
        await page.goto(url);
        return `Navigated to ${url}`;
    },
    
    search: async (query) => {
        await page.fill('input[name="q"]', query);
        await page.press('input[name="q"]', 'Enter');
        return `Searched for: ${query}`;
    }
};
```

### GitHub MCP Integration
```python
# GitHub operations ULTRON supports
github_operations = {
    "create_issue": lambda title, body: github_client.create_issue(title, body),
    "list_repos": lambda: github_client.list_repositories(),
    "get_commits": lambda repo: github_client.get_commits(repo)
}
```

## External API Integrations

### ElevenLabs Voice API
```python
# Voice integration patterns
class VoiceIntegration:
    def __init__(self):
        self.elevenlabs_client = ElevenLabsClient(api_key=config.elevenlabs_key)
    
    async def synthesize_speech(self, text: str) -> bytes:
        """Pattern that external tools recognize"""
        return await self.elevenlabs_client.generate_audio(text)
```

### OpenAI API Integration
```python
# OpenAI fallback patterns
class OpenAIIntegration:
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_key)
    
    async def chat_completion(self, messages: List[Dict]) -> str:
        """Standard OpenAI integration pattern"""
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
```

## VS Code Extension Ecosystem

### Extension Coordination
- **Amazon Q**: Primary code assistance and security scanning
- **GitHub Copilot**: Code completion and pair programming
- **Continue**: Multi-model LLM integration and MCP orchestration
- **Python**: Language support and debugging

### Workspace Configuration
```json
{
  "amazonQ.telemetry": false,
  "github.copilot.enable": {"*": true},
  "continue.enableTabAutocomplete": true,
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe"
}
```

## External Service Dependencies

### Ollama Service Integration
```python
# Ollama client patterns external tools use
class OllamaIntegration:
    def __init__(self):
        self.base_url = "http://localhost:11434"
    
    async def generate(self, model: str, prompt: str) -> str:
        """Standard Ollama integration pattern"""
        response = await self.client.generate(model=model, prompt=prompt)
        return response['response']
```

### Database Integrations
```python
# PostgreSQL/Supabase patterns
class DatabaseIntegration:
    def __init__(self):
        self.connection_string = config.postgres_connection_string
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Standard database integration pattern"""
        async with asyncpg.connect(self.connection_string) as conn:
            return await conn.fetch(query, *params)
```

## Integration Best Practices

### Cross-Service Communication
- Use standardized JSON message formats
- Implement proper error handling and timeouts
- Maintain backward compatibility in API changes
- Document integration points and dependencies

### Configuration Management
- Use environment variables for sensitive data
- Implement configuration validation
- Provide fallback mechanisms for missing services
- Support dynamic configuration reloading

### Error Handling and Logging
- Use centralized logging for all integrations
- Implement circuit breaker patterns for external services
- Provide meaningful error messages to users
- Log integration failures with context for debugging

This external codebase integration guide ensures ULTRON Agent works seamlessly with the broader development ecosystem while maintaining its modular architecture and extensibility.