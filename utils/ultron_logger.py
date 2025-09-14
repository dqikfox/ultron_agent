"""
CENTRALIZED LOGGING SYSTEM for ULTRON Agent 3.0
All components must use this for structured JSON logging with component-specific log files,
AI decision tracking, and file operation logging.

Following copilot instructions architecture patterns.
"""

import logging
import logging.handlers
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import os
import sys


class UltronLogger:
    """Centralized logger for ULTRON Agent with component-specific logging."""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._setup_loggers()
        self.correlation_id = str(uuid.uuid4())[:8]
    
    def _setup_loggers(self):
        """Setup component-specific loggers with JSON formatting."""
        # Component-specific log files
        self.components = {
            'agent_core': 'agent_core.log',
            'brain': 'brain.log', 
            'voice': 'voice.log',
            'gui': 'gui.log',
            'tools': 'tools.log',
            'ai_activities': 'ai_activities.log',
            'file_changes': 'file_changes.log',
            'system': 'system.log',
            'error': 'error.log'
        }
        
        # Setup loggers for each component
        for component, filename in self.components.items():
            logger = logging.getLogger(f"ultron.{component}")
            logger.setLevel(logging.DEBUG)
            
            # Remove existing handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.logs_dir / filename,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # JSON formatter for structured logging
            formatter = UltronJSONFormatter()
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.propagate = False
    
    def log_info(self, component: str, message: str, **kwargs):
        """Log informational message with component context."""
        logger = logging.getLogger(f"ultron.{component}")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'info',
            **kwargs
        }
        logger.info(message, extra=extra)
    
    def log_error(self, component: str, message: str, error: Exception = None, **kwargs):
        """Log error message with component context and optional exception."""
        logger = logging.getLogger(f"ultron.{component}")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'error',
            **kwargs
        }
        
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_details'] = str(error)
            
        logger.error(message, extra=extra)
        
        # Also log to error component for centralized error tracking
        error_logger = logging.getLogger("ultron.error")
        error_logger.error(f"[{component}] {message}", extra=extra)
    
    def log_ai_decision(self, component: str, message: str, ai_model: str = None, 
                       confidence_score: float = None, context: Dict = None, **kwargs):
        """Log AI decision with model and confidence information."""
        logger = logging.getLogger("ultron.ai_activities")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'ai_decision',
            'ai_model': ai_model,
            'confidence_score': confidence_score,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"AI Decision: {message}", extra=extra)
    
    def log_file_operation(self, component: str, message: str, file_path: str, 
                          action: str, **kwargs):
        """Log file operation with path and action details."""
        logger = logging.getLogger("ultron.file_changes")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'file_operation',
            'file_path': str(file_path),
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"File Operation: {message}", extra=extra)
    
    def log_performance(self, component: str, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics for operations."""
        logger = logging.getLogger(f"ultron.{component}")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'performance',
            'operation': operation,
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"Performance: {operation} took {duration_ms}ms", extra=extra)
    
    def log_security_event(self, component: str, event: str, user: str = None, 
                          severity: str = 'warning', **kwargs):
        """Log security-related events."""
        logger = logging.getLogger("ultron.system")
        extra = {
            'component': component,
            'correlation_id': self.correlation_id,
            'log_type': 'security_event',
            'event': event,
            'user': user,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        getattr(logger, severity.lower(), logger.warning)(f"Security Event: {event}", extra=extra)
    
    def get_recent_logs(self, component: str, limit: int = 100) -> list:
        """Get recent log entries for a component."""
        log_file = self.logs_dir / self.components.get(component, f"{component}.log")
        
        if not log_file.exists():
            return []
        
        entries = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.log_error("ultron_logger", f"Failed to read logs for {component}: {e}")
        
        return entries
    
    def get_ai_activities(self, limit: int = 50) -> list:
        """Get recent AI decision activities."""
        return self.get_recent_logs('ai_activities', limit)
    
    def get_file_changes(self, limit: int = 50) -> list:
        """Get recent file change activities."""
        return self.get_recent_logs('file_changes', limit)


class UltronJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        # Handle exceptions
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


# Global logger instance following copilot patterns
ultron_logger = UltronLogger()

# Convenience functions for direct import
def log_info(component: str, message: str, **kwargs):
    """Log informational message."""
    ultron_logger.log_info(component, message, **kwargs)

def log_error(component: str, message: str, error: Exception = None, **kwargs):
    """Log error message."""
    ultron_logger.log_error(component, message, error, **kwargs)

def log_ai_decision(component: str, message: str, ai_model: str = None, 
                   confidence_score: float = None, **kwargs):
    """Log AI decision."""
    ultron_logger.log_ai_decision(component, message, ai_model, confidence_score, **kwargs)

def log_file_operation(component: str, message: str, file_path: str, action: str, **kwargs):
    """Log file operation."""
    ultron_logger.log_file_operation(component, message, file_path, action, **kwargs)

def log_performance(component: str, operation: str, duration_ms: float, **kwargs):
    """Log performance metrics."""
    ultron_logger.log_performance(component, operation, duration_ms, **kwargs)

def log_security_event(component: str, event: str, user: str = None, 
                      severity: str = 'warning', **kwargs):
    """Log security event."""
    ultron_logger.log_security_event(component, event, user, severity, **kwargs)