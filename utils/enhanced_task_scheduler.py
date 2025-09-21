"""
Enhanced Task Scheduler with Advanced Features
Provides priority queues, dependency management, resource constraints, and workflow orchestration
"""
import asyncio
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any, Set, Tuple
from enum import Enum
import logging
import json
import psutil
from pathlib import Path
import threading
import time

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class TaskState(Enum):
    """Task execution states."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class ResourceType(Enum):
    """Types of resources that can be constrained."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    CONCURRENT_TASKS = "concurrent_tasks"

class TaskDependency:
    """Represents a dependency between tasks."""

    def __init__(self, task_id: str, dependency_type: str = "completion"):
        self.task_id = task_id
        self.dependency_type = dependency_type  # completion, success, failure
        self.satisfied = False

class TaskResource:
    """Resource requirements for a task."""

    def __init__(self,
                 cpu_percent: float = 0,
                 memory_mb: int = 0,
                 disk_io: bool = False,
                 network: bool = False):
        self.cpu_percent = cpu_percent
        self.memory_mb = memory_mb
        self.disk_io = disk_io
        self.network = network

class TaskGroup:
    """A group of related tasks with shared properties."""

    def __init__(self, group_id: str, name: str, max_concurrent: int = 5):
        self.group_id = group_id
        self.name = name
        self.max_concurrent = max_concurrent
        self.tasks: Set[str] = set()
        self.running_tasks: Set[str] = set()

