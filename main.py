from asyncio import run as asyncio_run
from logging import basicConfig, INFO, info, critical, getLogger
from threading import Thread
from agent_core import UltronAgent
from gui_ultimate import UltimateAgentGUI

def main():
    """Main entry point for the Ultron Agent 3.0."""
    try:
        # Initialize the core agent logic
        agent = UltronAgent()
        
        # Launch the Ultimate GUI if enabled in the config
        if agent.config.get("use_gui", True):
            info("ULTRON 3.0 GUI mode is enabled. Launching Ultimate Interface...")
            
            # The GUI must run in the main thread for stability on all OS
            # The agent's async tasks will run in background threads.
            ultimate_gui = UltimateAgentGUI(agent)
            ultimate_gui.run() # This will block until the GUI is closed

        else:
            # Fallback to command-line interface (CLI) mode if GUI is disabled
            info("ULTRON 3.0 GUI mode is disabled. Running in CommandLine Interface (CLI) mode.")
            # The agent's start() method contains its own blocking run loop.
            agent.start()

    except KeyboardInterrupt:
        info("ULTRON 3.0 shutdown signal received. Exiting Ultron Agent.")
    except (ImportError, ModuleNotFoundError) as e:
        critical(f"Missing required module in ULTRON 3.0: {e}", exc_info=True)
    except Exception as e:
        from security_utils import sanitize_log_input
        critical(f"A fatal error occurred in ULTRON 3.0 main application thread: {sanitize_log_input(str(e))}", exc_info=True)

if __name__ == "__main__":
    # Setup basic logging before anything else
    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    main()

