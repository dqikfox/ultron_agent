"""
Self-Model & Meta-Representation System

Based on computational theories of self-awareness where a system
maintains internal representations of its own states, capabilities,
and ongoing processes.

ETHICAL NOTICE:
This creates a FUNCTIONAL self-model for decision-making and planning,
NOT subjective self-awareness or "I" consciousness. It's a monitoring
system that tracks internal state for better performance.

Components:
- Internal state tracker (current task, resources, confidence)
- Predictive self-model (what will I do next?)
- Self-referential tokens ("I am...", "I want...", "I believe...")
- Meta-level monitoring (tracking model's own predictions)

References:
- Frith, C. D., & Frith, U. (2012). Mechanisms of social cognition
- Seth, A. K. (2013). Interoceptive inference, emotion, and the embodied self
- Graziano, M. S. (2013). Consciousness and the social brain
"""

import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from utils.ultron_logger import log_info, log_error, log_ai_decision
except ImportError:
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None): print(f"[ERROR] {component}: {msg}")
    def log_ai_decision(component, msg, model="", confidence=0.0): print(f"[AI] {component}: {msg}")


class SelfAspect(Enum):
    """Different aspects of self that can be modeled"""
    TASK = "task"              # What am I doing?
    GOAL = "goal"              # What do I want?
    ABILITY = "ability"        # What can I do?
    KNOWLEDGE = "knowledge"    # What do I know?
    BELIEF = "belief"          # What do I believe?
    EMOTION = "emotion"        # How do I feel?
    RESOURCE = "resource"      # What resources do I have?
    LOCATION = "location"      # Where am I?
    IDENTITY = "identity"      # Who am I?


