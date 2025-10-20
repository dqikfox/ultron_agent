#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.github_models_tool import GitHubModelsTool

tool = GitHubModelsTool()

query = """CONTINUE IMPLEMENTATION - You completed Task 1 (Pluggable Architecture). Now implement ALL remaining tasks 2-10 with COMPLETE working code:

Task 2: Enhanced Context Window Management
Task 3: Multi-modal Interface Integration  
Task 4: Enhanced Sandboxed Code Execution
Task 5: Improved Real-time Monitoring
Task 6: Performance Optimization
Task 7: Security and Privacy Enhancements
Task 8: Language Model Capabilities
Task 9: Multi-Agent Collaboration
Task 10: Documentation and Tutorials

REQUIREMENTS:
- Provide COMPLETE, WORKING code for each task
- Follow ULTRON Agent's existing architecture
- Use minimal, efficient implementations
- Include proper error handling
- Ensure backward compatibility

START with Task 2 and continue through Task 10. Do NOT stop until ALL tasks are completed."""

result = tool.execute(f"ask mistral: {query}")
print(result)