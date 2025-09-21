#!/usr/bin/env python3
"""
Ultron Agent 3.0 - Main entry point
"""

import asyncio
import sys
import signal
import logging
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent_core import UltronAgent
from security_utils import sanitize_log_input


def setup_signal_handlers() -> None:
    """Setup graceful shutdown on signals."""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> int:
    """Main entry point."""
    try:
        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

        logger.info("Starting ULTRON Agent 3.0...")

        # Setup signal handlers
        setup_signal_handlers()

        # Initialize and start agent
        agent = UltronAgent()
        logger.info(f"Agent initialized with status: {agent.status}")

        # Check for GUI mode preference
        if len(sys.argv) > 1 and sys.argv[1] == '--web':
            # Force web GUI mode
            logger.info("Starting in Web GUI mode (forced)...")
            from web_gui_server import UltronWebServer
            web_server = UltronWebServer(agent_ref=agent, port=8080)
            if web_server.start_server():
                try:
                    web_server.wait_for_shutdown()
                except KeyboardInterrupt:
                    logger.info("Shutdown requested by user")
                    web_server.stop_server()

        elif Path("web_gui").exists():
            # Web GUI mode - preferred if web_gui folder exists
            logger.info("Starting in Web GUI mode (web_gui folder detected)...")
            from web_gui_server import UltronWebServer
            web_server = UltronWebServer(agent_ref=agent, port=8080)
            if web_server.start_server():
                try:
                    web_server.wait_for_shutdown()
                except KeyboardInterrupt:
                    logger.info("Shutdown requested by user")
                    web_server.stop_server()

        elif agent.gui and hasattr(agent.gui, 'run_gui'):
            # New Pokédx GUI mode - run in main thread
            logger.info("Starting in Pokédx GUI mode...")
            agent.start_gui()  # This blocks in main thread

        elif agent.gui_thread:
            # Legacy GUI mode - GUI runs in background thread
            logger.info("Starting in legacy GUI mode...")
            try:
                agent.gui_thread.join()
            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
        else:
            # CLI mode - no GUI
            logger.info("Starting in CLI mode...")
            agent.start()

        return 0

    except Exception as e:
        error_msg = f"ULTRON Agent startup failed: {sanitize_log_input(str(e))}"
        print(error_msg, file=sys.stderr)
        logging.error(error_msg, exc_info=True)
        return 1





if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

