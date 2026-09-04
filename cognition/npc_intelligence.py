"""
ULTRON Cognition Module - NPC Behavioral Intelligence

Purpose: Create believable NPCs with conscious-like decision making
Use Case: Game AI, simulations, interactive narratives

ETHICAL STATEMENT:
This module creates FUNCTIONAL ANALOGUES of consciousness for
entertainment/simulation purposes. NPCs are clearly labeled as
artificial agents, not sentient beings.

Components:
1. StateIntrospector - Tracks NPC's current state
2. PersonalityModel - Defines character traits
3. GoalSystem - Manages objectives and motivations
4. DecisionEngine - Makes contextual choices
5. EmotionalState - Simulates emotional responses
6. MemorySystem - Remembers interactions
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Fallback logging if utils not available
try:
    from utils.ultron_logger import log_info, log_error
except ImportError:
    def log_info(component, msg):
        print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None):
        print(f"[ERROR] {component}: {msg}")


class EmotionType(Enum):
    """Basic emotion categories for NPC simulation"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    CURIOUS = "curious"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"


@dataclass
class NPCState:
    """Complete state representation of an NPC"""
    name: str
    current_task: str = "idle"
    location: str = "unknown"
    health: float = 100.0
    energy: float = 100.0
    emotional_state: EmotionType = EmotionType.NEUTRAL
    emotional_intensity: float = 0.5  # 0.0 to 1.0
    goals: List[str] = field(default_factory=list)
    beliefs: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, float] = field(default_factory=dict)  # name -> affinity (-1 to 1)
    knowledge: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize state for logging/saving"""
        return {
            "name": self.name,
            "current_task": self.current_task,
            "location": self.location,
            "health": self.health,
            "energy": self.energy,
            "emotion": self.emotional_state.value,
            "emotion_intensity": self.emotional_intensity,
            "goals": self.goals,
            "beliefs": self.beliefs,
            "relationships": self.relationships,
            "recent_events": self.recent_events[-5:]  # Last 5 events
        }


@dataclass
class PersonalityTraits:
    """Five-Factor Model (Big Five) personality traits"""
    openness: float = 0.5  # 0 = closed-minded, 1 = very open
    conscientiousness: float = 0.5  # 0 = careless, 1 = organized
    extraversion: float = 0.5  # 0 = introvert, 1 = extrovert
    agreeableness: float = 0.5  # 0 = competitive, 1 = cooperative
    neuroticism: float = 0.5  # 0 = calm, 1 = anxious

    # Additional traits for richer NPCs
    courage: float = 0.5
    honesty: float = 0.5
    curiosity: float = 0.5
    loyalty: float = 0.5


class StateIntrospector:
    """
    Tracks and reports NPC's internal state
    Provides "self-awareness" for decision making
    """

    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.state = NPCState(name=npc_name)
        self.state_history: List[Dict] = []
        log_info("cognition", f"StateIntrospector initialized for {npc_name}")

    def update_state(self, **kwargs):
        """Update current state"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)

        # Record history
        self.state_history.append({
            "timestamp": time.time(),
            "state": self.state.to_dict()
        })

        # Keep only last 100 states
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]

    def get_self_report(self) -> str:
        """Generate first-person self-description"""
        emotion = self.state.emotional_state.value
        task = self.state.current_task

        # Energy-based feelings
        if self.state.energy < 30:
            energy_desc = "I'm exhausted"
        elif self.state.energy < 60:
            energy_desc = "I'm getting tired"
        else:
            energy_desc = "I'm energetic"

        # Emotional description
        emotion_desc = f"I'm feeling {emotion}"

        # Goal description
        if self.state.goals:
            goal_desc = f"I want to {self.state.goals[0]}"
        else:
            goal_desc = "I'm not sure what to do"

        return f"I am {self.npc_name}. {emotion_desc}. {energy_desc}. {goal_desc}. Currently: {task}."

    def check_needs(self) -> Dict[str, bool]:
        """Check if NPC has unmet needs"""
        return {
            "needs_rest": self.state.energy < 40,
            "needs_healing": self.state.health < 50,
            "has_goals": len(self.state.goals) > 0,
            "is_emotional": self.state.emotional_intensity > 0.7
        }


