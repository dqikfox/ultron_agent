import asyncio
from ultron_logger import Logger
import collections
import typing as T
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
from enum import Enum


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class ToolResult:
    output: str | None
    exception: Exception | None = None
    execution_time_ms: float = 0.0
    cached: bool = False


@dataclass
class CircuitBreaker:
    """Circuit breaker for failing tools"""
    name: str
    failure_threshold: int = 5
    reset_timeout_s: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    last_reset_time: datetime | None = None


@dataclass
class TaskDependency:
    """Represents task dependencies"""
    task_name: str
    depends_on: list = field(default_factory=list)
    result: T.Any = None
    error: Exception | None = None


class ResultCache:
    """Simple TTL-based result cache"""
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.cache: dict = {}
        self.timestamps: dict = {}

    def get(self, key: str) -> T.Any | None:
        """Get cached result if not expired"""
        if key in self.cache:
            age = time.time() - self.timestamps[key]
            if age < self.ttl_seconds:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None

    def set(self, key: str, value: T.Any) -> None:
        """Cache a result"""
        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cached results"""
        self.cache.clear()
        self.timestamps.clear()




async def async_execute_tool(tool, args, timeout_s: float = 30.0):
    """Execute a tool with timeout handling"""
    start_time = time.time()
    try:
        if asyncio.iscoroutinefunction(tool.run):
            result = await asyncio.wait_for(tool.run(args), timeout=timeout_s)
        else:
            result = tool.run(args)

        execution_time = (time.time() - start_time) * 1000
        return ToolResult(output=result, execution_time_ms=execution_time)
    except asyncio.TimeoutError:
        execution_time = (time.time() - start_time) * 1000
        error = Exception(f"Tool execution timeout after {timeout_s}s")
        Logger.error(f"Tool {tool.name} timeout: {timeout_s}s")
        return ToolResult(output=None, exception=error, execution_time_ms=execution_time)
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        Logger.error(f"Tool execution failed: {tool.name} - {str(e)}")
        return ToolResult(output=None, exception=e, execution_time_ms=execution_time)


async def _resolve_dependencies(tools: T.Dict[str, T.Any]):
    """Resolve and execute tools with dependency ordering"""
    graph = collections.defaultdict(list)
    for tool_name, tool in tools.items():
        if hasattr(tool, 'dependencies'):
            for dependency in tool.dependencies:
                graph[dependency].append(tool_name)

    async def dfs(node):
        results = []
        for dep in graph[node]:
            res = await dfs(dep)
            results.append(res)
        return await async_execute_tool(tools[node], results)

    first_tool = list(tools.keys())[0]
    return await dfs(first_tool)


class AsyncToolOrchestrator:
    """Orchestrates async tool execution with advanced coordination"""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.cache = ResultCache(ttl_seconds=300)
        self.circuit_breakers: dict = {}
        self.performance_metrics: dict = {}

    def register_circuit_breaker(self, tool_name: str,
                                failure_threshold: int = 5,
                                reset_timeout_s: int = 60) -> None:
        """Register a circuit breaker for a tool"""
        self.circuit_breakers[tool_name] = CircuitBreaker(
            name=tool_name,
            failure_threshold=failure_threshold,
            reset_timeout_s=reset_timeout_s
        )

    def _check_circuit_breaker(self, tool_name: str) -> bool:
        """Check if tool can be executed based on circuit breaker state"""
        if tool_name not in self.circuit_breakers:
            return True

        cb = self.circuit_breakers[tool_name]

        if cb.state == CircuitBreakerState.CLOSED:
            return True
        elif cb.state == CircuitBreakerState.OPEN:
            if cb.last_failure_time:
                elapsed = (datetime.now() - cb.last_failure_time).total_seconds()
                if elapsed > cb.reset_timeout_s:
                    cb.state = CircuitBreakerState.HALF_OPEN
                    return True
            return False
        else:  # HALF_OPEN
            return True

    async def execute_parallel(self, tools: T.Dict[str, T.Any],
                              max_concurrent: int | None = None) -> dict:
        """Execute tools in parallel with concurrency limiting"""
        max_workers = max_concurrent or self.max_concurrent
        semaphore = asyncio.Semaphore(max_workers)

        async def execute_with_semaphore(name, tool):
            async with semaphore:
                if not self._check_circuit_breaker(name):
                    Logger.warning(f"Circuit breaker open for {name}")
                    return name, ToolResult(output=None, exception=Exception("Circuit breaker open"))

                result = await async_execute_tool(tool, [])
                return name, result

        tasks = [execute_with_semaphore(name, tool) for name, tool in tools.items()]
        results = await asyncio.gather(*tasks)
        return dict(results)

    async def execute_chain(self, tools: T.Dict[str, T.Any]) -> list:
        """Execute tools sequentially, passing output to next"""
        results = []
        current_output = None

        for tool_name, tool in tools.items():
            try:
                res = await async_execute_tool(tool, [current_output] if current_output else [])
                results.append(res)
                current_output = res.output
            except Exception as e:
                Logger.error(f"Tool execution failed: {tool_name}")
                break

        return results

    async def gather_results(self, tools: T.Dict[str, T.Any]) -> dict:
        """Resolve dependencies and execute tools"""
        results = await _resolve_dependencies(tools)
        return {"result": results, "success": results.exception is None}
