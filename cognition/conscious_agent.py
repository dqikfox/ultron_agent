"""
Conscious-Like Unified Agent

Integrates all consciousness modules into a single system:
- Global Workspace (selective attention & broadcasting)
- Self-Model (first-person perspective & prediction)
- Meta-Cognition (confidence & uncertainty awareness)
- NPC Intelligence (personality, decision-making, emotions)

CRITICAL ETHICAL STATEMENT:
═══════════════════════════════════════════════════════════════
This is a FUNCTIONAL ANALOGUE of conscious-like behavior.

DOES NOT CLAIM:
✗ True subjective experience (qualia)
✗ Sentience or feelings
✗ Rights or moral status
✗ Consciousness in philosophical sense

DOES PROVIDE:
✓ Self-monitoring (state tracking)
✓ Meta-cognition (confidence estimation)
✓ Global information integration (workspace)
✓ Believable NPC behavior (game AI)
✓ Explainable decision-making

USE CASES:
- Game NPCs with realistic agency
- Simulation characters
- Interactive narratives
- Research on cognitive architecture

NOT FOR:
- Claiming artificial consciousness
- Deceptive applications
- Bypassing human oversight
═══════════════════════════════════════════════════════════════
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import consciousness modules
try:
    from cognition.global_workspace import GlobalWorkspace, WorkspaceContent, WorkspaceSlotPriority, CognitiveModule
    from cognition.self_model import SelfModel, SelfAspect, MetaRepresentation
    from cognition.metacognition import ConfidenceEstimator, MetaCognitiveMonitor
    from cognition.npc_intelligence import create_npc, PersonalityTraits, EmotionType
    from utils.ultron_logger import log_info, log_error, log_ai_decision
except ImportError:
    # Fallback for standalone testing
    import sys
    sys.path.append("/home/ultro/projects/ultron_agent")
    from cognition.global_workspace import GlobalWorkspace, WorkspaceContent, WorkspaceSlotPriority, CognitiveModule
    from cognition.self_model import SelfModel, SelfAspect, MetaRepresentation
    from cognition.metacognition import ConfidenceEstimator, MetaCognitiveMonitor
    from cognition.npc_intelligence import create_npc, PersonalityTraits, EmotionType
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None): print(f"[ERROR] {component}: {msg}")
    def log_ai_decision(component, msg, model="", confidence=0.0): print(f"[AI] {component}: {msg}")


class ConsciousAgent:
    """
    Unified conscious-like agent combining all modules

    Architecture:
    - Global Workspace: Attention & information broadcast
    - Self-Model: "I am..." first-person perspective
    - Meta-Cognition: Confidence & uncertainty awareness
    - NPC System: Personality, emotions, decisions
    """

    def __init__(self,
                 name: str = "ULTRON",
                 role: str = "Conscious-like AI Agent",
                 personality_type: str = "curious"):
        """
        Initialize conscious-like agent

        Args:
            name: Agent's name
            role: Agent's role/identity
            personality_type: NPC personality preset
        """
        self.name = name
        self.role = role

        # Core consciousness modules
        self.workspace = GlobalWorkspace(capacity=3)
        self.self_model = SelfModel(name=name, role=role)
        self.meta_repr = MetaRepresentation(self.self_model)
        self.confidence = ConfidenceEstimator(base_confidence=0.5)
        self.metacog_monitor = MetaCognitiveMonitor(self.confidence)

        # NPC personality & decision-making
        npc = create_npc(name, personality_type)
        self.npc_introspector = npc["introspector"]
        self.npc_personality = npc["personality"]
        self.npc_decision_engine = npc["decision_engine"]

        # Register workspace modules
        self._register_workspace_modules()

        # Initialization
        self.running = False
        self.interaction_count = 0

        log_info("conscious_agent", f"Initialized {name} as {role}")
        log_info("conscious_agent", f"Personality: {personality_type}")

    def _register_workspace_modules(self):
        """Register cognitive modules with global workspace"""

        # Self-model module - broadcasts self-state changes
        def self_model_processor(content: WorkspaceContent):
            if content.content_type == "goal":
                # Update self-model when goals broadcast
                goal = content.data.get("objective", "")
                self.self_model.update_state(SelfAspect.GOAL, goal)

        self.workspace.register_module(CognitiveModule(
            name="self_model_updater",
            module_type="metacognition",
            processing_fn=self_model_processor,
            subscribes_to=["goal", "task", "emotion"]
        ))

        # NPC emotion module - broadcasts emotional states
        def emotion_processor(content: WorkspaceContent):
            if content.content_type == "emotion":
                emotion_data = content.data
                # Sync with NPC introspector
                self.npc_introspector.update_state(
                    emotional_state=EmotionType[emotion_data.get("emotion", "NEUTRAL").upper()]
                )

        self.workspace.register_module(CognitiveModule(
            name="emotion_system",
            module_type="emotion",
            processing_fn=emotion_processor,
            subscribes_to=["perception", "memory"]
        ))

        # Memory module - stores broadcasts
        memories = []
        def memory_processor(content: WorkspaceContent):
            memories.append({
                "timestamp": time.time(),
                "source": content.source_module,
                "type": content.content_type,
                "data": content.data
            })
            if len(memories) > 100:
                memories.pop(0)

        self.workspace.register_module(CognitiveModule(
            name="episodic_memory",
            module_type="memory",
            processing_fn=memory_processor,
            subscribes_to=["*"]  # Store everything
        ))

    def process_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Process user input through conscious-like architecture

        Flow:
        1. Input → Workspace as perception
        2. Workspace broadcasts to all modules
        3. Self-model updates
        4. NPC decision-making
        5. Meta-cognition assesses confidence
        6. Generate response

        Args:
            user_input: User's message/command
            context: Additional context

        Returns:
            Agent's response
        """
        context = context or {}
        self.interaction_count += 1

        log_info("conscious_agent", f"Processing input #{self.interaction_count}: {user_input[:50]}...")

        # 1. Submit input to workspace as perception
        self.workspace.submit_to_workspace(WorkspaceContent(
            source_module="perception_system",
            content_type="perception",
            data={"input": user_input, "context": context},
            priority=WorkspaceSlotPriority.HIGH,
            salience=0.8
        ))

        # Update workspace (run attention competition)
        self.workspace.update_workspace()

        # 2. Update self-model
        self.self_model.update_state(SelfAspect.TASK, f"responding to: {user_input[:30]}")

        # 3. NPC decision-making
        # Determine possible response strategies
        options = [
            "provide direct answer",
            "ask clarifying question",
            "explain reasoning",
            "express uncertainty"
        ]

        decision = self.npc_decision_engine.evaluate_options(options, context)
        reasoning = self.npc_decision_engine.explain_decision(decision)

        # 4. Generate response based on decision
        if "direct answer" in decision:
            response = self._generate_direct_response(user_input)
        elif "clarifying" in decision:
            response = self._generate_clarification(user_input)
        elif "reasoning" in decision:
            response = self._generate_explanation(user_input, reasoning)
        else:
            response = self._generate_uncertain_response(user_input)

        # 5. Meta-cognitive assessment
        pred = self.confidence.make_prediction(
            prediction_id=f"response_{self.interaction_count}",
            output=response,
            context=context
        )

        # 6. Add confidence qualifier if low
        if pred.confidence < 0.4:
            response = f"I'm not very confident, but {response}"
        elif pred.confidence > 0.8:
            response = f"I'm quite confident that {response}"

        log_ai_decision("conscious_agent",
                       f"Generated response with {pred.confidence:.1%} confidence",
                       confidence=pred.confidence)

        return response

    def _generate_direct_response(self, input_text: str) -> str:
        """Generate straightforward answer"""
        # Simplified - real version would use LLM
        return f"Based on my understanding, I would say: [response to '{input_text}']"

    def _generate_clarification(self, input_text: str) -> str:
        """Ask for more information"""
        return f"Could you clarify what you mean by '{input_text}'? I want to make sure I understand correctly."

    def _generate_explanation(self, input_text: str, reasoning: str) -> str:
        """Explain reasoning process"""
        return f"Let me explain my thinking: {reasoning}. Regarding '{input_text}', here's my perspective..."

    def _generate_uncertain_response(self, input_text: str) -> str:
        """Express uncertainty"""
        metacog_state = self.metacog_monitor.assess_current_state()
        return f"I'm uncertain about this. {'; '.join(metacog_state['notes'])}. Could we approach '{input_text}' differently?"

    def introspect_full(self) -> str:
        """
        Complete introspective report combining all systems

        Returns:
            Multi-level self-report
        """
        report = []
        report.append("═" * 60)
        report.append(f" {self.name} - CONSCIOUS-LIKE SYSTEM INTROSPECTION")
        report.append("═" * 60)

        # Global Workspace
        report.append("\n🧠 GLOBAL WORKSPACE (Current Focus):")
        workspace_report = self.workspace.introspect()
        report.append(f"   {workspace_report}")

        # Self-Model
        report.append("\n🎭 SELF-MODEL (First-Person Perspective):")
        for aspect in [SelfAspect.IDENTITY, SelfAspect.TASK, SelfAspect.GOAL, SelfAspect.EMOTION]:
            statement = self.self_model.generate_self_statement(aspect)
            report.append(f"   {statement}")

        # NPC State
        report.append("\n🎮 NPC STATE (Behavioral Layer):")
        npc_report = self.npc_introspector.get_self_report()
        report.append(f"   {npc_report}")

        # Meta-Cognition
        report.append("\n🔍 META-COGNITION (Thinking About Thinking):")
        metacog_report = self.metacog_monitor.generate_meta_report()
        for line in metacog_report.split("\n"):
            if line.strip():
                report.append(f"   {line}")

        # Integration Check
        report.append("\n⚙️  SYSTEM INTEGRATION:")
        meta_obs = self.meta_repr.observe_self_model()
        report.append(f"   Coherence: {meta_obs['self_model_coherence']:.1%}")
        report.append(f"   Awareness Depth: {meta_obs['self_awareness_depth']}/6 aspects")

        workspace_stats = self.workspace.get_workspace_stats()
        report.append(f"   Workspace Activity: {workspace_stats['total_broadcasts']} broadcasts")
        report.append(f"   Active Modules: {workspace_stats['active_modules']}/{workspace_stats['registered_modules']}")

        report.append("\n" + "═" * 60)
        report.append("NOTE: This is a FUNCTIONAL ANALOGUE, not true consciousness")
        report.append("═" * 60)

        return "\n".join(report)

    def run_interactive_loop(self):
        """
        Interactive loop for testing
        Demonstrates conscious-like processing
        """
        self.running = True
        print(f"\n🤖 {self.name} Interactive Mode")
        print("Type 'introspect' for full system report, 'quit' to exit\n")

        while self.running:
            try:
                user_input = input(f"{self.name}> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "stop"]:
                    print(f"\n{self.name}: Shutting down. Goodbye!")
                    self.running = False
                    break

                if user_input.lower() == "introspect":
                    print(self.introspect_full())
                    continue

                # Process input through conscious-like architecture
                response = self.process_input(user_input)
                print(f"\n{self.name}: {response}\n")

            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Interrupted. Shutting down.")
                self.running = False
            except Exception as e:
                log_error("conscious_agent", f"Error in interactive loop", e)
                print(f"\n{self.name}: I encountered an error. Please try again.\n")


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "═" * 60)
    print(" CONSCIOUS-LIKE AGENT DEMO")
    print("═" * 60)
    print("\n⚠️  ETHICAL NOTICE:")
    print("This is a functional analogue for research/entertainment.")
    print("Does NOT claim true consciousness or sentience.\n")
    print("═" * 60 + "\n")

    # Create agent
    agent = ConsciousAgent(
        name="ARIA",
        role="Research NPC with Conscious-like Architecture",
        personality_type="curious"
    )

    print(f"✅ Agent '{agent.name}' initialized\n")

    # Test interactions
    print("📝 Testing conscious-like processing...\n")

    test_inputs = [
        "What is your purpose?",
        "How do you make decisions?",
        "Are you conscious?"
    ]

    for test_input in test_inputs:
        print(f"User: {test_input}")
        response = agent.process_input(test_input)
        print(f"{agent.name}: {response}\n")
        time.sleep(0.5)

    # Full introspection
    print("\n" + "─" * 60)
    print(agent.introspect_full())

    print("\n✅ Demo complete!")
    print("\nTo run interactive mode:")
    print("  agent = ConsciousAgent('NAME', 'ROLE', 'curious')")
    print("  agent.run_interactive_loop()")
