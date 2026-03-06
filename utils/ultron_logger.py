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

# Compatibility
ultron_logger = type('Logger', (), {
    'info': lambda msg: print(f"[INFO] {msg}"),
    'error': lambda msg: print(f"[ERROR] {msg}")
})()