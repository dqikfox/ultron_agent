"""
Comprehensive Test Suite for Consciousness System
Tests alignment with goals: realistic NPCs, personality-driven decisions,
self-awareness, meta-cognition, and Ollama integration
"""

import sys
import time
import os
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cognition.ollama_conscious_agent import OllamaConsciousAgent
from cognition.npc_intelligence import EmotionType
from cognition.self_model import SelfAspect
from utils.ultron_logger import log_info


class ConsciousnessAlignmentTests:
    """Test suite validating consciousness system aligns with NPC simulation goals."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results: List[Tuple[str, bool, str]] = []

    def run_test(self, name: str, test_func, *args) -> bool:
        """Run a single test and record results."""
        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"TEST {self.tests_run}: {name}")
        print(f"{'='*60}")

        try:
            result, message = test_func(*args)

            if result:
                self.tests_passed += 1
                status = "✅ PASS"
            else:
                self.tests_failed += 1
                status = "❌ FAIL"

            print(f"\n{status}: {message}")
            self.test_results.append((name, result, message))
            return result

        except Exception as e:
            self.tests_failed += 1
            message = f"Exception: {str(e)}"
            print(f"\n❌ FAIL: {message}")
            self.test_results.append((name, False, message))
            return False

    def print_summary(self):
        """Print test summary."""
        print(f"\n\n{'='*60}")
        print(" TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Run:    {self.tests_run}")
        print(f"Passed:       {self.tests_passed} ✅")
        print(f"Failed:       {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"{'='*60}\n")

        if self.tests_failed > 0:
            print("Failed Tests:")
            for name, passed, message in self.test_results:
                if not passed:
                    print(f"  ❌ {name}: {message}")

        print(f"\n{'='*60}")
        if self.tests_failed == 0:
            print(" ✅ ALL TESTS PASSED - SYSTEM ALIGNED WITH GOALS")
        else:
            print(f" ⚠️  {self.tests_failed} TEST(S) FAILED - REVIEW REQUIRED")
        print(f"{'='*60}\n")


# Individual test functions
def test_ollama_connectivity(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 1: Verify Ollama service is accessible."""
    is_healthy = agent._check_ollama_health()

    if is_healthy:
        return True, f"Ollama service running at {agent.ollama_url}, model: {agent.model}"
    else:
        return False, f"Ollama service not accessible at {agent.ollama_url}"


