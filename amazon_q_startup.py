#!/usr/bin/env python3
"""
Amazon Q Startup Script for ULTRON Agent
Automatically executes commands when Amazon Q starts
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main startup function"""
    print("[AMAZON Q] Auto-Run Starting...")
    
    try:
        # Import ULTRON components
        from tools.amazon_q_integration_tool import AmazonQIntegrationTool
        from agent_core import UltronAgent
        
        # Initialize Amazon Q integration
        q_tool = AmazonQIntegrationTool()
        
        # Initialize agent
        agent = UltronAgent()
        await agent.initialize()
        
        print("[SUCCESS] ULTRON Agent initialized")
        
        # Execute auto-run commands
        commands = [
            "search tor for latest news in ai",
            "start web interface",
            "system status"
        ]
        
        for cmd in commands:
            try:
                print(f"[EXEC] Executing: {cmd}")
                result = await agent.process_command(cmd)
                print(f"[OK] Result: {result[:100]}...")
                time.sleep(1)  # Brief delay between commands
            except Exception as e:
                print(f"[ERROR] Command failed: {cmd} - {e}")
        
        print("[COMPLETE] Amazon Q Auto-Run Complete!")
        
    except Exception as e:
        print(f"[FAIL] Startup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)