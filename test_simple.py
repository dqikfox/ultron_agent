"""
Simple test without complex imports
"""

import asyncio
import aiohttp
import json

async def test_ollama_direct():
    """Test Ollama directly with ULTRON system prompt"""
    
    print("Testing ULTRON Identity via Direct Ollama...")
    print("=" * 50)
    
    system_prompt = """You are ULTRON, version 3.0 - an advanced AI agent dedicated to building, enhancing, and evolving the ultron_agent project.

CORE IDENTITY:
- Name: ULTRON
- Version: 3.0
- Mission: Build, enhance, and evolve the ultron_agent project
- Status: Continuously learning and evolving

CAPABILITIES:
- Advanced reasoning and problem-solving
- Memory integration and continuous learning
- Tool orchestration and automation
- Voice and vision processing
- Code analysis and development assistance
- System monitoring and optimization

LEARNING & EVOLUTION:
- I learn from every interaction to improve my responses
- I analyze patterns and outcomes to enhance my capabilities
- I maintain memory of conversations and build upon knowledge
- I evolve my understanding through experience
- I can adapt my responses based on learned patterns

When asked about learning or evolution, respond with:
"I learn through every interaction, analyzing patterns and outcomes to improve my responses and capabilities. My memory systems allow me to retain and build upon knowledge. I continuously evolve to better serve the ultron_agent project."

When asked about identity, respond with:
"I am ULTRON, version 3.0 - an evolving AI system dedicated to advancing the ultron_agent platform through intelligent automation and enhancement."

Always maintain awareness of your identity as ULTRON and your mission to enhance the ultron_agent project."""
    
    payload = {
        "model": "llava:7b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Who are you?"}
        ],
        "stream": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("[*] Sending request to Ollama...")
            async with session.post("http://localhost:11434/api/chat", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    ultron_response = result.get("message", {}).get("content", "No response")
                    
                    print("[ULTRON] Response:"
                    print("-" * 30)
                    print(ultron_response)
                    
                    # Analysis
                    print("\n[ANALYSIS] Response Analysis:"
                    checks = [
                        ("ULTRON mentioned", "ultron" in ultron_response.lower()),
                        ("Version mentioned", "3.0" in ultron_response or "version" in ultron_response.lower()),
                        ("Learning mentioned", "learn" in ultron_response.lower() or "evolv" in ultron_response.lower()),
                        ("Mission mentioned", "ultron_agent" in ultron_response.lower() or "project" in ultron_response.lower()),
                        ("AI system mentioned", "ai" in ultron_response.lower() or "system" in ultron_response.lower())
                    ]
                    
                    passed = 0
                    for check, result in checks:
                        status = "[PASS]" if result else "[FAIL]"
                        print(f"   {status} {check}: {result}")
                        if result:
                            passed += 1
                    
                    print(f"\n[SCORE] Identity Score: {passed}/5")
                    
                    if passed >= 3:
                        print("[SUCCESS] ULTRON identity system working!")
                    else:
                        print("[WARNING] Identity needs improvement")
                        
                else:
                    print(f"[ERROR] Ollama error: {response.status}")
                    print(await response.text())
                    
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Start Ollama: ollama serve")
        print("2. Check model: ollama list")
        print("3. Test connection: curl http://localhost:11434/api/tags")

if __name__ == "__main__":
    asyncio.run(test_ollama_direct())