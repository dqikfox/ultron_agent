#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Unified Launcher
Single entry point for all execution modes: API, Web, CLI, Full orchestration
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import Optional
from utils.ultron_logger import log_info, log_error

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_api_server(host: str = "0.0.0.0", port: int = 5000):
    """Start API server only"""
    log_info("launcher", f"Starting API server on {host}:{port}")
    try:
        from api_server import create_app
        app = create_app()
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        log_error("launcher", f"API server failed: {e}")
        sys.exit(1)

def run_web_gui_server(host: str = "0.0.0.0", port: int = 8080):
    """Start Web GUI server only"""
    log_info("launcher", f"Starting Web GUI on {host}:{port}")
    try:
        from web_gui_server import app, initialize_ultron_components
        initialize_ultron_components()
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        log_error("launcher", f"Web GUI server failed: {e}")
        sys.exit(1)

async def run_cli_agent():
    """Start CLI agent for direct interaction"""
    log_info("launcher", "Starting CLI agent")
    try:
        from agent_core import UltronAgent
        from config import get_config
        from memory import Memory
        
        config = get_config()
        memory = Memory()
        agent = UltronAgent(config, [], memory)
        
        await agent.start()
        
        # Interactive CLI loop
        while True:
            try:
                user_input = input("\n🤖 ULTRON> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    log_info("launcher", "CLI agent shutting down")
                    break
                    
                # Process command
                response = await agent.process_command(user_input)
                print(f"\nAssistant: {response}")
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        await agent.shutdown()
    except Exception as e:
        log_error("launcher", f"CLI agent failed: {e}")
        sys.exit(1)

async def run_full_orchestration(
    api_port: int = 5000,
    web_port: int = 8080
):
    """Start all services in orchestrated mode (async coordination)"""
    log_info("launcher", f"Starting full orchestration (API:{api_port}, Web:{web_port})")
    
    # This would require running services in parallel with proper lifecycle management
    # For now, we recommend using run.sh for full orchestration
    print("Full orchestration mode: Use ./run.sh for complete startup with health checks")
    print("Starting API server as primary service...")
    run_api_server(port=api_port)

def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(
        description="ULTRON Agent 3.0 - Unified Launcher",
        epilog="Examples:\n"
               "  python ultron_launch.py --mode api\n"
               "  python ultron_launch.py --mode web\n"
               "  python ultron_launch.py --mode cli\n"
               "  python ultron_launch.py --mode full",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode",
        choices=["api", "web", "cli", "full"],
        default="api",
        help="Execution mode (default: api)"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=5000,
        help="API server port (default: 5000)"
    )
    
    parser.add_argument(
        "--web-port",
        type=int,
        default=8080,
        help="Web GUI port (default: 8080)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    log_info("launcher", f"ULTRON Agent 3.0 launching in {args.mode} mode")
    
    try:
        if args.mode == "api":
            run_api_server(host=args.host, port=args.api_port)
        elif args.mode == "web":
            run_web_gui_server(host=args.host, port=args.web_port)
        elif args.mode == "cli":
            asyncio.run(run_cli_agent())
        elif args.mode == "full":
            asyncio.run(run_full_orchestration(api_port=args.api_port, web_port=args.web_port))
    except KeyboardInterrupt:
        log_info("launcher", "Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        log_error("launcher", f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
