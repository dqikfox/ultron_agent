#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Enhanced Main Entry Point
Features centralized logging, model awareness, and security enhancements
"""

import asyncio
import sys
import signal
import os
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Enhanced imports
from utils.ultron_logger import log_info, log_error, setup_logging
from utils.model_awareness import initialize_model_awareness
from agent_core_enhanced import UltronAgentEnhanced, create_enhanced_agent

def setup_signal_handlers(agent: Optional[UltronAgentEnhanced] = None) -> None:
    """Setup graceful shutdown on signals"""
    
    def signal_handler(signum, frame):
        log_info("main", f"Received signal {signum}, initiating graceful shutdown...")
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        
        if agent:
            try:
                asyncio.create_task(agent.shutdown_enhanced())
            except Exception as e:
                log_error("main", f"Error during agent shutdown: {e}")
        
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_system_requirements() -> bool:
    """Check if system meets requirements"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            log_error("main", f"Python 3.8+ required, found {sys.version}")
            return False
        
        # Check required directories
        required_dirs = ["logs", "utils", "tools", "gui"]
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                log_info("main", f"Creating required directory: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # Check configuration
        config_path = Path("ultron_config.json")
        if not config_path.exists():
            log_error("main", "Configuration file not found: ultron_config.json")
            return False
        
        log_info("main", "System requirements check passed")
        return True
    
    except Exception as e:
        log_error("main", f"System requirements check failed: {e}")
        return False

async def start_web_gui_mode(agent: UltronAgentEnhanced):
    """Start in web GUI mode"""
    try:
        log_info("main", "Starting in Web GUI mode...")
        
        # Try to import and start web server
        try:
            from web_gui_server import UltronWebServer
            web_server = UltronWebServer(agent_ref=agent, port=8080)
            
            if web_server.start_server():
                log_info("main", "Web GUI server started successfully")
                try:
                    web_server.wait_for_shutdown()
                except KeyboardInterrupt:
                    log_info("main", "Web GUI shutdown requested by user")
                    web_server.stop_server()
            else:
                log_error("main", "Failed to start web GUI server")
        
        except ImportError as e:
            log_error("main", f"Web GUI server not available: {e}")
            print("Web GUI server not available, falling back to CLI mode")
            await start_cli_mode(agent)
    
    except Exception as e:
        log_error("main", f"Web GUI mode failed: {e}")
        await start_cli_mode(agent)

async def start_gui_mode(agent: UltronAgentEnhanced):
    """Start in GUI mode"""
    try:
        log_info("main", "Starting in Enhanced GUI mode...")
        
        if hasattr(agent, 'gui') and agent.gui:
            if hasattr(agent.gui, "run_gui"):
                log_info("main", "Starting Pokédex GUI...")
                agent.gui.run_gui()  # This blocks in main thread
            else:
                log_info("main", "GUI available but no run_gui method")
        else:
            log_info("main", "No GUI available, starting CLI mode")
            await start_cli_mode(agent)
    
    except Exception as e:
        log_error("main", f"GUI mode failed: {e}")
        await start_cli_mode(agent)

async def start_cli_mode(agent: UltronAgentEnhanced):
    """Start in CLI mode with enhanced interaction"""
    try:
        log_info("main", "Starting in Enhanced CLI mode...")
        print("\n" + "="*60)
        print("🤖 ULTRON Agent 3.0 - Enhanced CLI Mode")
        print("="*60)
        print("Type 'help' for commands, 'quit' to exit")
        print("Voice commands available if voice system is enabled")
        print("="*60 + "\n")
        
        # Start voice listening if available
        if agent.voice and agent.config.get("use_voice", False):
            asyncio.create_task(agent.start_voice_listening_enhanced())
            print("🎤 Voice listening started in background")
        
        # CLI interaction loop
        while agent.is_running:
            try:
                user_input = input("ULTRON> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print_help_message(agent)
                    continue
                
                if user_input.lower() == 'status':
                    status = agent.get_system_status()
                    print_status(status)
                    continue
                
                if user_input.lower() == 'tools':
                    tools = agent.list_tools_enhanced()
                    print_tools(tools)
                    continue
                
                # Process command through agent
                log_info("main", f"Processing CLI command: {user_input}")
                response = await agent.process_command_enhanced(user_input)
                
                if response.get("success"):
                    if response.get("response"):
                        print(f"🤖 {response['response']}")
                    
                    # Show tool results if any
                    if response.get("tools"):
                        for tool_result in response["tools"]:
                            if tool_result.get("success"):
                                print(f"🔧 {tool_result['tool']}: {tool_result.get('result', 'Completed')}")
                            else:
                                print(f"❌ {tool_result['tool']}: {tool_result.get('error', 'Failed')}")
                else:
                    print(f"❌ Error: {response.get('error', 'Unknown error')}")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                log_error("main", f"CLI interaction error: {e}")
                print(f"❌ Error: {e}")
    
    except Exception as e:
        log_error("main", f"CLI mode failed: {e}")
        print(f"❌ CLI mode failed: {e}")

def print_help_message(agent: UltronAgentEnhanced):
    """Print help message"""
    print("\n📖 ULTRON Agent 3.0 - Enhanced Commands:")
    print("  help     - Show this help message")
    print("  status   - Show system status")
    print("  tools    - List available tools")
    print("  quit     - Exit the agent")
    print("\n🔧 Available Tools:")
    tools = agent.list_tools_enhanced()
    for tool in tools[:5]:  # Show first 5 tools
        print(f"  {tool['name']} - {tool.get('description', 'No description')}")
    if len(tools) > 5:
        print(f"  ... and {len(tools) - 5} more tools")
    print()

def print_status(status: dict):
    """Print system status"""
    print(f"\n📊 System Status:")
    print(f"  Version: {status.get('agent_version', 'Unknown')}")
    print(f"  Status: {status.get('status', 'Unknown')}")
    print(f"  Uptime: {status.get('uptime_formatted', 'Unknown')}")
    print(f"  Security Mode: {'✅ Enabled' if status.get('security_mode') else '❌ Disabled'}")
    print(f"  Tools Loaded: {status.get('tools_loaded', 0)}")
    
    components = status.get('components', {})
    print(f"  Components:")
    for comp, available in components.items():
        status_icon = "✅" if available else "❌"
        print(f"    {comp}: {status_icon}")
    print()

def print_tools(tools: list):
    """Print available tools"""
    print(f"\n🔧 Available Tools ({len(tools)}):")
    for tool in tools:
        status_icons = []
        if tool.get('has_match'):
            status_icons.append("M")
        if tool.get('has_execute'):
            status_icons.append("E")
        if tool.get('has_schema'):
            status_icons.append("S")
        
        status_str = f"[{'/'.join(status_icons)}]" if status_icons else "[?]"
        print(f"  {tool['name']} {status_str} - {tool.get('description', 'No description')}")
    print()

async def main() -> int:
    """Enhanced main entry point"""
    try:
        # Initialize logging and model awareness
        setup_logging()
        initialize_model_awareness()
        
        log_info("main", "Starting ULTRON Agent 3.0 Enhanced...")
        print("🚀 ULTRON Agent 3.0 - Enhanced Edition")
        print("Initializing systems...")
        
        # Check system requirements
        if not check_system_requirements():
            log_error("main", "System requirements not met")
            return 1
        
        # Create and initialize enhanced agent
        agent = await create_enhanced_agent()
        
        # Setup signal handlers
        setup_signal_handlers(agent)
        
        log_info("main", f"Agent initialized with status: {agent.status}")
        print(f"✅ Agent initialized successfully")
        
        # Determine startup mode
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == "--web":
                await start_web_gui_mode(agent)
            elif mode == "--gui":
                await start_gui_mode(agent)
            elif mode == "--cli":
                await start_cli_mode(agent)
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: --web, --gui, --cli")
                return 1
        else:
            # Auto-detect best mode
            if Path("web_gui").exists():
                await start_web_gui_mode(agent)
            elif agent.config.get("use_gui", True):
                await start_gui_mode(agent)
            else:
                await start_cli_mode(agent)
        
        # Cleanup
        await agent.shutdown_enhanced()
        log_info("main", "ULTRON Agent 3.0 Enhanced shutdown complete")
        return 0
    
    except Exception as e:
        error_msg = f"ULTRON Agent Enhanced startup failed: {e}"
        log_error("main", error_msg)
        print(f"❌ {error_msg}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)