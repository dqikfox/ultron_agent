"""
Quick Integration Test - Ollama + Consciousness System
Tests the full stack with proper API usage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
from cognition.ollama_conscious_agent import OllamaConsciousAgent
from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
from cognition.self_model import SelfAspect
from cognition.npc_intelligence import EmotionType


print("="*70)
print(" CONSCIOUSNESS + OLLAMA - QUICK INTEGRATION TEST")
print("="*70)

# Test 1: Ollama Health
print("\n[1/5] Checking Ollama service...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"   ✅ Ollama running - {len(models)} models available")
        if models:
            print(f"      Models: {[m['name'] for m in models[:3]]}")
    else:
        print(f"   ⚠️  Ollama returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama not accessible: {e}")

# Test 2: Create Agent
print("\n[2/5] Creating conscious agent...")
agent = OllamaConsciousAgent(
    name="ARIA",
    role="Test Assistant",
    personality_type="curious",
    model="llava:7b"
)
print(f"   ✅ Agent created: {agent.name} ({agent.role})")
print(f"      Personality type: {agent.npc_personality.npc_name}")
print(f"      Model: {agent.model}")

# Test 3: Consciousness Components
print("\n[3/5] Verifying consciousness components...")

# Global Workspace
agent.workspace.submit_to_workspace(
    WorkspaceContent(
        source_module="test",
        content_type="perception",
        data={"stimulus": "test input"},
        priority=WorkspaceSlotPriority.HIGH
    )
)
agent.workspace.update_workspace()
workspace_content = agent.workspace.get_current_content()
print(f"   ✅ Global Workspace: {len(workspace_content)} items active")

# Self-Model
agent.self_model.update_state(SelfAspect.IDENTITY, agent.name)
identity = agent.self_model.generate_self_statement(SelfAspect.IDENTITY)
print(f"   ✅ Self-Model: '{identity}'")

# Personality
personality_summary = agent.npc_personality.get_personality_summary()
print(f"   ✅ Personality: {personality_summary[:60]}...")

# Meta-Cognition
prediction = agent.confidence.make_prediction(
    prediction_id="test_001",
    output="test_prediction",
    context={"test": True}
)
print(f"   ✅ Meta-Cognition: {prediction.confidence:.0%} confidence")

# Test 4: Simple Ollama Query
print("\n[4/5] Testing Ollama response...")
test_query = "Hi! In one sentence, what are you?"

try:
    response = agent.process_input(test_query)
    print(f"   INPUT: '{test_query}'")
    print(f"   RESPONSE: '{response[:150]}{'...' if len(response) > 150 else ''}'")
    print(f"   ✅ Ollama integration working ({len(response)} chars)")
except Exception as e:
    print(f"   ❌ Ollama query failed: {e}")

# Test 5: Personality-Driven Response
print("\n[5/5] Testing personality-driven behavior...")

# Update emotional state to curious
agent.npc_introspector.state.emotional_state = EmotionType.CURIOUS
agent.npc_introspector.state.emotional_intensity = 0.8

# Ask question that should trigger curious personality
curious_query = "What would you like to learn about?"

try:
    response2 = agent.process_input(curious_query)
    print(f"   INPUT: '{curious_query}'")
    print(f"   EMOTION: {agent.npc_introspector.state.emotional_state.value} ({agent.npc_introspector.state.emotional_intensity:.0%})")
    print(f"   RESPONSE: '{response2[:150]}{'...' if len(response2) > 150 else ''}'")
    print(f"   ✅ Personality + emotion integration working")
except Exception as e:
    print(f"   ❌ Personality test failed: {e}")

# Final Summary
print("\n" + "="*70)
print(" INTEGRATION TEST SUMMARY")
print("="*70)
print(f" Agent: {agent.name} ({agent.role})")
print(f" Personality: {agent.npc_personality.npc_name}")
print(f" Conversation History: {len(agent.conversation_history)} exchanges")
print(f" Workspace Items: {len(agent.workspace.get_current_content())}")
print(f" Predictions Made: {len(agent.confidence.predictions_history)}")
print(f" Self-Model Aspects: {len(agent.self_model.state_history)} tracked")
print("="*70)

# Show full introspection
print("\n[FULL CONSCIOUSNESS INTROSPECTION]")
print(agent.introspect_full())

print("\n✅ Integration test complete!")
