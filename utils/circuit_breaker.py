"""
ULTRON Agent — Circuit Breaker

Provides the classic three-state circuit breaker pattern (CLOSED → OPEN →
HALF_OPEN → CLOSED) as a reusable async/sync decorator and context-manager.

Usage
-----
Decorator (async)::

    from utils.circuit_breaker import circuit_breaker

    @circuit_breaker(name="ollama", failure_threshold=3, recovery_timeout=30)
    async def call_ollama(prompt: str) -> str:
        ...

Decorator (sync)::

    @circuit_breaker(name="db_write", failure_threshold=5)
    def write_to_db(record):
        ...

Direct instance::

    from utils.circuit_breaker import CircuitBreaker, CircuitOpenError

    cb = CircuitBreaker(name="my_service", failure_threshold=3)

    try:
        result = await cb.call(my_async_fn, arg1, kwarg=val)
    except CircuitOpenError:
        result = cached_fallback()
"""

from __future__ import annotations

import asyncio
import functools
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional


class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation; failures are counted
    OPEN = "open"            # Failures exceeded threshold; calls rejected
    HALF_OPEN = "half_open"  # Recovery probe: one call allowed through


class CircuitOpenError(Exception):
    """Raised when a call is attempted while the circuit is OPEN."""

    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit '{name}' is OPEN. "
            f"Retry after {retry_after:.1f}s."
        )


@dataclass
class CircuitStats:
    """Runtime statistics for a CircuitBreaker instance."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None


class CircuitBreaker:
    """
    Thread- and coroutine-safe circuit breaker.

    Parameters
    ----------
    name:
        Human-readable identifier used in logs and error messages.
    failure_threshold:
        Number of consecutive failures that trip the circuit to OPEN.
    recovery_timeout:
        Seconds to wait in the OPEN state before probing with a single
        HALF_OPEN call.
    success_threshold:
        Number of consecutive successes in HALF_OPEN needed to close
        the circuit again.
    expected_exceptions:
        Tuple of exception types that count as failures.  Any other
        exception propagates but does *not* count against the circuit.
        Defaults to ``(Exception,)`` — all exceptions count.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 1,
        expected_exceptions: tuple = (Exception,),
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.expected_exceptions = expected_exceptions

        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._half_open_successes: int = 0
        self._opened_at: Optional[float] = None
        self._lock = asyncio.Lock()
        self._sync_lock = threading.Lock()
        self.stats = CircuitStats()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        return self._state

    def _retry_after(self) -> float:
        """Seconds until the circuit may attempt a half-open probe."""
        if self._opened_at is None:
            return 0.0
        elapsed = time.monotonic() - self._opened_at
        return max(0.0, self.recovery_timeout - elapsed)

    def _should_attempt_reset(self) -> bool:
        return (
            self._state == CircuitState.OPEN
            and self._opened_at is not None
            and (time.monotonic() - self._opened_at) >= self.recovery_timeout
        )

    def _trip(self) -> None:
        """Transition to OPEN."""
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        self._failure_count = 0
        self._half_open_successes = 0
        self.stats.state_transitions += 1

    def _reset(self) -> None:
        """Transition to CLOSED after successful recovery."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_successes = 0
        self._opened_at = None
        self.stats.state_transitions += 1

    def _record_success(self) -> None:
        self.stats.successful_calls += 1
        self.stats.last_success_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_successes += 1
            if self._half_open_successes >= self.success_threshold:
                self._reset()
        else:
            self._failure_count = 0

    def _record_failure(self) -> None:
        self.stats.failed_calls += 1
        self.stats.last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            self._trip()
        else:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._trip()

    # ------------------------------------------------------------------
    # Async call interface
    # ------------------------------------------------------------------

    async def call(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute *fn* under circuit-breaker protection (async-safe).

        Raises
        ------
        CircuitOpenError
            When the circuit is OPEN and the recovery timeout has not elapsed.
        """
        async with self._lock:
            self.stats.total_calls += 1
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self.stats.state_transitions += 1
                else:
                    self.stats.rejected_calls += 1
                    raise CircuitOpenError(self.name, self._retry_after())

        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn(*args, **kwargs)
            else:
                result = fn(*args, **kwargs)
        except self.expected_exceptions:
            async with self._lock:
                self._record_failure()
            raise
        else:
            async with self._lock:
                self._record_success()
            return result

    # ------------------------------------------------------------------
    # Sync call interface
    # ------------------------------------------------------------------

    def call_sync(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute *fn* under circuit-breaker protection (sync, thread-safe).

        Raises
        ------
        CircuitOpenError
            When the circuit is OPEN and the recovery timeout has not elapsed.
        """
        with self._sync_lock:
            self.stats.total_calls += 1
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self.stats.state_transitions += 1
                else:
                    self.stats.rejected_calls += 1
                    raise CircuitOpenError(self.name, self._retry_after())

        try:
            result = fn(*args, **kwargs)
        except self.expected_exceptions:
            with self._sync_lock:
                self._record_failure()
            raise
        else:
            with self._sync_lock:
                self._record_success()
            return result

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "total_calls": self.stats.total_calls,
            "successful_calls": self.stats.successful_calls,
            "failed_calls": self.stats.failed_calls,
            "rejected_calls": self.stats.rejected_calls,
            "state_transitions": self.stats.state_transitions,
            "retry_after_seconds": self._retry_after(),
        }

    def reset(self) -> None:
        """Manually close the circuit (e.g. after operator intervention)."""
        self._reset()


# ---------------------------------------------------------------------------
# Global registry
# ---------------------------------------------------------------------------

_registry: Dict[str, CircuitBreaker] = {}
_registry_lock = threading.Lock()


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 1,
    expected_exceptions: tuple = (Exception,),
) -> CircuitBreaker:
    """Return a named ``CircuitBreaker``, creating it if it doesn't exist."""
    global _registry
    if name not in _registry:
        with _registry_lock:
            if name not in _registry:
                _registry[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    success_threshold=success_threshold,
                    expected_exceptions=expected_exceptions,
                )
    return _registry[name]


def list_circuit_breakers() -> Dict[str, Dict[str, Any]]:
    """Return stats for all registered circuit breakers."""
    return {name: cb.get_stats() for name, cb in _registry.items()}


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 1,
    expected_exceptions: tuple = (Exception,),
    fallback: Optional[Callable] = None,
):
    """
    Decorator that wraps a function with a named circuit breaker.

    Parameters
    ----------
    name:
        Circuit breaker name (shared across all uses of the same name).
    failure_threshold:
        Number of failures before the circuit opens.
    recovery_timeout:
        Seconds until a half-open probe is attempted.
    success_threshold:
        Successes needed in HALF_OPEN before closing.
    expected_exceptions:
        Exception types counted as failures.
    fallback:
        Optional callable invoked when the circuit is OPEN instead of
        raising ``CircuitOpenError``.  Receives the same ``*args``
        and ``**kwargs`` as the decorated function.

    Example
    -------
    ::

        @circuit_breaker("ollama", failure_threshold=3, recovery_timeout=15)
        async def ask_ollama(prompt):
            ...
    """
    cb = get_circuit_breaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        expected_exceptions=expected_exceptions,
    )

    def decorator(fn: Callable) -> Callable:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await cb.call(fn, *args, **kwargs)
                except CircuitOpenError:
                    if fallback:
                        return (
                            await fallback(*args, **kwargs)
                            if asyncio.iscoroutinefunction(fallback)
                            else fallback(*args, **kwargs)
                        )
                    raise
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return cb.call_sync(fn, *args, **kwargs)
                except CircuitOpenError:
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise
            return sync_wrapper

    return decorator
