# ULTRON Agent Memory & Vector Database Integration Guide

Comprehensive guide to ULTRON's memory system with Pinecone vector database integration.

## Architecture Overview

ULTRON uses a **dual-layer memory system**:

```
┌─────────────────────────────────────────┐
│     CONVERSATION INPUT / USER QUERY     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Short-term Memory   │
        │   (Session Cache)    │
        │  [Last N messages]   │
        └──────────────────────┘
                   │
                   ├─→ Immediate context
                   │   (fast, limited)
                   │
                   ▼
        ┌──────────────────────┐
        │  Long-term Memory    │
        │  (Persistent Store)  │
        │  [SQLite JSON logs]  │
        └──────────────────────┘
                   │
                   ├─→ Full conversation history
                   │   (archived, searchable)
                   │
                   ▼
        ┌──────────────────────┐
        │  Vector Memory       │
        │  (Pinecone / FAISS)  │
        │  [Semantic Search]   │
        └──────────────────────┘
                   │
                   └─→ Semantic similarity matching
                       (knowledge retrieval)
```

## Memory System Files

### 1. Core Memory System

**File:** `memory.py`
```python
class Memory:
    """Dual-layer memory with short-term and long-term storage"""
    
    # Short-term: Fixed-size deque (last N conversations)
    short_term_memory = deque(maxlen=50)
    
    # Long-term: JSON file storage
    long_term_memory_file = "memory/long_term_memory.json"
    
    def add_short_term(message: str, role: str = "user"):
        """Add to session cache"""
        
    def add_long_term(message: str, metadata: Dict):
        """Archive to persistent storage"""
        
    def save_long_term_memory():
        """Persist to disk"""
```

**Key Methods:**
- `add_short_term(message, role)` - Add to session cache (fast)
- `add_long_term(message, metadata)` - Archive to JSON (permanent)
- `save_long_term_memory()` - Write to disk
- `get_context(limit=10)` - Retrieve recent context
- `search(query)` - Search long-term memory

### 2. Enhanced Memory System with Vectors

**File:** `enhanced_memory_system.py`
```python
class EnhancedMemorySystem:
    """Advanced memory with vector embeddings and semantic search"""
    
    def __init__(self, db_path="memory/ultron_memory.db"):
        # SQLite for structured storage
        # Supports vectors and embeddings
        
    def semantic_search(query: str, top_k: int = 5):
        """Find similar conversations by meaning"""
        
    def store_embedding(text: str, embedding: List[float]):
        """Save embedding for later retrieval"""
```

**Database Schema:**
```sql
-- Conversations with embeddings
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_input TEXT,
    agent_response TEXT,
    context TEXT,
    embedding BLOB  -- Vector representation
);

-- Knowledge base with semantic indexing
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY,
    topic TEXT,
    content TEXT,
    source TEXT,
    timestamp TEXT,
    embedding BLOB
);
```

## Vector Database Integration

### Pinecone Setup

**File:** `tools/pinecone_tool.py`

```python
from tools.tool_interface import ToolInterface

class PineconeTool(ToolInterface):
    """Vector database integration for semantic search"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("pinecone_api_key")
        self.environment = config.get("pinecone_environment")
        self.index_name = config.get("pinecone_index", "ultron-memory")
        
        from pinecone import Pinecone
        self.client = Pinecone(api_key=self.api_key)
        self.index = self.client.Index(self.index_name)
```

### Configuration

**File:** `ultron_config.json`

```json
{
  "memory": {
    "short_term_limit": 50,
    "long_term_path": "memory/long_term_memory.json",
    "enable_vector_db": true
  },
  "vector_db": {
    "provider": "pinecone",
    "pinecone_api_key": "${PINECONE_API_KEY}",
    "pinecone_environment": "us-west1",
    "pinecone_index": "ultron-memory",
    "embedding_model": "text-embedding-3-small"
  }
}
```

## Using Memory in Your Code

### Short-term Memory (Fast)

```python
from memory import Memory

# Add user message
Memory.add_short_term("Hello ULTRON", role="user")

# Add agent response
Memory.add_short_term("Hello! How can I help?", role="agent")

# Get recent context (for LLM prompt)
context = Memory.get_context(limit=10)
# Returns last 10 messages for immediate context
```

### Long-term Memory (Persistent)

