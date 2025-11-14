"""
ULTRON Agent Task Scheduler
Provides cron-like scheduling with retry logic and task persistence
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
import time
from pathlib import Path
from enum import Enum
from utils.ultron_logger import ultron_logger


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    name: str
    cron_expression: str
    task_func: Callable = field(default=None, repr=False)
    max_retries: int = 3
    backoff_factor: float = 2.0
    timeout_s: float = 30.0
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    last_status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of task execution"""
    task_name: str
    success: bool
    output: Any = None
    error: str = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    retry_attempt: int = 0


class TaskScheduler:
    """
    Manages task scheduling with cron expressions and retry logic
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tasks: Dict[str, ScheduledTask] = {}
        self.results_history: List[TaskResult] = []
        self.max_history = 1000
        self.max_workers = config.get('max_workers', 5) if config else 5
        self.persistence_file = Path(config.get('persistence_file', 'cache/task_schedules.json')) if config else Path('cache/task_schedules.json')
        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None

        # Load persisted schedules
        self._load_schedules()

    def schedule_cron(self, name: str, cron_expression: str, task_func: Callable,
                     max_retries: int = 3, backoff_factor: float = 2.0) -> None:
        """
        Schedule a task with cron expression

        Args:
            name: Task name
            cron_expression: Cron format (e.g., "0 12 * * *" for daily at noon)
            task_func: Async function to execute
            max_retries: Maximum retry attempts on failure
            backoff_factor: Exponential backoff multiplier
        """
        if name in self.tasks:
            ultron_logger.log_info("task_scheduler", f"Overwriting existing task: {name}")

        task = ScheduledTask(
            name=name,
            cron_expression=cron_expression,
            task_func=task_func,
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )

        self.tasks[name] = task
        ultron_logger.log_info("task_scheduler", f"Task scheduled: {name}", cron=cron_expression)
        self._persist_schedules()

    async def execute_with_retry(self, task: ScheduledTask) -> TaskResult:
        """
        Execute task with exponential backoff retry logic

        Args:
            task: Task to execute

        Returns:
            TaskResult with execution details
        """
        task.last_status = TaskStatus.RUNNING
        start = time.time()
        last_error = None

        for attempt in range(task.max_retries + 1):
            try:
                # Calculate backoff
                if attempt > 0:
                    backoff_delay = (task.backoff_factor ** (attempt - 1))
                    await asyncio.sleep(backoff_delay)

                # Execute with timeout
                result = await asyncio.wait_for(
                    task.task_func(),
                    timeout=task.timeout_s
                )

                execution_time = (time.time() - start) * 1000
                task.last_status = TaskStatus.SUCCESS
                task.last_run = datetime.now()
                task.retry_count = 0

                task_result = TaskResult(
                    task_name=task.name,
                    success=True,
                    output=result,
                    execution_time_ms=execution_time,
                    retry_attempt=attempt
                )

                # Record in history
                task.execution_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'attempt': attempt,
                    'execution_time_ms': execution_time
                })

                self._record_result(task_result)
                ultron_logger.log_info("task_scheduler",
                                     f"Task executed successfully: {task.name} (attempt {attempt + 1})")
                return task_result

            except asyncio.TimeoutError:
                last_error = f"Task timeout after {task.timeout_s}s"
                ultron_logger.log_error("task_scheduler",
                                      f"Timeout on attempt {attempt + 1} for {task.name}")

            except Exception as e:
                last_error = str(e)
                ultron_logger.log_error("task_scheduler",
                                      f"Error on attempt {attempt + 1} for {task.name}: {last_error}")

        # All retries exhausted
        execution_time = (time.time() - start) * 1000
        task.last_status = TaskStatus.FAILED
        task.retry_count = task.max_retries

        task_result = TaskResult(
            task_name=task.name,
            success=False,
            error=last_error,
            execution_time_ms=execution_time,
            retry_attempt=task.max_retries
        )

        task.execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'attempts': task.max_retries + 1,
            'error': last_error,
            'execution_time_ms': execution_time
        })

        self._record_result(task_result)
        return task_result

    async def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled tasks"""
        tasks_list = []
        for name, task in self.tasks.items():
            tasks_list.append({
                'name': name,
                'cron_expression': task.cron_expression,
                'max_retries': task.max_retries,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'last_status': task.last_status.value,
                'created_at': task.created_at.isoformat()
            })
        return tasks_list

    async def persist_schedules(self, file_path: str = None) -> bool:
        """
        Persist schedules to file for recovery after restart

        Args:
            file_path: Optional custom path

        Returns:
            True if successful
        """
        try:
            path = Path(file_path) if file_path else self.persistence_file
            path.parent.mkdir(parents=True, exist_ok=True)

            schedules_data = {
                'timestamp': datetime.now().isoformat(),
                'tasks': []
            }

            for name, task in self.tasks.items():
                schedules_data['tasks'].append({
                    'name': name,
                    'cron_expression': task.cron_expression,
                    'max_retries': task.max_retries,
                    'backoff_factor': task.backoff_factor,
                    'timeout_s': task.timeout_s,
                    'created_at': task.created_at.isoformat(),
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'last_status': task.last_status.value
                })

            with open(path, 'w') as f:
                json.dump(schedules_data, f, indent=2)

            ultron_logger.log_info("task_scheduler", f"Schedules persisted to {path}")
            return True

        except Exception as e:
            ultron_logger.log_error("task_scheduler", f"Failed to persist schedules: {str(e)}")
            return False

    async def load_schedules(self, file_path: str = None) -> bool:
        """
        Load schedules from file

        Args:
            file_path: Optional custom path

        Returns:
            True if successful
        """
        try:
            path = Path(file_path) if file_path else self.persistence_file

            if not path.exists():
                ultron_logger.log_info("task_scheduler", f"No persisted schedules found at {path}")
                return False

            with open(path, 'r') as f:
                data = json.load(f)

            # Restore task metadata (note: functions must be re-registered)
            for task_data in data.get('tasks', []):
                if task_data['name'] in self.tasks:
                    task = self.tasks[task_data['name']]
                    if task_data['last_run']:
                        task.last_run = datetime.fromisoformat(task_data['last_run'])
                    task.last_status = TaskStatus(task_data['last_status'])

            ultron_logger.log_info("task_scheduler", f"Schedules loaded from {path}")
            return True

        except Exception as e:
            ultron_logger.log_error("task_scheduler", f"Failed to load schedules: {str(e)}")
            return False

    def _load_schedules(self) -> None:
        """Load persisted schedules on initialization"""
        try:
            if self.persistence_file.exists():
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                # Metadata loaded but functions must be re-registered
                ultron_logger.log_info("task_scheduler", "Loaded persisted schedule metadata")
        except Exception as e:
            ultron_logger.log_error("task_scheduler", f"Error loading persisted schedules: {str(e)}")

    def _persist_schedules(self) -> None:
        """Persist schedules to file (synchronous wrapper)"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'tasks': []
            }

            for name, task in self.tasks.items():
                data['tasks'].append({
                    'name': name,
                    'cron_expression': task.cron_expression,
                    'max_retries': task.max_retries,
                    'backoff_factor': task.backoff_factor,
                    'timeout_s': task.timeout_s,
                    'created_at': task.created_at.isoformat(),
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'last_status': task.last_status.value
                })

            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            ultron_logger.log_error("task_scheduler", f"Failed to persist schedules: {str(e)}")

    def _record_result(self, result: TaskResult) -> None:
        """Record task execution result"""
        self.results_history.append(result)

        # Keep only recent history
        if len(self.results_history) > self.max_history:
            self.results_history = self.results_history[-self.max_history:]

    def get_task_history(self, task_name: str = None, limit: int = None) -> List[TaskResult]:
        """Get task execution history"""
        history = self.results_history

        if task_name:
            history = [r for r in history if r.task_name == task_name]

        if limit:
            history = history[-limit:]

        return history