class PersonalityModel:
    """
    Defines NPC personality that influences decisions
    """

    def __init__(self, npc_name: str, traits: Optional[PersonalityTraits] = None):
        self.npc_name = npc_name
        self.traits = traits or PersonalityTraits()
        log_info("cognition", f"PersonalityModel created for {npc_name}")

    def get_personality_summary(self) -> str:
        """Generate personality description"""
        descriptions = []

        if self.traits.extraversion > 0.7:
            descriptions.append("outgoing")
        elif self.traits.extraversion < 0.3:
            descriptions.append("reserved")

        if self.traits.agreeableness > 0.7:
            descriptions.append("friendly")
        elif self.traits.agreeableness < 0.3:
            descriptions.append("competitive")

        if self.traits.conscientiousness > 0.7:
            descriptions.append("organized")
        elif self.traits.conscientiousness < 0.3:
            descriptions.append("spontaneous")

        if self.traits.courage > 0.7:
            descriptions.append("brave")
        elif self.traits.courage < 0.3:
            descriptions.append("cautious")

        if self.traits.curiosity > 0.7:
            descriptions.append("inquisitive")

        return f"{self.npc_name} is {', '.join(descriptions) if descriptions else 'balanced'}"

    def would_do_action(self, action: str, context: Dict) -> float:
        """
        Estimate probability NPC would take action given personality
        Returns 0.0 to 1.0
        """
        base_prob = 0.5

        # Personality-based modifiers
        if "social" in action.lower():
            base_prob += (self.traits.extraversion - 0.5) * 0.4

        if "help" in action.lower():
            base_prob += (self.traits.agreeableness - 0.5) * 0.4

        if "risky" in action.lower() or "dangerous" in action.lower():
            base_prob += (self.traits.courage - 0.5) * 0.4
            base_prob -= (self.traits.neuroticism - 0.5) * 0.3

        if "explore" in action.lower() or "investigate" in action.lower():
            base_prob += (self.traits.curiosity - 0.5) * 0.4

        # Clamp to valid range
        return max(0.0, min(1.0, base_prob))


class DecisionEngine:
    """
    Makes conscious-like decisions based on state, personality, goals
    """

    def __init__(self, introspector: StateIntrospector, personality: PersonalityModel):
        self.introspector = introspector
        self.personality = personality
        self.decision_history: List[Dict] = []

    def evaluate_options(self, options: List[str], context: Dict = None) -> str:
        """
        Evaluate options and choose one

        Args:
            options: List of possible actions
            context: Additional context for decision

        Returns:
            Chosen action with reasoning
        """
        context = context or {}
        state = self.introspector.state

        # Score each option
        scores = {}
        for option in options:
            score = 0.5  # Base score

            # Personality influence
            personality_factor = self.personality.would_do_action(option, context)
            score += (personality_factor - 0.5) * 0.3

            # Goal alignment
            if state.goals:
                current_goal = state.goals[0]
                if any(word in option.lower() for word in current_goal.lower().split()):
                    score += 0.3

            # Energy constraints
            if "rest" in option.lower() and state.energy < 40:
                score += 0.4
            elif "active" in option.lower() and state.energy < 30:
                score -= 0.3

            # Emotional influence
            if state.emotional_state == EmotionType.FEARFUL:
                if "flee" in option.lower() or "hide" in option.lower():
                    score += 0.3
                elif "fight" in option.lower() or "confront" in option.lower():
                    score -= 0.2

            scores[option] = max(0.0, min(1.0, score))

        # Choose best option
        best_option = max(scores, key=scores.get)

        # Log decision
        decision_log = {
            "timestamp": time.time(),
            "options": options,
            "scores": scores,
            "chosen": best_option,
            "state": state.to_dict()
        }
        self.decision_history.append(decision_log)

        log_info("cognition", f"{self.personality.npc_name} chose: {best_option} (score: {scores[best_option]:.2f})")

        return best_option

    def explain_decision(self, decision: str) -> str:
        """Generate explanation for why decision was made"""
        if not self.decision_history:
            return "No decision history available"

        last_decision = self.decision_history[-1]
        if last_decision["chosen"] != decision:
            return f"That wasn't my last decision"

        state = self.introspector.state
        reasons = []

        # Energy-based reasoning
        if state.energy < 40 and "rest" in decision.lower():
            reasons.append("I'm tired and need to rest")

        # Goal-based reasoning
        if state.goals and any(word in decision.lower() for word in state.goals[0].lower().split()):
            reasons.append(f"This helps me {state.goals[0]}")

        # Emotion-based reasoning
        if state.emotional_state == EmotionType.FEARFUL:
            reasons.append("I'm afraid and need to be careful")
        elif state.emotional_state == EmotionType.CURIOUS:
            reasons.append("I'm curious to see what happens")

        # Personality-based reasoning
        if self.personality.traits.courage > 0.7 and "brave" in decision.lower():
            reasons.append("It's the brave thing to do")

        if reasons:
            return f"I chose '{decision}' because: {'; '.join(reasons)}"
        else:
            return f"I chose '{decision}' because it seemed like the best option"


