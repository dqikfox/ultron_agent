"""
Pinecone Vector Database Integration Tool
Provides semantic search and memory storage capabilities
"""

from typing import Dict, Any, List, Optional
from utils.ultron_logger import log_info, log_error

class PineconeTool:
    name = "pinecone"
    description = "Vector database for semantic search and long-term memory"
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("pinecone_api_key", "")
        self.environment = config.get("pinecone_environment", "")
        self.index_name = config.get("pinecone_index", "ultron-memory")
        self.client = None
        self.index = None
        
        if self.api_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone client"""
        try:
            from pinecone import Pinecone
            self.client = Pinecone(api_key=self.api_key)
            self.index = self.client.Index(self.index_name)
            log_info("pinecone", f"Connected to index: {self.index_name}")
        except ImportError:
            log_error("pinecone", "pinecone-client not installed. Run: pip install pinecone-client")
        except Exception as e:
            log_error("pinecone", f"Init failed: {str(e)}")
    
    def match(self, command: str) -> bool:
        """Check if command is for Pinecone"""
        keywords = ["search memory", "remember", "recall", "find similar", "semantic search"]
        return any(kw in command.lower() for kw in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute Pinecone operations"""
        if not self.client:
            return "Pinecone not configured. Set pinecone_api_key in config."
        
        try:
            if "search" in command.lower() or "recall" in command.lower():
                query = kwargs.get("query", command)
                return self._search(query, top_k=kwargs.get("top_k", 5))
            
            elif "store" in command.lower() or "remember" in command.lower():
                text = kwargs.get("text", command)
                metadata = kwargs.get("metadata", {})
                return self._store(text, metadata)
            
            return "Supported: search/recall, store/remember"
            
        except Exception as e:
            log_error("pinecone", f"Execute failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _search(self, query: str, top_k: int = 5) -> str:
        """Search for similar vectors"""
        try:
            # Generate embedding (placeholder - use actual embedding model)
            vector = self._get_embedding(query)
            
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            
            if not results.matches:
                return "No similar memories found."
            
            output = []
            for match in results.matches:
                score = match.score
                text = match.metadata.get("text", "")
                output.append(f"[{score:.2f}] {text}")
            
            return "\n".join(output)
            
        except Exception as e:
            log_error("pinecone", f"Search failed: {str(e)}")
            return f"Search error: {str(e)}"
    
    def _store(self, text: str, metadata: Dict[str, Any]) -> str:
        """Store text with vector embedding"""
        try:
            vector = self._get_embedding(text)
            vector_id = f"mem_{hash(text)}"
            
            metadata["text"] = text
            
            self.index.upsert(vectors=[(vector_id, vector, metadata)])
            
            log_info("pinecone", f"Stored: {text[:50]}...")
            return f"Stored memory: {text[:100]}"
            
        except Exception as e:
            log_error("pinecone", f"Store failed: {str(e)}")
            return f"Store error: {str(e)}"
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector (placeholder)"""
        # TODO: Use actual embedding model (OpenAI, Sentence Transformers, etc.)
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        # Generate 1536-dim vector (OpenAI ada-002 size)
        return [(hash_val >> i) % 100 / 100.0 for i in range(1536)]
    
    @staticmethod
    def schema():
        return {
            "name": "pinecone",
            "description": "Vector database for semantic search and memory",
            "parameters": {
                "query": {"type": "string", "description": "Search query"},
                "text": {"type": "string", "description": "Text to store"},
                "top_k": {"type": "integer", "description": "Number of results"}
            }
        }
