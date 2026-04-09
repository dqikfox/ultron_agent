"""Minimal Logger"""

def log_info(component, message, **kwargs):
    """Log an info message with optional metadata."""
    print(f"[INFO] {component}: {message}")

def log_error(component, message, exception=None, **kwargs):
    """Log an error message with optional exception details and metadata."""
    print(f"[ERROR] {component}: {message}")
    if exception:
        print(f"[ERROR] Exception: {type(exception).__name__}: {exception}")

def log_ai_decision(component, message, ai_model=None, confidence_score=None):
    print(f"[AI] {component}: {message}")


class _Logger:
    """Minimal logger compatible with the stdlib logging.Logger interface."""

    @staticmethod
    def info(msg, *args, **kwargs):
        print(f"[INFO] {msg}")

    @staticmethod
    def warning(msg, *args, **kwargs):
        print(f"[WARNING] {msg}")

    @staticmethod
    def error(msg, *args, **kwargs):
        print(f"[ERROR] {msg}")

    @staticmethod
    def debug(msg, *args, **kwargs):
        print(f"[DEBUG] {msg}")

    @staticmethod
    def critical(msg, *args, **kwargs):
        print(f"[CRITICAL] {msg}")


# Compatibility singleton
ultron_logger = _Logger()
