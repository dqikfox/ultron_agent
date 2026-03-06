"""
Episodic Memory System

Persistent memory for interaction history with:
- Temporal ordering (when did events happen?)
- Contextual binding (who, what, where?)
- Privacy filters (sanitize sensitive data)
- Bounded storage (prevent memory overflow)
- Semantic search (find relevant memories)

ETHICAL NOTICE:
This is a FUNCTIONAL memory system for conversation tracking,
NOT biological episodic memory or autobiographical consciousness.
Privacy-aware with configurable retention limits.

References:
- Tulving, E. (1972). Episodic and semantic memory
- Conway, M. A. (2001). Sensory-perceptual episodic memory
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta

try:
    from utils.ultron_logger import log_info, log_error
    from utils.security_utils import sanitize_log_input
except ImportError:
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None): print(f"[ERROR] {component}: {msg}")
    def sanitize_log_input(text): return text[:200]  # Truncate


@dataclass
class Episode:
    """
    A single episodic memory

    What: content of the event
    When: timestamp
    Where: location/context
    Who: participants
    Emotion: emotional valence
    """
    episode_id: str
    timestamp: float
    event_type: str  # "conversation", "perception", "action", "decision"
    content: Dict[str, Any]
    participants: List[str] = field(default_factory=list)
    location: str = "unknown"
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    importance: float = 0.5  # 0.0 to 1.0, for retention priority
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize episode"""
        return {
            "id": self.episode_id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "type": self.event_type,
            "content": self.content,
            "participants": self.participants,
            "location": self.location,
            "emotion": self.emotional_valence,
            "importance": self.importance,
            "tags": self.tags
        }

    def matches_query(self, query: str) -> bool:
        """Check if episode matches search query"""
        query_lower = query.lower()

        # Search in content
        content_str = json.dumps(self.content).lower()
        if query_lower in content_str:
            return True

        # Search in tags
        if any(query_lower in tag.lower() for tag in self.tags):
            return True

        # Search in participants
        if any(query_lower in p.lower() for p in self.participants):
            return True

        return False


