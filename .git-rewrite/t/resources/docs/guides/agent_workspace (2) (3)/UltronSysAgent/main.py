#!/usr/bin/env python3
"""
UltronSysAgent - Fully Autonomous AI Voice Assistant
Author: MiniMax Agent
Version: 1.0.0
Platform: Windows 11 with NVIDIA RTX 3050 support
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.application import UltronSysAgent
from src.core.config import ConfigManager
from src.core.logger import setup_logging

def main():
    """Main entry point for UltronSysAgent"""
    print("🤖 UltronSysAgent Initializing...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = ConfigManager()
        config.load()
        
        # Initialize and run UltronSysAgent
        agent = UltronSysAgent(config)
        
        # Run the agent
        asyncio.run(agent.run())
        
    except KeyboardInterrupt:
        print("\n🔴 UltronSysAgent shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error in main: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
