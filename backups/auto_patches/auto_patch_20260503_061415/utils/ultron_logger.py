"""Minimal Logger"""
import logging
from pathlib import Path
from typing import Optional

def log_info(component, message, **kwargs):
    """Log an info message with optional metadata."""
    print(f"[INFO] {component}: {message}")

def log_error(component, message, exception=None, **kwargs):
    """Log an error message with optional exception details and metadata."""
    print(f"[ERROR] {component}: {message}")
    if exception:
        print(f"[ERROR] Exception: {type(exception).__name__}: {exception}")

def log_ai_decision(component, message, ai_model=None, confidence_score=None, reasoning=None):
    print(f"[AI] {component}: {message}")
    if reasoning:
        print(f"[AI] Reasoning: {reasoning}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def log_file_operation(operation: str, file_path: str, status: str = "success", details: Optional[str] = None):
    """Log a file operation with details."""
    msg = f"File {operation}: {file_path} - Status: {status}"
    if details:
        msg += f" - {details}"
    print(f"[FILE] {msg}")

# Compatibility
ultron_logger = type('Logger', (), {
    'info': lambda msg: print(f"[INFO] {msg}"),
    'error': lambda msg: print(f"[ERROR] {msg}")
})()
