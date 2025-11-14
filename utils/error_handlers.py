"""
ULTRON Error Handling Framework
Comprehensive exception hierarchy and recovery strategies
Following production-grade error handling patterns

PEP 484 Type Hints Standardization: ✅ COMPLETE
"""

import asyncio
import logging
from typing import (
    Optional, Dict, Any, List, Callable, Tuple, Type, TypeVar
)
from datetime import datetime
from functools import wraps
from enum import Enum

# Type variables for generic error handling
T = TypeVar('T')
E = TypeVar('E', bound='UltronError')


# ============================================================================
# ERROR SEVERITY & CLASSIFICATION
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity classification"""
    CRITICAL: str = "critical"      # System failure, needs immediate attention
    HIGH: str = "high"              # Major functionality affected
    MEDIUM: str = "medium"          # Some functionality degraded
    LOW: str = "low"                # Minor issue, system continues
    INFO: str = "info"              # Informational, no impact


class ErrorCategory(Enum):
    """Error categorization for handling strategies"""
    NETWORK: str = "network"           # Connection/HTTP errors
    CONFIG: str = "config"             # Configuration issues
    TOOL: str = "tool"                 # Tool execution failures
    API: str = "api"                   # API/endpoint errors
    FILE_IO: str = "file_io"          # File operations
    ASYNC: str = "async"               # Async/concurrency issues
    RESOURCE: str = "resource"         # Resource management
    VALIDATION: str = "validation"     # Data validation
    TIMEOUT: str = "timeout"           # Operation timeouts
    UNKNOWN: str = "unknown"           # Uncategorized


# ============================================================================
# BASE EXCEPTION HIERARCHY
# ============================================================================

class UltronError(Exception):
    """Base ULTRON exception with enhanced context"""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        retriable: bool = False,
        recovery_suggestion: Optional[str] = None
    ) -> None:
        """Initialize ULTRON error with full context"""
        self.message: str = message
        self.severity: ErrorSeverity = severity
        self.category: ErrorCategory = category
        self.context: Dict[str, Any] = context or {}
        self.retriable: bool = retriable
        self.recovery_suggestion: Optional[str] = recovery_suggestion
        self.timestamp: datetime = datetime.now()
        self.attempt: int = 1

        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "retriable": self.retriable,
            "recovery": self.recovery_suggestion,
            "timestamp": self.timestamp.isoformat(),
            "attempt": self.attempt
        }

    def __str__(self) -> str:
        """String representation"""
        return f"[{self.severity.value.upper()}] {self.message}"


# ============================================================================
# NETWORK ERRORS
# ============================================================================

class NetworkError(UltronError):
    """Network communication error with retry support"""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        retriable: bool = True,
        **kwargs: Any
    ) -> None:
        """Initialize network error"""
        self.url: Optional[str] = url
        self.status_code: Optional[int] = status_code

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "url": url,
            "status_code": status_code
        })

        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.NETWORK,
            context=context,
            retriable=retriable,
            recovery_suggestion="Check network connectivity and retry"
        )


class TimeoutError(UltronError):
    """Operation timeout error"""

    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        **kwargs: Any
    ) -> None:
        """Initialize timeout error"""
        self.operation: str = operation
        self.timeout_seconds: float = timeout_seconds

        msg: str = (
            f"Operation '{operation}' timed out after "
            f"{timeout_seconds}s"
        )
        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "operation": operation,
            "timeout": timeout_seconds
        })

        super().__init__(
            message=msg,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TIMEOUT,
            context=context,
            retriable=True,
            recovery_suggestion="Increase timeout or reduce operation scope"
        )


# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================

class ConfigError(UltronError):
    """Configuration validation error"""

    def __init__(
        self,
        message: str,
        missing_fields: Optional[List[str]] = None,
        invalid_fields: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize configuration error"""
        self.missing_fields: List[str] = missing_fields or []
        self.invalid_fields: Dict[str, str] = invalid_fields or {}

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "missing": self.missing_fields,
            "invalid": self.invalid_fields
        })

        super().__init__(
            message=message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIG,
            context=context,
            retriable=False,
            recovery_suggestion="Fix configuration file and restart"
        )


# ============================================================================
# TOOL ERRORS
# ============================================================================

