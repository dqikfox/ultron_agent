#!/usr/bin/env python3
import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

def ultron_aware_assistant(query):
    client = OpenAI()
    
    ultron_context = """
You are integrated with ULTRON Agent 3.0 - Advanced AI Agent Platform.

SYSTEM OVERVIEW:
- Multi-modal AI platform with voice, vision, GUI, CLI, API access
- 80+ tools available for system control, web access, cloud services
- Event-driven architecture with real-time monitoring
- Supports multiple AI models: Ollama (llava:7b), OpenAI, Anthropic, AWS Bedrock

AVAILABLE TOOLS:
- aws_bedrock_tool - AWS AI models
- browser_mcp_tool - Web automation
- windows_system_tool - System control
- web_search_tool - Web search
- screenshot_analyzer_tool - Screen analysis
- voice_aws_tool - Voice processing
- unity_ai_tool - Game development
- docker_integration_tool - Container management
- github_models_tool - GitHub integration
- langflow_integration_tool - Workflow automation
- memory_context_tool - Conversation memory
- pyautogui_tool - GUI automation
- stable_diffusion_tool - Image generation
- tor_search_tool - Anonymous search
- vscode_integration_tool - IDE integration

CONFIGURATION:
- Voice: ElevenLabs TTS/STT with wake word "hey ultron"
- Vision: OCR, screenshot analysis, multimodal processing
- GUI: Pokédex-style interface on port 8080
- API: REST endpoints on port 5000
- Memory: Persistent conversation storage

When providing code or suggestions, consider ULTRON's architecture and available tools.
"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ultron_context},
            {"role": "user", "content": query}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content

# Test ULTRON-aware queries
tests = [
    "How can I use ULTRON's voice system?",
    "What tools are available for web automation?",
    "Write code to integrate with ULTRON's GUI system",
    "How do I use ULTRON's AWS tools?"
]

for test in tests:
    print(f"🤖 ULTRON Query: {test}")
    result = ultron_aware_assistant(test)
    print(f"🤖 ULTRON Assistant: {result}\n" + "="*60 + "\n")