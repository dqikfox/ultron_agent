"""Centralized logging configuration for Ultron Agent."""
from __future__ import annotations

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import json
import uuid
from datetime import datetime
from pythonjsonlogger import jsonlogger


class UltronJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with Ultron-specific fields."""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add correlation ID if available
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            log_record['correlation_id'] = correlation_id

        # Add source component
        source = getattr(record, 'source', None)
        if source:
            log_record['source'] = source
        elif record.name:
            # Derive source from logger name
            name_parts = record.name.split('.')
            if len(name_parts) > 1:
                log_record['source'] = name_parts[-1]
            else:
                log_record['source'] = 'core'

        # Add session info if available
        session_id = getattr(record, 'session_id', None)
        if session_id:
            log_record['session_id'] = session_id

        # Add performance metrics if available
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms
        if hasattr(record, 'memory_mb'):
            log_record['memory_mb'] = record.memory_mb


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to all log records."""

    def __init__(self):
        super().__init__()
        self.correlation_id = str(uuid.uuid4())[:8]

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID if not present."""
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = self.correlation_id
        return True


def setup_logging(
    log_level: str = "INFO",
    log_directory: Optional[Path] = None,
    enable_json: bool = True,
    enable_console: bool = True,
    correlation_id: Optional[str] = None
) -> logging.Logger:
    """
    Configure centralized logging for Ultron Agent.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_directory: Directory for log files (defaults to ./logs)
        enable_json: Enable structured JSON logging
        enable_console: Enable console logging
        correlation_id: Correlation ID for this session

    Returns:
        Configured root logger
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level
    log_level_obj = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level_obj)

    # Create log directory
    if log_directory is None:
        log_directory = Path("logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    # Setup correlation filter
    correlation_filter = CorrelationFilter()
    if correlation_id:
        correlation_filter.correlation_id = correlation_id

    handlers = []

    # File handler with rotation
    if enable_json:
        file_handler = logging.handlers.RotatingFileHandler(
            log_directory / "ultron.jsonl",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level_obj)

        # JSON formatter
        json_formatter = UltronJsonFormatter(
            fmt='%(timestamp)s %(name)s %(levelname)s %(message)s'
        )
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(correlation_filter)
        handlers.append(file_handler)

    # Console handler
    if enable_console:
        # Use UTF-8 encoding for Windows compatibility with emoji
        if sys.platform == "win32":
            import io
            console_handler = logging.StreamHandler(
                io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level_obj)

        # Simple formatter for console (safe characters for Windows)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(correlation_filter)
        handlers.append(console_handler)

    # Error handler - separate file for errors
    error_handler = logging.handlers.RotatingFileHandler(
        log_directory / "ultron_errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s\n%(pathname)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    error_handler.addFilter(correlation_filter)
    handlers.append(error_handler)

    # Add all handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)

    # Set up specific loggers
    _configure_component_loggers(log_level_obj)

    # Log startup
    logger = logging.getLogger("ultron.logging")
    logger.info(f"Logging initialized - Level: {log_level}, JSON: {enable_json}, Console: {enable_console}")
    logger.info(f"Log directory: {log_directory.absolute()}")
    logger.info(f"Correlation ID: {correlation_filter.correlation_id}")

    return root_logger


def _configure_component_loggers(log_level: int) -> None:
    """Configure loggers for specific components."""

    # Component-specific log levels
    component_levels = {
        "ultron.voice": log_level,
        "ultron.gui": log_level,
        "ultron.api": log_level,
        "ultron.core": log_level,
        "ultron.models": log_level,
        "ultron.automation": log_level,
        "uvicorn": logging.WARNING,  # Reduce uvicorn noise
        "websockets": logging.WARNING,
        "asyncio": logging.WARNING,
    }

    for logger_name, level in component_levels.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str, source: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with optional source tagging.

    Args:
        name: Logger name
        source: Component source (gui, api, voice, core, etc.)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    if source:
        # Add a filter to tag all records from this logger
        class SourceFilter(logging.Filter):
            def filter(self, record):
                record.source = source
                return True

        logger.addFilter(SourceFilter())

    return logger


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **kwargs) -> None:
    """
    Log performance metrics.

    Args:
        logger: Logger instance
        operation: Name of operation
        duration_ms: Duration in milliseconds
        **kwargs: Additional metrics (memory_mb, etc.)
    """
    extra = {'duration_ms': duration_ms, **kwargs}
    logger.info(f"Performance: {operation} completed", extra=extra)


def log_security_event(logger: logging.Logger, event: str, user: Optional[str] = None, **context) -> None:
    """
    Log security-related events.

    Args:
        logger: Logger instance
        event: Security event description
        user: User identifier if available
        **context: Additional context
    """
    extra = {'security_event': True, **context}
    if user:
        extra['user'] = user

    logger.warning(f"Security: {event}", extra=extra)


def sanitize_log_input(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for logging to prevent injection and limit size.

    Args:
        text: Text to sanitize
        max_length: Maximum length to allow

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove/escape potential log injection characters
    text = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

    # Limit length
    if len(text) > max_length:
        text = text[:max_length-3] + '...'

    return text


# Context manager for correlated logging
class LogContext:
    """Context manager for correlated logging within a specific operation."""

    def __init__(self, operation: str, logger: Optional[logging.Logger] = None, **context):
        self.operation = operation
        self.logger = logger or logging.getLogger("ultron.context")
        self.context = context
        self.start_time = None
        self.correlation_id = str(uuid.uuid4())[:8]

    def __enter__(self) -> 'LogContext':
        self.start_time = datetime.utcnow()

        # Add correlation ID to all logs in this context
        correlation_id = self.correlation_id

        class ContextFilter(logging.Filter):
            def filter(self, record):
                record.correlation_id = correlation_id
                return True

        self.filter = ContextFilter()
        self.logger.addFilter(self.filter)

        extra = {'correlation_id': self.correlation_id, **self.context}
        self.logger.info(f"Started: {self.operation}", extra=extra)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000

        extra = {
            'correlation_id': self.correlation_id,
            'duration_ms': duration,
            **self.context
        }

        if exc_type:
            self.logger.error(f"Failed: {self.operation} - {exc_val}", extra=extra)
        else:
            self.logger.info(f"Completed: {self.operation}", extra=extra)

        self.logger.removeFilter(self.filter)

    def log(self, message: str, level: int = logging.INFO, **kwargs) -> None:
        """Log a message within this context."""
        extra = {'correlation_id': self.correlation_id, **kwargs}
        self.logger.log(level, f"{self.operation}: {message}", extra=extra)
