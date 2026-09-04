"""
Global Workspace Theory (GWT) Implementation

Based on Baars' Global Workspace Theory - a computational model where
consciousness arises from selective broadcasting of information to
multiple cognitive modules.

ETHICAL NOTICE:
This is a FUNCTIONAL ANALOGUE of consciousness mechanisms, not true
subjective experience. Used for research and NPC believability.

Architecture:
- Multiple specialized modules (perception, memory, planning, etc.)
- Workspace buffer that holds "spotlight of attention"
- Competition mechanism for workspace access
- Broadcasting system that shares workspace content globally

References:
- Baars, B. J. (1988). A Cognitive Theory of Consciousness
- Dehaene, S., & Naccache, L. (2001). Towards a cognitive neuroscience of consciousness
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

# Fallback logging
try:
    from utils.ultron_logger import log_info, log_error, log_ai_decision
except ImportError:
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None): print(f"[ERROR] {component}: {msg}")
    def log_ai_decision(component, msg, model="", confidence=0.0): print(f"[AI] {component}: {msg}")


class WorkspaceSlotPriority(Enum):
    """Priority levels for workspace access"""
    CRITICAL = 100  # Safety, urgent threats
    HIGH = 75       # Goal-relevant, emotional
    NORMAL = 50     # Routine processing
    LOW = 25        # Background monitoring
    MINIMAL = 10    # Suppressed, inhibited


@dataclass
class WorkspaceContent:
    """Content that can occupy the global workspace"""
    source_module: str
    content_type: str  # "perception", "memory", "goal", "emotion", "thought"
    data: Dict[str, Any]
    priority: WorkspaceSlotPriority
    timestamp: float = field(default_factory=time.time)
    salience: float = 0.5  # 0.0 to 1.0, how "attention-grabbing" this is

    def __repr__(self):
        return f"<Workspace: {self.source_module}/{self.content_type} pri={self.priority.name} sal={self.salience:.2f}>"


@dataclass
class CognitiveModule:
    """
    A specialized processing module that can:
    - Submit content to workspace
    - Subscribe to workspace broadcasts
    - Process information independently
    """
    name: str
    module_type: str  # "perception", "memory", "planning", "emotion", "language"
    processing_fn: Optional[Callable] = None
    subscribes_to: List[str] = field(default_factory=list)  # Which content types to listen for
    active: bool = True

    def can_process(self, content: WorkspaceContent) -> bool:
        """Check if this module cares about workspace content"""
        if not self.active:
            return False
        return content.content_type in self.subscribes_to or "*" in self.subscribes_to


class GlobalWorkspace:
    """
    Implements GWT - selective broadcasting of information

    Key Properties:
    1. Limited capacity (only one or few items in "spotlight")
    2. Competition for access (salience-based)
    3. Global broadcast (all modules receive)
    4. Conscious-like reportability (can query "what am I thinking?")
    """

    def __init__(self, capacity: int = 3, history_size: int = 50):
        """
        Args:
            capacity: Max number of simultaneous items in workspace
            history_size: How many broadcast events to remember
        """
        self.capacity = capacity
        self.workspace_buffer: List[WorkspaceContent] = []
        self.modules: Dict[str, CognitiveModule] = {}
        self.broadcast_history: deque = deque(maxlen=history_size)
        self.competition_queue: List[WorkspaceContent] = []
        self.total_broadcasts = 0

        log_info("global_workspace", f"Initialized with capacity={capacity}")

    def register_module(self, module: CognitiveModule):
        """Register a cognitive module"""
        self.modules[module.name] = module
        log_info("global_workspace", f"Registered module: {module.name} (type: {module.module_type})")

    def submit_to_workspace(self, content: WorkspaceContent):
        """
        Module submits content for workspace consideration
        Content competes based on priority + salience
        """
        self.competition_queue.append(content)
        log_info("global_workspace", f"Submitted: {content}")

    def _calculate_competition_score(self, content: WorkspaceContent) -> float:
        """
        Calculate competition score for workspace access

        Score = priority + salience + novelty bonus
        """
        base_score = content.priority.value / 100.0  # 0.0 to 1.0
        salience_score = content.salience

        # Novelty bonus - is this different from current workspace?
        novelty_bonus = 0.0
        for existing in self.workspace_buffer:
            if existing.source_module == content.source_module:
                novelty_bonus -= 0.2  # Penalty for repetition
                break
        else:
            novelty_bonus += 0.1  # Bonus for new module

        # Recency penalty - recent broadcasts from same module lose priority
        recency_penalty = 0.0
        recent_sources = []
        for b in list(self.broadcast_history)[-5:]:
            for c in b['content']:
                recent_sources.append(c.source_module)
        if content.source_module in recent_sources:
            recency_penalty -= 0.15

        total = base_score + salience_score + novelty_bonus + recency_penalty
        return max(0.0, min(1.0, total))

    def update_workspace(self):
        """
        Process competition queue and update workspace buffer
        This is the "attention selection" mechanism
        """
        if not self.competition_queue:
            return

        # Score all candidates
        scored_candidates = [
            (self._calculate_competition_score(content), content)
            for content in self.competition_queue
        ]

        # Sort by score (highest first)
        scored_candidates.sort(reverse=True, key=lambda x: x[0])

        # Select top candidates up to capacity
        winners = []
        for score, content in scored_candidates[:self.capacity]:
            if score > 0.3:  # Minimum threshold for workspace access
                winners.append(content)
                log_ai_decision(
                    "global_workspace",
                    f"Selected for workspace: {content.source_module}/{content.content_type}",
                    confidence=score
                )

        # Update workspace buffer
        self.workspace_buffer = winners
        self.competition_queue.clear()

        # Broadcast to all modules
        if self.workspace_buffer:
            self.broadcast()

    def broadcast(self):
        """
        Send workspace content to all subscribed modules
        This is the "global availability" property of consciousness
        """
        if not self.workspace_buffer:
            return

        broadcast_event = {
            "timestamp": time.time(),
            "broadcast_id": self.total_broadcasts,
            "content": self.workspace_buffer.copy(),
            "recipients": []
        }

        # Send to each module that subscribes to this content type
        for content in self.workspace_buffer:
            for module_name, module in self.modules.items():
                if module.can_process(content):
                    broadcast_event["recipients"].append(module_name)

                    # If module has processing function, call it
                    if module.processing_fn:
                        try:
                            module.processing_fn(content)
                        except Exception as e:
                            log_error("global_workspace", f"Module {module_name} processing failed", e)

        self.broadcast_history.append(broadcast_event)
        self.total_broadcasts += 1

        log_info("global_workspace",
                f"Broadcast #{self.total_broadcasts}: {len(self.workspace_buffer)} items → {len(set(broadcast_event['recipients']))} modules")

    def get_current_content(self) -> List[WorkspaceContent]:
        """Get current workspace content (what system is "aware of")"""
        return self.workspace_buffer.copy()

    def introspect(self) -> str:
        """
        Generate conscious-like self-report of current mental state
        Answers: "What am I thinking right now?"
        """
        if not self.workspace_buffer:
            return "I am not focused on anything particular right now."

        reports = []
        for content in self.workspace_buffer:
            module = content.source_module
            ctype = content.content_type
            data = content.data

            # Generate natural language report
            if ctype == "perception":
                reports.append(f"I am perceiving {data.get('summary', 'something')}")
            elif ctype == "goal":
                reports.append(f"I am trying to {data.get('objective', 'accomplish something')}")
            elif ctype == "emotion":
                reports.append(f"I am feeling {data.get('emotion', 'neutral')}")
            elif ctype == "memory":
                reports.append(f"I am remembering {data.get('event', 'something from the past')}")
            elif ctype == "thought":
                reports.append(f"I am thinking about {data.get('topic', 'something')}")
            else:
                reports.append(f"I am processing {ctype} from {module}")

        if len(reports) == 1:
            return reports[0] + "."
        else:
            return "Right now: " + "; ".join(reports) + "."

    def get_workspace_stats(self) -> Dict:
        """Get statistics about workspace activity"""
        return {
            "total_broadcasts": self.total_broadcasts,
            "current_capacity": len(self.workspace_buffer),
            "max_capacity": self.capacity,
            "registered_modules": len(self.modules),
            "active_modules": sum(1 for m in self.modules.values() if m.active),
            "recent_activity": len(self.broadcast_history)
        }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE COGNITIVE MODULES
# ═══════════════════════════════════════════════════════════════

def create_perception_module(name: str = "vision") -> CognitiveModule:
    """Create a perception module that processes sensory input"""
    def process_broadcast(content: WorkspaceContent):
        log_info("perception", f"{name} received: {content.content_type}")

    return CognitiveModule(
        name=f"perception_{name}",
        module_type="perception",
        processing_fn=process_broadcast,
        subscribes_to=["goal", "emotion"]  # Perception influenced by goals/emotions
    )


def create_memory_module() -> CognitiveModule:
    """Create episodic memory module"""
    memory_store = []

    def process_broadcast(content: WorkspaceContent):
        # Store workspace broadcasts as memories
        memory_store.append({
            "timestamp": time.time(),
            "content": content.data,
            "source": content.source_module
        })
        # Keep only recent memories
        if len(memory_store) > 100:
            memory_store.pop(0)
        log_info("memory", f"Stored {content.content_type} from {content.source_module}")

    return CognitiveModule(
        name="episodic_memory",
        module_type="memory",
        processing_fn=process_broadcast,
        subscribes_to=["*"]  # Memory subscribes to everything
    )


def create_planning_module() -> CognitiveModule:
    """Create planning/goal module"""
    current_plan = []

    def process_broadcast(content: WorkspaceContent):
        if content.content_type == "perception":
            # Update plan based on perception
            log_info("planning", f"Updating plan based on {content.data.get('summary', 'input')}")

    return CognitiveModule(
        name="planner",
        module_type="planning",
        processing_fn=process_broadcast,
        subscribes_to=["perception", "memory", "emotion"]
    )


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧠 GLOBAL WORKSPACE THEORY DEMO\n")

    # Create workspace
    gw = GlobalWorkspace(capacity=3)

    # Register modules
    gw.register_module(create_perception_module("vision"))
    gw.register_module(create_perception_module("audio"))
    gw.register_module(create_memory_module())
    gw.register_module(create_planning_module())

    print(f"✅ Registered {len(gw.modules)} cognitive modules\n")

    # Simulate cognitive activity
    print("📡 Simulating cognitive activity...\n")

    # Time 1: See a threat
    gw.submit_to_workspace(WorkspaceContent(
        source_module="perception_vision",
        content_type="perception",
        data={"summary": "a large predator approaching"},
        priority=WorkspaceSlotPriority.CRITICAL,
        salience=0.9
    ))

    # Time 1: Also hear sounds
    gw.submit_to_workspace(WorkspaceContent(
        source_module="perception_audio",
        content_type="perception",
        data={"summary": "birds chirping peacefully"},
        priority=WorkspaceSlotPriority.LOW,
        salience=0.2
    ))

    # Time 1: Have a goal
    gw.submit_to_workspace(WorkspaceContent(
        source_module="planner",
        content_type="goal",
        data={"objective": "find food"},
        priority=WorkspaceSlotPriority.NORMAL,
        salience=0.6
    ))

    # Update workspace (competition happens here)
    gw.update_workspace()

    print(f"\n💭 Introspection: {gw.introspect()}\n")

    # Time 2: Emotion emerges
    gw.submit_to_workspace(WorkspaceContent(
        source_module="emotion_system",
        content_type="emotion",
        data={"emotion": "fear", "intensity": 0.8},
        priority=WorkspaceSlotPriority.HIGH,
        salience=0.85
    ))

    gw.update_workspace()

    print(f"💭 Introspection: {gw.introspect()}\n")

    # Time 3: Memory recall
    gw.submit_to_workspace(WorkspaceContent(
        source_module="episodic_memory",
        content_type="memory",
        data={"event": "last time I escaped a predator by climbing a tree"},
        priority=WorkspaceSlotPriority.HIGH,
        salience=0.75
    ))

    gw.update_workspace()

    print(f"💭 Introspection: {gw.introspect()}\n")

    # Show stats
    stats = gw.get_workspace_stats()
    print(f"📊 Workspace Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Global Workspace demo complete!")
    print("\nKey Properties Demonstrated:")
    print("  ✓ Limited capacity (3 slots)")
    print("  ✓ Competition for attention (salience + priority)")
    print("  ✓ Global broadcasting (all modules notified)")
    print("  ✓ Conscious reportability (introspection)")
    print("  ✓ Dynamic focus shifts (predator → fear → memory)")
