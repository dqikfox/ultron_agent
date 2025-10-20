#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.github_models_tool import GitHubModelsTool

tool = GitHubModelsTool()

query = """I'm working on the ULTRON Agent project - an advanced AI agent platform with:
- Agent-based workflow engine with event-driven task orchestration
- Sandboxed code interpreter for secure Python execution
- Dual-layer memory system (short-term context + long-term knowledge)
- Multi-modal interfaces (voice, vision, GUI, CLI, API)
- OpenAI-compatible API with function calling
- 15+ built-in tools for system control, web access, AI operations
- Real-time monitoring and state persistence
- Modular tool ecosystem with dynamic discovery

What are your top suggestions for improving this AI agent platform? Focus on practical enhancements for functionality, performance, and user experience."""

result = tool.execute(f"ask mistral: {query}")
print(result)