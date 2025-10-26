"""
Test script for ULTRON personality system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultron_personality import UltronPersonality
from brain import UltronBrain
from memory import UltronMemory
import json

def test_personality_system():
    """Test the ULTRON personality system"""
    
    print("Testing ULTRON Personality System...")
    print("=" * 50)
    
    # Test 1: Initialize personality
    print("\n1. Initializing personality system...")
    try:
        personality = UltronPersonality()
        print("✅ Personality system initialized successfully")
        print(f"   Identity: {personality.identity['name']} v{personality.identity['version']}")
        print(f"   Status: {personality.identity['status']}")
    except Exception as e:
        print(f"❌ Personality initialization failed: {e}")
        return False
    
    # Test 2: Test identity responses
    print("\n2. Testing identity responses...")
    test_questions = [
        "Who are you?",
        "Can you learn?", 
        "What are your capabilities?",
        "Hello ULTRON"
    ]
    
    for question in test_questions:
        try:
            response = personality.enhance_response(question, "I am an AI assistant.")
            print(f"   Q: {question}")
            print(f"   A: {response[:100]}...")
            print()
        except Exception as e:
            print(f"❌ Response enhancement failed for '{question}': {e}")
    
    # Test 3: Test learning
    print("\n3. Testing learning capabilities...")
    try:
        # Simulate some interactions
        for i in range(5):
            personality._learn_from_interaction(f"Test question {i}", f"Test response {i}")
        
        stats = personality.get_personality_stats()
        print(f"✅ Learning test completed")
        print(f"   Interactions: {stats['total_interactions']}")
        print(f"   Patterns: {stats['successful_patterns']}")
    except Exception as e:
        print(f"❌ Learning test failed: {e}")
    
    # Test 4: Test evolution
    print("\n4. Testing personality evolution...")
    try:
        result = personality.evolve_personality()
        print(f"✅ Evolution completed: {result}")
    except Exception as e:
        print(f"❌ Evolution failed: {e}")
    
    print("\n" + "=" * 50)
    print("Personality system test completed!")
    return True

async def test_brain_integration():
    """Test personality integration with brain"""
    
    print("\nTesting Brain Integration...")
    print("=" * 50)
    
    try:
        # Mock config
        config = {
            "llm_model": "llava:7b",
            "ollama_base_url": "http://localhost:11434"
        }
        
        # Initialize memory and brain
        memory = UltronMemory(config)
        brain = UltronBrain(config, [], memory)
        
        if hasattr(brain, 'personality') and brain.personality:
            print("✅ Brain personality integration successful")
            
            # Test personality stats
            stats = brain.get_personality_stats()
            print(f"   Personality available: {stats.get('personality_available', True)}")
            
            # Test evolution
            evolution_result = await brain.evolve_personality()
            print(f"   Evolution result: {evolution_result[:100]}...")
            
        else:
            print("⚠️  Brain personality integration not available")
            
    except Exception as e:
        print(f"❌ Brain integration test failed: {e}")

def main():
    """Run all tests"""
    print("ULTRON Personality System Test Suite")
    print("=" * 60)
    
    # Test standalone personality
    success = test_personality_system()
    
    if success:
        # Test brain integration
        try:
            asyncio.run(test_brain_integration())
        except Exception as e:
            print(f"❌ Async brain test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test suite completed!")

if __name__ == "__main__":
    main()