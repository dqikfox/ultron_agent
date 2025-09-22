#!/usr/bin/env python3
"""
Ultron Bridge Runner - Simple execution script
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ultron_bridge import UltronBridge, logger

async def interactive_mode():
    """Run bridge in interactive mode"""
    bridge = UltronBridge(port=5001)
    
    logger.info("Initializing Ultron Bridge...")
    success = await bridge.initialize()
    
    if not success:
        logger.error("Bridge initialization failed")
        return
    
    logger.info("Bridge ready! Type 'quit' to exit, 'status' for info")
    
    while True:
        try:
            command = input("\nUltron> ").strip()
            
            if command.lower() in ['quit', 'exit']:
                break
            elif command.lower() == 'status':
                status = bridge.get_status()
                print(f"Status: {status}")
            elif command:
                result = await bridge.process_command(command)
                print(f"Result: {result}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Command error: {e}")
    
    logger.info("Bridge session ended")

if __name__ == "__main__":
    asyncio.run(interactive_mode())