# ULTRON Agent API Reference

Complete API documentation for ULTRON Agent 3.0, including REST endpoints, WebSocket connections, Python SDK, and tool system.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)  
3. [REST API Endpoints](#rest-api-endpoints)
4. [WebSocket API](#websocket-api)
5. [Python SDK](#python-sdk)
6. [Tool System API](#tool-system-api)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger/OpenAPI documentation.

## 🔐 Authentication

### API Key Authentication
```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello ULTRON"}'
```

### Session-Based Authentication
```python
import requests

# Login
response = requests.post("http://localhost:8000/auth/login", 
    json={"username": "admin", "password": "password"})
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.post("http://localhost:8000/query", 
    headers=headers, json={"message": "Hello"})
```

## 🌐 REST API Endpoints

### Core Endpoints

#### `GET /health`
System health check and status information.

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "uptime": 3600,
  "components": {
    "database": "healthy",
    "ai_models": "healthy",
    "voice_system": "healthy"
  }
}
```

#### `POST /query`
Send a query to ULTRON Agent.

**Request Body:**
```json
{
  "message": "What's the weather like today?",
  "model": "gpt-4o",
  "context": {},
  "stream": false
}
```

**Response:**
```json
{
  "response": "The weather is sunny with a temperature of 72°F...",
  "model_used": "gpt-4o",
  "processing_time": 1.23,
  "tokens_used": 150,
  "context_id": "ctx_123456"
}
```

#### `GET /status`
Detailed system status and metrics.

**Response:**
```json
{
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 68.1,
    "disk_usage": 82.5,
    "uptime": 86400
  },
  "models": {
    "ollama": {
      "status": "healthy",
      "available_models": ["llama3.2:latest", "codellama:latest"]
    },
    "openai": {
      "status": "healthy",
      "rate_limit_remaining": 4500
    }
  },
  "voice": {
    "status": "healthy",
    "input_device": "Built-in Microphone",
    "output_device": "Built-in Speakers"
  }
}
```

### Model Management

#### `GET /models`
List available AI models.

**Response:**
```json
{
  "models": [
    {
      "provider": "ollama",
      "name": "llama3.2:latest",
      "status": "available",
      "size": "4.7GB",
      "capabilities": ["text", "code"]
    },
    {
      "provider": "openai", 
      "name": "gpt-4o",
      "status": "available",
      "capabilities": ["text", "vision", "code"]
    }
  ]
}
```

#### `POST /models/{model_name}/switch`
Switch to a different AI model.

**Response:**
```json
{
  "success": true,
  "previous_model": "gpt-4o-mini",
  "current_model": "gpt-4o",
  "message": "Model switched successfully"
}
```

### Tool Management

#### `GET /tools`
List available tools and their schemas.

**Response:**
```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web for information",
      "schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "Search query"},
          "num_results": {"type": "integer", "default": 5}
        },
        "required": ["query"]
      }
    }
  ]
}
```

#### `POST /tools/{tool_name}`
Execute a specific tool.

**Request Body:**
```json
{
  "query": "Python machine learning tutorials",
  "num_results": 10
}
```

**Response:**
```json
{
  "success": true,
  "tool": "web_search",
  "result": {
    "results": [
      {
        "title": "Machine Learning with Python Tutorial",
        "url": "https://example.com/ml-tutorial",
        "snippet": "Complete guide to ML with Python..."
      }
    ],
    "query": "Python machine learning tutorials",
    "num_results": 10
  },
  "execution_time": 0.85
}
```

### Configuration

#### `GET /config`
Get current configuration (sensitive values masked).

#### `PUT /config`
Update configuration settings.

**Request Body:**
```json
{
  "voice": {
    "enabled": true,
    "engine": "enhanced"
  },
  "models": {
    "default": "ollama"
  }
}
```

### Voice System

#### `POST /voice/speak`
Convert text to speech.

**Request Body:**
```json
{
  "text": "Hello, this is ULTRON speaking.",
  "voice": "default",
  "speed": 1.0,
  "pitch": 0.0
}
```

#### `POST /voice/listen`
Start voice recognition.

**Response:**
```json
{
  "success": true,
  "transcript": "What is the weather like today?",
  "confidence": 0.95,
  "duration": 3.2
}
```

### File Operations

#### `POST /files/upload`
Upload files for processing.

#### `GET /files/{file_id}`
Get file information and content.

#### `POST /files/{file_id}/analyze`
Analyze uploaded file with AI.

## 🔌 WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Message Format
```json
{
  "type": "query|tool|status|subscribe",
  "data": {},
  "request_id": "req_123456"
}
```

### Query Example
```javascript
// Send query
ws.send(JSON.stringify({
  "type": "query",
  "data": {
    "message": "What's the current time?",
    "stream": true
  },
  "request_id": "req_001"
}));

