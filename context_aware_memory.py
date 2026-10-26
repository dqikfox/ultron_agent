"""
Context-Aware Memory System - Enhanced conversation memory with learning
Understands context, learns user preferences, and provides personalized responses
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from utils.ultron_logger import log_info, log_error, log_ai_decision
import hashlib


class ContextMemoryNode:
    """A single memory node with context"""
    
    def __init__(
        self,
        content: str,
        context_type: str,
        timestamp: Optional[datetime] = None
    ):
        self.content = content
        self.context_type = context_type
        self.timestamp = timestamp or datetime.now()
        self.access_count = 0
        self.last_accessed = self.timestamp
        self.tags = set()
        self.related_nodes = set()
        self.importance_score = 0.5
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for this node"""
        data = f"{self.content}{self.timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def access(self):
        """Mark this node as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        # Increase importance with access
        self.importance_score = min(
            1.0,
            self.importance_score + 0.05
        )
    
    def add_tag(self, tag: str):
        """Add a tag to this memory"""
        self.tags.add(tag.lower())
    
    def link_to(self, node_id: str):
        """Link this node to another"""
        self.related_nodes.add(node_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "context_type": self.context_type,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "tags": list(self.tags),
            "related_nodes": list(self.related_nodes),
            "importance_score": self.importance_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextMemoryNode':
        """Create from dictionary"""
        node = cls(
            content=data["content"],
            context_type=data["context_type"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        node.id = data["id"]
        node.access_count = data["access_count"]
        node.last_accessed = datetime.fromisoformat(data["last_accessed"])
        node.tags = set(data.get("tags", []))
        node.related_nodes = set(data.get("related_nodes", []))
        node.importance_score = data.get("importance_score", 0.5)
        return node


class ContextAwareMemory:
    """Advanced memory system with context understanding"""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or (
            Path(__file__).parent / "memory_storage"
        )
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.memory_dir / "context_memory.json"
        self.preferences_file = self.memory_dir / "user_preferences.json"
        
        self.memories: Dict[str, ContextMemoryNode] = {}
        self.user_preferences = {}
        self.conversation_context = []
        
        self._load_memories()
        self._load_preferences()
    
    def _load_memories(self):
        """Load memories from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                
                for node_data in data.get("memories", []):
                    node = ContextMemoryNode.from_dict(node_data)
                    self.memories[node.id] = node
                
                log_info(
                    "context_memory",
                    f"Loaded {len(self.memories)} memories"
                )
            except Exception as e:
                log_error("context_memory", f"Failed to load memories: {e}")
    
    def _load_preferences(self):
        """Load user preferences"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
            except Exception as e:
                log_error(
                    "context_memory",
                    f"Failed to load preferences: {e}"
                )
    
    def _save_memories(self):
        """Save memories to disk"""
        try:
            data = {
                "memories": [node.to_dict() for node in self.memories.values()],
                "last_updated": datetime.now().isoformat(),
                "total_memories": len(self.memories)
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            log_error("context_memory", f"Failed to save memories: {e}")
    
    def _save_preferences(self):
        """Save user preferences"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            log_error("context_memory", f"Failed to save preferences: {e}")
    
    def remember(
        self,
        content: str,
        context_type: str = "general",
        tags: Optional[List[str]] = None,
        importance: float = 0.5
    ) -> ContextMemoryNode:
        """Store a new memory"""
        
        node = ContextMemoryNode(content, context_type)
        node.importance_score = importance
        
        if tags:
            for tag in tags:
                node.add_tag(tag)
        
        # Auto-extract tags from content
        auto_tags = self._extract_tags(content)
        for tag in auto_tags:
            node.add_tag(tag)
        
        # Link to recent related memories
        self._link_related_memories(node)
        
        # Store
        self.memories[node.id] = node
        
        # Add to conversation context
        self.conversation_context.append(node.id)
        self._trim_conversation_context()
        
        # Save to disk
        self._save_memories()
        
        log_info(
            "context_memory",
            f"Remembered: {content[:50]}... "
            f"(type: {context_type}, tags: {list(node.tags)})"
        )
        
        return node
    
    def recall(
        self,
        query: str,
        context_type: Optional[str] = None,
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[ContextMemoryNode]:
        """Retrieve relevant memories"""
        
        # Score all memories by relevance
        scored_memories = []
        query_words = set(query.lower().split())
        
        for memory in self.memories.values():
            if context_type and memory.context_type != context_type:
                continue
            
            if memory.importance_score < min_importance:
                continue
            
            score = self._calculate_relevance_score(
                memory, query_words
            )
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and recency
        scored_memories.sort(
            key=lambda x: (x[0], x[1].timestamp),
            reverse=True
        )
        
        # Mark as accessed
        results = []
        for score, memory in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self._save_memories()
        
        return results
    
    def _calculate_relevance_score(
        self,
        memory: ContextMemoryNode,
        query_words: set
    ) -> float:
        """Calculate how relevant a memory is to the query"""
        score = 0.0
        
        # Content word overlap
        content_words = set(memory.content.lower().split())
        word_overlap = len(query_words & content_words)
        if content_words:
            score += (word_overlap / len(content_words)) * 0.4
        
        # Tag matching
        query_tags = {word for word in query_words if len(word) > 3}
        tag_overlap = len(query_tags & memory.tags)
        if tag_overlap > 0:
            score += tag_overlap * 0.3
        
        # Recency boost (memories from last 7 days get bonus)
        days_old = (datetime.now() - memory.timestamp).days
        if days_old < 7:
            score += (7 - days_old) / 7 * 0.15
        
        # Access frequency boost
        score += min(memory.access_count / 10, 0.1)
        
        # Importance score
        score += memory.importance_score * 0.05
        
        return score
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract potential tags from content"""
        words = content.lower().split()
        
        # Keywords that might be important
        important_words = [
            w for w in words
            if len(w) > 4 and w.isalpha()
        ]
        
        return important_words[:5]  # Top 5 words
    
    def _link_related_memories(self, new_node: ContextMemoryNode):
        """Link new memory to related existing memories"""
        
        # Find memories with similar tags or context
        for memory in self.memories.values():
            # Same context type
            if memory.context_type == new_node.context_type:
                new_node.link_to(memory.id)
                memory.link_to(new_node.id)
            
            # Shared tags
            shared_tags = new_node.tags & memory.tags
            if len(shared_tags) >= 2:
                new_node.link_to(memory.id)
                memory.link_to(new_node.id)
    
    def _trim_conversation_context(self, max_context: int = 20):
        """Trim conversation context to reasonable size"""
        if len(self.conversation_context) > max_context:
            self.conversation_context = self.conversation_context[-max_context:]
    
    def get_conversation_context(
        self,
        max_items: int = 10
    ) -> List[ContextMemoryNode]:
        """Get recent conversation context"""
        context_nodes = []
        
        for node_id in reversed(self.conversation_context[-max_items:]):
            if node_id in self.memories:
                context_nodes.append(self.memories[node_id])
        
        return list(reversed(context_nodes))
    
    def learn_preference(self, category: str, preference: str, value: Any):
        """Learn a user preference"""
        if category not in self.user_preferences:
            self.user_preferences[category] = {}
        
        self.user_preferences[category][preference] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
            "confidence": 0.7
        }
        
        self._save_preferences()
        
        log_ai_decision(
            "context_memory",
            f"Learned preference: {category}.{preference} = {value}",
            ai_model="preference_learning",
            confidence_score=0.7
        )
    
    def get_preference(
        self,
        category: str,
        preference: str,
        default: Any = None
    ) -> Any:
        """Get a learned user preference"""
        return self.user_preferences.get(category, {}).get(
            preference, {}
        ).get("value", default)
    
    def forget_old_memories(self, days: int = 90):
        """Remove old, unimportant memories"""
        cutoff = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for node_id, memory in self.memories.items():
            if (memory.timestamp < cutoff and
                memory.importance_score < 0.3 and
                memory.access_count < 2):
                to_remove.append(node_id)
        
        for node_id in to_remove:
            del self.memories[node_id]
        
        if to_remove:
            self._save_memories()
            log_info(
                "context_memory",
                f"Forgot {len(to_remove)} old memories"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self.memories:
            return {"total_memories": 0}
        
        # Calculate stats
        total = len(self.memories)
        by_type = defaultdict(int)
        total_importance = 0.0
        total_access = 0
        
        for memory in self.memories.values():
            by_type[memory.context_type] += 1
            total_importance += memory.importance_score
            total_access += memory.access_count
        
        return {
            "total_memories": total,
            "by_type": dict(by_type),
            "avg_importance": total_importance / total,
            "avg_access_count": total_access / total,
            "conversation_context_size": len(self.conversation_context),
            "total_preferences": sum(
                len(prefs) for prefs in self.user_preferences.values()
            )
        }
    
    def export_to_text(self) -> str:
        """Export memories to readable text format"""
        lines = ["=" * 60]
        lines.append("🔴 CONTEXT MEMORY EXPORT 🔴")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
        lines.append("")
        
        stats = self.get_statistics()
        lines.append(f"Total Memories: {stats['total_memories']}")
        lines.append(f"Average Importance: {stats['avg_importance']:.2f}")
        lines.append("")
        
        # Group by type
        by_type = defaultdict(list)
        for memory in self.memories.values():
            by_type[memory.context_type].append(memory)
        
        for context_type, memories in by_type.items():
            lines.append(f"\n## {context_type.upper()}")
            lines.append("-" * 40)
            
            for memory in sorted(
                memories,
                key=lambda m: m.importance_score,
                reverse=True
            )[:10]:
                lines.append(f"\n- {memory.content}")
                lines.append(f"  Importance: {memory.importance_score:.2f}")
                lines.append(f"  Accessed: {memory.access_count} times")
                if memory.tags:
                    lines.append(f"  Tags: {', '.join(memory.tags)}")
        
        return "\n".join(lines)


# Global memory instance
_memory = None


def get_memory() -> ContextAwareMemory:
    """Get or create the global memory instance"""
    global _memory
    if _memory is None:
        _memory = ContextAwareMemory()
    return _memory


if __name__ == "__main__":
    # Test the memory system
    memory = ContextAwareMemory()
    
    # Store some memories
    memory.remember(
        "User prefers Python for scripting tasks",
        "user_preference",
        tags=["python", "scripting"],
        importance=0.8
    )
    
    memory.remember(
        "User likes detailed code explanations",
        "interaction_style",
        tags=["explanations", "code"],
        importance=0.7
    )
    
    memory.remember(
        "Project uses Ollama with llava:7b model",
        "technical_context",
        tags=["ollama", "llava", "ai"],
        importance=0.9
    )
    
    # Recall memories
    results = memory.recall("python code", limit=3)
    print(f"\nRecalled {len(results)} memories for 'python code':")
    for r in results:
        print(f"- {r.content} (importance: {r.importance_score:.2f})")
    
    # Learn a preference
    memory.learn_preference("editor", "preferred", "vscode")
    
    # Get statistics
    stats = memory.get_statistics()
    print(f"\nMemory Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Export
    export = memory.export_to_text()
    print("\n" + export)
