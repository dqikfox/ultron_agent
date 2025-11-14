# LangFlow Integration Setup Guide

## Quick Setup Steps

### 1. Install LangFlow
```bash
pip install langflow
```

### 2. Start LangFlow Server
```bash
langflow run --host 0.0.0.0 --port 7860
```

### 3. Create Required Flows

#### Memory Storage Flow
1. Open LangFlow UI: `http://localhost:7860`
2. Create new flow: "memory-storage-flow"
3. Add components:
   - Text Input (user content)
   - Embedding Generator (sentence-transformers)
   - ChromaDB (vector storage)
4. Connect: Input → Embedder → ChromaDB
5. Save flow ID: `memory-storage-flow`

#### Enhanced Chat Flow
1. Create new flow: "enhanced-chat-flow"
2. Add components:
   - Text Input (message)
   - Memory Retrieval (from ChromaDB)
   - LLM Chain (OpenAI/Ollama)
   - Tool Selector
   - Response Generator
3. Connect components in sequence
4. Save flow ID: `enhanced-chat-flow`

#### Complex Reasoning Flow
1. Create new flow: "complex-reasoning-flow"
2. Add components:
   - Query Analyzer (LLM)
   - Reasoning Chain (Multi-step LLM)
   - Confidence Scorer
   - Final Synthesizer
3. Connect for chain-of-thought processing
4. Save flow ID: `complex-reasoning-flow`

## Integration Test

```python
# Test LangFlow integration
from langflow_integration import langflow_agent

# Check status
status = langflow_agent.get_status()
print(f"LangFlow available: {status['langflow_available']}")

# Test chat
result = await langflow_agent.process_message("Hello, test complex reasoning")
print(f"Response: {result}")
```

## API Endpoints Added

```
GET  /api/langflow/status     - LangFlow system status
POST /api/langflow/chat       - Enhanced chat processing
POST /api/langflow/memory     - Memory search
POST /api/langflow/reasoning  - Complex reasoning
```

## Configuration

Update `ultron_config.json`:
```json
{
  "langflow": {
    "enabled": true,
    "base_url": "http://localhost:7860/api/v1",
    "fallback_enabled": true,
    "flows": {
      "memory_storage": "memory-storage-flow",
      "enhanced_chat": "enhanced-chat-flow",
      "complex_reasoning": "complex-reasoning-flow"
    }
  }
}
```