// Receive response
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  console.log(message);
  // {
  //   "type": "query_response",
  //   "data": {
  //     "response": "The current time is 2:30 PM EST",
  //     "chunk": false
  //   },
  //   "request_id": "req_001"
  // }
};
```

### Real-time Events
```javascript
// Subscribe to system events
ws.send(JSON.stringify({
  "type": "subscribe",
  "data": {
    "events": ["system_status", "model_switch", "tool_execution"]
  }
}));

// Receive events
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  if (message.type === "system_status") {
    console.log("System status update:", message.data);
  }
};
```

## 🐍 Python SDK

### Installation
```bash
pip install ultron-agent-sdk
```

### Basic Usage
```python
from ultron_agent import UltronClient
import asyncio

# Initialize client
client = UltronClient(base_url="http://localhost:8000")

async def main():
    # Send query
    response = await client.query("What's the weather like?")
    print(response.text)
    
    # Execute tool
    result = await client.execute_tool("web_search", 
        query="Python tutorials")
    print(result.data)
    
    # Get system status
    status = await client.get_status()
    print(f"CPU: {status.system.cpu_percent}%")

asyncio.run(main())
```

### Advanced Features
```python
from ultron_agent import UltronClient, StreamingQuery

async def streaming_example():
    client = UltronClient("http://localhost:8000")
    
    # Streaming responses
    async for chunk in client.query_stream("Write a long story about AI"):
        print(chunk.text, end="", flush=True)
    
    # Context management
    context = client.create_context()
    await context.add_message("Remember that I like Python")
    response = await context.query("Recommend a programming book")
    
    # Tool chaining
    chain = client.create_chain()
    chain.add_tool("web_search", query="Python news")
    chain.add_tool("summarize", length="short")
    result = await chain.execute()

asyncio.run(streaming_example())
```

### Voice Integration
```python
from ultron_agent.voice import VoiceClient

async def voice_example():
    voice_client = VoiceClient("http://localhost:8000")
    
    # Text to speech
    await voice_client.speak("Hello, I'm ULTRON")
    
    # Speech to text
    transcript = await voice_client.listen(timeout=5)
    print(f"You said: {transcript}")
    
    # Voice conversation
    async with voice_client.conversation() as conv:
        while True:
            user_input = await conv.listen()
            if user_input.lower() == "goodbye":
                break
            response = await conv.respond(user_input)
            await conv.speak(response)

asyncio.run(voice_example())
```

## 🔧 Tool System API

### Tool Interface
```python
from typing import Dict, Any
from ultron_agent.tools import BaseTool

