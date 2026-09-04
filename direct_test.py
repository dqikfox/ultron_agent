#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ultro/projects/ultron_agent')

# Test both tools directly
try:
    from tools.vercel_assistant_tool import VercelAssistantTool
    
    print("🌐 Testing Vercel Assistant Tool...")
    vercel_tool = VercelAssistantTool()
    result = vercel_tool.execute("What is Python?")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"❌ Vercel test failed: {e}")

# Test OpenAI (if available)
try:
    # Set API key directly
    os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"
    
    from tools.openai_assistant_tool import OpenAIAssistantTool
    
    print("\n🤖 Testing OpenAI Assistant Tool...")
    openai_tool = OpenAIAssistantTool()
    result = openai_tool.execute("Hello world")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"❌ OpenAI test failed: {e}")

print("\n✅ Tests complete")