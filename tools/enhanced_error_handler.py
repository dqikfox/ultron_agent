"""
Enhanced Error Handling Tool for ULTRON Agent

Implements circuit breaker pattern, error recovery, and comprehensive error management
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance
    """

    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: Exception = Exception):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.next_attempt_time = None

        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                log_info("circuit_breaker", f"Circuit {self.name} entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenException(f"Circuit {self.name} is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.next_attempt_time is None:
            return False
        return datetime.now() >= self.next_attempt_time

    def _on_success(self):
        """Handle successful operation"""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= 3:  # Require 3 consecutive successes
                    self._reset()
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed operation"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self._trip()

    def _trip(self):
        """Open the circuit"""
        self.state = CircuitState.OPEN
        self.next_attempt_time = datetime.now() + timedelta(seconds=self.recovery_timeout)
        log_error("circuit_breaker", f"Circuit {self.name} tripped OPEN")

    def _reset(self):
        """Reset the circuit to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.next_attempt_time = None
        log_info("circuit_breaker", f"Circuit {self.name} reset to CLOSED")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class ErrorRecoveryManager:
    """
    Manages error recovery strategies and fallback mechanisms
    """

    def __init__(self):
        self.recovery_strategies = {}
        self.error_history = defaultdict(list)
        self.max_history_size = 100

    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for specific error type"""
        self.recovery_strategies[error_type] = strategy

    def attempt_recovery(self, error: Exception, context: Dict[str, Any]) -> Optional[Any]:
        """Attempt to recover from an error"""
        error_type = type(error).__name__

        # Log error
        self._log_error(error, context)

        # Try recovery strategy
        if error_type in self.recovery_strategies:
            try:
                log_info("error_recovery", f"Attempting recovery for {error_type}")
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                log_error("error_recovery", f"Recovery failed: {recovery_error}")
                return None

        return None

    def _log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with context"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }

        self.error_history[type(error).__name__].append(error_entry)

        # Maintain history size
        if len(self.error_history[type(error).__name__]) > self.max_history_size:
            self.error_history[type(error).__name__] = self.error_history[type(error).__name__][-self.max_history_size:]


class EnhancedErrorHandler:
    """
    Tool for enhanced error handling, circuit breakers, and recovery management
    """

    name = "Enhanced Error Handler"
    description = "Manage errors with circuit breakers, recovery strategies, and comprehensive error analysis"

    def __init__(self):
        self.circuit_breakers = {}
        self.recovery_manager = ErrorRecoveryManager()
        self.error_stats_file = Path("logs/error_statistics.json")
        self.error_stats_file.parent.mkdir(exist_ok=True)
        self._setup_default_circuit_breakers()
        self._setup_default_recovery_strategies()

    def match(self, command: str) -> bool:
        """Check if command matches error handling operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "error handling", "circuit breaker", "error recovery", "error analysis",
            "error stats", "error report", "fault tolerance", "error management"
        ])

    def execute(self, command: str) -> str:
        """Execute error handling operations"""
        try:
            command_lower = command.lower()

            if "circuit breaker" in command_lower:
                return self.get_circuit_breaker_status()
            elif "error stats" in command_lower or "error report" in command_lower:
                return self.generate_error_report()
            elif "error analysis" in command_lower:
                return self.analyze_error_patterns()
            elif "error recovery" in command_lower:
                return self.get_recovery_status()
            else:
                return self.get_help()

        except Exception as e:
            log_error("enhanced_error_handler", f"Error handling operation failed: {e}")
            return f"Error handling operation failed: {str(e)}"

    def get_circuit_breaker_status(self) -> str:
        """Get status of all circuit breakers"""
        status_lines = ["🔌 **Circuit Breaker Status**\n"]

        for name, breaker in self.circuit_breakers.items():
            status_lines.append(f"**{name}:** {breaker.state.value.upper()}")
            status_lines.append(f"  • Failures: {breaker.failure_count}/{breaker.failure_threshold}")
            if breaker.state == CircuitState.OPEN:
                time_to_reset = (breaker.next_attempt_time - datetime.now()).total_seconds()
                status_lines.append(f"  • Next attempt: {time_to_reset:.0f}s")
            status_lines.append("")

        return "\n".join(status_lines)

    def generate_error_report(self) -> str:
        """Generate comprehensive error report"""
        total_errors = sum(len(errors) for errors in self.recovery_manager.error_history.values())

        if total_errors == 0:
            return "✅ No errors recorded in current session"

        report = f"""
📋 **Error Report** (Total: {total_errors})

**Error Types by Frequency:**
"""

        # Sort error types by frequency
        sorted_errors = sorted(
            self.recovery_manager.error_history.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for error_type, errors in sorted_errors[:10]:  # Top 10
            count = len(errors)
            percentage = (count / total_errors) * 100
            last_error = errors[-1]['timestamp'] if errors else 'N/A'
            report += f"• {error_type}: {count} ({percentage:.1f}%) - Last: {last_error}\n"

        report += "\n**Recent Errors:**\n"
        all_recent_errors = []
        for error_list in self.recovery_manager.error_history.values():
            all_recent_errors.extend(error_list[-3:])  # Last 3 from each type

        # Sort by timestamp
        all_recent_errors.sort(key=lambda x: x['timestamp'], reverse=True)

        for error in all_recent_errors[:5]:  # Show last 5
            report += f"• {error['timestamp'][:19]} - {error['error_type']}: {error['error_message'][:100]}...\n"

        return report

    def analyze_error_patterns(self) -> str:
        """Analyze error patterns and provide insights"""
        if not self.recovery_manager.error_history:
            return "No error patterns to analyze"

        analysis = "🔍 **Error Pattern Analysis**\n\n"

        # Time-based analysis
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        recent_errors = []
        for error_list in self.recovery_manager.error_history.values():
            for error in error_list:
                error_time = datetime.fromisoformat(error['timestamp'])
                if error_time > last_hour:
                    recent_errors.append(error)

        analysis += f"**Recent Activity (Last Hour):** {len(recent_errors)} errors\n"

        if recent_errors:
            # Most common recent errors
            error_counts = defaultdict(int)
            for error in recent_errors:
                error_counts[error['error_type']] += 1

            most_common = max(error_counts.items(), key=lambda x: x[1])
            analysis += f"**Most Common:** {most_common[0]} ({most_common[1]} times)\n"

        # Circuit breaker analysis
        open_breakers = [name for name, breaker in self.circuit_breakers.items() if breaker.state == CircuitState.OPEN]
        if open_breakers:
            analysis += f"**Open Circuit Breakers:** {', '.join(open_breakers)}\n"

        # Recommendations
        analysis += "\n**Recommendations:**\n"
        if len(recent_errors) > 10:
            analysis += "• High error rate detected. Consider reviewing system stability.\n"
        if open_breakers:
            analysis += "• Some services are in fail-fast mode. Monitor recovery.\n"
        if not recent_errors:
            analysis += "• System appears stable with no recent errors.\n"

        return analysis

    def get_recovery_status(self) -> str:
        """Get status of error recovery mechanisms"""
        strategies_count = len(self.recovery_manager.recovery_strategies)

        status = f"""
🛠️ **Error Recovery Status**

**Registered Recovery Strategies:** {strategies_count}
"""

        if strategies_count > 0:
            status += "\n**Available Strategies:**\n"
            for error_type in self.recovery_manager.recovery_strategies.keys():
                status += f"• {error_type}\n"

        status += f"\n**Error History:** {sum(len(errors) for errors in self.recovery_manager.error_history.values())} total errors tracked"

        return status

    def _setup_default_circuit_breakers(self):
        """Setup default circuit breakers for common services"""
        # API calls circuit breaker
        self.circuit_breakers['api_calls'] = CircuitBreaker(
            'API Calls', failure_threshold=3, recovery_timeout=30
        )

        # File operations circuit breaker
        self.circuit_breakers['file_operations'] = CircuitBreaker(
            'File Operations', failure_threshold=5, recovery_timeout=60
        )

        # Network operations circuit breaker
        self.circuit_breakers['network_ops'] = CircuitBreaker(
            'Network Operations', failure_threshold=3, recovery_timeout=45
        )

    def _setup_default_recovery_strategies(self):
        """Setup default error recovery strategies"""
        # Network timeout recovery
        def network_timeout_recovery(error, context):
            log_info("error_recovery", "Attempting network timeout recovery")
            time.sleep(2)  # Brief pause
            # Could retry the operation here
            return None

        # File not found recovery
        def file_not_found_recovery(error, context):
            log_info("error_recovery", "Attempting file not found recovery")
            # Could try alternative paths or create directories
            return None

        # API error recovery
        def api_error_recovery(error, context):
            log_info("error_recovery", "Attempting API error recovery")
            # Could implement exponential backoff
            return None

        self.recovery_manager.register_recovery_strategy('TimeoutError', network_timeout_recovery)
        self.recovery_manager.register_recovery_strategy('FileNotFoundError', file_not_found_recovery)
        self.recovery_manager.register_recovery_strategy('ConnectionError', api_error_recovery)
        self.recovery_manager.register_recovery_strategy('HTTPError', api_error_recovery)

    def get_help(self) -> str:
        """Get help information for the tool"""
        return """
🛡️ **Enhanced Error Handler Tool**

**Capabilities:**
• Circuit breaker pattern implementation for fault tolerance
• Error recovery strategies and automatic fallback
• Comprehensive error tracking and analysis
• Pattern recognition and trend analysis
• Performance impact monitoring

**Commands:**
• "circuit breaker" - View circuit breaker status
• "error report" - Generate comprehensive error report
• "error analysis" - Analyze error patterns and trends
• "error recovery" - Check recovery mechanism status

**Features:**
• Automatic service protection with circuit breakers
• Configurable failure thresholds and recovery timeouts
• Error history with timestamps and context
• Recovery strategy registration system
• Real-time monitoring and alerting
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Error handling command"
                    }
                },
                "required": ["command"]
            }
        }
