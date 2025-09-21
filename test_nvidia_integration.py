#!/usr/bin/env python3
"""
Test script for NVIDIA NIM integration in ULTRON Brain
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import UltronBrain

async def test_nvidia_suggestions():
    """Test the NVIDIA NIM suggestion functionality"""

    # Mock config for testing - create object that matches expected interface
    class MockConfig:
        def __init__(self, data_dict):
            self.data = data_dict

        def get(self, key, default=None):
            return self.data.get(key, default)

    config = MockConfig({
        "ollama_base_url": "http://localhost:11434",
        "llm_model": "qwen2.5:latest",
        "openai_api_key": None,  # No OpenAI key for this test
        "ollama_api_key": None
    })

    # Initialize brain
    brain = UltronBrain(config, [], None)

    print("🧠 ULTRON Brain initialized")
    print(f"NVIDIA Router Available: {brain.nvidia_router is not None}")

    # Test different types of suggestions
    test_queries = [
        ("How can I improve my Python code?", "code"),
        ("What should I analyze in my project?", "analysis"),
        ("How do I plan a software development project?", "planning"),
        ("What's the best way to organize files?", "general")
    ]

    for query, expected_type in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {query}")
        print(f"Expected Type: {expected_type}")
        print(f"{'='*60}")

        try:
            suggestions = await brain.get_suggestions(
                query=query,
                suggestion_type=expected_type
            )

            print(f"Suggestions received ({len(suggestions)} chars):")
            print(suggestions[:500] + "..." if len(suggestions) > 500 else suggestions)

        except Exception as e:
            print(f"❌ Error getting suggestions: {e}")

    print(f"\n{'='*60}")
    print("NVIDIA NIM Integration Test Complete")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_nvidia_suggestions())