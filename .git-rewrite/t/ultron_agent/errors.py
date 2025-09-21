"""Error taxonomy and handling for Ultron Agent."""
from __future__ import annotations

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VOICE = "voice"
    MODEL = "model"
    SYSTEM = "system"
    CONFIG = "config"
    API = "api"
    GUI = "gui"
    AUTOMATION = "automation"
    SECURITY = "security"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UltronError(Exception):
    """Base exception class for Ultron Agent errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recovery_suggestion = recovery_suggestion
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recovery_suggestion": self.recovery_suggestion,
            "original_error": str(self.original_error) if self.original_error else None
        }

    def get_user_message(self) -> str:
        """Get sanitized message safe for user display."""
        # Override in subclasses for user-friendly messages
        return str(self)


class VoiceError(UltronError):
    """Errors related to voice processing (TTS/STT)."""

    def __init__(
        self,
        message: str,
        engine: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.VOICE, severity, **kwargs)
        if engine:
            self.details["engine"] = engine

    def get_user_message(self) -> str:
        """User-friendly voice error message."""
        if "timeout" in str(self).lower():
            return "Voice recognition timed out. Please try again."
        elif "microphone" in str(self).lower():
            return "Microphone not available. Please check your audio settings."
        elif "connection" in str(self).lower():
            return "Voice service temporarily unavailable. Using fallback mode."
        else:
            return "Voice processing error. Please try again."


class ModelError(UltronError):
    """Errors related to AI model operations."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.MODEL, severity, **kwargs)
        if model:
            self.details["model"] = model
        if provider:
            self.details["provider"] = provider

    def get_user_message(self) -> str:
        """User-friendly model error message."""
        if "not found" in str(self).lower():
            return f"AI model '{self.details.get('model', 'unknown')}' not available. Switching to default model."
        elif "memory" in str(self).lower() or "vram" in str(self).lower():
            return "Insufficient memory for AI model. Switching to lighter model."
        elif "timeout" in str(self).lower():
            return "AI model response timeout. Please try again."
        else:
            return "AI model error. Switching to backup model."


class SystemError(UltronError):
    """System-level errors (resources, permissions, etc.)."""

    def __init__(
        self,
        message: str,
        component: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.SYSTEM, severity, **kwargs)
        if component:
            self.details["component"] = component

    def get_user_message(self) -> str:
        """User-friendly system error message."""
        if "permission" in str(self).lower():
            return "Permission denied. Please run as administrator or check file permissions."
        elif "disk" in str(self).lower() or "space" in str(self).lower():
            return "Insufficient disk space. Please free up storage."
        elif "memory" in str(self).lower():
            return "System memory low. Consider closing other applications."
        else:
            return "System error occurred. Please check logs for details."


class ConfigError(UltronError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.CONFIG, severity, **kwargs)
        if field:
            self.details["field"] = field
        self.recovery_suggestion = "Please check your configuration file and restart the application."

    def get_user_message(self) -> str:
        """User-friendly config error message."""
        if "api_key" in str(self).lower():
            return "API key missing or invalid. Please check your configuration."
        elif "file" in str(self).lower() and "not found" in str(self).lower():
            return "Configuration file not found. Using default settings."
        else:
            return "Configuration error. Please check your settings."


class APIError(UltronError):
    """API-related errors."""

    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.API, severity, **kwargs)
        if endpoint:
            self.details["endpoint"] = endpoint
        if status_code:
            self.details["status_code"] = status_code

    def get_user_message(self) -> str:
        """User-friendly API error message."""
        status_code = self.details.get("status_code", 0)

        if status_code == 401:
            return "Authentication failed. Please check your API credentials."
        elif status_code == 403:
            return "Access denied. You may not have permission for this action."
        elif status_code == 429:
            return "Rate limit exceeded. Please wait before trying again."
        elif status_code >= 500:
            return "Service temporarily unavailable. Please try again later."
        else:
            return "Network error. Please check your connection and try again."


class AutomationError(UltronError):
    """Automation-related errors (PyAutoGUI, workflows, etc.)."""

    def __init__(
        self,
        message: str,
        action: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.AUTOMATION, severity, **kwargs)
        if action:
            self.details["action"] = action

    def get_user_message(self) -> str:
        """User-friendly automation error message."""
        return "Automation action failed. Please try manual execution or check screen/window access."


class SecurityError(UltronError):
    """Security-related errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        **kwargs
    ):
        super().__init__(message, ErrorCategory.SECURITY, severity, **kwargs)

    def get_user_message(self) -> str:
        """User-friendly security error message."""
        return "Security violation detected. Action blocked for safety."


# Error handling utilities
def handle_error(error: Exception, logger, context: Optional[str] = None) -> UltronError:
    """
    Convert generic exceptions to UltronError instances.

    Args:
        error: Original exception
        logger: Logger instance for recording
        context: Additional context for the error

    Returns:
        UltronError instance
    """
    # If already a UltronError, just log and return
    if isinstance(error, UltronError):
        logger.error(f"UltronError in {context or 'unknown context'}: {error.to_dict()}")
        return error

    # Map common exception types
    error_type = type(error).__name__
    error_message = str(error)

    if isinstance(error, (ConnectionError, TimeoutError)):
        ultron_error = APIError(
            error_message,
            severity=ErrorSeverity.HIGH,
            original_error=error
        )
    elif isinstance(error, PermissionError):
        ultron_error = SystemError(
            error_message,
            severity=ErrorSeverity.HIGH,
            original_error=error
        )
    elif isinstance(error, (ValueError, TypeError)) and context == "config":
        ultron_error = ConfigError(
            error_message,
            severity=ErrorSeverity.HIGH,
            original_error=error
        )
    elif isinstance(error, ImportError):
        ultron_error = SystemError(
            error_message,
            component="dependencies",
            severity=ErrorSeverity.CRITICAL,
            original_error=error
        )
    else:
        # Generic system error for unknown exceptions
        ultron_error = SystemError(
            f"{error_type}: {error_message}",
            severity=ErrorSeverity.MEDIUM,
            original_error=error
        )

    # Add context if provided
    if context:
        ultron_error.details["context"] = context

    logger.error(f"Converted {error_type} to UltronError: {ultron_error.to_dict()}")
    return ultron_error


def get_recovery_actions(error: UltronError) -> list[str]:
    """
    Get suggested recovery actions for an error.

    Args:
        error: UltronError instance

    Returns:
        List of recovery action suggestions
    """
    actions = []

    if error.recovery_suggestion:
        actions.append(error.recovery_suggestion)

    # Category-specific recovery actions
    if error.category == ErrorCategory.VOICE:
        actions.extend([
            "Check microphone permissions",
            "Test audio devices in system settings",
            "Try using text input instead of voice"
        ])
    elif error.category == ErrorCategory.MODEL:
        actions.extend([
            "Switch to a different AI model",
            "Check Ollama server status",
            "Restart the AI service"
        ])
    elif error.category == ErrorCategory.SYSTEM:
        actions.extend([
            "Check available disk space",
            "Restart the application",
            "Run as administrator"
        ])
    elif error.category == ErrorCategory.CONFIG:
        actions.extend([
            "Validate configuration file",
            "Reset to default settings",
            "Check API key configuration"
        ])

    # Severity-specific actions
    if error.severity == ErrorSeverity.CRITICAL:
        actions.append("Contact support if problem persists")

    return actions