```python
from memory import Memory

# Archive important information
Memory.add_long_term(
    message="User set preference: dark mode",
    metadata={
        "category": "user_preference",
        "importance": "high",
        "timestamp": datetime.now().isoformat()
    }
)

# Save to disk
Memory.save_long_term_memory()

# Later: search long-term memory
results = Memory.search("user preferences")
```

### Semantic Search with Vectors

```python
from enhanced_memory_system import EnhancedMemorySystem
from tools.openai_tools import OpenAITool

# Initialize
memory_system = EnhancedMemorySystem()
embedder = OpenAITool()

# Store conversation with embedding
user_input = "How do I integrate Pinecone?"
embedding = embedder.create_embedding(user_input)

memory_system.store_embedding(user_input, embedding)

# Later: semantic search
similar = memory_system.semantic_search(
    query="Vector database setup",
    top_k=5  # Return top 5 similar conversations
)

for result in similar:
    print(f"Match: {result['text']} (score: {result['similarity']})")
```

## Memory Flow in Conversation

### 1. User Sends Message

```python
user_message = "Tell me about ULTRON"

# Step 1: Add to short-term (cache)
Memory.add_short_term(user_message, role="user")

# Step 2: Create embedding for semantic search
embedding = create_embedding(user_message)
memory_system.store_embedding(user_message, embedding)
```

### 2. Agent Processes Request

```python
# Step 3: Get context for LLM
recent_context = Memory.get_context(limit=10)

# Step 4: Optionally retrieve similar past conversations
similar_conversations = memory_system.semantic_search(
    user_message, 
    top_k=3
)

# Step 5: Build LLM prompt with context
prompt = build_prompt_with_context(
    message=user_message,
    recent_context=recent_context,
    similar_conversations=similar_conversations
)

# Step 6: Send to LLM
response = llm.generate(prompt)
```

### 3. Store Response

```python
# Step 7: Add response to short-term
Memory.add_short_term(response, role="agent")

# Step 8: Archive to long-term
Memory.add_long_term(
    message=response,
    metadata={
        "conversation_turn": turn_number,
        "model": "gpt-4",
        "timestamp": datetime.now().isoformat()
    }
)

# Step 9: Embed response for future retrieval
response_embedding = create_embedding(response)
memory_system.store_embedding(response, response_embedding)

# Step 10: Persist to disk
Memory.save_long_term_memory()
```

## Pinecone Operations

### Initialize Connection

```python
from tools.pinecone_tool import PineconeTool

config = {
    "pinecone_api_key": "your-api-key",
    "pinecone_environment": "us-west1",
    "pinecone_index": "ultron-memory"
}

pinecone_tool = PineconeTool(config)
```

### Upsert Vectors

```python
# Store conversation embedding in Pinecone
vectors = [
    {
        "id": "conv_123",
        "values": embedding,  # 1536-dim vector from text-embedding-3-small
        "metadata": {
            "text": user_message,
            "role": "user",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
]

pinecone_tool.index.upsert(vectors=vectors)
```

### Query Similar Vectors

```python
# Find similar conversations
query_embedding = create_embedding("How to use ULTRON?")

results = pinecone_tool.index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

for match in results["matches"]:
    print(f"Match: {match['metadata']['text']}")
    print(f"Score: {match['score']}")  # Similarity score 0-1
```

### Delete and Cleanup

```python
# Remove old vectors (e.g., after 90 days)
pinecone_tool.index.delete(ids=["conv_123", "conv_124"])

# Clear entire index (careful!)
pinecone_tool.index.delete(delete_all=True)
```

## Configuration & Environment

### Set API Keys

```bash
# Pinecone
export PINECONE_API_KEY="your-api-key-here"
export PINECONE_ENVIRONMENT="us-west1"

# OpenAI (for embeddings)
export OPENAI_API_KEY="your-openai-key-here"
```

### Enable in Config

Edit `ultron_config.json`:

```json
{
  "vector_db": {
    "enabled": true,
    "provider": "pinecone",
    "pinecone_api_key": "${PINECONE_API_KEY}",
    "pinecone_environment": "us-west1",
    "pinecone_index": "ultron-memory",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536
  },
  "memory": {
    "enable_vector_db": true,
    "vector_search_top_k": 5
  }
}
```

## Embedding Models

### Recommended Options

