"""
ULTRON Diagnostics Integration
Auto-wraps components with crash reporting and telemetry
"""

import functools
import asyncio
from typing import Callable, Any
from diagnostics.diagnostics_core import get_diagnostics


def diagnostic_wrapper(component_name: str, track_performance: bool = True):
    """
    Decorator to add automatic crash reporting and performance tracking

    Usage:
        @diagnostic_wrapper("brain", track_performance=True)
        async def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            diagnostics = get_diagnostics()

            # Track start time if performance monitoring enabled
            import time
            start_time = time.time() if track_performance else None

            try:
                result = await func(*args, **kwargs)

                # Record success metric
                if track_performance:
                    duration = time.time() - start_time
                    await diagnostics.record_performance_metric(
                        component=component_name,
                        metric_name=f"{func.__name__}_duration",
                        value=duration,
                        unit="seconds"
                    )

                return result

            except Exception as e:
                # Capture crash
                await diagnostics.capture_crash(
                    component=component_name,
                    exception=e,
                    severity="error",
                    additional_context={
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    }
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            diagnostics = get_diagnostics()

            import time
            start_time = time.time() if track_performance else None

            try:
                result = func(*args, **kwargs)

                if track_performance:
                    duration = time.time() - start_time
                    # Record sync (use asyncio.run for recording)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        diagnostics.record_performance_metric(
                            component=component_name,
                            metric_name=f"{func.__name__}_duration",
                            value=duration,
                            unit="seconds"
                        )
                    )
                    loop.close()

                return result

            except Exception as e:
                # Capture crash sync
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    diagnostics.capture_crash(
                        component=component_name,
                        exception=e,
                        severity="error",
                        additional_context={
                            "function": func.__name__,
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200]
                        }
                    )
                )
                loop.close()
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_metric(component: str, metric_name: str, value: float, unit: str = "count"):
    """
    Quick helper to track a performance metric

    Usage:
        track_metric("brain", "tokens_processed", 1024, "tokens")
    """
    diagnostics = get_diagnostics()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        diagnostics.record_performance_metric(
            component=component,
            metric_name=metric_name,
            value=value,
            unit=unit
        )
    )
    loop.close()


def report_crash(component: str, exception: Exception, severity: str = "error"):
    """
    Manually report a crash/exception

    Usage:
        try:
            risky_operation()
        except Exception as e:
            report_crash("tool_executor", e, severity="critical")
            raise
    """
    diagnostics = get_diagnostics()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    crash_id = loop.run_until_complete(
        diagnostics.capture_crash(
            component=component,
            exception=exception,
            severity=severity
        )
    )
    loop.close()
    return crash_id
