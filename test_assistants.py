#!/usr/bin/env python3
"""Test OpenAI and Vercel Assistant Tools"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.openai_assistant_tool import OpenAIAssistantTool
from tools.vercel_assistant_tool import VercelAssistantTool

def test_openai_assistant():
    print("🤖 Testing OpenAI Assistant...")
    tool = OpenAIAssistantTool()
    result = tool.execute("Write a simple hello world function in Python")
    print(f"Result: {result}")
    return "✅" in result

def test_vercel_assistant():
    print("🌐 Testing Vercel Assistant...")
    tool = VercelAssistantTool()
    result = tool.execute("What is Python?")
    print(f"Result: {result}")
    return "🌐" in result

if __name__ == "__main__":
    print("Testing AI Assistant Tools\n")
    
    # Test OpenAI
    openai_success = test_openai_assistant()
    print(f"OpenAI Assistant: {'✅ PASS' if openai_success else '❌ FAIL'}\n")
    
    # Test Vercel
    vercel_success = test_vercel_assistant()
    print(f"Vercel Assistant: {'✅ PASS' if vercel_success else '❌ FAIL'}\n")
    
    print(f"Overall: {'✅ ALL PASS' if openai_success and vercel_success else '❌ SOME FAILED'}")