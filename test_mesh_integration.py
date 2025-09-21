#!/usr/bin/env python3
"""
ULTRON Agent - Mesh Transformer Integration Test
Tests the enhanced mesh transformer manager integration with ULTRON Agent brain
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import UltronBrain
from enhanced_mesh_transformer_manager import (
    is_enhanced_mesh_transformer_available,
    get_enhanced_mesh_transformer_manager
)


def test_mesh_transformer_availability():
    """Test if mesh transformer components are available"""
    print("🔍 Testing Mesh Transformer Availability...")

    available = is_enhanced_mesh_transformer_available()
    print(f"✅ Enhanced Mesh Transformer Available: {available}")

    if available:
        try:
            manager = get_enhanced_mesh_transformer_manager({})
            models = manager.get_available_models()
            print(f"📋 Available Models: {models}")

            memory_info = manager.get_memory_usage()
            print(f"💾 Memory Info: {memory_info}")

            perf_stats = manager.get_performance_stats()
            print(f"⚡ Performance Stats: {perf_stats}")

        except Exception as e:
            print(f"❌ Error testing manager: {e}")
    else:
        print("⚠️ Mesh transformer not available - check installation")

    return available


async def test_brain_integration():
    """Test brain integration with mesh transformer"""
    print("\n🧠 Testing Brain Integration...")

    # Create a minimal config
    config = {
        "ollama_base_url": "http://localhost:11434",
        "llm_model": "qwen2.5:latest"
    }

    # Create brain instance
    brain = UltronBrain(config, None, None)

    # Test mesh transformer status
    status = brain.get_mesh_transformer_status()
    print(f"🔧 Mesh Transformer Status: {status}")

    # Test initialization
    if brain.mesh_integration:
        print("🚀 Initializing mesh integration...")
        success = await brain.initialize_mesh_integration_async()
        print(f"✅ Initialization Success: {success}")

        if success:
            # Test a simple query
            print("💬 Testing enhanced response...")
            test_query = "Explain what a neural network is"
            response = await brain.plan_and_act(test_query)
            print(f"📝 Response: {response[:200]}...")
    else:
        print("⚠️ Mesh integration not available in brain")

    return True


async def test_enhanced_response():
    """Test enhanced response generation"""
    print("\n✨ Testing Enhanced Response Generation...")

    if not is_enhanced_mesh_transformer_available():
        print("⚠️ Skipping enhanced response test - mesh transformer not available")
        return False

    try:
        manager = get_enhanced_mesh_transformer_manager({})

        # Test model loading
        print("📥 Testing model loading...")
        model_name = "gpt-neox-1.3b"  # Use smaller model for testing

        success = await manager.load_model_async(model_name)
        if success:
            print(f"✅ Model {model_name} loaded successfully")

            # Test text generation
            print("🎯 Testing text generation...")
            prompt = "The future of AI is"
            response = await manager.generate_text_async(
                model_name=model_name,
                prompt=prompt,
                max_length=50,
                temperature=0.7
            )

            if response:
                print(f"📝 Generated: {response}")
                print("✅ Text generation successful")
            else:
                print("❌ Text generation failed")
        else:
            print(f"❌ Failed to load model {model_name}")

    except Exception as e:
        print(f"❌ Error in enhanced response test: {e}")
        return False

    return True


async def main():
    """Main test function"""
    print("🧪 ULTRON Agent - Mesh Transformer Integration Tests")
    print("=" * 60)

    # Test 1: Availability
    available = test_mesh_transformer_availability()

    # Test 2: Brain Integration
    await test_brain_integration()

    # Test 3: Enhanced Response (if available)
    if available:
        await test_enhanced_response()

    print("\n" + "=" * 60)
    print("🎉 Tests completed!")
    print("\n💡 To use mesh transformer features:")
    print("   1. Ensure Ollama is running")
    print("   2. Use brain.plan_and_act() for enhanced responses")
    print("   3. Check brain.get_mesh_transformer_status() for status")


if __name__ == "__main__":
    asyncio.run(main())
