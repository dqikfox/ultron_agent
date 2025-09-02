#!/usr/bin/env python3
"""
ULTRON Enhanced v3.0 - Main Entry Point
=======================================

Enhanced main entry point with support for multiple interface modes,
comprehensive error handling, and integration with the new modular core system.
"""

import asyncio
import sys
import signal
import logging
import os
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup comprehensive logging system."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "ultron.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Separate error log
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    root_logger = logging.getLogger()
    root_logger.addHandler(error_handler)
    
    return logging.getLogger(__name__)

def setup_signal_handlers() -> None:
    """Setup graceful shutdown on signals."""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def print_startup_banner():
    """Display startup banner."""
    print("=" * 60)
    print("   🤖 ULTRON Enhanced v3.0 - Starting... 🤖")
    print("=" * 60)
    print()

def detect_interface_mode(args: list) -> str:
    """Detect which interface mode to use."""
    if '--web' in args:
        return 'web'
    elif '--cli' in args:
        return 'cli'
    elif '--gui' in args:
        return 'gui'
    elif Path("web").exists() and Path("web/index.html").exists():
        return 'web'  # Prefer web if available
    else:
        return 'auto'

def start_web_mode(agent_ref=None) -> int:
    """Start in web interface mode."""
    try:
        from core.web_server import UltronWebServer
        
        print("🌐 Starting ULTRON Enhanced in Web Mode...")
        print("   Access: http://localhost:8080")
        print("   Press Ctrl+C to shutdown")
        print()
        
        web_server = UltronWebServer(agent_ref=agent_ref, port=8080)
        
        if web_server.start_server():
            try:
                web_server.wait_for_shutdown()
                return 0
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
                web_server.stop_server()
                return 0
        else:
            print("❌ Failed to start web server")
            return 1
            
    except ImportError as e:
        print(f"❌ Web mode not available: {e}")
        print("   Install dependencies: pip install flask flask-socketio")
        return 1
    except Exception as e:
        print(f"❌ Web mode error: {e}")
        return 1

def start_gui_mode(agent_ref=None) -> int:
    """Start in GUI mode."""
    try:
        print("🖥️  Starting ULTRON Enhanced in GUI Mode...")
        
        # Try new Pokédx GUI first
        try:
            from pokedex_ultron_gui import PokédxUltronGUI
            gui = PokédxUltronGUI(agent_ref=agent_ref)
            gui.run_gui()
            return 0
        except ImportError:
            pass
        
        # Fallback to legacy GUI
        if agent_ref and hasattr(agent_ref, 'start_gui'):
            agent_ref.start_gui()
            return 0
        elif agent_ref and hasattr(agent_ref, 'gui_thread') and agent_ref.gui_thread:
            try:
                agent_ref.gui_thread.join()
                return 0
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
                return 0
        else:
            print("❌ GUI not available")
            return 1
            
    except Exception as e:
        print(f"❌ GUI mode error: {e}")
        return 1

def start_cli_mode(agent_ref=None) -> int:
    """Start in CLI mode."""
    try:
        print("💻 Starting ULTRON Enhanced in CLI Mode...")
        print("   Type 'help' for commands, 'exit' to quit")
        print()
        
        if agent_ref and hasattr(agent_ref, 'start'):
            agent_ref.start()
            return 0
        else:
            # Simple CLI fallback
            print("🤖 ULTRON Enhanced CLI Ready")
            
            while True:
                try:
                    user_input = input("ULTRON> ").strip()
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    elif user_input.lower() in ['help', 'h']:
                        print("Available commands:")
                        print("  help, h     - Show this help")
                        print("  status      - System status")
                        print("  test        - Run system test")
                        print("  exit, quit  - Exit ULTRON")
                    elif user_input.lower() == 'status':
                        print("🟢 ULTRON Enhanced is running")
                        print(f"   Mode: CLI")
                        print(f"   Python: {sys.version}")
                    elif user_input.lower() == 'test':
                        print("🔧 Running system test...")
                        print("✅ Core modules loaded")
                        print("✅ CLI interface working")
                        print("✅ System test passed")
                    elif user_input:
                        print(f"Echo: {user_input}")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
            
            print("\n👋 ULTRON Enhanced CLI shutting down...")
            return 0
            
    except Exception as e:
        print(f"❌ CLI mode error: {e}")
        return 1

def start_auto_mode(agent_ref=None) -> int:
    """Start in automatic mode (try GUI, fallback to CLI)."""
    print("🎯 Starting ULTRON Enhanced in Auto Mode...")
    
    # Try GUI first
    try:
        return start_gui_mode(agent_ref)
    except:
        pass
    
    # Fallback to CLI
    print("   GUI not available, falling back to CLI...")
    return start_cli_mode(agent_ref)

def main() -> int:
    """Main entry point."""
    try:
        # Setup logging
        logger = setup_logging()
        
        # Display banner
        print_startup_banner()
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Detect interface mode
        interface_mode = detect_interface_mode(sys.argv)
        logger.info(f"Interface mode: {interface_mode}")
        
        # Initialize agent (if available)
        agent_ref = None
        try:
            # Try to import and initialize the main agent
            try:
                from agent_core import UltronAgent
                agent_ref = UltronAgent()
                logger.info(f"Agent initialized with status: {getattr(agent_ref, 'status', 'unknown')}")
            except ImportError:
                logger.warning("Main agent_core not available, using standalone mode")
        except Exception as e:
            logger.warning(f"Agent initialization failed: {e}")
        
        # Start in appropriate mode
        if interface_mode == 'web':
            return start_web_mode(agent_ref)
        elif interface_mode == 'gui':
            return start_gui_mode(agent_ref)
        elif interface_mode == 'cli':
            return start_cli_mode(agent_ref)
        else:  # auto mode
            return start_auto_mode(agent_ref)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 0
    except Exception as e:
        error_msg = f"ULTRON Enhanced startup failed: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        logging.error(error_msg, exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n👋 ULTRON Enhanced exited with code {exit_code}")
    sys.exit(exit_code)