"""
Ollama-Integrated Conscious Agent
Connects consciousness modules to Ollama LLM for realistic NPC responses
"""

import sys
import os
from pathlib import Path
import requests
import json
from typing import Dict, Any, Optional, List

# Add parent directory to path if needed
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from cognition.conscious_agent import ConsciousAgent
from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
from cognition.self_model import SelfAspect
from cognition.npc_intelligence import EmotionType
from utils.ultron_logger import log_info, log_error, log_ai_decision


class OllamaConsciousAgent(ConsciousAgent):
    """
    Conscious agent with Ollama LLM integration.
    Combines consciousness modules with language generation.
    """

    def __init__(
        self,
        name: str,
        role: str,
        personality_type: str = "balanced",
        ollama_url: str = "http://localhost:11434",
        model: str = "llava:7b"
    ):
        """
        Initialize Ollama-integrated conscious agent.

        Args:
            name: Agent's name
            role: Agent's role/purpose
            personality_type: Personality preset (brave, cautious, friendly, curious, balanced)
            ollama_url: Ollama API endpoint
            model: Model name (llava:7b, deepseek-r1:14b, qwen2.5, etc.)
        """
        super().__init__(name, role, personality_type)

        self.ollama_url = ollama_url
        self.model = model
        self.conversation_history = []
        self.max_history = 10  # Keep last 10 exchanges

        log_info("ollama_conscious_agent",
                f"Initialized {name} ({role}) with model {model}")

    def _check_ollama_health(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            log_error("ollama_conscious_agent", f"Ollama health check failed: {e}")
            return False

    def _build_consciousness_context(self, user_input: str) -> str:
        """
        Build rich context from consciousness modules for LLM.

        Returns:
            Context string with personality, emotions, goals, confidence
        """
        # Get current state from all modules
        npc_state_obj = self.npc_introspector.state
        personality = self.npc_personality.get_personality_summary()
        workspace_content = self.workspace.get_current_content()
        self_statement = self.self_model.generate_self_statement(SelfAspect.IDENTITY)
        meta_report = self.metacog_monitor.generate_meta_report()

        # Build consciousness context
        context_parts = [
            f"=== IDENTITY ===",
            f"Name: {self.name}",
            f"Role: {self.role}",
            f"Self-Awareness: {self_statement}",
            f"",
            f"=== PERSONALITY ===",
            f"{personality}",
            f"",
            f"=== CURRENT STATE ===",
            f"Health: {npc_state_obj.health}%",
            f"Energy: {npc_state_obj.energy}%",
            f"",
            f"=== EMOTIONS ===",
            f"Primary Emotion: {npc_state_obj.emotional_state.value}",
            f"Emotion Intensity: {npc_state_obj.emotional_intensity:.1%}",
            f"",
            f"=== CURRENT FOCUS (Global Workspace) ===",
        ]

        if workspace_content:
            for i, content in enumerate(workspace_content[:3], 1):
                desc = f"{content.source_module}/{content.content_type}"
                context_parts.append(f"{i}. {desc} (priority: {content.priority.value})")
        else:
            context_parts.append("(No active focus)")

        context_parts.extend([
            f"",
            f"=== META-COGNITION ===",
            f"{meta_report}",
            f"",
            f"=== GOALS ===",
            f"{', '.join(npc_state_obj.goals) if npc_state_obj.goals else 'survival, task completion'}",
        ])

        return "\n".join(context_parts)

    def _query_ollama(self, prompt: str, system_context: str) -> str:
        """
        Query Ollama with consciousness-enriched prompt.

        Args:
            prompt: User input
            system_context: Consciousness state context

        Returns:
            LLM response
        """
        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.name}, a conscious-like NPC with rich internal states.

{system_context}

INSTRUCTIONS:
- Respond authentically based on your personality, emotions, and current state
- Show awareness of your internal processes when relevant
- Make decisions that align with your personality traits
- Express confidence levels when uncertain
- Consider your active goals and current focus
- Be concise but genuine (2-4 sentences typical)

