"""
Robust Error Handler for Ultron Agent 2

Provides centralized error logging, user-friendly reporting, and recovery hooks.
Integrates with voice and GUI for notifications.
"""
import logging
import traceback
import sys

class RobustErrorHandler:
    def __init__(self, log_file: str = "error.log"):
        self.logger = logging.getLogger("RobustErrorHandler")
        self.logger.setLevel(logging.ERROR)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.addHandler(handler)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.error(f"Unhandled exception: {error_msg}")
        # Integrate with voice/GUI notification here
        print("[ERROR] An internal error occurred. See error.log.")

    def log_error(self, error: Exception):
        self.logger.error(f"Error: {error}")
        print(f"[ERROR] {error}")

# Global hook
error_handler = RobustErrorHandler()
sys.excepthook = error_handler.handle_exception

if __name__ == "__main__":
    try:
        raise ValueError("Test error for demonstration.")
    except Exception as e:
        error_handler.log_error(e)