class ToolError(UltronError):
    """Tool execution error with context"""

    def __init__(
        self,
        tool_name: str,
        command: str,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Initialize tool execution error"""
        self.tool_name: str = tool_name
        self.command: str = command
        self.original_error: Exception = error

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "tool": tool_name,
            "command": command,
            "original_error": str(error)
        })

        msg: str = (
            f"Tool '{tool_name}' failed executing '{command}': "
            f"{error}"
        )

        super().__init__(
            message=msg,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.TOOL,
            context=context,
            retriable=True,
            recovery_suggestion="Check tool configuration and retry"
        )


class ToolNotFoundError(UltronError):
    """Tool not found error"""

    def __init__(
        self,
        tool_name: str,
        available_tools: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize tool not found error"""
        self.tool_name: str = tool_name
        self.available_tools: List[str] = available_tools or []

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "requested_tool": tool_name,
            "available_tools": self.available_tools
        })

        message: str = f"Tool '{tool_name}' not found"

        tools_str: str = ", ".join(self.available_tools)
        recovery: str = f"Available tools: {tools_str}"

        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TOOL,
            context=context,
            retriable=False,
            recovery_suggestion=recovery
        )


# ============================================================================
# API ERRORS
# ============================================================================

class APIError(UltronError):
    """API endpoint error"""

    def __init__(
        self,
        message: str,
        status_code: int,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Initialize API error"""
        self.status_code: int = status_code
        self.endpoint: Optional[str] = endpoint
        self.details: Dict[str, Any] = details or {}

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "status_code": status_code,
            "endpoint": endpoint,
            "details": self.details
        })

        severity: ErrorSeverity = (
            ErrorSeverity.CRITICAL if status_code >= 500
            else ErrorSeverity.HIGH if status_code >= 400
            else ErrorSeverity.MEDIUM
        )

        super().__init__(
            message=message,
            severity=severity,
            category=ErrorCategory.API,
            context=context,
            retriable=status_code >= 500,
            recovery_suggestion="Check API logs and configuration"
        )


# ============================================================================
# FILE I/O ERRORS
# ============================================================================

class FileError(UltronError):
    """File operation error"""

    def __init__(
        self,
        message: str,
        path: str,
        operation: str,
        reason: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize file error"""
        self.path: str = path
        self.operation: str = operation
        self.reason: Optional[str] = reason

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "path": path,
            "operation": operation,
            "reason": reason
        })

        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.FILE_IO,
            context=context,
            retriable=False,
            recovery_suggestion="Check file permissions and path"
        )


# ============================================================================
# ASYNC ERRORS
# ============================================================================

class AsyncError(UltronError):
    """Async operation error"""

    def __init__(
        self,
        message: str,
        operation: str,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> None:
        """Initialize async error"""
        self.operation: str = operation
        self.timeout: Optional[float] = timeout

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "operation": operation,
            "timeout": timeout
        })

        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.ASYNC,
            context=context,
            retriable=True,
            recovery_suggestion="Check system resources and retry"
        )


# ============================================================================
# RESOURCE ERRORS
# ============================================================================

class ResourceError(UltronError):
    """Resource management error"""

    def __init__(
        self,
        resource: str,
        operation: str,
        reason: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize resource error"""
        self.resource: str = resource
        self.operation: str = operation
        self.reason: Optional[str] = reason

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "resource": resource,
            "operation": operation,
            "reason": reason
        })

        message: str = f"Resource error ({resource}): {operation}"

        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RESOURCE,
            context=context,
            retriable=True,
            recovery_suggestion="Check resource availability and cleanup"
        )


# ============================================================================
# VALIDATION ERRORS
# ============================================================================

class ValidationError(UltronError):
    """Data validation error"""

    def __init__(
        self,
        message: str,
        field: str,
        value: Any,
        expected_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize validation error"""
        self.field: str = field
        self.value: Any = value
        self.expected_type: Optional[str] = expected_type

        context: Dict[str, Any] = kwargs.get("context", {})
        context.update({
            "field": field,
            "value": str(value)[:100],  # Truncate for safety
            "expected_type": expected_type
        })

        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context,
            retriable=False,
            recovery_suggestion="Check input data and format"
        )


# ============================================================================
# RETRY STRATEGY
# ============================================================================

