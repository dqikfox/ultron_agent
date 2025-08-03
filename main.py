import asyncio
import logging
import threading
from agent_core import UltronAgent
from gui_ultimate import UltimateAgentGUI

def main():
    """Main entry point for the Ultron Agent 3.0."""
    try:
        # Initialize the core agent logic
        agent = UltronAgent()
        
        # Launch the Ultimate GUI if enabled in the config
        if agent.config.get("use_gui", True):
            logging.info("ULTRON 3.0 GUI mode is enabled. Launching Ultimate Interface... - main.py:15")
            
            # The GUI must run in the main thread for stability on all OS
            # The agent's async tasks will run in background threads.
            ultimate_gui = UltimateAgentGUI(agent)
            ultimate_gui.run() # This will block until the GUI is closed

        else:
            # Fallback to command-line interface (CLI) mode if GUI is disabled
            logging.info("ULTRON 3.0 GUI mode is disabled. Running in CommandLine Interface (CLI) mode. - main.py:24")
            # The agent's start() method contains its own blocking run loop.
            agent.start()

    except KeyboardInterrupt:
        logging.info("ULTRON 3.0 shutdown signal received. Exiting Ultron Agent. - main.py:29")
    except Exception as e:
        logging.critical(f"A fatal error occurred in ULTRON 3.0 main application thread: {e} - main.py:31", exc_info=True)

if __name__ == "__main__":
    # Setup basic logging before anything else
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()

