"""
Quick test script to verify ULTRON identity response
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain import UltronBrain
from memory import UltronMemory

async def test_identity():
    """Test ULTRON identity response"""
    
    print("Testing ULTRON Identity Response...")
    print("=" * 50)
    
    # Mock config
    config = {
        "llm_model": "llava:7b",
        "ollama_base_url": "http://localhost:11434"
    }
    
    try:
        # Initialize memory and brain
        memory = UltronMemory(config)
        brain = UltronBrain(config, [], memory)
        
        print("✅ Brain initialized successfully")
        print(f"   Model: {config['llm_model']}")
        print(f"   Ollama URL: {config['ollama_base_url']}")
        
        # Test identity question
        print("\n🤖 Testing: 'Who are you?'")
        print("-" * 30)
        
        response = await brain.direct_chat("Who are you?")
        
        print("ULTRON Response:")
        print(response)
        
        # Check for key identity markers
        print("\n📊 Response Analysis:")
        identity_markers = [
            ("ULTRON mentioned", "ultron" in response.lower()),
            ("Version mentioned", "3.0" in response or "version" in response.lower()),
            ("Learning mentioned", "learn" in response.lower() or "evolv" in response.lower()),
            ("Mission mentioned", "ultron_agent" in response.lower() or "project" in response.lower()),
            ("Capabilities mentioned", "capabilit" in response.lower() or "tool" in response.lower())
        ]
        
        for marker, found in identity_markers:
            status = "✅" if found else "❌"
            print(f"   {status} {marker}: {found}")
        
        # Overall assessment
        passed_checks = sum(1 for _, found in identity_markers if found)
        print(f"\n🎯 Identity Score: {passed_checks}/5")
        
        if passed_checks >= 3:
            print("✅ ULTRON identity system working correctly!")
        else:
            print("⚠️  Identity system may need adjustment")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check if model is available: ollama list")
        print("3. Verify network connection to localhost:11434")

if __name__ == "__main__":
    asyncio.run(test_identity())