class MyTool(BaseTool):
    """Custom tool implementation."""
    
    @staticmethod
    def match(user_input: str) -> bool:
        """Determine if this tool should handle the input."""
        return "my tool" in user_input.lower()
    
    @staticmethod
    async def execute(**kwargs) -> Dict[str, Any]:
        """Execute the tool's functionality."""
        return {
            "success": True,
            "result": "Tool executed successfully",
            "data": kwargs
        }
    
    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return JSON schema for API documentation."""
        return {
            "name": "my_tool",
            "description": "Custom tool for specific functionality",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First parameter"},
                    "param2": {"type": "integer", "description": "Second parameter"}
                },
                "required": ["param1"]
            }
        }
```

### Tool Registration
```python
from ultron_agent.tools import ToolRegistry

# Register tool
registry = ToolRegistry()
registry.register(MyTool)

# Auto-discovery from package
registry.discover_tools("my_package.tools")

# List registered tools
tools = registry.list_tools()
print([tool.schema()["name"] for tool in tools])
```

## ❌ Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": {
      "field": "message",
      "issue": "Message cannot be empty"
    },
    "request_id": "req_123456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_REQUEST` | Request validation failed | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMITED` | Too many requests | 429 |
| `MODEL_ERROR` | AI model failure | 500 |
| `TOOL_ERROR` | Tool execution failure | 500 |
| `SYSTEM_ERROR` | Internal system error | 500 |

### Python SDK Error Handling
```python
from ultron_agent import UltronClient
from ultron_agent.exceptions import (
    UltronAPIError, 
    ModelError, 
    ToolError,
    RateLimitError
)

client = UltronClient("http://localhost:8000")

try:
    response = await client.query("Hello ULTRON")
except RateLimitError as e:
    print(f"Rate limited: {e.retry_after} seconds")
except ModelError as e:
    print(f"Model error: {e.message}")
except ToolError as e:
    print(f"Tool failed: {e.tool_name} - {e.message}")
except UltronAPIError as e:
    print(f"API error: {e.code} - {e.message}")
```

## 📊 Rate Limiting

### Default Limits
- **Queries**: 100 requests per minute
- **Tool Executions**: 50 requests per minute  
- **Voice Operations**: 20 requests per minute
- **File Uploads**: 10 requests per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642261800
X-RateLimit-Retry-After: 60
```

### Handling Rate Limits
```python
import time
from ultron_agent import UltronClient
from ultron_agent.exceptions import RateLimitError

client = UltronClient("http://localhost:8000")

async def query_with_retry(message):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return await client.query(message)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(e.retry_after)
                continue
            raise
```

## 📋 Examples

### Complete Chat Application
```python
import asyncio
from ultron_agent import UltronClient

class ChatApp:
    def __init__(self):
        self.client = UltronClient("http://localhost:8000")
        self.context = None
    
    async def start_chat(self):
        self.context = self.client.create_context()
        print("ULTRON: Hello! How can I help you today?")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "bye"]:
                break
                
            try:
                response = await self.context.query(user_input)
                print(f"ULTRON: {response.text}")
            except Exception as e:
                print(f"Error: {e}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()

# Run the chat application
async def main():
    async with ChatApp() as app:
        await app.start_chat()

if __name__ == "__main__":
    asyncio.run(main())
```

### Voice-Enabled Assistant
```python
import asyncio
from ultron_agent import UltronClient
from ultron_agent.voice import VoiceClient

async def voice_assistant():
    client = UltronClient("http://localhost:8000")
    voice = VoiceClient("http://localhost:8000")
    
    await voice.speak("Hello! I'm ULTRON. How can I help you?")
    
    while True:
        # Listen for voice input
        print("Listening...")
        transcript = await voice.listen(timeout=10)
        
        if not transcript:
            continue
            
        print(f"You said: {transcript}")
        
        if "goodbye" in transcript.lower():
            await voice.speak("Goodbye! Have a great day!")
            break
        
        # Process query
        response = await client.query(transcript)
        print(f"ULTRON: {response.text}")
        
        # Speak response
        await voice.speak(response.text)

asyncio.run(voice_assistant())
```

### Tool Integration Example
```python
import asyncio
from ultron_agent import UltronClient

async def productivity_assistant():
    client = UltronClient("http://localhost:8000")
    
    # Morning routine
    tasks = [
        ("weather", {"location": "New York"}),
        ("calendar", {"date": "today"}),
        ("news", {"category": "technology", "limit": 5}),
        ("email", {"action": "check_unread"})
    ]
    
    results = {}
    for tool_name, params in tasks:
        try:
            result = await client.execute_tool(tool_name, **params)
            results[tool_name] = result.data
        except Exception as e:
            print(f"Error with {tool_name}: {e}")
    
    # Generate summary
    summary = await client.query(
        f"Create a morning briefing from this data: {results}"
    )
    print("Morning Briefing:", summary.text)

asyncio.run(productivity_assistant())
```

---

## 📖 Additional Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **WebSocket Playground**: `http://localhost:8000/ws-test`
- **Python SDK Documentation**: [SDK Docs](https://ultron-agent-sdk.readthedocs.io/)
- **Tool Development Guide**: [Tool Development](docs/tool_development.md)
- **Authentication Guide**: [Auth Guide](docs/authentication.md)

For more examples and advanced usage patterns, see the [Usage Guide](USAGE.md) and [GitHub Examples](https://github.com/dqikfox/ultron_agent/tree/main/examples).
