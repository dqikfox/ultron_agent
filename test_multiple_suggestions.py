#!/usr/bin/env python3
import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

def get_code_suggestion(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

# Test different code suggestions
tests = [
    "Write a Python function to sort a list",
    "Create a class for a simple calculator",
    "Write code to read a CSV file"
]

for test in tests:
    print(f"🤖 Request: {test}")
    result = get_code_suggestion(test)
    print(f"✅ Response: {result}\n" + "="*50 + "\n")