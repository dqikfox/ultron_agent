#!/usr/bin/env python3
"""
Test script to verify ULTRON Agent 3.0 integration.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ultron_agent import setup_logging, get_config, get_logger
from ultron_agent.core import get_agent


async def test_agent_integration():
    """Test the integrated agent functionality."""
    # Setup basic logging
    config = get_config()
    setup_logging(
        log_level=config.log_level.value,
        log_directory=config.log_directory,
        enable_json=True,
        enable_console=True
    )

    logger = get_logger("test", source="integration_test")
    logger.info("Starting ULTRON Agent 3.0 integration test...")

    try:
        # Test agent initialization
        logger.info("Testing agent initialization...")
        agent = await get_agent()

        logger.info(f"✓ Agent initialized successfully")
        logger.info(f"  Status: {agent.status}")
        logger.info(f"  Brain: {'✓' if agent.brain else '✗'}")
        logger.info(f"  Voice: {'✓' if agent.voice else '✗'}")
        logger.info(f"  Vision: {'✓' if agent.vision else '✗'}")
        logger.info(f"  GUI: {'✓' if agent.gui else '✗'}")
        logger.info(f"  Maverick: {'✓' if agent.maverick else '✗'}")
        logger.info(f"  Tools: {len(agent.tools)} loaded")

        # Test health checks
        logger.info("\nTesting health checks...")
        health_result = await agent.health_checker.check_all_health()
        logger.info(f"✓ Health check completed: {health_result['status']}")

        # Test command handling
        logger.info("\nTesting command handling...")
        test_commands = [
            "list tools",
            "hello",
            "what is your status?"
        ]

        for command in test_commands:
            logger.info(f"Testing command: '{command}'")
            try:
                result = agent.handle_text(command)
                logger.info(f"  Result: {result[:100]}..." if len(result) > 100 else f"  Result: {result}")
            except Exception as e:
                logger.error(f"  Error: {e}")

        # Test Maverick status
        logger.info("\nTesting Maverick status...")
        maverick_status = agent.get_maverick_status()
        logger.info(f"✓ Maverick status: {maverick_status}")

        logger.info("\n🎉 Integration test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


def main():
    """Main test function."""
    try:
        success = asyncio.run(test_agent_integration())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
