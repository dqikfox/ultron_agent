#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/ultro/projects/ultron_agent')

os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

try:
    from tools.openai_assistant_tool import OpenAIAssistantTool
    
    tool = OpenAIAssistantTool()
    result = tool.execute("Write a Python function to calculate fibonacci numbers")
    print(result)
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Fallback direct test
    from openai import OpenAI
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}],
        max_tokens=200
    )
    
    print("✅ Direct OpenAI:", response.choices[0].message.content)