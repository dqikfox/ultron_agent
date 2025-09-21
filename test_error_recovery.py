#!/usr/bin/env python3
"""
Test script for ErrorRecoveryOrchestrator
"""
import asyncio
import sys
import os

# Change to the utils directory to make imports work
os.chdir(os.path.join(os.path.dirname(__file__), 'utils'))

from error_recovery import (
    ErrorRecoveryOrchestrator,
    CircuitBreaker
)

def failing_function(should_fail=True):
    """Test function that can fail."""
    if should_fail:
        raise Exception("Simulated failure")
    return "Success"

async def async_failing_function(should_fail=True):
    """Async test function that can fail."""
    await asyncio.sleep(0.1)
    if should_fail:
        raise Exception("Simulated async failure")
    return "Async Success"

async def test_error_recovery():
    """Test the error recovery orchestrator."""
    print("Testing ErrorRecoveryOrchestrator...")

    # Initialize orchestrator
    orchestrator = ErrorRecoveryOrchestrator()

    # Register recovery mechanisms
    orchestrator.register_retry_mechanism("test_operation", max_attempts=3, base_delay=0.1)
    orchestrator.register_circuit_breaker("test_operation", failure_threshold=2, recovery_timeout=1)

    # Test 1: Basic retry mechanism
    print("\n1. Testing retry mechanism...")
    try:
        result = await orchestrator.execute_with_recovery(
            "test_operation",
            failing_function,
            should_fail=False  # This should succeed
        )
        print(f"✅ Retry test passed: {result}")
    except Exception as e:
        print(f"❌ Retry test failed: {e}")

    # Test 2: Retry with failure (should eventually fail)
    print("\n2. Testing retry with persistent failure...")
    try:
        result = await orchestrator.execute_with_recovery(
            "test_operation",
            failing_function,
            should_fail=True  # This should fail and retry
        )
        print(f"❌ Expected failure but got: {result}")
    except Exception as e:
        print(f"✅ Expected failure occurred: {e}")

    # Test 3: Circuit breaker
    print("\n3. Testing circuit breaker...")
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    # First failures
    try:
        circuit_breaker.call(failing_function, True)
    except:
        pass

    try:
        circuit_breaker.call(failing_function, True)
    except:
        pass

    # Circuit should be open now
    try:
        circuit_breaker.call(failing_function, False)  # This should succeed but circuit is open
        print("❌ Circuit breaker should have been open")
    except Exception as e:
        print(f"✅ Circuit breaker correctly blocked call: {e}")

    # Test 4: Graceful degradation
    print("\n4. Testing graceful degradation...")

    def normal_func():
        raise Exception("Normal function failed")

    def degraded_func():
        return "Degraded mode result"

    orchestrator.register_degradation_component(
        "test_component",
        normal_func,
        degraded_func
    )

    # Test normal failure -> degraded fallback
    try:
        result = orchestrator.degradation_manager.execute_with_degradation("test_component")
        print(f"✅ Graceful degradation worked: {result}")
    except Exception as e:
        print(f"❌ Graceful degradation failed: {e}")

    # Test 5: Error statistics
    print("\n5. Testing error statistics...")
    stats = orchestrator.get_error_statistics()
    print("Error Statistics:")
    print(f"  - Total errors: {stats['total_errors']}")
    print(f"  - Operations with errors: {stats['operations_with_errors']}")

    print("\n✅ ErrorRecoveryOrchestrator test completed!")

if __name__ == "__main__":
    asyncio.run(test_error_recovery())