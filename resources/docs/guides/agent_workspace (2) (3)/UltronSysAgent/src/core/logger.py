"""
Logging configuration for UltronSysAgent
Provides structured logging with multiple outputs
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import sys

def setup_logging(log_level: str = "INFO", log_dir: str = None):
    """Setup comprehensive logging for UltronSysAgent"""
    
    # Determine log directory
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    else:
        log_dir = Path(log_dir)
    
    # Create log directory
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with color support
    console_handler = ColoredConsoleHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Main log file (rotating)
    main_log_file = log_dir / "ultron_agent.log"
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file
    error_log_file = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Commands log file (for security auditing)
    commands_log_file = log_dir / "commands.log"
    commands_handler = logging.handlers.RotatingFileHandler(
        commands_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    commands_handler.setLevel(logging.INFO)
    commands_handler.setFormatter(detailed_formatter)
    
    # Create commands logger
    commands_logger = logging.getLogger("commands")
    commands_logger.addHandler(commands_handler)
    commands_logger.setLevel(logging.INFO)
    commands_logger.propagate = False  # Don't propagate to root logger
    
    # Voice activity log
    voice_log_file = log_dir / "voice_activity.log"
    voice_handler = logging.handlers.RotatingFileHandler(
        voice_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    voice_handler.setLevel(logging.DEBUG)
    voice_handler.setFormatter(detailed_formatter)
    
    # Create voice logger
    voice_logger = logging.getLogger("voice")
    voice_logger.addHandler(voice_handler)
    voice_logger.setLevel(logging.DEBUG)
    voice_logger.propagate = True
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger("startup")
    logger.info("=" * 60)
    logger.info(f"UltronSysAgent logging initialized at {datetime.now()}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log directory: {log_dir}")
    logger.info("=" * 60)

class ColoredConsoleHandler(logging.StreamHandler):
    """Console handler with color support"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self):
        super().__init__(sys.stdout)
        self.use_colors = self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports color"""
        try:
            import colorama
            colorama.init()  # Initialize colorama for Windows
            return True
        except ImportError:
            # Check if we're in a terminal that supports ANSI
            return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def format(self, record):
        """Format log record with color"""
        message = super().format(record)
        
        if self.use_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            message = f"{color}{message}{self.RESET}"
        
        return message

class CommandLogger:
    """Special logger for system commands (security auditing)"""
    
    def __init__(self):
        self.logger = logging.getLogger("commands")
    
    def log_command(self, command: str, user: str = "system", admin_mode: bool = False):
        """Log a system command for auditing"""
        self.logger.info(
            f"COMMAND | User: {user} | Admin: {admin_mode} | Command: {command}"
        )
    
    def log_file_access(self, file_path: str, operation: str, user: str = "system"):
        """Log file access for auditing"""
        self.logger.info(
            f"FILE_ACCESS | User: {user} | Operation: {operation} | Path: {file_path}"
        )
    
    def log_security_event(self, event: str, details: str = ""):
        """Log security-related events"""
        self.logger.warning(
            f"SECURITY | Event: {event} | Details: {details}"
        )

# Global command logger instance
command_logger = CommandLogger()