Remember: You are simulating consciousness-like behavior with personality, emotions, self-awareness, and meta-cognition."""
                }
            ]

            # Add conversation history
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                messages.append(msg)

            # Add current user input
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Call Ollama
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7 + (self.npc_personality.traits.get("openness", 0.5) * 0.3),
                    "top_p": 0.9,
                    "num_predict": 200
                }
            }

            log_ai_decision(
                "ollama_conscious_agent",
                f"Querying {self.model} with consciousness context",
                self.model,
                self.confidence.confidence_history[-1] if self.confidence.confidence_history else 0.5
            )

            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")

                # Update conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": prompt
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                # Trim history
                if len(self.conversation_history) > self.max_history * 2:
                    self.conversation_history = self.conversation_history[-self.max_history * 2:]

                return assistant_message
            else:
                log_error("ollama_conscious_agent",
                         f"Ollama returned status {response.status_code}")
                return self._fallback_response(prompt)

        except requests.exceptions.Timeout:
            log_error("ollama_conscious_agent", "Ollama request timeout")
            return self._fallback_response(prompt)
        except Exception as e:
            log_error("ollama_conscious_agent", f"Ollama query failed: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, user_input: str) -> str:
        """Generate fallback response when Ollama unavailable."""
        state_obj = self.npc_introspector.state
        emotion = state_obj.emotional_state

        return (
            f"[Ollama unavailable] As {self.name}, I'm currently feeling {emotion.value}. "
            f"I would respond based on my personality, but the "
            f"language model is offline."
        )

    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process user input with full consciousness + Ollama integration.

        Args:
            user_input: User's message/query
            context: Optional additional context

        Returns:
            Agent's response
        """
        # 1. Submit to Global Workspace
        self.workspace.submit_to_workspace(
            WorkspaceContent(
                source_module="user_interface",
                content_type="user_input",
                data={"text": user_input, "context": context or {}},
                priority=WorkspaceSlotPriority.HIGH
            )
        )

        # 2. Update workspace (attention competition)
        self.workspace.update_workspace()

        # 3. Update self-model
        self.self_model.update_state(SelfAspect.TASK, f"responding to: {user_input[:30]}")

        # 4. Make prediction with confidence
        prediction = self.confidence.make_prediction(
            prediction_id=f"response_{len(self.conversation_history)}",
            output=f"will_respond_to:{user_input[:20]}",
            context={"input": user_input}
        )

        # 5. Build consciousness context
        consciousness_context = self._build_consciousness_context(user_input)

        # 6. Query Ollama with enriched context
        if self._check_ollama_health():
            response = self._query_ollama(user_input, consciousness_context)
        else:
            response = self._fallback_response(user_input)

        # 7. Update meta-cognition
        meta_state = self.metacog_monitor.assess_current_state()
        if meta_state["state"] == "uncertain":
            response += f"\n[Confidence: {prediction.confidence:.0%}]"

        # 8. Log decision
        log_ai_decision(
            "ollama_conscious_agent",
            f"Generated response with consciousness integration",
            self.model,
            prediction.confidence
        )

        return response

    def switch_model(self, new_model: str):
        """Switch to a different Ollama model."""
        old_model = self.model
        self.model = new_model
        log_info("ollama_conscious_agent", f"Switched model: {old_model} → {new_model}")

        # Test new model
        if not self._check_ollama_health():
            log_error("ollama_conscious_agent", f"Model {new_model} not available, reverting")
            self.model = old_model


# Demo and testing functions
def demo_ollama_conscious_agent():
    """Demonstrate Ollama-integrated conscious agent."""
    print("=" * 60)
    print(" OLLAMA-INTEGRATED CONSCIOUS AGENT DEMO")
    print("=" * 60)

    # Create agent with personality
    agent = OllamaConsciousAgent(
        name="ARIA",
        role="Research Assistant",
        personality_type="curious",
        model="llava:7b"
    )

    # Check Ollama health
    print(f"\n1. Checking Ollama service...")
    if agent._check_ollama_health():
        print(f"   ✓ Ollama running at {agent.ollama_url}")
        print(f"   ✓ Using model: {agent.model}")
    else:
        print(f"   ✗ Ollama not available - will use fallback")

    # Test conversation with consciousness
    test_inputs = [
        "Hello! What are you thinking about right now?",
        "Can you tell me about your personality?",
        "How confident are you in your abilities?",
        "What emotions are you experiencing?"
    ]

    print(f"\n2. Testing conversation with consciousness integration:\n")

    for i, user_input in enumerate(test_inputs, 1):
        print(f"   [{i}] USER: {user_input}")

        # Process with full consciousness
        response = agent.process_input(user_input)

        print(f"       ARIA: {response}\n")

    # Show internal state
    print(f"\n3. Internal consciousness state:")
    print(agent.introspect_full())

    print("=" * 60)
    print(" ✓ Ollama-integrated conscious agent demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo_ollama_conscious_agent()