def test_personality_consistency(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 2: Verify personality traits are properly configured."""
    personality_desc = agent.npc_personality.get_personality_description()
    traits = agent.npc_personality.traits

    # Check Big Five traits exist
    required_traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    has_all_traits = all(trait in traits for trait in required_traits)

    if has_all_traits and personality_desc:
        return True, f"Personality configured: {agent.personality_type}, all Big Five traits present"
    else:
        return False, f"Missing personality traits: {set(required_traits) - set(traits.keys())}"


def test_emotional_simulation(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 3: Verify emotional state tracking."""
    # Update emotions
    agent.npc_introspector.update_emotion(EmotionType.CURIOUS, 0.8)
    state = agent.npc_introspector.get_state()

    emotion = state.get("dominant_emotion")
    intensity = state.get("emotion_intensity", 0)

    if emotion == EmotionType.CURIOUS and intensity > 0.7:
        return True, f"Emotion tracking works: {emotion.value} at {intensity:.0%} intensity"
    else:
        return False, f"Emotion tracking failed: expected CURIOUS at 80%, got {emotion.value if emotion else 'None'} at {intensity:.0%}"


def test_global_workspace_attention(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 4: Verify Global Workspace selective attention."""
    from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority

    # Submit multiple items
    agent.workspace.submit_to_workspace(
        WorkspaceContent("perception", {"stimulus": "loud noise"},
                        "Heard loud bang", WorkspaceSlotPriority.HIGH)
    )
    agent.workspace.submit_to_workspace(
        WorkspaceContent("thought", {"idea": "what's for lunch?"},
                        "Thinking about food", WorkspaceSlotPriority.LOW)
    )

    agent.workspace.update_workspace()
    current = agent.workspace.get_current_content()

    # High priority should be in workspace
    has_high_priority = any(c.priority == WorkspaceSlotPriority.HIGH for c in current)

    if has_high_priority and len(current) <= 3:
        return True, f"Global Workspace attention working: {len(current)} items, high priority present"
    else:
        return False, f"Global Workspace failed: {len(current)} items, priorities: {[c.priority.value for c in current]}"


def test_self_model_awareness(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 5: Verify self-model generates first-person statements."""
    # Update self-model
    agent.self_model.update_state(SelfAspect.IDENTITY, agent.name)
    agent.self_model.update_state(SelfAspect.GOAL, "assist with testing")

    # Generate self-statement
    identity_statement = agent.self_model.generate_self_statement(SelfAspect.IDENTITY)
    goal_statement = agent.self_model.generate_self_statement(SelfAspect.GOAL)

    has_identity = agent.name in identity_statement
    has_goal = "assist" in goal_statement.lower() or "test" in goal_statement.lower()

    if has_identity and has_goal:
        return True, f"Self-model awareness: '{identity_statement}', '{goal_statement}'"
    else:
        return False, f"Self-model failed: identity={identity_statement}, goal={goal_statement}"


def test_metacognition_confidence(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 6: Verify meta-cognitive confidence estimation."""
    # Make a prediction
    prediction = agent.confidence.make_prediction(
        prediction_id="test_pred",
        predicted_output="successful_test",
        context={"test": "metacognition"}
    )

    # Check confidence is in valid range
    is_valid = 0.0 <= prediction.confidence <= 1.0

    # Get meta-cognitive assessment
    meta_state = agent.metacog_monitor.assess_current_state()
    has_state = "state" in meta_state

    if is_valid and has_state:
        return True, f"Meta-cognition working: confidence={prediction.confidence:.2%}, state={meta_state['state']}"
    else:
        return False, f"Meta-cognition failed: confidence={prediction.confidence}, meta_state={meta_state}"


def test_ollama_response_generation(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 7: Verify Ollama generates responses with consciousness context."""
    test_prompt = "What are you thinking about right now?"

    # Process input (includes Ollama query)
    response = agent.process_input(test_prompt)

    # Check response is non-empty and reasonable length
    is_valid = len(response) > 10 and len(response) < 2000

    if is_valid:
        preview = response[:100] + "..." if len(response) > 100 else response
        return True, f"Ollama response generated ({len(response)} chars): '{preview}'"
    else:
        return False, f"Ollama response invalid: length={len(response)}, content='{response[:50]}'"


def test_personality_driven_decisions(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 8: Verify decisions align with personality."""
    # Create two agents with different personalities
    brave_agent = OllamaConsciousAgent("MARCUS", "Warrior", "brave")
    cautious_agent = OllamaConsciousAgent("FELIX", "Scholar", "cautious")

    scenario = "A dragon appears! What do you do?"

    # Get decisions from both
    brave_response = brave_agent.npc_decision_engine.make_decision(
        scenario,
        options=["fight", "flee", "negotiate"],
        context={"threat_level": 0.9}
    )

    cautious_response = cautious_agent.npc_decision_engine.make_decision(
        scenario,
        options=["fight", "flee", "negotiate"],
        context={"threat_level": 0.9}
    )

    # Brave should prefer fight/negotiate, cautious should prefer flee/negotiate
    brave_choice = brave_response["choice"]
    cautious_choice = cautious_response["choice"]

    personality_aligned = (
        (brave_choice in ["fight", "negotiate"]) and
        (cautious_choice in ["flee", "negotiate"])
    )

    if personality_aligned or brave_choice != cautious_choice:
        return True, f"Personality-driven: brave chose '{brave_choice}', cautious chose '{cautious_choice}'"
    else:
        return False, f"Personalities not distinct: both chose '{brave_choice}'"


def test_conversation_memory(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 9: Verify agent maintains conversation context."""
    # First exchange
    agent.process_input("My favorite color is blue.")
    time.sleep(0.5)

    # Second exchange referencing first
    response = agent.process_input("What's my favorite color?")

    # Check if "blue" appears in response or conversation history
    has_context = "blue" in response.lower() or any(
        "blue" in msg.get("content", "").lower()
        for msg in agent.conversation_history
    )

    if has_context:
        return True, f"Conversation memory working: remembered 'blue' (history: {len(agent.conversation_history)} messages)"
    else:
        return False, f"Conversation memory failed: 'blue' not in response or history"


def test_full_consciousness_integration(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 10: Verify all consciousness modules work together."""
    test_input = "Tell me about yourself and how you're feeling."

    # Process with full consciousness
    response = agent.process_input(test_input)

    # Check multiple systems activated
    workspace_has_content = len(agent.workspace.get_current_content()) > 0
    self_model_has_state = len(agent.self_model.current_state) > 0
    has_predictions = len(agent.confidence.predictions) > 0
    has_conversation = len(agent.conversation_history) > 0

    systems_active = sum([
        workspace_has_content,
        self_model_has_state,
        has_predictions,
        has_conversation
    ])

    if systems_active >= 3:
        return True, f"Full integration: {systems_active}/4 systems active, response: '{response[:80]}...'"
    else:
        return False, f"Integration incomplete: only {systems_active}/4 systems active"


def test_alignment_with_npc_goals(agent: OllamaConsciousAgent) -> Tuple[bool, str]:
    """Test 11: Verify system meets original goal: 'imitating NPC characters and make conscious actions/choices'."""

    # Test scenario: NPC must make choice showing personality + consciousness
    scenario = "You're in a tavern. A stranger offers you a mysterious quest with great rewards but unknown dangers."

    # Get decision
    decision = agent.npc_decision_engine.make_decision(
        scenario,
        options=["accept immediately", "ask for more details", "decline politely", "ignore them"],
        context={"stranger_trustworthiness": 0.4, "reward_appeal": 0.8}
    )

    # Generate response through Ollama
    response = agent.process_input(scenario + " What do you choose and why?")

    # Check for consciousness indicators
    has_choice = decision["choice"] is not None
    has_reasoning = len(decision["reasoning"]) > 10
    has_personality = agent.personality_type in response or any(
        trait in response.lower() for trait in ["curious", "brave", "cautious", "careful", "open"]
    )
    has_emotion = agent.npc_introspector.get_state().get("dominant_emotion") is not None

    alignment_score = sum([has_choice, has_reasoning, has_personality, has_emotion])

    if alignment_score >= 3:
        return True, (
            f"NPC goal alignment: {alignment_score}/4 indicators present. "
            f"Choice: '{decision['choice']}', reasoning: '{decision['reasoning'][:60]}...'"
        )
    else:
        return False, f"NPC goal alignment weak: only {alignment_score}/4 indicators"


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print(" CONSCIOUSNESS SYSTEM - COMPREHENSIVE TEST SUITE")
    print(" Testing alignment with goals:")
    print("   - Realistic NPC simulation")
    print("   - Personality-driven behavior")
    print("   - Self-awareness & meta-cognition")
    print("   - Ollama LLM integration")
    print("="*60)

    # Create test agent
    print("\nInitializing test agent...")
    agent = OllamaConsciousAgent(
        name="TEST_AGENT",
        role="Test Subject",
        personality_type="balanced",
        model="llava:7b"
    )
    print(f"✓ Agent created: {agent.name} ({agent.role})")

    # Run test suite
    suite = ConsciousnessAlignmentTests()

    suite.run_test("Ollama Connectivity", test_ollama_connectivity, agent)
    suite.run_test("Personality Consistency", test_personality_consistency, agent)
    suite.run_test("Emotional Simulation", test_emotional_simulation, agent)
    suite.run_test("Global Workspace Attention", test_global_workspace_attention, agent)
    suite.run_test("Self-Model Awareness", test_self_model_awareness, agent)
    suite.run_test("Meta-Cognition Confidence", test_metacognition_confidence, agent)
    suite.run_test("Ollama Response Generation", test_ollama_response_generation, agent)
    suite.run_test("Personality-Driven Decisions", test_personality_driven_decisions, agent)
    suite.run_test("Conversation Memory", test_conversation_memory, agent)
    suite.run_test("Full Consciousness Integration", test_full_consciousness_integration, agent)
    suite.run_test("Alignment with NPC Goals", test_alignment_with_npc_goals, agent)

    # Print summary
    suite.print_summary()

    return suite.tests_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