class RetryStrategy:
    """Exponential backoff retry strategy"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ) -> None:
        """Initialize retry strategy"""
        self.max_attempts: int = max_attempts
        self.base_delay: float = base_delay
        self.max_delay: float = max_delay
        self.exponential_base: float = exponential_base
        self.attempt: int = 0

    def calculate_delay(self) -> float:
        """Calculate delay for current attempt"""
        base_exp: float = self.exponential_base ** self.attempt
        delay: float = self.base_delay * base_exp
        return min(delay, self.max_delay)

    def should_retry(self) -> bool:
        """Check if retry is possible"""
        return self.attempt < self.max_attempts

    async def wait(self) -> None:
        """Wait before retry"""
        delay: float = self.calculate_delay()
        await asyncio.sleep(delay)
        self.attempt += 1


# ============================================================================
# ERROR HANDLING DECORATORS
# ============================================================================

def handle_errors(
    error_class: Type[E] = UltronError,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    logger: Optional[logging.Logger] = None,
    reraise: bool = True
) -> Callable:
    """
    Decorator for error handling in sync functions

    Args:
        error_class: Custom error class to raise
        severity: Error severity level
        category: Error category
        logger: Logger instance
        reraise: Whether to reraise the error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {e}")

                if reraise:
                    if isinstance(e, UltronError):
                        raise
                    raise error_class(
                        message=str(e),
                        severity=severity,
                        category=category,
                        context={"function": func.__name__}
                    )
                return None
        return wrapper
    return decorator


def handle_errors_async(
    error_class: Type[E] = UltronError,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    logger: Optional[logging.Logger] = None,
    reraise: bool = True
) -> Callable:
    """
    Decorator for error handling in async functions

    Args:
        error_class: Custom error class to raise
        severity: Error severity level
        category: Error category
        logger: Logger instance
        reraise: Whether to reraise the error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {e}")

                if reraise:
                    if isinstance(e, UltronError):
                        raise
                    raise error_class(
                        message=str(e),
                        severity=severity,
                        category=category,
                        context={"function": func.__name__}
                    )
                return None
        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retriable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for automatic retry with exponential backoff

    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        retriable_exceptions: Tuple of exception types to retry on
        logger: Logger instance
    """
    if retriable_exceptions is None:
        retriable_exceptions = (NetworkError, TimeoutError, AsyncError)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            strategy: RetryStrategy = RetryStrategy(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay
            )

            last_error: Optional[Exception] = None

            while strategy.should_retry():
                try:
                    return await func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_error = e
                    if logger:
                        logger.warning(
                            f"Attempt {strategy.attempt + 1}/{max_attempts} "
                            f"failed: {e}. Retrying..."
                        )
                    await strategy.wait()

            if last_error:
                raise last_error
            return None
        return wrapper
    return decorator


# ============================================================================
# ERROR CONTEXT MANAGER
# ============================================================================

class ErrorContext:
    """Context manager for error handling and cleanup"""

    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None,
        cleanup_func: Optional[Callable[[], None]] = None
    ) -> None:
        """Initialize error context"""
        self.name: str = name
        self.logger: Optional[logging.Logger] = logger
        self.cleanup_func: Optional[Callable[[], None]] = cleanup_func
        self.error: Optional[Exception] = None

    def __enter__(self) -> 'ErrorContext':
        """Enter context"""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        exc_tb: Any
    ) -> bool:
        """Exit context with cleanup"""
        if exc_val:
            self.error = exc_val
            if self.logger:
                self.logger.error(f"Error in {self.name}: {exc_val}")

        if self.cleanup_func:
            try:
                self.cleanup_func()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Cleanup failed: {e}")

        # Don't suppress the exception
        return False


# ============================================================================
# ERROR LOGGING HELPER
# ============================================================================

def log_error_context(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log error with full context

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
    """
    context = context or {}

    if isinstance(error, UltronError):
        logger.error(
            f"ULTRON Error [{error.severity.value}] ({error.category.value}): "
            f"{error.message} | Context: {error.context}",
            exc_info=True
        )
    else:
        logger.error(f"Error: {error} | Context: {context}", exc_info=True)


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def get_error_class(category: ErrorCategory) -> Type[UltronError]:
    """Get error class for category"""
    mapping: Dict[ErrorCategory, Type[UltronError]] = {
        ErrorCategory.NETWORK: NetworkError,
        ErrorCategory.CONFIG: ConfigError,
        ErrorCategory.TOOL: ToolError,
        ErrorCategory.API: APIError,
        ErrorCategory.FILE_IO: FileError,
        ErrorCategory.ASYNC: AsyncError,
        ErrorCategory.RESOURCE: ResourceError,
        ErrorCategory.VALIDATION: ValidationError,
        ErrorCategory.TIMEOUT: TimeoutError,
    }
    return mapping.get(category, UltronError)


def is_retriable(error: Exception) -> bool:
    """Check if error is retriable"""
    if isinstance(error, UltronError):
        return error.retriable
    return isinstance(error, (NetworkError, TimeoutError, AsyncError))
