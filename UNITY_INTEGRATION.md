# Unity AI Integration for ULTRON Agent

## Overview

Connects Unity AI capabilities (Assistant, Generators, Inference) to ULTRON's Ollama-based AI system.

## Components

### 1. Unity AI Tool (`tools/unity_ai_tool.py`)
- ULTRON tool for Unity AI commands
- Auto-discovered by agent_core.py
- Handles: asset generation, inference, assistant queries

### 2. Unity Bridge Server (`unity_bridge.py`)
- Translates Unity AI API calls to Ollama
- Runs on port 8765
- Provides REST endpoints for Unity integration

### 3. Launcher (`start_unity_bridge.bat`)
- One-click bridge startup

## Quick Start

```bash
# 1. Start Unity Bridge
.\start_unity_bridge.bat

# 2. Use in ULTRON
"unity generate a player controller script"
"unity run inference on this data"
"unity help with shader code"
```

## API Endpoints

### Assistant (POST /api/assistant)
```json
{"query": "How do I create a shader?"}
```

### Generator (POST /api/generate)
```json
{"prompt": "Create a player movement script", "type": "auto"}
```

### Inference (POST /inference)
```json
{"input": "Analyze this game state"}
```

## Configuration

Add to `ultron_config.json`:
```json
{
  "unity_host": "http://localhost:8765",
  "unity_inference_port": 8080
}
```

## Architecture

```
Unity Editor
    ↓ (HTTP)
Unity Bridge (port 8765)
    ↓ (Ollama API)
ULTRON Ollama (port 11434)
    ↓ (qwen3-coder:480b-cloud)
Response
```

## Usage Examples

### From Unity
```csharp
// Unity C# code
var response = await UnityWebRequest.Post(
    "http://localhost:8765/api/assistant",
    "{\"query\": \"Optimize this script\"}"
).SendWebRequest();
```

### From ULTRON
```python
# Voice command
"Hey ULTRON, unity generate a health bar UI"

# Direct tool call
unity_tool.execute("generate player controller")
```

## Features

- ✅ Unity AI Assistant integration
- ✅ Asset generation via AI
- ✅ ML model inference
- ✅ Ollama backend connection
- ✅ Automatic tool discovery
- ✅ Centralized logging

## Requirements

- ULTRON Agent 3.0+
- Ollama running (port 11434)
- qwen3-coder:480b-cloud model
- Python 3.10+
- aiohttp library

## Troubleshooting

**Bridge won't start**: Check port 8765 availability
**No response**: Verify Ollama is running on port 11434
**Tool not found**: Restart ULTRON to reload tools

## Integration Status

- [x] Tool implementation
- [x] Bridge server
- [x] API endpoints
- [x] Documentation
- [ ] Unity package (optional)
- [ ] Advanced inference models
