"""
ULTRON Agent 3.0 - Modern Entry Point
Entry point using the new modular architecture
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ultron_agent import (
    ModernUltronAgent, setup_logging, get_logger,
    UltronError, ErrorCategory, ErrorSeverity
)

logger = get_logger("ultron.main", source="main")


async def main(config_path: Optional[str] = None) -> None:
    """Main entry point for the modern ULTRON Agent."""
    try:
        logger.info("🚀 Starting ULTRON Agent 3.0...")
        
        # Initialize the agent
        agent = ModernUltronAgent(config_path)
        
        # Start the server if API is enabled
        if agent.config.use_api:
            logger.info(f"🌐 Starting web server on {agent.config.api_host}:{agent.config.api_port}")
            await agent.run_server(
                host=agent.config.api_host,
                port=agent.config.api_port
            )
        else:
            logger.info("💬 Starting in CLI mode...")
            await cli_mode(agent)
            
    except UltronError as e:
        logger.error(f"❌ ULTRON Error: {e}")
        if e.recovery_suggestion:
            logger.error(f"💡 Suggestion: {e.recovery_suggestion}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down ULTRON Agent...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


async def cli_mode(agent: ModernUltronAgent) -> None:
    """Run the agent in CLI mode for direct interaction."""
    logger.info("🎯 ULTRON Agent ready for CLI interaction")
    print("🤖 ULTRON Agent 3.0 - CLI Mode")
    print("Type 'quit' or 'exit' to stop, 'help' for commands")
    
    while True:
        try:
            user_input = input("\n🔵 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'status':
                await print_status(agent)
                continue
            elif not user_input:
                continue
                
            # Process the message
            response = await agent.process_message(user_input, session_id="cli")
            print(f"🤖 ULTRON: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"❌ Error: {e}")


def print_help() -> None:
    """Print CLI help information."""
    print("""
🆘 Available Commands:
  help     - Show this help message
  status   - Show agent status
  quit/exit - Exit the agent
  
Just type your message to chat with ULTRON!
    """)


async def print_status(agent: ModernUltronAgent) -> None:
    """Print agent status information."""
    try:
        status = await agent._get_detailed_status()
        
        print("\n📊 ULTRON Agent Status:")
        print(f"  Status: {status['agent']['status']}")
        print(f"  Version: {status['agent']['version']}")
        print(f"  Running: {status['agent']['is_running']}")
        
        if 'components' in status:
            print("\n🔧 Components:")
            for name, comp_status in status['components'].items():
                if isinstance(comp_status, dict):
                    if name == 'ollama':
                        print(f"  {name.title()}: {'✅' if comp_status.get('connected') else '❌'}")
                    else:
                        print(f"  {name.title()}: ✅")
                else:
                    print(f"  {name.title()}: {'✅' if comp_status else '❌'}")
        
        if 'statistics' in status:
            stats = status['statistics']
            print(f"\n📈 Statistics:")
            print(f"  Conversations: {stats.get('conversations', 0)}")
            print(f"  Messages: {stats.get('total_messages', 0)}")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")


if __name__ == "__main__":
    # Parse command line arguments
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        
    # Run the agent
    asyncio.run(main(config_path))