class EpisodicMemory:
    """
    Manages episodic memories with privacy and storage limits
    """

    def __init__(self,
                 max_episodes: int = 1000,
                 retention_days: int = 30,
                 privacy_mode: bool = True):
        """
        Args:
            max_episodes: Maximum number of episodes to store
            retention_days: Auto-delete episodes older than this
            privacy_mode: Enable privacy filtering
        """
        self.max_episodes = max_episodes
        self.retention_seconds = retention_days * 24 * 3600
        self.privacy_mode = privacy_mode

        self.episodes: deque = deque(maxlen=max_episodes)
        self.index_by_type: Dict[str, List[str]] = {}  # event_type -> [episode_ids]
        self.index_by_participant: Dict[str, List[str]] = {}  # participant -> [episode_ids]
        self.episode_count = 0

        log_info("episodic_memory",
                f"Initialized (max={max_episodes}, retention={retention_days}d, privacy={privacy_mode})")

    def _generate_episode_id(self) -> str:
        """Generate unique episode ID"""
        self.episode_count += 1
        timestamp = str(time.time())
        unique_str = f"episode_{self.episode_count}_{timestamp}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]

    def _apply_privacy_filter(self, content: Dict) -> Dict:
        """Remove or sanitize sensitive information"""
        if not self.privacy_mode:
            return content

        filtered = content.copy()

        # Remove sensitive keys
        sensitive_keys = ["password", "api_key", "secret", "token", "ssn", "credit_card"]
        for key in list(filtered.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = "[REDACTED]"

        # Sanitize text fields
        for key, value in filtered.items():
            if isinstance(value, str):
                filtered[key] = sanitize_log_input(value)

        return filtered

    def store(self,
              event_type: str,
              content: Dict[str, Any],
              participants: Optional[List[str]] = None,
              location: str = "unknown",
              emotional_valence: float = 0.0,
              importance: float = 0.5,
              tags: Optional[List[str]] = None) -> Episode:
        """
        Store new episodic memory

        Args:
            event_type: Type of event
            content: Event data
            participants: Who was involved
            location: Where it happened
            emotional_valence: Emotional tone
            importance: Retention priority
            tags: Search tags

        Returns:
            Created episode
        """
        # Apply privacy filter
        filtered_content = self._apply_privacy_filter(content)

        # Create episode
        episode = Episode(
            episode_id=self._generate_episode_id(),
            timestamp=time.time(),
            event_type=event_type,
            content=filtered_content,
            participants=participants or [],
            location=location,
            emotional_valence=emotional_valence,
            importance=importance,
            tags=tags or []
        )

        # Store episode
        self.episodes.append(episode)

        # Update indices
        if event_type not in self.index_by_type:
            self.index_by_type[event_type] = []
        self.index_by_type[event_type].append(episode.episode_id)

        for participant in episode.participants:
            if participant not in self.index_by_participant:
                self.index_by_participant[participant] = []
            self.index_by_participant[participant].append(episode.episode_id)

        log_info("episodic_memory", f"Stored episode {episode.episode_id} ({event_type})")

        return episode

    def recall_recent(self, limit: int = 10) -> List[Episode]:
        """Get most recent episodes"""
        return list(self.episodes)[-limit:]

    def recall_by_type(self, event_type: str, limit: int = 10) -> List[Episode]:
        """Get episodes of specific type"""
        if event_type not in self.index_by_type:
            return []

        episode_ids = self.index_by_type[event_type][-limit:]
        return [ep for ep in self.episodes if ep.episode_id in episode_ids]

    def recall_by_participant(self, participant: str, limit: int = 10) -> List[Episode]:
        """Get episodes involving specific participant"""
        if participant not in self.index_by_participant:
            return []

        episode_ids = self.index_by_participant[participant][-limit:]
        return [ep for ep in self.episodes if ep.episode_id in episode_ids]

    def search(self, query: str, limit: int = 10) -> List[Episode]:
        """
        Semantic search through memories

        Args:
            query: Search query
            limit: Max results

        Returns:
            Matching episodes
        """
        matches = []

        for episode in reversed(list(self.episodes)):  # Search recent first
            if episode.matches_query(query):
                matches.append(episode)
                if len(matches) >= limit:
                    break

        return matches

    def recall_time_window(self, hours_ago: float) -> List[Episode]:
        """Get episodes from specific time window"""
        cutoff_time = time.time() - (hours_ago * 3600)
        return [ep for ep in self.episodes if ep.timestamp >= cutoff_time]

    def forget_old_episodes(self):
        """Delete episodes older than retention period"""
        cutoff_time = time.time() - self.retention_seconds

        before_count = len(self.episodes)
        self.episodes = deque(
            (ep for ep in self.episodes if ep.timestamp >= cutoff_time),
            maxlen=self.max_episodes
        )
        after_count = len(self.episodes)

        deleted = before_count - after_count
        if deleted > 0:
            log_info("episodic_memory", f"Forgot {deleted} old episodes")

        # Rebuild indices
        self._rebuild_indices()

    def _rebuild_indices(self):
        """Rebuild search indices"""
        self.index_by_type = {}
        self.index_by_participant = {}

        for episode in self.episodes:
            # Type index
            if episode.event_type not in self.index_by_type:
                self.index_by_type[episode.event_type] = []
            self.index_by_type[episode.event_type].append(episode.episode_id)

            # Participant index
            for participant in episode.participants:
                if participant not in self.index_by_participant:
                    self.index_by_participant[participant] = []
                self.index_by_participant[participant].append(episode.episode_id)

    def get_summary(self) -> Dict:
        """Get memory statistics"""
        if not self.episodes:
            return {"total_episodes": 0}

        oldest = min(ep.timestamp for ep in self.episodes)
        newest = max(ep.timestamp for ep in self.episodes)

        return {
            "total_episodes": len(self.episodes),
            "max_capacity": self.max_episodes,
            "usage": f"{len(self.episodes)/self.max_episodes:.1%}",
            "oldest_episode": datetime.fromtimestamp(oldest).isoformat(),
            "newest_episode": datetime.fromtimestamp(newest).isoformat(),
            "time_span_hours": (newest - oldest) / 3600,
            "event_types": list(self.index_by_type.keys()),
            "participants": list(self.index_by_participant.keys())
        }

    def export_to_json(self, filepath: str):
        """Export all episodes to JSON file"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_episodes": len(self.episodes),
            "episodes": [ep.to_dict() for ep in self.episodes]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        log_info("episodic_memory", f"Exported {len(self.episodes)} episodes to {filepath}")


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧠 EPISODIC MEMORY DEMO\n")

    # Create memory system
    memory = EpisodicMemory(max_episodes=100, retention_days=7, privacy_mode=True)

    print(f"✅ Memory system initialized\n")

    # Store some episodes
    print("📝 Storing memories...\n")

    memory.store(
        event_type="conversation",
        content={"user_said": "Hello, how are you?", "agent_replied": "I'm doing well!"},
        participants=["user", "ULTRON"],
        emotional_valence=0.5,
        importance=0.3,
        tags=["greeting", "small_talk"]
    )

    memory.store(
        event_type="decision",
        content={"situation": "police chase", "chose": "take alley", "outcome": "escaped"},
        participants=["CJ"],
        location="Los Santos",
        emotional_valence=-0.3,
        importance=0.9,
        tags=["chase", "escape", "high_stakes"]
    )

    memory.store(
        event_type="conversation",
        content={"user_said": "What's the meaning of life?", "agent_replied": "42, according to Douglas Adams"},
        participants=["user", "ULTRON"],
        emotional_valence=0.1,
        importance=0.5,
        tags=["philosophy", "humor"]
    )

    memory.store(
        event_type="perception",
        content={"saw": "police helicopter", "threat_level": 0.9},
        location="downtown",
        emotional_valence=-0.7,
        importance=0.85,
        tags=["threat", "police"]
    )

    # Recall tests
    print("🔍 Memory Recall Tests:\n")

    print("1. Recent memories:")
    recent = memory.recall_recent(limit=3)
    for ep in recent:
        print(f"   [{ep.event_type}] {list(ep.content.values())[0]}")

    print("\n2. Conversations only:")
    conversations = memory.recall_by_type("conversation")
    for ep in conversations:
        print(f"   {ep.content.get('user_said', 'N/A')}")

    print("\n3. Search for 'police':")
    results = memory.search("police")
    for ep in results:
        print(f"   [{ep.event_type}] at {ep.location}: {ep.content}")

    print("\n4. Memories involving ULTRON:")
    ultron_memories = memory.recall_by_participant("ULTRON")
    print(f"   Found {len(ultron_memories)} memories with ULTRON")

    # Summary
    print("\n📊 Memory Statistics:")
    summary = memory.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    print("\n✅ Episodic memory demo complete!")
