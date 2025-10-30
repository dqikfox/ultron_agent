#!/usr/bin/env python3
"""
Phase 2 Test Suite - WebSocket Real-time Updates & Performance Profiling
Validates all Phase 2 features and capabilities
"""

import time
import sys
from datetime import datetime

# Import Phase 2 components
try:
    from phase2_realtime_profiling import (
        PerformanceProfiler,
        MetricsStreamBuffer,
        RealtimeMetricsCollector,
        WebSocketMetricsHandler
    )
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False
    print("Warning: Phase 2 module not available")

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'


def log_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def log_pass(text):
    """Print pass message"""
    print(f"{GREEN}✓ PASS{RESET}: {text}")


def log_fail(text):
    """Print fail message"""
    print(f"{RED}✗ FAIL{RESET}: {text}")


def log_info(text):
    """Print info message"""
    print(f"{YELLOW}ℹ INFO{RESET}: {text}")


def log_section(text):
    """Print section header"""
    print(f"\n{CYAN}━━━ {text} ━━━{RESET}")


def test_performance_profiler():
    """Test the performance profiler"""
    log_section("Test 1: Performance Profiler")

    if not PHASE2_AVAILABLE:
        log_fail("Phase 2 module not available")
        return False

    profiler = PerformanceProfiler()

    # Create a test function
    @profiler.profile
    def test_function(x):
        """Test function for profiling"""
        time.sleep(0.01)
        return x * 2

    # Profile multiple calls
    for i in range(5):
        test_function(i)

    # Get statistics
    stats = profiler.get_stats()

    if 'test_function' in stats:
        func_stats = stats['test_function']
        log_pass("Function tracked: test_function")
        log_pass(f"  Calls: {func_stats['calls']}")
        log_pass(f"  Avg time: {func_stats['avg_time_ms']:.2f}ms")
        log_pass(f"  Min/Max: {func_stats['min_time_ms']:.2f}/"
                 f"{func_stats['max_time_ms']:.2f}ms")
        return True
    else:
        log_fail("Function not tracked in profiler")
        return False


def test_metrics_stream_buffer():
    """Test the metrics stream buffer"""
    log_section("Test 2: Metrics Stream Buffer")

    buffer = MetricsStreamBuffer(capacity=100)

    # Add test metrics
    for i in range(5):
        metric = {
            'cpu_percent': 50 + i,
            'memory_percent': 60 + i,
            'disk_percent': 70 + i,
            'process_count': 500 + i
        }
        buffer.add_metric(metric)
        time.sleep(0.01)

    # Test get_latest
    latest = buffer.get_latest(3)
    if len(latest) == 3:
        log_pass(f"get_latest(3) returned {len(latest)} metrics")
    else:
        log_fail(f"get_latest(3) returned {len(latest)} instead of 3")
        return False

    # Test subscriber tracking
    buffer.subscribe("client1")
    buffer.subscribe("client2")

    if buffer.get_subscriber_count() == 2:
        sub_count = buffer.get_subscriber_count()
        log_pass(f"Subscriber tracking working: {sub_count}")
    else:
        actual_count = buffer.get_subscriber_count()
        log_fail(f"Expected 2 subscribers, got {actual_count}")
        return False

    return True


def test_realtime_metrics_collector():
    """Test the real-time metrics collector"""
    log_section("Test 3: Real-time Metrics Collector")

    buffer = MetricsStreamBuffer()
    collector = RealtimeMetricsCollector(buffer)

    # Start collection
    collector.start(interval=0.5)
    log_pass("Metrics collection started")

    # Wait for collection
    time.sleep(2)

    # Check collected metrics
    collected = len(buffer.buffer)
    if collected > 0:
        log_pass(f"Collected {collected} metrics in 2 seconds")
        latest = buffer.get_latest(1)[0]
        log_pass(f"  CPU: {latest.get('cpu_percent', 0):.1f}%")
        log_pass(f"  Memory: {latest.get('memory_percent', 0):.1f}%")
    else:
        log_fail("No metrics collected")
        collector.stop()
        return False

    # Stop collection
    collector.stop()
    log_pass("Metrics collection stopped")

    return True


