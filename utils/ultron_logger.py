"""
ULTRON Agent 3.0 - Centralized Logging System
Provides structured JSON logging with component-specific log files
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading

# Create a default logger instance for backward compatibility
class UltronLogger:
    """Wrapper class providing logging methods"""

    def log_info(self, component: str, message: str, **kwargs):
        log_info(component, message, **kwargs)

    def log_error(self, component: str, message: str, **kwargs):
        log_error(component, message, **kwargs)

    def log_ai_decision(self, component: str, message: str, ai_model: str = None, confidence_score: float = None, **kwargs):
        log_ai_decision(component, message, ai_model, confidence_score, **kwargs)

    def log_file_operation(self, component: str, message: str, file_path: str, action: str, **kwargs):
        log_file_operation(component, message, file_path, action, **kwargs)

    # Standard logging methods for compatibility
    def info(self, message: str, **kwargs):
        log_info("ultron", message, **kwargs)

    def error(self, message: str, **kwargs):
        log_error("ultron", message, **kwargs)

    def warning(self, message: str, **kwargs):
        log_info("ultron", f"WARNING: {message}", **kwargs)

    def debug(self, message: str, **kwargs):
        log_info("ultron", f"DEBUG: {message}", **kwargs)

# Thread-safe logger instances
_loggers: Dict[str, logging.Logger] = {}
_lock = threading.Lock()

def setup_logging():
    """Initialize the centralized logging system"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "ultron_master.log"),
            logging.StreamHandler()
        ]
    )

def get_logger(component: str) -> logging.Logger:
    """Get or create a component-specific logger"""
    with _lock:
        if component not in _loggers:
            logger = logging.getLogger(f"ultron.{component}")

            # Create component-specific log file
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)

            handler = logging.FileHandler(logs_dir / f"{component}.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            _loggers[component] = logger

        return _loggers[component]

def log_info(component: str, message: str, **kwargs):
    """Log info message with structured data"""
    logger = get_logger(component)

    # Create structured log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "level": "INFO",
        "message": message,
        **kwargs
    }

    # Log to component file
    logger.info(json.dumps(log_entry))

    # Also log to activities file
    _log_to_activities(log_entry)

def log_error(component: str, message: str, **kwargs):
    """Log error message with structured data"""
    logger = get_logger(component)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "level": "ERROR",
        "message": message,
        **kwargs
    }

    logger.error(json.dumps(log_entry))
    _log_to_activities(log_entry)

def log_ai_decision(component: str, message: str, ai_model: str = None, confidence_score: float = None, **kwargs):
    """Log AI decision with context and confidence"""
    logger = get_logger("ai_activities")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "level": "AI_DECISION",
        "message": message,
        "ai_model": ai_model,
        "confidence_score": confidence_score,
        **kwargs
    }

    logger.info(json.dumps(log_entry))
    _log_to_activities(log_entry)

def log_file_operation(component: str, message: str, file_path: str, action: str, **kwargs):
    """Log file operations with path and action"""
    logger = get_logger("file_operations")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "level": "FILE_OP",
        "message": message,
        "file_path": file_path,
        "action": action,
        **kwargs
    }

    logger.info(json.dumps(log_entry))
    _log_to_activities(log_entry)

def _log_to_activities(log_entry: Dict[str, Any]):
    """Log to central activities file"""
    try:
        activities_file = Path("logs") / "activities.jsonl"
        with open(activities_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Fallback logging to avoid infinite recursion
        print(f"Failed to log to activities file: {e} - ultron_logger.py:163")

def get_recent_logs(component: str = None, limit: int = 100) -> list:
    """Get recent log entries"""
    try:
        activities_file = Path("logs") / "activities.jsonl"
        if not activities_file.exists():
            return []

        logs = []
        with open(activities_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if component is None or entry.get("component") == component:
                        logs.append(entry)
                except json.JSONDecodeError:
                    continue

        # Return most recent entries
        return logs[-limit:] if len(logs) > limit else logs

    except Exception as e:
        print(f"Failed to read logs: {e} - ultron_logger.py:186")
        return []

def cleanup_old_logs(days: int = 30):
    """Clean up log files older than specified days"""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                print(f"Cleaned up old log file: {log_file} - ultron_logger.py:201")

    except Exception as e:
        print(f"Failed to cleanup logs: {e} - ultron_logger.py:204")

# Initialize logging on import
setup_logging()

# Alias for backward compatibility
ultron_logger = UltronLogger()
