import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional, Union
from enum import Enum
import functools

class RecoveryStrategy(Enum):
    """Different recovery strategies for error handling."""
    RETRY = "retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FALLBACK = "fallback"
    ESCALATION = "escalation"

class CircuitBreakerState(Enum):
    """States for circuit breaker pattern."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered

class ErrorContext:
    """Context information for error handling."""
    def __init__(self,
                 operation: str,
                 error: Exception,
                 attempt: int = 1,
                 max_attempts: int = 3,
                 start_time: Optional[datetime] = None):
        self.operation = operation
        self.error = error
        self.attempt = attempt
        self.max_attempts = max_attempts
        self.start_time = start_time or datetime.now()
        self.metadata: Dict[str, Any] = {}

    def add_metadata(self, key: str, value: Any):
        """Add metadata to the error context."""
        self.metadata[key] = value

    def get_duration(self) -> float:
        """Get duration since error context was created."""
        return (datetime.now() - self.start_time).total_seconds()

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.state != CircuitBreakerState.OPEN:
            return False

        if not self.last_failure_time:
            return True

        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout

    def _record_success(self):
        """Record a successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            # Require a few successes before closing
            if self.success_count >= 2:
                self._reset()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0

    def _record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logging.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def _reset(self):
        """Reset the circuit breaker to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logging.info("Circuit breaker reset to closed state")

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logging.info("Circuit breaker attempting reset")
            else:
                raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception as e:
            self._record_failure()
            raise e

class RetryMechanism:
    """Advanced retry mechanism with exponential backoff."""

    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_factor: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))

        # Add jitter to prevent thundering herd
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay

        return min(delay, self.max_delay)

    async def execute_with_retry(self,
                                func: Callable,
                                *args,
                                **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logging.warning(f"Attempt {attempt}/{self.max_attempts} failed for {func.__name__}: {e}")

                if attempt < self.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logging.info(f"Retrying {func.__name__} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error(f"All {self.max_attempts} attempts failed for {func.__name__}")

        raise last_exception

class GracefulDegradationManager:
    """Manages graceful degradation of system capabilities."""

    def __init__(self):
        self.degradation_levels: Dict[str, Dict[str, Any]] = {}
        self.current_level = "normal"
        self.component_status: Dict[str, str] = {}

    def register_component(self,
                          component_name: str,
                          normal_func: Callable,
                          degraded_func: Callable,
                          critical_func: Optional[Callable] = None):
        """Register component with different degradation levels."""
        self.degradation_levels[component_name] = {
            'normal': normal_func,
            'degraded': degraded_func,
            'critical': critical_func or degraded_func
        }
        self.component_status[component_name] = 'normal'

    def set_component_status(self, component_name: str, status: str):
        """Set the status of a component (normal, degraded, critical)."""
        if component_name in self.degradation_levels:
            self.component_status[component_name] = status
            logging.info(f"Component {component_name} status set to {status}")

    def execute_with_degradation(self, component_name: str, *args, **kwargs) -> Any:
        """Execute component function based on current degradation level."""
        if component_name not in self.degradation_levels:
            raise ValueError(f"Component {component_name} not registered")

        # Determine which function to use based on component status
        status = self.component_status.get(component_name, 'normal')
        func = self.degradation_levels[component_name][status]

        try:
            if asyncio.iscoroutinefunction(func):
                return asyncio.run(func(*args, **kwargs))
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error executing {component_name} in {status} mode: {e}")
            # If normal/degraded fails, try critical
            if status != 'critical':
                critical_func = self.degradation_levels[component_name]['critical']
                logging.warning(f"Falling back to critical mode for {component_name}")
                try:
                    if asyncio.iscoroutinefunction(critical_func):
                        return asyncio.run(critical_func(*args, **kwargs))
                    else:
                        return critical_func(*args, **kwargs)
                except Exception as critical_error:
                    logging.error(f"Critical mode also failed for {component_name}: {critical_error}")
                    raise critical_error
            else:
                raise e

class ErrorRecoveryOrchestrator:
    """Main orchestrator for error recovery and resilience patterns."""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_mechanisms: Dict[str, RetryMechanism] = {}
        self.degradation_manager = GracefulDegradationManager()
        self.error_history: List[ErrorContext] = []
        self.recovery_strategies: Dict[str, List[RecoveryStrategy]] = {}

    def register_circuit_breaker(self,
                                name: str,
                                failure_threshold: int = 5,
                                recovery_timeout: int = 60):
        """Register a circuit breaker for a specific operation."""
        self.circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        logging.info(f"Registered circuit breaker: {name}")

    def register_retry_mechanism(self,
                                name: str,
                                max_attempts: int = 3,
                                base_delay: float = 1.0):
        """Register a retry mechanism for a specific operation."""
        self.retry_mechanisms[name] = RetryMechanism(
            max_attempts=max_attempts,
            base_delay=base_delay
        )
        logging.info(f"Registered retry mechanism: {name}")

    def register_degradation_component(self,
                                     component_name: str,
                                     normal_func: Callable,
                                     degraded_func: Callable,
                                     critical_func: Optional[Callable] = None):
        """Register a component for graceful degradation."""
        self.degradation_manager.register_component(
            component_name, normal_func, degraded_func, critical_func
        )

    def set_recovery_strategies(self,
                               operation: str,
                               strategies: List[RecoveryStrategy]):
        """Set recovery strategies for an operation."""
        self.recovery_strategies[operation] = strategies

    async def execute_with_recovery(self,
                                   operation: str,
                                   func: Callable,
                                   *args,
                                   **kwargs) -> Any:
        """
        Execute function with comprehensive error recovery.

        Args:
            operation: Name of the operation for tracking
            func: Function to execute
            *args, **kwargs: Arguments for the function

        Returns:
            Result of the function execution
        """
        strategies = self.recovery_strategies.get(operation, [RecoveryStrategy.RETRY])

        for strategy in strategies:
            try:
                if strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                    if operation in self.circuit_breakers:
                        return self.circuit_breakers[operation].call(func, *args, **kwargs)
                    else:
                        logging.warning(f"No circuit breaker registered for {operation}")

                elif strategy == RecoveryStrategy.RETRY:
                    if operation in self.retry_mechanisms:
                        return await self.retry_mechanisms[operation].execute_with_retry(
                            func, *args, **kwargs
                        )
                    else:
                        # Use default retry mechanism
                        retry = RetryMechanism()
                        return await retry.execute_with_retry(func, *args, **kwargs)

                elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                    # This would be handled by the degradation manager
                    # For now, just execute normally
                    pass

                elif strategy == RecoveryStrategy.FALLBACK:
                    # Implement fallback logic here
                    pass

                elif strategy == RecoveryStrategy.ESCALATION:
                    # Escalate to higher-level error handling
                    pass

                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                # Record the error
                error_context = ErrorContext(
                    operation=operation,
                    error=e,
                    attempt=strategies.index(strategy) + 1,
                    max_attempts=len(strategies)
                )
                self.error_history.append(error_context)

                logging.error(f"Recovery strategy {strategy.value} failed for {operation}: {e}")

                # Continue to next strategy if available
                if strategy != strategies[-1]:
                    continue
                else:
                    # All strategies exhausted
                    raise e

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        total_errors = len(self.error_history)
        operation_errors = {}

        for error in self.error_history:
            op = error.operation
            if op not in operation_errors:
                operation_errors[op] = []
            operation_errors[op].append(error)

        # Calculate error rates and patterns
        stats = {
            'total_errors': total_errors,
            'operations_with_errors': len(operation_errors),
            'error_rate_by_operation': {}
        }

        for op, errors in operation_errors.items():
            error_count = len(errors)
            if errors:
                avg_duration = sum(e.get_duration() for e in errors) / len(errors)
                stats['error_rate_by_operation'][op] = {
                    'count': error_count,
                    'avg_duration': round(avg_duration, 2),
                    'most_common_error': self._get_most_common_error_type(errors)
                }

        return stats

    def _get_most_common_error_type(self, errors: List[ErrorContext]) -> str:
        """Get the most common error type from a list of errors."""
        error_types = {}
        for error in errors:
            error_type = type(error.error).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1

        if error_types:
            return max(error_types, key=error_types.get)
        return "Unknown"

    def clear_error_history(self, days_to_keep: int = 7):
        """Clear old error history."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        self.error_history = [
            error for error in self.error_history
            if error.start_time >= cutoff_date
        ]
        logging.info(f"Error history cleaned up, {len(self.error_history)} entries remaining")

# Decorator for easy error recovery
def with_error_recovery(orchestrator: ErrorRecoveryOrchestrator,
                       operation: str,
                       strategies: Optional[List[RecoveryStrategy]] = None):
    """
    Decorator to add error recovery to any function.

    Usage:
    @with_error_recovery(orchestrator, "my_operation", [RecoveryStrategy.RETRY])
    async def my_function():
        pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if strategies:
                orchestrator.set_recovery_strategies(operation, strategies)
            return await orchestrator.execute_with_recovery(operation, func, *args, **kwargs)
        return wrapper
    return decorator