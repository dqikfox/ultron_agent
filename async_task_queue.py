"""
Async Task Queue for ULTRON Agent 3.0
Provides background task processing and priority management
"""

import asyncio
import time
from enum import IntEnum
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from security_utils import sanitize_log_input

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Background task definition."""
    id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    timeout: Optional[float] = None
    callback: Optional[Callable] = None
    
    def __lt__(self, other) -> bool:
        """Compare tasks by priority for priority queue."""
        if self.priority == other.priority:
            return self.created_at < other.created_at
        return self.priority > other.priority


@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)


class AsyncTaskQueue:
    """Async task queue with priority and retry support."""
    
    def __init__(self, 
                 max_workers: int = 5,
                 max_queue_size: int = 1000):
        
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        
        self.task_queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.scheduled_tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_retried': 0,
            'total_execution_time': 0.0,
            'queue_size': 0
        }
    
    async def start(self) -> None:
        """Start the task queue workers."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        # Start scheduler for delayed tasks
        self.scheduler_task = asyncio.create_task(self._scheduler())
        
        logger.info(f"Started async task queue with {self.max_workers} workers")
    
    async def stop(self) -> None:
        """Stop the task queue and cleanup."""
        self.is_running = False
        
        # Cancel scheduler
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Cancel running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        self.workers.clear()
        self.running_tasks.clear()
        
        logger.info("Async task queue stopped")
    
    async def add_task(self, 
                      func: Callable,
                      *args,
                      task_id: Optional[str] = None,
                      priority: TaskPriority = TaskPriority.NORMAL,
                      delay_seconds: float = 0,
                      max_retries: int = 3,
                      timeout: Optional[float] = None,
                      callback: Optional[Callable] = None,
                      **kwargs) -> str:
        """Add task to the queue."""
        
        if task_id is None:
            task_id = f"task-{int(time.time() * 1000000)}"
        
        scheduled_for = None
        if delay_seconds > 0:
            scheduled_for = datetime.now() + timedelta(seconds=delay_seconds)
        
        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_for=scheduled_for,
            max_retries=max_retries,
            timeout=timeout,
            callback=callback
        )
        
        if scheduled_for:
            self.scheduled_tasks[task_id] = task
        else:
            try:
                await self.task_queue.put(task)
                self.stats['queue_size'] = self.task_queue.qsize()
            except asyncio.QueueFull:
                logger.error(f"Task queue is full, dropping task: {sanitize_log_input(task_id)}")
                raise ValueError("Task queue is full")
        
        logger.debug(f"Added task: {sanitize_log_input(task_id)}")
        return task_id
    
    async def _worker(self, worker_id: str) -> None:
        """Worker process to execute tasks."""
        logger.info(f"Started task worker: {worker_id}")
        
        while self.is_running:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                self.stats['queue_size'] = self.task_queue.qsize()
                
                # Execute task
                await self._execute_task(task, worker_id)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks available, continue
                continue
            except asyncio.CancelledError:
                logger.info(f"Worker cancelled: {worker_id}")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {sanitize_log_input(str(e))}")
    
    async def _execute_task(self, task: Task, worker_id: str) -> None:
        """Execute a single task."""
        start_time = time.time()
        
        try:
            logger.debug(f"Worker {worker_id} executing task: {sanitize_log_input(task.id)}")
            
            # Create execution task with timeout
            if asyncio.iscoroutinefunction(task.func):
                exec_coro = task.func(*task.args, **task.kwargs)
            else:
                exec_coro = asyncio.to_thread(task.func, *task.args, **task.kwargs)
            
            if task.timeout:
                result = await asyncio.wait_for(exec_coro, timeout=task.timeout)
            else:
                result = await exec_coro
            
            execution_time = time.time() - start_time
            
            # Record successful result
            task_result = TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
            self.completed_tasks[task.id] = task_result
            self.stats['tasks_completed'] += 1
            self.stats['total_execution_time'] += execution_time
            
            # Call callback if provided
            if task.callback:
                try:
                    if asyncio.iscoroutinefunction(task.callback):
                        await task.callback(task_result)
                    else:
                        task.callback(task_result)
                except Exception as e:
                    logger.error(f"Task callback error: {sanitize_log_input(str(e))}")
            
            logger.debug(f"Task completed successfully: {sanitize_log_input(task.id)}")
            
        except asyncio.TimeoutError:
            await self._handle_task_failure(task, "Task timeout", start_time)
        except Exception as e:
            await self._handle_task_failure(task, str(e), start_time)
    
    async def _handle_task_failure(self, task: Task, error_msg: str, start_time: float) -> None:
        """Handle task execution failure."""
        execution_time = time.time() - start_time
        
        logger.error(f"Task failed: {sanitize_log_input(task.id)} - {sanitize_log_input(error_msg)}")
        
        # Check if we should retry
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            
            # Add exponential backoff delay
            delay = min(2 ** task.retry_count, 60)  # Max 60 seconds
            task.scheduled_for = datetime.now() + timedelta(seconds=delay)
            
            self.scheduled_tasks[task.id] = task
            self.stats['tasks_retried'] += 1
            
            logger.info(f"Scheduling task retry: {sanitize_log_input(task.id)} (attempt {task.retry_count + 1})")
            
        else:
            # Record failed result
            task_result = TaskResult(
                task_id=task.id,
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
            self.completed_tasks[task.id] = task_result
            self.stats['tasks_failed'] += 1
            
            # Call callback with error
            if task.callback:
                try:
                    if asyncio.iscoroutinefunction(task.callback):
                        await task.callback(task_result)
                    else:
                        task.callback(task_result)
                except Exception as e:
                    logger.error(f"Task error callback failed: {sanitize_log_input(str(e))}")
    
    async def _scheduler(self) -> None:
        """Schedule delayed tasks."""
        logger.info("Started task scheduler")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                ready_tasks = []
                
                # Find ready tasks
                for task_id, task in list(self.scheduled_tasks.items()):
                    if task.scheduled_for and task.scheduled_for <= current_time:
                        ready_tasks.append(task_id)
                
                # Move ready tasks to queue
                for task_id in ready_tasks:
                    task = self.scheduled_tasks.pop(task_id)
                    try:
                        await self.task_queue.put(task)
                        self.stats['queue_size'] = self.task_queue.qsize()
                    except asyncio.QueueFull:
                        logger.error(f"Queue full, dropping scheduled task: {sanitize_log_input(task_id)}")
                
                await asyncio.sleep(1.0)  # Check every second
                
            except asyncio.CancelledError:
                logger.info("Task scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {sanitize_log_input(str(e))}")
                await asyncio.sleep(5.0)
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result of completed task."""
        return self.completed_tasks.get(task_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'queue_size': self.task_queue.qsize(),
            'scheduled_tasks': len(self.scheduled_tasks),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'workers_active': len([w for w in self.workers if not w.done()]),
            'stats': self.stats.copy()
        }
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Wait for task completion and return result."""
        start_time = time.time()
        
        while True:
            result = self.get_task_result(task_id)
            if result:
                return result
            
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            await asyncio.sleep(0.1)
    
    async def clear_completed(self, keep_recent: int = 100) -> int:
        """Clear old completed task results."""
        if len(self.completed_tasks) <= keep_recent:
            return 0
        
        # Sort by completion time and keep most recent
        sorted_tasks = sorted(
            self.completed_tasks.items(),
            key=lambda x: x[1].completed_at,
            reverse=True
        )
        
        tasks_to_keep = dict(sorted_tasks[:keep_recent])
        removed_count = len(self.completed_tasks) - len(tasks_to_keep)
        
        self.completed_tasks = tasks_to_keep
        return removed_count


# Global task queue instance
task_queue = AsyncTaskQueue()