# ═══════════════════════════════════════════════════════════════
# NPC FACTORY
# ═══════════════════════════════════════════════════════════════

def create_npc(name: str, personality_type: str = "balanced") -> Dict:
    """
    Factory function to create complete NPC

    Args:
        name: NPC name
        personality_type: Preset personality ("brave", "cautious", "friendly", "curious", "balanced")

    Returns:
        Dictionary with all NPC components
    """
    # Define personality presets
    presets = {
        "brave": PersonalityTraits(courage=0.9, neuroticism=0.2, conscientiousness=0.7),
        "cautious": PersonalityTraits(courage=0.3, neuroticism=0.7, conscientiousness=0.8),
        "friendly": PersonalityTraits(extraversion=0.8, agreeableness=0.9, openness=0.7),
        "curious": PersonalityTraits(curiosity=0.9, openness=0.9, extraversion=0.6),
        "balanced": PersonalityTraits(),
    }

    traits = presets.get(personality_type, PersonalityTraits())

    # Create components
    introspector = StateIntrospector(name)
    personality = PersonalityModel(name, traits)
    decision_engine = DecisionEngine(introspector, personality)

    log_info("cognition", f"Created NPC: {name} ({personality_type})")

    return {
        "name": name,
        "introspector": introspector,
        "personality": personality,
        "decision_engine": decision_engine,
        "type": personality_type
    }


if __name__ == "__main__":
    # Demo: Create an NPC and simulate decision making
    print("\n🎮 NPC COGNITION DEMO\n")

    # Create a brave warrior NPC
    npc = create_npc("Aria the Brave", "brave")

    introspector = npc["introspector"]
    personality = npc["personality"]
    decision_engine = npc["decision_engine"]

    print(f"✅ {personality.get_personality_summary()}\n")

    # Set up initial state
    introspector.update_state(
        location="village_square",
        goals=["protect the village"],
        emotional_state=EmotionType.CONFIDENT
    )

    print(f"💭 {introspector.get_self_report()}\n")

    # Present a decision
    print("⚔️  A dragon appears! What should Aria do?\n")

    options = [
        "fight the dragon bravely",
        "flee to safety",
        "negotiate with the dragon",
        "call for help"
    ]

    decision = decision_engine.evaluate_options(options)
    explanation = decision_engine.explain_decision(decision)

    print(f"🎯 Decision: {decision}")
    print(f"📝 Reasoning: {explanation}\n")

    # Change state and see different decision
    introspector.update_state(
        health=30.0,
        energy=20.0,
        emotional_state=EmotionType.FEARFUL
    )

    print(f"💭 {introspector.get_self_report()}\n")
    print("⚔️  After being wounded, what now?\n")

    decision2 = decision_engine.evaluate_options(options)
    explanation2 = decision_engine.explain_decision(decision2)

    print(f"🎯 Decision: {decision2}")
    print(f"📝 Reasoning: {explanation2}\n")

    print("✅ NPC cognition demo complete!")