class EnhancedTaskScheduler:
    """Enhanced task scheduler with advanced features."""

    def __init__(self, save_file: str = "enhanced_scheduled_tasks.json"):
        self.tasks: Dict[str, Dict] = {}
        self.task_groups: Dict[str, TaskGroup] = {}
        self.save_file = Path(save_file)
        self.running = False

        # Priority queue for task execution
        self.priority_queue: List[Tuple[int, str]] = []
        self.task_states: Dict[str, TaskState] = {}

        # Resource management
        self.resource_limits = {
            ResourceType.CPU: 80.0,  # Max 80% CPU usage
            ResourceType.MEMORY: 1024,  # Max 1GB memory per task
            ResourceType.CONCURRENT_TASKS: 10  # Max 10 concurrent tasks
        }
        self.current_resources = {
            ResourceType.CPU: 0.0,
            ResourceType.MEMORY: 0,
            ResourceType.CONCURRENT_TASKS: 0
        }

        # Dependency tracking
        self.task_dependencies: Dict[str, List[TaskDependency]] = {}
        self.dependent_tasks: Dict[str, Set[str]] = {}

        # Performance monitoring
        self.execution_stats = {}
        self.resource_monitor = threading.Thread(target=self._monitor_resources, daemon=True)

        self._load_state()

    def _load_state(self):
        """Load scheduler state from file."""
        try:
            if self.save_file.exists():
                with open(self.save_file, 'r') as f:
                    state = json.load(f)

                self.tasks = state.get('tasks', {})
                self.task_groups = {}
                for gid, gdata in state.get('task_groups', {}).items():
                    group = TaskGroup(gid, gdata['name'], gdata['max_concurrent'])
                    group.tasks = set(gdata['tasks'])
                    self.task_groups[gid] = group

                self.task_dependencies = state.get('task_dependencies', {})
                self.dependent_tasks = state.get('dependent_tasks', {})

                # Rebuild priority queue
                self._rebuild_priority_queue()

                logging.info(f"Loaded enhanced scheduler state with {len(self.tasks)} tasks")
        except Exception as e:
            logging.error(f"Error loading scheduler state: {e}")

    def _save_state(self):
        """Save scheduler state to file."""
        try:
            state = {
                'tasks': self.tasks,
                'task_groups': {
                    gid: {
                        'name': g.name,
                        'max_concurrent': g.max_concurrent,
                        'tasks': list(g.tasks)
                    } for gid, g in self.task_groups.items()
                },
                'task_dependencies': self.task_dependencies,
                'dependent_tasks': self.dependent_tasks
            }

            with open(self.save_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Error saving scheduler state: {e}")

    def _rebuild_priority_queue(self):
        """Rebuild the priority queue from current tasks."""
        self.priority_queue = []
        for task_id, task in self.tasks.items():
            if task.get('enabled', True) and task.get('state') == TaskState.READY.value:
                priority = task.get('priority', TaskPriority.NORMAL.value)
                heapq.heappush(self.priority_queue, (priority, task_id))

    def _monitor_resources(self):
        """Monitor system resources in background."""
        while self.running:
            try:
                # Update current resource usage
                self.current_resources[ResourceType.CPU] = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.current_resources[ResourceType.MEMORY] = memory.used / (1024 * 1024)  # MB

                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                logging.error(f"Error monitoring resources: {e}")
                time.sleep(10)

    def create_task_group(self, group_id: str, name: str, max_concurrent: int = 5) -> bool:
        """Create a new task group."""
        if group_id in self.task_groups:
            return False

        self.task_groups[group_id] = TaskGroup(group_id, name, max_concurrent)
        self._save_state()
        logging.info(f"Created task group: {group_id}")
        return True

    def schedule_enhanced_task(self,
                              task_id: str,
                              command: str,
                              schedule: Dict[str, Any],
                              priority: TaskPriority = TaskPriority.NORMAL,
                              group_id: Optional[str] = None,
                              dependencies: Optional[List[TaskDependency]] = None,
                              resource_requirements: Optional[TaskResource] = None,
                              description: str = "",
                              retry_count: int = 3,
                              timeout: Optional[int] = None) -> bool:
        """Schedule an enhanced task with advanced features."""
        try:
            if task_id in self.tasks:
                return False

            task = {
                'command': command,
                'schedule': schedule,
                'description': description,
                'priority': priority.value,
                'group_id': group_id,
                'dependencies': [dep.__dict__ for dep in (dependencies or [])],
                'resource_requirements': resource_requirements.__dict__ if resource_requirements else None,
                'created_at': datetime.now().isoformat(),
                'last_run': None,
                'next_run': self._calculate_next_run(schedule),
                'enabled': True,
                'runs': 0,
                'failures': 0,
                'retry_count': retry_count,
                'timeout': timeout,
                'state': TaskState.PENDING.value,
                'execution_history': [],
                'performance_metrics': {
                    'avg_execution_time': 0,
                    'success_rate': 100,
                    'resource_usage': {}
                }
            }

            self.tasks[task_id] = task
            self.task_states[task_id] = TaskState.PENDING

            # Add to task group
            if group_id and group_id in self.task_groups:
                self.task_groups[group_id].tasks.add(task_id)

            # Set up dependencies
            if dependencies:
                self.task_dependencies[task_id] = dependencies
                for dep in dependencies:
                    if dep.task_id not in self.dependent_tasks:
                        self.dependent_tasks[dep.task_id] = set()
                    self.dependent_tasks[dep.task_id].add(task_id)

            # Check if task can be made ready
            self._update_task_readiness(task_id)

            self._save_state()
            logging.info(f"Scheduled enhanced task: {task_id} with priority {priority.name}")
            return True

        except Exception as e:
            logging.error(f"Error scheduling enhanced task {task_id}: {e}")
            return False

    def _update_task_readiness(self, task_id: str):
        """Update task readiness based on dependencies and resources."""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]

        # Check dependencies
        dependencies_satisfied = True
        if task_id in self.task_dependencies:
            for dep in self.task_dependencies[task_id]:
                dep_task = self.tasks.get(dep.task_id)
                if not dep_task:
                    dependencies_satisfied = False
                    break

                if dep.dependency_type == "completion":
                    if dep_task.get('state') not in [TaskState.COMPLETED.value, TaskState.FAILED.value]:
                        dependencies_satisfied = False
                        break
                elif dep.dependency_type == "success":
                    if dep_task.get('state') != TaskState.COMPLETED.value:
                        dependencies_satisfied = False
                        break

        # Check resource availability
        resources_available = self._check_resource_availability(task)

        # Check group concurrency
        group_available = True
        if task.get('group_id'):
            group = self.task_groups.get(task['group_id'])
            if group and len(group.running_tasks) >= group.max_concurrent:
                group_available = False

        # Update task state
        if dependencies_satisfied and resources_available and group_available:
            task['state'] = TaskState.READY.value
            self.task_states[task_id] = TaskState.READY
            # Add to priority queue
            heapq.heappush(self.priority_queue, (task['priority'], task_id))
        else:
            task['state'] = TaskState.BLOCKED.value
            self.task_states[task_id] = TaskState.BLOCKED

    def _check_resource_availability(self, task: Dict) -> bool:
        """Check if resources are available for task execution."""
        resource_reqs = task.get('resource_requirements')
        if not resource_reqs:
            return True

        # Check CPU
        if resource_reqs.get('cpu_percent', 0) > 0:
            available_cpu = self.resource_limits[ResourceType.CPU] - self.current_resources[ResourceType.CPU]
            if resource_reqs['cpu_percent'] > available_cpu:
                return False

        # Check memory
        if resource_reqs.get('memory_mb', 0) > 0:
            available_memory = self.resource_limits[ResourceType.MEMORY] - self.current_resources[ResourceType.MEMORY]
            if resource_reqs['memory_mb'] > available_memory:
                return False

        # Check concurrent tasks
        if self.current_resources[ResourceType.CONCURRENT_TASKS] >= self.resource_limits[ResourceType.CONCURRENT_TASKS]:
            return False

        return True

    def _calculate_next_run(self, schedule: Dict[str, Any]) -> Optional[datetime]:
        """Calculate next run time (same as original implementation)."""
        # Implementation same as original TaskScheduler
        try:
            now = datetime.now()
            if schedule.get('type') == 'interval':
                interval = timedelta(**schedule['interval'])
                return now + interval
            elif schedule.get('type') == 'daily':
                time_config = schedule['time']
                next_run = now.replace(
                    hour=time_config['hour'],
                    minute=time_config.get('minute', 0),
                    second=time_config.get('second', 0)
                )
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
            # Add other schedule types as needed
            return now + timedelta(minutes=5)  # Default fallback
        except Exception as e:
            logging.error(f"Error calculating next run: {e}")
            return None

    async def start(self):
        """Start the enhanced task scheduler."""
        self.running = True
        self.resource_monitor.start()

        logging.info("Enhanced Task Scheduler started")

        while self.running:
            try:
                # Process ready tasks from priority queue
                while self.priority_queue and self._can_execute_more_tasks():
                    priority, task_id = heapq.heappop(self.priority_queue)
                    await self._execute_enhanced_task(task_id)

                # Check for newly ready tasks
                for task_id in self.tasks:
                    if self.task_states.get(task_id) == TaskState.PENDING:
                        self._update_task_readiness(task_id)

                await asyncio.sleep(1)

            except Exception as e:
                logging.error(f"Error in enhanced scheduler main loop: {e}")
                await asyncio.sleep(5)

    def _can_execute_more_tasks(self) -> bool:
        """Check if more tasks can be executed based on resource limits."""
        return self.current_resources[ResourceType.CONCURRENT_TASKS] < self.resource_limits[ResourceType.CONCURRENT_TASKS]

    async def _execute_enhanced_task(self, task_id: str):
        """Execute an enhanced task with full resource and dependency management."""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        self.task_states[task_id] = TaskState.RUNNING
        task['state'] = TaskState.RUNNING.value

        # Update group tracking
        if task.get('group_id'):
            group = self.task_groups.get(task['group_id'])
            if group:
                group.running_tasks.add(task_id)

        # Update resource usage
        resource_reqs = task.get('resource_requirements', {})
        self.current_resources[ResourceType.CONCURRENT_TASKS] += 1
        if resource_reqs.get('cpu_percent'):
            self.current_resources[ResourceType.CPU] += resource_reqs['cpu_percent']
        if resource_reqs.get('memory_mb'):
            self.current_resources[ResourceType.MEMORY] += resource_reqs['memory_mb']

        start_time = datetime.now()
        success = False

        try:
            # Execute with timeout if specified
            if task.get('timeout'):
                result = await asyncio.wait_for(
                    self._execute_task_command(task),
                    timeout=task['timeout']
                )
            else:
                result = await self._execute_task_command(task)

            success = True
            task['last_result'] = str(result)

        except asyncio.TimeoutError:
            logging.error(f"Task {task_id} timed out")
            task['last_error'] = "Task timed out"
        except Exception as e:
            logging.error(f"Error executing task {task_id}: {e}")
            task['last_error'] = str(e)

            # Handle retries
            if task['failures'] < task.get('retry_count', 3):
                task['failures'] += 1
                # Reschedule for retry
                task['next_run'] = datetime.now() + timedelta(minutes=1)
                task['state'] = TaskState.PENDING.value
                self.task_states[task_id] = TaskState.PENDING
            else:
                task['failures'] += 1

        finally:
            # Update task metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            task['last_run'] = start_time.isoformat()
            task['runs'] += 1
            task['last_execution_time'] = execution_time

            # Update performance metrics
            metrics = task['performance_metrics']
            total_runs = task['runs']
            metrics['avg_execution_time'] = (
                (metrics['avg_execution_time'] * (total_runs - 1)) + execution_time
            ) / total_runs
            metrics['success_rate'] = ((total_runs - task['failures']) / total_runs) * 100

            # Update execution history
            task['execution_history'].append({
                'timestamp': start_time.isoformat(),
                'duration': execution_time,
                'success': success,
                'error': task.get('last_error'),
                'resources_used': resource_reqs
            })

            # Keep only last 20 executions
            task['execution_history'] = task['execution_history'][-20:]

            # Update task state
            if success:
                self.task_states[task_id] = TaskState.COMPLETED
                task['state'] = TaskState.COMPLETED.value
                task['next_run'] = self._calculate_next_run(task['schedule'])

                # Notify dependent tasks
                self._notify_dependents(task_id)
            else:
                self.task_states[task_id] = TaskState.FAILED
                task['state'] = TaskState.FAILED.value

            # Update group tracking
            if task.get('group_id'):
                group = self.task_groups.get(task['group_id'])
                if group:
                    group.running_tasks.discard(task_id)

            # Release resources
            self.current_resources[ResourceType.CONCURRENT_TASKS] -= 1
            if resource_reqs.get('cpu_percent'):
                self.current_resources[ResourceType.CPU] -= resource_reqs['cpu_percent']
            if resource_reqs.get('memory_mb'):
                self.current_resources[ResourceType.MEMORY] -= resource_reqs['memory_mb']

            self._save_state()

    def _notify_dependents(self, completed_task_id: str):
        """Notify dependent tasks that a task has completed."""
        if completed_task_id not in self.dependent_tasks:
            return

        for dependent_id in self.dependent_tasks[completed_task_id]:
            self._update_task_readiness(dependent_id)

    async def _execute_task_command(self, task: Dict) -> Any:
        """Execute the actual task command."""
        if hasattr(self, 'command_handler'):
            if asyncio.iscoroutinefunction(self.command_handler):
                return await self.command_handler(task['command'])
            else:
                return self.command_handler(task['command'])
        else:
            raise RuntimeError("No command handler registered")

    async def stop(self):
        """Stop the enhanced task scheduler."""
        self.running = False
        self._save_state()
        logging.info("Enhanced Task Scheduler stopped")

    def get_scheduler_analytics(self) -> Dict[str, Any]:
        """Get comprehensive scheduler analytics."""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.get('state') == TaskState.COMPLETED.value)
        failed_tasks = sum(1 for t in self.tasks.values() if t.get('state') == TaskState.FAILED.value)
        running_tasks = sum(1 for t in self.tasks.values() if t.get('state') == TaskState.RUNNING.value)

        # Performance metrics
        avg_execution_time = sum(t.get('performance_metrics', {}).get('avg_execution_time', 0)
                                for t in self.tasks.values()) / max(total_tasks, 1)

        success_rate = sum(t.get('performance_metrics', {}).get('success_rate', 100)
                          for t in self.tasks.values()) / max(total_tasks, 1)

        # Resource utilization
        resource_utilization = {
            res_type.value: (self.current_resources.get(res_type, 0) / max(self.resource_limits.get(res_type, 1), 1)) * 100
            for res_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.CONCURRENT_TASKS]
        }

        # Group performance
        group_performance = {}
        for gid, group in self.task_groups.items():
            group_tasks = [self.tasks[tid] for tid in group.tasks if tid in self.tasks]
            if group_tasks:
                group_success = sum(t.get('performance_metrics', {}).get('success_rate', 100)
                                  for t in group_tasks) / len(group_tasks)
                group_performance[gid] = {
                    'name': group.name,
                    'task_count': len(group.tasks),
                    'running_tasks': len(group.running_tasks),
                    'success_rate': round(group_success, 2)
                }

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'running_tasks': running_tasks,
            'pending_tasks': sum(1 for t in self.tasks.values() if t.get('state') == TaskState.PENDING.value),
            'blocked_tasks': sum(1 for t in self.tasks.values() if t.get('state') == TaskState.BLOCKED.value),
            'average_execution_time': round(avg_execution_time, 3),
            'overall_success_rate': round(success_rate, 2),
            'resource_utilization': resource_utilization,
            'group_performance': group_performance,
            'priority_distribution': self._get_priority_distribution(),
            'scheduler_health_score': self._calculate_health_score()
        }

    def _get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of tasks by priority."""
        distribution = {p.name: 0 for p in TaskPriority}
        for task in self.tasks.values():
            priority = TaskPriority(task.get('priority', TaskPriority.NORMAL.value))
            distribution[priority.name] += 1
        return distribution

    def _calculate_health_score(self) -> float:
        """Calculate overall scheduler health score."""
        if not self.tasks:
            return 100.0

        # Factors: success rate, resource utilization, blocked tasks ratio
        success_rate = sum(t.get('performance_metrics', {}).get('success_rate', 100)
                          for t in self.tasks.values()) / len(self.tasks)

        blocked_ratio = sum(1 for t in self.tasks.values()
                           if t.get('state') == TaskState.BLOCKED.value) / len(self.tasks)

        avg_resource_util = sum(self.current_resources.get(res_type, 0) / max(self.resource_limits.get(res_type, 1), 1)
                               for res_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.CONCURRENT_TASKS]) / 3 * 100

        # Health score: weighted average
        health_score = (
            success_rate * 0.5 +           # 50% weight on success rate
            (100 - blocked_ratio * 100) * 0.3 +  # 30% weight on task flow
            (100 - avg_resource_util) * 0.2      # 20% weight on resource efficiency
        )

        return round(max(0, min(100, health_score)), 2)

    def register_command_handler(self, handler: Callable[[str], Any]):
        """Register a command handler function."""
        self.command_handler = handler
        logging.info("Command handler registered with EnhancedTaskScheduler")

    # Additional management methods
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or pending task."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task['state'] in [TaskState.RUNNING.value, TaskState.READY.value, TaskState.PENDING.value]:
            task['state'] = TaskState.CANCELLED.value
            self.task_states[task_id] = TaskState.CANCELLED
            self._save_state()
            logging.info(f"Cancelled task: {task_id}")
            return True
        return False

    def get_task_workflow(self, task_id: str) -> Dict[str, Any]:
        """Get workflow information for a task including dependencies."""
        if task_id not in self.tasks:
            return {}

        task = self.tasks[task_id]
        workflow = {
            'task': task,
            'dependencies': [],
            'dependents': list(self.dependent_tasks.get(task_id, [])),
            'group': None,
            'state': self.task_states.get(task_id, TaskState.PENDING)
        }

        # Add dependency details
        if task_id in self.task_dependencies:
            for dep in self.task_dependencies[task_id]:
                dep_task = self.tasks.get(dep.task_id, {})
                workflow['dependencies'].append({
                    'task_id': dep.task_id,
                    'type': dep.dependency_type,
                    'satisfied': dep.satisfied,
                    'state': dep_task.get('state')
                })

        # Add group information
        if task.get('group_id'):
            group = self.task_groups.get(task['group_id'])
            if group:
                workflow['group'] = {
                    'id': group.group_id,
                    'name': group.name,
                    'concurrent_running': len(group.running_tasks),
                    'max_concurrent': group.max_concurrent
                }

        return workflow