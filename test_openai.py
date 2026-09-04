#!/usr/bin/env python3
import os
os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

try:
    from openai import OpenAI
    client = OpenAI()
    
    # Test basic completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    
    print("✅ OpenAI working:", response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ OpenAI error: {e}")