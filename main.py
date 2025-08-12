#!/usr/bin/env python3
"""
Ultron Agent 3.0 - Main entry point with proper structure and error handling.
"""
from __future__ import annotations

import asyncio
import sys
import signal
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ultron_agent import setup_logging, get_config, get_logger
from ultron_agent.errors import handle_error, UltronError, ErrorSeverity
from ultron_agent.api import run_server
from ultron_agent.core import get_agent


def setup_signal_handlers(logger) -> None:
    """Setup graceful shutdown on signals."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main_async() -> int:
    """Main async entry point."""
    logger = None

    try:
        # Load configuration first
        config = get_config()

        # Setup logging with correlation ID
        setup_logging(
            log_level=config.log_level.value,
            log_directory=config.log_directory,
            enable_json=True,
            enable_console=True
        )

        logger = get_logger("ultron.main", source="core")
        logger.info("Starting Ultron Agent 3.0...")
        logger.info(f"Configuration loaded: {config.sanitized_dict()}")

        # Setup signal handlers
        setup_signal_handlers(logger)

        # Initialize integrated agent with all components
        logger.info("Initializing integrated ULTRON Agent...")
        agent = await get_agent()
        
        logger.info(f"Agent initialized successfully with status: {agent.status}")
        logger.info(f"Components status: Brain={agent.brain is not None}, "
                   f"Voice={agent.voice is not None}, GUI={agent.gui is not None}, "
                   f"Maverick={agent.maverick is not None}, Tools={len(agent.tools)}")

        # Start API server with agent integration
        logger.info("Starting API server...")
        
        # Store agent reference in app state for API endpoints
        import ultron_agent.api as api_module
        api_module._agent_instance = agent
        
        await run_server(
            host=config.api_host,
            port=config.api_port,
            reload=config.debug,
            log_level=config.log_level.value
        )

        return 0

    except UltronError as e:
        if logger:
            logger.critical(f"Ultron error during startup: {e.to_dict()}")
        else:
            print(f"CRITICAL: Ultron error during startup: {e.get_user_message()}", file=sys.stderr)
        return 1

    except Exception as e:
        ultron_error = handle_error(e, logger or get_logger("ultron.main"), "startup")

        if ultron_error.severity == ErrorSeverity.CRITICAL:
            if logger:
                logger.critical(f"Critical startup failure: {ultron_error.to_dict()}")
            else:
                print(f"CRITICAL: Startup failed: {ultron_error.get_user_message()}", file=sys.stderr)
            return 1
        else:
            if logger:
                logger.error(f"Startup error (continuing): {ultron_error.to_dict()}")
            return 0


def main() -> int:
    """Main entry point."""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nShutdown requested by user", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"FATAL: Unhandled exception: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

