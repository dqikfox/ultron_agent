"""
Async HTTP Session Manager for ULTRON Agent 3.0
Provides connection pooling and request optimization
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging
from security_utils import sanitize_log_input

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """HTTP request performance metrics."""
    url: str
    method: str
    status_code: int
    response_time: float
    content_length: int
    timestamp: float


class AsyncHTTPManager:
    """Manages async HTTP sessions with connection pooling."""
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_connections_per_host: int = 30,
                 timeout_seconds: int = 30):
        
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.timeout_seconds = timeout_seconds
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        self.request_metrics: List[RequestMetrics] = []
        self.max_metrics = 1000
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling."""
        if self._session is None or self._session.closed:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    
                    # Create connector with connection pooling
                    connector = aiohttp.TCPConnector(
                        limit=self.max_connections,
                        limit_per_host=self.max_connections_per_host,
                        ttl_dns_cache=300,  # 5 minute DNS cache
                        use_dns_cache=True,
                        keepalive_timeout=60,
                        enable_cleanup_closed=True
                    )
                    
                    # Create session with optimized settings
                    timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
                    self._session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=timeout,
                        headers={
                            'User-Agent': 'ULTRON-Agent/3.0',
                            'Connection': 'keep-alive'
                        }
                    )
                    
                    logger.info("Created new HTTP session with connection pooling")
        
        return self._session
    
    async def request(self, 
                     method: str, 
                     url: str, 
                     **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with performance tracking."""
        start_time = time.time()
        session = await self._get_session()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                content_length = int(response.headers.get('content-length', 0))
                
                # Record metrics
                metrics = RequestMetrics(
                    url=url,
                    method=method,
                    status_code=response.status,
                    response_time=time.time() - start_time,
                    content_length=content_length,
                    timestamp=time.time()
                )
                
                await self._record_metrics(metrics)
                return response
                
        except Exception as e:
            logger.error(f"HTTP request failed: {sanitize_log_input(str(e))}")
            raise
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request."""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request."""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make PUT request."""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make DELETE request."""
        return await self.request('DELETE', url, **kwargs)
    
    async def _record_metrics(self, metrics: RequestMetrics) -> None:
        """Record request metrics."""
        try:
            self.request_metrics.append(metrics)
            
            # Limit metrics history
            if len(self.request_metrics) > self.max_metrics:
                self.request_metrics = self.request_metrics[-self.max_metrics//2:]
                
        except Exception as e:
            logger.error(f"Failed to record HTTP metrics: {sanitize_log_input(str(e))}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get HTTP performance metrics summary."""
        if not self.request_metrics:
            return {'total_requests': 0}
        
        recent_metrics = [m for m in self.request_metrics 
                         if time.time() - m.timestamp < 300]  # Last 5 minutes
        
        if not recent_metrics:
            return {'total_requests': len(self.request_metrics), 'recent_requests': 0}
        
        response_times = [m.response_time for m in recent_metrics]
        status_codes = [m.status_code for m in recent_metrics]
        
        return {
            'total_requests': len(self.request_metrics),
            'recent_requests': len(recent_metrics),
            'avg_response_time': sum(response_times) / len(response_times),
            'max_response_time': max(response_times),
            'min_response_time': min(response_times),
            'success_rate': len([s for s in status_codes if 200 <= s < 300]) / len(status_codes) * 100,
            'total_data_mb': sum(m.content_length for m in recent_metrics) / (1024 * 1024)
        }
    
    async def close(self) -> None:
        """Close HTTP session and cleanup connections."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("HTTP session closed")
    
    @asynccontextmanager
    async def request_context(self, method: str, url: str, **kwargs):
        """Context manager for HTTP requests."""
        try:
            response = await self.request(method, url, **kwargs)
            yield response
        finally:
            pass


class BatchRequestManager:
    """Manages batched HTTP requests for improved performance."""
    
    def __init__(self, 
                 http_manager: AsyncHTTPManager,
                 batch_size: int = 10,
                 batch_timeout: float = 1.0):
        
        self.http_manager = http_manager
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests: List[Dict[str, Any]] = []
        self._batch_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None
    
    async def add_request(self, method: str, url: str, **kwargs) -> Any:
        """Add request to batch queue."""
        future = asyncio.Future()
        
        request_data = {
            'method': method,
            'url': url,
            'kwargs': kwargs,
            'future': future
        }
        
        async with self._batch_lock:
            self.pending_requests.append(request_data)
            
            # Start batch processing if not already running
            if self._batch_task is None or self._batch_task.done():
                self._batch_task = asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _process_batch(self) -> None:
        """Process pending requests in batches."""
        try:
            await asyncio.sleep(self.batch_timeout)
            
            async with self._batch_lock:
                if not self.pending_requests:
                    return
                
                batch = self.pending_requests[:self.batch_size]
                self.pending_requests = self.pending_requests[self.batch_size:]
            
            # Execute batch concurrently
            tasks = []
            for request_data in batch:
                task = asyncio.create_task(
                    self._execute_single_request(request_data)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Continue processing if more requests pending
            async with self._batch_lock:
                if self.pending_requests:
                    self._batch_task = asyncio.create_task(self._process_batch())
                    
        except Exception as e:
            logger.error(f"Batch processing failed: {sanitize_log_input(str(e))}")
    
    async def _execute_single_request(self, request_data: Dict[str, Any]) -> None:
        """Execute single request from batch."""
        try:
            response = await self.http_manager.request(
                request_data['method'],
                request_data['url'],
                **request_data['kwargs']
            )
            
            # Read response content
            content = await response.text()
            result = {
                'status': response.status,
                'headers': dict(response.headers),
                'content': content
            }
            
            request_data['future'].set_result(result)
            
        except Exception as e:
            request_data['future'].set_exception(e)


# Global HTTP manager instance
http_manager = AsyncHTTPManager()
batch_manager = BatchRequestManager(http_manager)