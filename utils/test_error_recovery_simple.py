#!/usr/bin/env python3
"""
Simple test for ErrorRecoveryOrchestrator
"""
import asyncio
from error_recovery import ErrorRecoveryOrchestrator, CircuitBreaker

def failing_function(should_fail=True):
    """Test function that can fail."""
    if should_fail:
        raise Exception("Simulated failure")
    return "Success"

async def test_basic():
    """Basic test of error recovery."""
    print("Testing ErrorRecoveryOrchestrator...")

    # Initialize orchestrator
    orchestrator = ErrorRecoveryOrchestrator()

    # Test circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    print("✅ Error recovery system loaded successfully!")
    print("✅ Circuit breaker created successfully!")

    # Test basic functionality
    try:
        result = circuit_breaker.call(failing_function, False)
        print(f"✅ Circuit breaker test passed: {result}")
    except Exception as e:
        print(f"❌ Circuit breaker test failed: {e}")

    print("✅ Basic test completed!")

if __name__ == "__main__":
    asyncio.run(test_basic())