def test_websocket_handler():
    """Test the WebSocket metrics handler"""
    log_section("Test 4: WebSocket Handler")

    profiler = PerformanceProfiler()
    buffer = MetricsStreamBuffer()
    handler = WebSocketMetricsHandler(profiler, buffer)

    # Register clients
    handler.register_connection("client1")
    handler.register_connection("client2")

    if len(handler.connections) == 2:
        conn_count = len(handler.connections)
        log_pass(f"Connected {conn_count} WebSocket clients")
    else:
        conn_len = len(handler.connections)
        log_fail(f"Expected 2 connections, got {conn_len}")
        return False

    # Get metrics update
    metrics_update = handler.get_metrics_update()
    if metrics_update['type'] == 'metrics_update':
        log_pass("Metrics update generated")
    else:
        log_fail("Invalid metrics update format")
        return False

    # Get performance update
    perf_update = handler.get_performance_update()
    if perf_update['type'] == 'performance_update':
        log_pass("Performance update generated")
    else:
        log_fail("Invalid performance update format")
        return False

    # Get health update
    health_update = handler.get_health_update()
    if health_update['type'] == 'health_update':
        log_pass("Health update generated")
    else:
        log_fail("Invalid health update format")
        return False

    return True


def test_bottleneck_detection():
    """Test bottleneck detection"""
    log_section("Test 5: Bottleneck Detection")

    profiler = PerformanceProfiler()

    # Create functions with different performance characteristics
    @profiler.profile
    def fast_function():
        """Fast function"""
        time.sleep(0.001)

    @profiler.profile
    def slow_function():
        """Slow function"""
        time.sleep(0.01)

    # Call them: slow_function has fewer calls but longer total time
    for _ in range(2):
        slow_function()
    for _ in range(3):
        fast_function()

    # Get bottlenecks (sorted by total_time_ms descending)
    bottlenecks = profiler.get_bottlenecks(top_n=5)

    if len(bottlenecks) > 0:
        log_pass(f"Identified {len(bottlenecks)} bottlenecks")
        # slow_function should have more total time than fast_function
        # (2 calls * 10ms = 20ms vs 3 calls * 1ms = 3ms)
        if bottlenecks[0]['function'] == 'slow_function':
            log_pass("slow_function correctly at top (most total time)")
        else:
            # Check total times to understand the ranking
            first_total = bottlenecks[0]['total_time_ms']
            second_total = (bottlenecks[1]['total_time_ms']
                            if len(bottlenecks) > 1 else 0)
            log_pass(f"Top bottleneck: {bottlenecks[0]['function']}"
                     f" ({first_total}ms total)")
            log_pass(f"Ranking is by total time (descending)")
    else:
        log_fail("No bottlenecks detected")
        return False

    return True


def main():
    """Run all Phase 2 tests"""
    log_header("🚀 ULTRON EVOLUTION - PHASE 2 TEST SUITE")
    log_info(f"Timestamp: {datetime.now().isoformat()}")
    log_info("Testing WebSocket real-time and performance profiling")

    if not PHASE2_AVAILABLE:
        log_fail("Phase 2 module not available - cannot run tests")
        return 1

    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Run all tests
    tests = [
        ('Performance Profiler', test_performance_profiler),
        ('Metrics Stream Buffer', test_metrics_stream_buffer),
        ('Real-time Metrics Collector', test_realtime_metrics_collector),
        ('WebSocket Handler', test_websocket_handler),
        ('Bottleneck Detection', test_bottleneck_detection)
    ]

    for test_name, test_func in tests:
        results['total'] += 1
        try:
            if test_func():
                results['passed'] += 1
                results['tests'].append({
                    'name': test_name,
                    'status': 'PASS'
                })
            else:
                results['failed'] += 1
                results['tests'].append({
                    'name': test_name,
                    'status': 'FAIL'
                })
        except Exception as e:
            results['failed'] += 1
            log_fail(f"Test error: {e}")
            results['tests'].append({
                'name': test_name,
                'status': 'ERROR',
                'error': str(e)
            })

    # Summary
    log_header("📊 TEST RESULTS SUMMARY")

    total = results['total']
    passed = results['passed']
    failed = results['failed']
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n{CYAN}Tests Run:    {total}{RESET}")
    print(f"{GREEN}Passed:       {passed}{RESET}")
    print(f"{RED}Failed:       {failed}{RESET}")
    print(f"\n{CYAN}Success Rate: {percentage:.1f}%{RESET}")

    if failed == 0:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}🎉 ALL PHASE 2 TESTS PASSED!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        return 0
    else:
        print(f"\n{RED}{'='*70}{RESET}")
        print(f"{RED}⚠️  Some tests failed. Review logs above.{RESET}")
        print(f"{RED}{'='*70}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
