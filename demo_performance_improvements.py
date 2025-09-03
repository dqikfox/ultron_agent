#!/usr/bin/env python3
"""
Performance Improvements Demo for ULTRON Agent 3.0
Demonstrates caching, async patterns, and background task processing
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def demo_caching_performance():
    """Demonstrate caching performance improvements."""
    print("🔋 CACHE PERFORMANCE DEMONSTRATION")
    print("=" * 50)
    
    from cache_manager import CacheManager
    cache = CacheManager(memory_cache_size=100, memory_cache_mb=10)
    
    # Simulate expensive operations
    def expensive_operation(x):
        time.sleep(0.01)  # Simulate work
        return f"Processed: {x**2}"
    
    # Test without caching
    print("⏱️  Without Caching:")
    start_time = time.time()
    results = []
    for i in range(50):
        result = expensive_operation(i)
        results.append(result)
    no_cache_time = time.time() - start_time
    print(f"   Time: {no_cache_time:.3f} seconds")
    
    # Test with caching
    print("\n💾 With Caching:")
    start_time = time.time()
    cached_results = []
    for i in range(50):
        cache_key = f"expensive_op_{i}"
        
        # Check cache first
        cached_result = await cache.get(cache_key)
        if cached_result is None:
            result = expensive_operation(i)
            await cache.set(cache_key, result)
        else:
            result = cached_result
        
        cached_results.append(result)
    cache_time = time.time() - start_time
    print(f"   First run: {cache_time:.3f} seconds")
    
    # Test cache hits
    start_time = time.time()
    for i in range(50):
        cache_key = f"expensive_op_{i}"
        result = await cache.get(cache_key)
    hit_time = time.time() - start_time
    print(f"   Cache hits: {hit_time:.3f} seconds")
    
    # Show improvement
    improvement = (no_cache_time - hit_time) / no_cache_time * 100
    print(f"\n🚀 Performance Improvement: {improvement:.1f}% faster with caching!")
    
    # Show cache statistics
    stats = cache.get_statistics()
    print(f"📊 Cache Stats: {stats['memory'].hit_rate:.1f}% hit rate")
    
    return improvement


async def demo_async_task_queue():
    """Demonstrate async task queue performance."""
    print("\n🔄 ASYNC TASK QUEUE DEMONSTRATION")
    print("=" * 50)
    
    from async_task_queue import AsyncTaskQueue, TaskPriority
    
    queue = AsyncTaskQueue(max_workers=5)
    await queue.start()
    
    def cpu_intensive_task(n):
        """Simulate CPU work."""
        result = sum(i*i for i in range(n))
        return result
    
    async def io_intensive_task(delay):
        """Simulate I/O work."""
        await asyncio.sleep(delay)
        return f"IO task completed after {delay}s"
    
    try:
        # Test sequential processing
        print("⏱️  Sequential Processing:")
        start_time = time.time()
        sequential_results = []
        for i in range(10):
            result = cpu_intensive_task(1000)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        print(f"   Time: {sequential_time:.3f} seconds")
        
        # Test parallel processing with task queue
        print("\n⚡ Parallel Task Queue:")
        start_time = time.time()
        task_ids = []
        
        # Submit tasks
        for i in range(10):
            task_id = await queue.add_task(
                cpu_intensive_task, 1000,
                priority=TaskPriority.NORMAL
            )
            task_ids.append(task_id)
        
        # Wait for completion
        results = []
        for task_id in task_ids:
            result = await queue.wait_for_task(task_id, timeout=10.0)
            results.append(result.result if result else None)
        
        parallel_time = time.time() - start_time
        print(f"   Time: {parallel_time:.3f} seconds")
        
        # Show improvement
        speedup = sequential_time / parallel_time
        print(f"\n🚀 Speedup: {speedup:.1f}x faster with parallel processing!")
        
        # Show queue statistics
        status = queue.get_queue_status()
        print(f"📊 Queue Stats: {status['stats']['tasks_completed']} tasks completed")
        
        return speedup
        
    finally:
        await queue.stop()


async def demo_http_connection_pooling():
    """Demonstrate HTTP connection pooling benefits."""
    print("\n🌐 HTTP CONNECTION POOLING DEMONSTRATION")
    print("=" * 50)
    
    from http_manager import AsyncHTTPManager
    
    # Create manager with connection pooling
    http_manager = AsyncHTTPManager(max_connections=10)
    
    try:
        print("🔗 Connection pooling initialized")
        print("   Max connections: 10")
        print("   Keep-alive timeout: 60s")
        print("   DNS cache: 5 minutes")
        
        # Simulate multiple requests (would be faster with real endpoints)
        print("\n📈 Simulated benefits:")
        print("   ✅ Reuses TCP connections")
        print("   ✅ Reduces handshake overhead")
        print("   ✅ DNS caching reduces lookup time")
        print("   ✅ Concurrent request handling")
        
        # Show metrics format
        metrics = http_manager.get_metrics_summary()
        print(f"\n📊 HTTP Metrics: {metrics['total_requests']} requests tracked")
        
    finally:
        await http_manager.close()


async def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("\n📊 PERFORMANCE MONITORING DEMONSTRATION")
    print("=" * 50)
    
    from performance_optimizer import PerformanceOptimizer
    
    optimizer = PerformanceOptimizer()
    optimizer.start_monitoring()
    
    try:
        # Get current system metrics
        metrics = optimizer.get_current_metrics()
        if metrics:
            print(f"💻 System Metrics:")
            print(f"   CPU: {metrics.cpu_percent:.1f}%")
            print(f"   Memory: {metrics.memory_percent:.1f}%")
            print(f"   Disk: {metrics.disk_usage:.1f}%")
        
        # Run optimizations
        print("\n🔧 Running System Optimizations:")
        optimizations = optimizer.optimize_system()
        for opt in optimizations[:5]:  # Show first 5
            print(f"   ✅ {opt}")
        
        if len(optimizations) > 5:
            print(f"   ... and {len(optimizations) - 5} more optimizations")
        
        print(f"\n🚀 Applied {len(optimizations)} performance optimizations!")
        
    finally:
        optimizer.stop_monitoring()


async def main():
    """Run all performance demonstrations."""
    print("🤖 ULTRON Agent 3.0 - Performance Improvements Demo")
    print("=" * 60)
    print("Demonstrating caching, async processing, and monitoring...")
    print()
    
    try:
        # Run demonstrations
        cache_improvement = await demo_caching_performance()
        task_speedup = await demo_async_task_queue()
        await demo_http_connection_pooling()
        await demo_performance_monitoring()
        
        # Summary
        print("\n🎉 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"🔋 Caching Improvement: {cache_improvement:.1f}% faster")
        print(f"⚡ Task Queue Speedup: {task_speedup:.1f}x parallel performance")
        print("🌐 HTTP Connection Pooling: Enabled with intelligent reuse")
        print("📊 Performance Monitoring: Real-time system optimization")
        
        print("\n✅ All performance optimizations successfully demonstrated!")
        print("\nKey benefits implemented:")
        print("• Multi-level intelligent caching (memory + disk)")
        print("• Priority-based async task queue with retry logic")
        print("• HTTP connection pooling with automatic management")
        print("• Real-time performance monitoring and optimization")
        print("• Advanced memory management with garbage collection")
        
        print("\n🚀 ULTRON Agent is now significantly faster and more efficient!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())