| Model | Dimension | Speed | Cost | Best For |
|-------|-----------|-------|------|----------|
| text-embedding-3-small | 1536 | Fast | $0.02/M | Default, good balance |
| text-embedding-3-large | 3072 | Medium | $0.13/M | Semantic precision |
| text-embedding-ada-002 | 1536 | Medium | $0.10/M | Legacy, still good |
| local embeddings | varies | Fastest | Free | Privacy-first |

### Create Embeddings

```python
from tools.openai_tools import OpenAITool

embedder = OpenAITool(model="text-embedding-3-small")

# Single embedding
embedding = embedder.create_embedding("Your text here")
# Returns: List[float] of dimension 1536

# Batch embeddings
texts = ["First text", "Second text", "Third text"]
embeddings = embedder.create_embeddings(texts)
# Returns: List[List[float]]
```

## Memory Lifecycle

### Session Memory (Ephemeral)
- **Storage:** In-memory deque (50 messages)
- **Lifetime:** Current session only
- **Speed:** Microseconds
- **Use case:** Immediate conversation context

### Persistent Memory (Long-term)
- **Storage:** SQLite database + JSON file
- **Lifetime:** Indefinite (until manually deleted)
- **Speed:** Milliseconds
- **Use case:** Conversation history, preferences

### Vector Memory (Semantic)
- **Storage:** Pinecone vector index
- **Lifetime:** Configurable (usually indefinite)
- **Speed:** Milliseconds (with Pinecone)
- **Use case:** Finding similar past conversations

## Memory Management & Cleanup

### Archive Old Conversations

```python
from datetime import datetime, timedelta

# Archive conversations older than 30 days
cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()

old_conversations = memory_system.get_old_conversations(cutoff_date)

# Archive to storage
for conv in old_conversations:
    memory_system.archive(conv)

# Remove from active memory
memory_system.delete_old(cutoff_date)
```

### Monitor Memory Usage

```python
# Check short-term memory size
short_term_size = len(Memory.short_term_memory)
print(f"Short-term: {short_term_size} messages")

# Check database size
import os
db_size = os.path.getsize("memory/ultron_memory.db")
print(f"Database: {db_size / 1024 / 1024:.2f} MB")

# Check Pinecone index stats
stats = pinecone_tool.index.describe_index_stats()
print(f"Vectors in Pinecone: {stats['total_vector_count']}")
```

## Troubleshooting

### Issue: Vector Search Returns Empty Results

**Causes:**
- Embeddings not computed correctly
- Pinecone index empty
- Dimension mismatch

**Solution:**
```python
# Verify embedding dimension
embedding = create_embedding("test")
print(f"Embedding dim: {len(embedding)}")  # Should be 1536 for text-embedding-3-small

# Check index status
stats = pinecone_tool.index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
```

### Issue: Memory Grows Too Large

**Solution:**
```python
# Archive old data monthly
from datetime import timedelta

cutoff = datetime.now() - timedelta(days=30)
old_data = memory_system.get_old_conversations(cutoff)
memory_system.archive(old_data)
memory_system.delete_old(cutoff)
```

### Issue: Pinecone Connection Fails

**Solution:**
```python
# Verify credentials
print(f"API Key: {config['pinecone_api_key'][:10]}...")
print(f"Environment: {config['pinecone_environment']}")

# Test connection
try:
    index = pinecone_tool.index.describe_index_stats()
    print("Connected successfully")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Performance Tips

1. **Batch embeddings** - Create multiple at once, not one-by-one
2. **Use vector search sparingly** - It's powerful but slower than keyword search
3. **Archive regularly** - Keep active memory trim
4. **Monitor costs** - Embedding API calls add up; use smaller models when possible
5. **Cache embeddings** - Don't recompute for identical text

## Best Practices

1. **Always persist important data** - Don't rely on short-term only
2. **Use appropriate embedding model** - Balance speed vs. quality
3. **Set TTL on vectors** - Automatically age out old data
4. **Monitor memory usage** - Watch database size and vector count
5. **Test vector similarity** - Ensure embeddings work as expected
6. **Version your embeddings** - Track which model created each vector

## Resources

- **Pinecone Docs:** https://docs.pinecone.io/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings/
- **Vector Database Comparison:** https://benchmark.superlinked.com/
- **ULTRON Repository:** https://github.com/dqikfox/ultron_agent
