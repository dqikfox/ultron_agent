"""
Basic Error Handler for Ultron Agent 2

Provides simple error logging and reporting for integration with other modules.
"""
import logging

class ErrorHandler:
    def __init__(self, log_file: str = "error.log"):
        self.logger = logging.getLogger("ErrorHandler")
        self.logger.setLevel(logging.ERROR)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.addHandler(handler)

    def log_error(self, error: Exception):
        self.logger.error(f"Error: {error}")
        print(f"[ERROR] {error}")

if __name__ == "__main__":
    handler = ErrorHandler()
    try:
        raise RuntimeError("Test error for basic handler.")
    except Exception as e:
        handler.log_error(e)
