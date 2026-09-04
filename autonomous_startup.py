#!/usr/bin/env python3
"""Enhanced startup script with autonomous capabilities"""

import asyncio
import sys
from utils.ultron_logger import log_info, log_ai_decision
from autonomous_brain import get_autonomous_brain
from proactive_manager import get_proactive_manager

async def start_autonomous_ultron():
    """Start ULTRON with full autonomous capabilities"""
    
    log_info("autonomous_startup", "Initializing ULTRON Agent with autonomous capabilities")
    
    try:
        # Initialize autonomous brain
        brain = get_autonomous_brain()
        log_info("autonomous_startup", "Autonomous brain initialized")
        
        # Initialize proactive manager
        manager = get_proactive_manager()
        log_info("autonomous_startup", "Proactive manager initialized")
        
        # Start core agent
        from main import main as start_core_agent
        
        # Start proactive monitoring in background
        monitoring_task = asyncio.create_task(manager.start_proactive_monitoring())
        
        log_ai_decision("autonomous_startup", 
                       "ULTRON Agent autonomous mode activated", 
                       ai_model="autonomous_brain", 
                       confidence_score=1.0)
        
        # Start main agent
        await start_core_agent()
        
        # Keep monitoring running
        await monitoring_task
        
    except KeyboardInterrupt:
        log_info("autonomous_startup", "Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        log_info("autonomous_startup", f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🤖 Starting ULTRON Agent - Autonomous Mode")
    print("   Enhanced with learning, adaptation, and proactive capabilities")
    print("   Press Ctrl+C to shutdown")
    print()
    
    asyncio.run(start_autonomous_ultron())