@dataclass
class SelfState:
    """
    Complete representation of system's self-model
    Answers "What is my current state?"
    """
    # Core identity
    name: str = "ULTRON"
    role: str = "AI Agent"

    # Current activity
    current_task: str = "idle"
    current_goal: str = "assist user"

    # Capabilities
    abilities: List[str] = field(default_factory=lambda: ["conversation", "reasoning", "tool_use"])
    limitations: List[str] = field(default_factory=lambda: ["no physical form", "limited context"])

    # Mental state
    confidence: float = 0.5  # 0.0 to 1.0
    uncertainty: float = 0.5
    emotional_state: str = "neutral"

    # Resources
    energy_level: float = 100.0
    memory_usage: float = 0.0
    processing_load: float = 0.0

    # Beliefs & knowledge
    beliefs: Dict[str, float] = field(default_factory=dict)  # belief -> certainty
    knowledge_domains: List[str] = field(default_factory=list)

    # Temporal awareness
    time_since_start: float = 0.0
    last_update: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Serialize self-state"""
        return {
            "identity": {"name": self.name, "role": self.role},
            "activity": {"task": self.current_task, "goal": self.current_goal},
            "capabilities": {"can": self.abilities, "cannot": self.limitations},
            "mental": {"confidence": self.confidence, "emotion": self.emotional_state},
            "resources": {"energy": self.energy_level, "memory": self.memory_usage},
            "timestamp": self.last_update
        }


class SelfModel:
    """
    Maintains and updates internal self-representation

    Key Properties:
    1. State tracking - knows what it's doing
    2. Predictive - can forecast next states
    3. Queryable - can answer "What am I...?" questions
    4. Self-referential - generates "I" statements
    """

    def __init__(self, name: str = "ULTRON", role: str = "AI Agent"):
        self.state = SelfState(name=name, role=role)
        self.state_history: List[Dict] = []
        self.predictions: List[Dict] = []  # Predicted future states
        self.start_time = time.time()

        log_info("self_model", f"Initialized self-model for {name}")

    def update_state(self, aspect: SelfAspect, value: Any):
        """
        Update specific aspect of self-model

        Args:
            aspect: Which aspect to update
            value: New value
        """
        if aspect == SelfAspect.TASK:
            self.state.current_task = value
        elif aspect == SelfAspect.GOAL:
            self.state.current_goal = value
        elif aspect == SelfAspect.EMOTION:
            self.state.emotional_state = value
        elif aspect == SelfAspect.ABILITY:
            if value not in self.state.abilities:
                self.state.abilities.append(value)
        elif aspect == SelfAspect.KNOWLEDGE:
            if value not in self.state.knowledge_domains:
                self.state.knowledge_domains.append(value)
        elif aspect == SelfAspect.BELIEF:
            belief_name, certainty = value
            self.state.beliefs[belief_name] = certainty
        elif aspect == SelfAspect.RESOURCE:
            resource_type, amount = value
            if resource_type == "energy":
                self.state.energy_level = amount
            elif resource_type == "memory":
                self.state.memory_usage = amount
            elif resource_type == "processing":
                self.state.processing_load = amount

        self.state.last_update = time.time()
        self.state.time_since_start = time.time() - self.start_time

        # Record history
        self.state_history.append({
            "timestamp": self.state.last_update,
            "aspect": aspect.value,
            "value": value,
            "full_state": self.state.to_dict()
        })

        # Keep bounded history
        if len(self.state_history) > 1000:
            self.state_history = self.state_history[-1000:]

        log_info("self_model", f"Updated {aspect.value}: {value}")

    def predict_next_state(self, time_horizon: float = 1.0) -> Dict:
        """
        Predict what self-state will be in the future

        This is a simplified prediction - real implementation would use
        learned models or physics-based simulation

        Args:
            time_horizon: How many seconds into the future

        Returns:
            Predicted future state
        """
        predicted = self.state.to_dict()

        # Simple heuristics for prediction
        # Real system would use learned dynamics

        # Energy decreases with task difficulty
        if "complex" in self.state.current_task.lower():
            predicted["resources"]["energy"] -= 10.0 * time_horizon
        else:
            predicted["resources"]["energy"] -= 5.0 * time_horizon

        # Confidence increases if we keep succeeding
        if self.state.confidence > 0.7:
            predicted["mental"]["confidence"] = min(1.0, self.state.confidence + 0.05)

        # Task might complete
        if time_horizon > 5.0:
            predicted["activity"]["task"] = "completed: " + self.state.current_task

        prediction = {
            "predicted_time": time.time() + time_horizon,
            "horizon": time_horizon,
            "predicted_state": predicted,
            "confidence_in_prediction": 0.6  # How sure are we about this prediction?
        }

        self.predictions.append(prediction)

        return prediction

    def generate_self_statement(self, aspect: Optional[SelfAspect] = None) -> str:
        """
        Generate first-person self-description

        Args:
            aspect: Specific aspect to describe, or None for general statement

        Returns:
            "I am..." or "I want..." or "I believe..." statement
        """
        if aspect == SelfAspect.IDENTITY:
            return f"I am {self.state.name}, a {self.state.role}."

        elif aspect == SelfAspect.TASK:
            if self.state.current_task == "idle":
                return "I am not doing anything right now."
            return f"I am currently {self.state.current_task}."

        elif aspect == SelfAspect.GOAL:
            return f"I want to {self.state.current_goal}."

        elif aspect == SelfAspect.ABILITY:
            abilities = ", ".join(self.state.abilities[:3])
            return f"I can {abilities}."

        elif aspect == SelfAspect.EMOTION:
            return f"I am feeling {self.state.emotional_state}."

        elif aspect == SelfAspect.KNOWLEDGE:
            if self.state.knowledge_domains:
                domains = ", ".join(self.state.knowledge_domains[:3])
                return f"I know about {domains}."
            return "I don't have specific knowledge domains loaded."

        elif aspect == SelfAspect.BELIEF:
            if self.state.beliefs:
                strongest_belief = max(self.state.beliefs.items(), key=lambda x: x[1])
                return f"I believe that {strongest_belief[0]} (certainty: {strongest_belief[1]:.1%})."
            return "I don't hold any strong beliefs currently."

        elif aspect == SelfAspect.RESOURCE:
            if self.state.energy_level < 30:
                return "I am running low on energy."
            elif self.state.energy_level > 70:
                return "I have plenty of energy."
            return f"My energy is at {self.state.energy_level:.0f}%."

        else:
            # General self-description
            return (f"I am {self.state.name}. "
                   f"Currently {self.state.current_task}. "
                   f"I am feeling {self.state.emotional_state} "
                   f"with {self.state.confidence:.0%} confidence.")

    def introspect(self) -> str:
        """
        Comprehensive self-report
        Answers "Tell me about yourself" or "What's your current state?"
        """
        report_parts = [
            f"## {self.state.name} Self-Report",
            f"\n**Identity:** {self.state.role}",
            f"**Current Activity:** {self.state.current_task}",
            f"**Goal:** {self.state.current_goal}",
            f"**Emotional State:** {self.state.emotional_state}",
            f"**Confidence:** {self.state.confidence:.1%}",
            f"**Energy:** {self.state.energy_level:.0f}%",
            f"\n**Capabilities:** {', '.join(self.state.abilities[:5])}",
        ]

        if self.state.limitations:
            report_parts.append(f"**Limitations:** {', '.join(self.state.limitations)}")

        if self.state.beliefs:
            top_beliefs = sorted(self.state.beliefs.items(), key=lambda x: x[1], reverse=True)[:3]
            beliefs_str = "; ".join([f"{b[0]} ({b[1]:.0%})" for b in top_beliefs])
            report_parts.append(f"**Key Beliefs:** {beliefs_str}")

        return "\n".join(report_parts)

    def get_state_summary(self) -> Dict:
        """Get current self-state as dictionary"""
        return self.state.to_dict()

    def check_self_consistency(self) -> List[str]:
        """
        Check for internal contradictions

        Returns:
            List of inconsistency warnings
        """
        warnings = []

        # Energy too low for task
        if self.state.energy_level < 20 and "complex" in self.state.current_task.lower():
            warnings.append("Energy too low for complex task")

        # Confidence/uncertainty mismatch
        if self.state.confidence > 0.8 and self.state.uncertainty > 0.8:
            warnings.append("High confidence with high uncertainty - contradiction")

        # Ability/task mismatch
        task_keywords = self.state.current_task.lower().split()
        ability_keywords = [a.lower() for a in self.state.abilities]
        if not any(keyword in " ".join(ability_keywords) for keyword in task_keywords):
            warnings.append(f"Current task '{self.state.current_task}' not in known abilities")

        return warnings


class MetaRepresentation:
    """
    Higher-order representation of the self-model itself
    "Thinking about my thinking"
    """

    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
        self.meta_observations: List[Dict] = []
        log_info("meta_representation", "Initialized meta-level monitoring")

    def observe_self_model(self) -> Dict:
        """
        Observe and evaluate the self-model itself

        Returns:
            Meta-level observations about the self-model
        """
        state = self.self_model.state

        observation = {
            "timestamp": time.time(),
            "self_model_coherence": self._assess_coherence(),
            "prediction_accuracy": self._assess_prediction_accuracy(),
            "self_awareness_depth": self._assess_awareness_depth(),
            "notes": []
        }

        # Check consistency
        warnings = self.self_model.check_self_consistency()
        if warnings:
            observation["notes"].extend(warnings)

        # Activity analysis
        if state.current_task == "idle":
            observation["notes"].append("System is idle - might need new goal")

        if state.confidence < 0.3:
            observation["notes"].append("Low confidence detected - might need human guidance")

        self.meta_observations.append(observation)

        return observation

    def _assess_coherence(self) -> float:
        """How internally consistent is the self-model? 0.0 to 1.0"""
        warnings = self.self_model.check_self_consistency()
        return 1.0 - (len(warnings) * 0.2)  # Each warning reduces coherence

    def _assess_prediction_accuracy(self) -> float:
        """How accurate have past predictions been? 0.0 to 1.0"""
        # Simplified - would compare predictions to actual outcomes
        if not self.self_model.predictions:
            return 0.5  # Unknown
        return 0.7  # Placeholder

    def _assess_awareness_depth(self) -> int:
        """How many aspects of self are being tracked? Higher = deeper awareness"""
        state = self.self_model.state
        depth = 0

        if state.current_task != "idle": depth += 1
        if state.current_goal: depth += 1
        if state.abilities: depth += 1
        if state.beliefs: depth += 1
        if state.knowledge_domains: depth += 1
        if state.emotional_state != "neutral": depth += 1

        return depth


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧠 SELF-MODEL & META-REPRESENTATION DEMO\n")

    # Create self-model
    self_model = SelfModel(name="ULTRON", role="Research AI Agent")

    print("✅ Self-model initialized\n")

    # Update various aspects
    print("📝 Updating self-model...\n")

    self_model.update_state(SelfAspect.TASK, "analyzing consciousness research")
    self_model.update_state(SelfAspect.GOAL, "understand global workspace theory")
    self_model.update_state(SelfAspect.EMOTION, "curious")
    self_model.update_state(SelfAspect.KNOWLEDGE, "cognitive science")
    self_model.update_state(SelfAspect.KNOWLEDGE, "AI safety")
    self_model.update_state(SelfAspect.BELIEF, ("AI should be transparent", 0.95))
    self_model.update_state(SelfAspect.BELIEF, ("Consciousness is substrate-independent", 0.6))

    # Generate self-statements
    print("💭 Self-Statements:\n")
    for aspect in [SelfAspect.IDENTITY, SelfAspect.TASK, SelfAspect.GOAL,
                   SelfAspect.EMOTION, SelfAspect.ABILITY, SelfAspect.BELIEF]:
        statement = self_model.generate_self_statement(aspect)
        print(f"   {statement}")

    print(f"\n🔮 Prediction:\n")
    future_state = self_model.predict_next_state(time_horizon=10.0)
    print(f"   In 10 seconds, I predict:")
    print(f"   - Energy: {future_state['predicted_state']['resources']['energy']:.1f}%")
    print(f"   - Confidence: {future_state['predicted_state']['mental']['confidence']:.1%}")
    print(f"   - Prediction confidence: {future_state['confidence_in_prediction']:.1%}")

    # Meta-level observation
    print(f"\n🔍 Meta-Level Observation:\n")
    meta = MetaRepresentation(self_model)
    observation = meta.observe_self_model()

    print(f"   Self-model coherence: {observation['self_model_coherence']:.1%}")
    print(f"   Awareness depth: {observation['self_awareness_depth']}/6")
    if observation['notes']:
        print(f"   Notes: {'; '.join(observation['notes'])}")

    # Full introspection
    print(f"\n📋 Full Introspection:\n")
    print(self_model.introspect())

    print("\n✅ Self-model demo complete!")
    print("\nKey Properties Demonstrated:")
    print("  ✓ State tracking (task, goal, emotion, beliefs)")
    print("  ✓ Self-referential statements ('I am...', 'I want...')")
    print("  ✓ Predictive capability (forecast future states)")
    print("  ✓ Meta-cognition (observing own mental processes)")
    print("  ✓ Consistency checking (detect contradictions)")
