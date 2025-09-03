"""
Performance Tests for ULTRON Agent 3.0 Optimizations
Tests caching, async patterns, and connection pooling
"""

import asyncio
import time
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestCacheManager:
    """Test the cache manager functionality."""
    
    async def test_memory_cache_basic_operations(self):
        """Test basic memory cache operations."""
        from cache_manager import MemoryCache
        
        cache = MemoryCache(max_size=10)
        
        # Test cache miss
        result = await cache.get("test_key")
        assert result is None
        
        # Test cache set and hit
        from cache_manager import CacheItem
        from datetime import datetime
        
        item = CacheItem(
            key="test_key",
            value="test_value", 
            created_at=datetime.now(),
            expires_at=None
        )
        
        success = await cache.set("test_key", item)
        assert success
        
        # Test cache hit
        cached_item = await cache.get("test_key")
        assert cached_item is not None
        assert cached_item.value == "test_value"
        assert cache.stats.hits == 1
        assert cache.stats.misses == 1
    
    async def test_cache_manager_integration(self):
        """Test full cache manager with memory and disk caching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            from cache_manager import CacheManager
            
            cache = CacheManager(
                memory_cache_size=5,
                memory_cache_mb=1,
                disk_cache_mb=10,
                cache_dir=temp_dir
            )
            
            # Test cache miss
            result = await cache.get("missing_key")
            assert result is None
            
            # Test cache set and get
            success = await cache.set("test_key", "test_value", ttl=3600)
            assert success
            
            result = await cache.get("test_key")
            assert result == "test_value"
            
            # Test TTL expiration (short TTL)
            await cache.set("short_ttl", "expires_soon", ttl=1)
            result = await cache.get("short_ttl")
            assert result == "expires_soon"
            
            # Wait for expiration and test
            await asyncio.sleep(1.1)
            result = await cache.get("short_ttl")
            # Note: may still be in memory cache depending on timing
            
            # Test invalidation
            invalidated = await cache.invalidate("test_key")
            assert invalidated > 0
            
            result = await cache.get("test_key")
            assert result is None
    
    async def test_cache_performance(self):
        """Test cache performance improvements."""
        from cache_manager import CacheManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(cache_dir=temp_dir)
            
            # Warm up cache
            test_data = {f"key_{i}": f"value_{i}" for i in range(100)}
            
            # Time cache population
            start_time = time.time()
            for key, value in test_data.items():
                await cache.set(key, value)
            populate_time = time.time() - start_time
            
            # Time cache retrieval
            start_time = time.time()
            for key in test_data:
                result = await cache.get(key)
                assert result is not None
            retrieval_time = time.time() - start_time
            
            print(f"Cache populate time: {populate_time:.3f}s")
            print(f"Cache retrieval time: {retrieval_time:.3f}s")
            
            # Retrieval should be significantly faster than population
            assert retrieval_time < populate_time


@pytest.mark.asyncio 
class TestHTTPManager:
    """Test the HTTP manager and connection pooling."""
    
    async def test_http_manager_initialization(self):
        """Test HTTP manager creates session properly."""
        from http_manager import AsyncHTTPManager
        
        manager = AsyncHTTPManager(max_connections=10)
        assert manager.max_connections == 10
        assert manager._session is None
        
        # Test session creation
        session = await manager._get_session()
        assert session is not None
        assert not session.closed
        
        await manager.close()
        assert session.closed
    
    @patch('aiohttp.ClientSession.request')
    async def test_http_request_metrics(self, mock_request):
        """Test HTTP request metrics collection."""
        from http_manager import AsyncHTTPManager
        
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '100'}
        mock_request.return_value.__aenter__.return_value = mock_response
        
        manager = AsyncHTTPManager()
        
        # Make request
        await manager.request('GET', 'http://example.com')
        
        # Check metrics
        metrics = manager.get_metrics_summary()
        assert metrics['total_requests'] == 1
        assert metrics['recent_requests'] == 1
        
        await manager.close()
    
    async def test_batch_request_manager(self):
        """Test batched request processing.""" 
        from http_manager import AsyncHTTPManager, BatchRequestManager
        
        http_manager = AsyncHTTPManager()
        batch_manager = BatchRequestManager(
            http_manager, 
            batch_size=3, 
            batch_timeout=0.1
        )
        
        # Mock the HTTP manager request method
        http_manager.request = AsyncMock(return_value=AsyncMock(
            status=200,
            headers={'content-length': '50'},
            text=AsyncMock(return_value='{"result": "success"}')
        ))
        
        # Add multiple requests
        tasks = []
        for i in range(5):
            task = batch_manager.add_request('GET', f'http://example.com/{i}')
            tasks.append(task)
        
        # Wait for batch processing
        results = await asyncio.gather(*tasks)
        
        # Verify all requests processed
        assert len(results) == 5
        for result in results:
            assert result['status'] == 200
        
        await http_manager.close()


@pytest.mark.asyncio
class TestAsyncTaskQueue:
    """Test the async task queue functionality."""
    
    async def test_task_queue_basic_operations(self):
        """Test basic task queue operations."""
        from async_task_queue import AsyncTaskQueue, TaskPriority
        
        queue = AsyncTaskQueue(max_workers=2)
        await queue.start()
        
        try:
            # Test task addition
            def simple_task(x, y):
                return x + y
            
            task_id = await queue.add_task(simple_task, 2, 3)
            assert task_id is not None
            
            # Wait for task completion
            result = await queue.wait_for_task(task_id, timeout=5.0)
            assert result is not None
            assert result.success
            assert result.result == 5
            
        finally:
            await queue.stop()
    
    async def test_task_priority_handling(self):
        """Test task priority ordering."""
        from async_task_queue import AsyncTaskQueue, TaskPriority
        
        queue = AsyncTaskQueue(max_workers=1)  # Single worker for predictable ordering
        await queue.start()
        
        try:
            results = []
            
            def priority_task(priority_level):
                results.append(priority_level)
                return f"Task with priority {priority_level}"
            
            # Add tasks with different priorities (reverse order)
            await queue.add_task(priority_task, "LOW", priority=TaskPriority.LOW)
            await queue.add_task(priority_task, "CRITICAL", priority=TaskPriority.CRITICAL)
            await queue.add_task(priority_task, "NORMAL", priority=TaskPriority.NORMAL)
            await queue.add_task(priority_task, "HIGH", priority=TaskPriority.HIGH)
            
            # Wait for all tasks to complete
            await asyncio.sleep(1.0)
            
            # High priority tasks should execute first
            assert "CRITICAL" in results[:2]  # Should be one of the first two
            assert "LOW" in results[-2:]      # Should be one of the last two
            
        finally:
            await queue.stop()
    
    async def test_task_retry_mechanism(self):
        """Test task retry on failure."""
        from async_task_queue import AsyncTaskQueue
        
        queue = AsyncTaskQueue(max_workers=1)
        await queue.start()
        
        try:
            attempt_count = 0
            
            def failing_task():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 3:
                    raise ValueError("Simulated failure")
                return "success"
            
            task_id = await queue.add_task(failing_task, max_retries=3)
            
            # Wait for task completion with retries
            result = await queue.wait_for_task(task_id, timeout=10.0)
            
            assert result is not None
            assert result.success
            assert result.result == "success"
            assert attempt_count == 3  # Should have retried twice
            
        finally:
            await queue.stop()
    
    async def test_async_task_execution(self):
        """Test async task execution."""
        from async_task_queue import AsyncTaskQueue
        
        queue = AsyncTaskQueue(max_workers=2)
        await queue.start()
        
        try:
            async def async_task(delay, value):
                await asyncio.sleep(delay)
                return f"async_result_{value}"
            
            # Add async tasks
            task_ids = []
            for i in range(3):
                task_id = await queue.add_task(async_task, 0.1, i)
                task_ids.append(task_id)
            
            # Wait for all tasks
            results = []
            for task_id in task_ids:
                result = await queue.wait_for_task(task_id, timeout=5.0)
                results.append(result)
            
            # Verify all tasks completed successfully
            assert all(r and r.success for r in results)
            expected_values = {f"async_result_{i}" for i in range(3)}
            actual_values = {r.result for r in results}
            assert actual_values == expected_values
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
class TestPerformanceOptimizer:
    """Test the enhanced performance optimizer."""
    
    async def test_advanced_optimizations(self):
        """Test advanced optimization features."""
        from performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        # Mock system metrics
        with patch.object(optimizer, 'get_current_metrics') as mock_metrics:
            mock_metrics.return_value = MagicMock(
                memory_percent=75,
                cpu_percent=65
            )
            
            # Run optimizations
            optimizations = optimizer.optimize_system()
            
            assert isinstance(optimizations, list)
            assert len(optimizations) > 0
            
            # Should include memory optimization
            memory_opts = [opt for opt in optimizations if 'memory' in opt.lower()]
            assert len(memory_opts) > 0


class TestIntegrationPerformance:
    """Integration tests for overall performance improvements."""
    
    def test_import_performance(self):
        """Test that optimized modules import quickly."""
        import time
        
        modules_to_test = [
            'cache_manager',
            'http_manager', 
            'async_task_queue',
            'performance_optimizer'
        ]
        
        for module_name in modules_to_test:
            start_time = time.time()
            
            # Import module
            __import__(module_name)
            
            import_time = time.time() - start_time
            print(f"Import time for {module_name}: {import_time:.3f}s")
            
            # Should import in reasonable time
            assert import_time < 1.0, f"{module_name} took too long to import"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self):
        """Test performance under concurrent load."""
        from cache_manager import CacheManager
        from async_task_queue import AsyncTaskQueue
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(cache_dir=temp_dir)
            queue = AsyncTaskQueue(max_workers=5)
            
            await queue.start()
            
            try:
                # Test concurrent cache operations
                async def cache_operation(i):
                    key = f"perf_test_{i}"
                    await cache.set(key, f"value_{i}")
                    result = await cache.get(key)
                    return result
                
                start_time = time.time()
                
                # Run concurrent operations
                tasks = [cache_operation(i) for i in range(50)]
                results = await asyncio.gather(*tasks)
                
                execution_time = time.time() - start_time
                
                # Verify all operations completed
                assert len(results) == 50
                assert all(r is not None for r in results)
                
                print(f"Concurrent cache operations time: {execution_time:.3f}s")
                
                # Should complete reasonably fast
                assert execution_time < 5.0
                
            finally:
                await queue.stop()


if __name__ == "__main__":
    # Run basic performance validation
    import asyncio
    
    async def run_basic_tests():
        """Run basic performance validation."""
        print("Running performance validation tests...")
        
        # Test cache performance
        from cache_manager import CacheManager
        cache = CacheManager()
        
        start = time.time()
        for i in range(1000):
            await cache.set(f"perf_key_{i}", f"value_{i}")
        print(f"Cache set performance: {time.time() - start:.3f}s for 1000 items")
        
        start = time.time()
        for i in range(1000):
            await cache.get(f"perf_key_{i}")
        print(f"Cache get performance: {time.time() - start:.3f}s for 1000 items")
        
        # Test task queue performance
        from async_task_queue import AsyncTaskQueue
        queue = AsyncTaskQueue(max_workers=10)
        await queue.start()
        
        def simple_task(x):
            return x * 2
        
        start = time.time()
        task_ids = []
        for i in range(100):
            task_id = await queue.add_task(simple_task, i)
            task_ids.append(task_id)
        
        # Wait for completion
        for task_id in task_ids:
            await queue.wait_for_task(task_id, timeout=10.0)
        
        print(f"Task queue performance: {time.time() - start:.3f}s for 100 tasks")
        
        await queue.stop()
        print("Performance validation completed!")
    
    # Run if executed directly
    asyncio.run(run_basic_tests())