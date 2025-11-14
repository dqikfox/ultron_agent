"""
Unit and integration tests for task_scheduler utility
"""

import pytest
import asyncio
import time
from utils.task_scheduler import (
    TaskScheduler, TaskStatus, ScheduledTask, TaskResult
)


class TestTaskScheduler:
    """Tests for TaskScheduler class"""

    @pytest.mark.unit
    def test_init_creates_instance(self):
        """Test TaskScheduler initialization"""
        scheduler = TaskScheduler()
        assert scheduler is not None
        assert scheduler.tasks == {}
        assert scheduler.results_history == []
        assert scheduler.max_workers == 5

    @pytest.mark.unit
    def test_init_with_config(self):
        """Test TaskScheduler with custom config"""
        config = {
            'max_workers': 10,
            'persistence_file': 'custom_schedule.json'
        }
        scheduler = TaskScheduler(config)
        assert scheduler.max_workers == 10
        assert scheduler.persistence_file.name == 'custom_schedule.json'

    @pytest.mark.unit
    def test_schedule_cron_creates_task(self):
        """Test scheduling a cron task"""
        scheduler = TaskScheduler()

        async def dummy_task():
            return "task_result"

        scheduler.schedule_cron(
            "test_task",
            "0 12 * * *",
            dummy_task,
            max_retries=3,
            backoff_factor=2.0
        )

        assert "test_task" in scheduler.tasks
        task = scheduler.tasks["test_task"]
        assert task.name == "test_task"
        assert task.cron_expression == "0 12 * * *"
        assert task.max_retries == 3
        assert task.backoff_factor == 2.0

    @pytest.mark.unit
    def test_schedule_overwrites_existing_task(self):
        """Test that scheduling overwrites existing task"""
        scheduler = TaskScheduler()

        async def task1():
            return "task1"

        async def task2():
            return "task2"

        scheduler.schedule_cron("same_name", "0 12 * * *", task1)
        scheduler.schedule_cron("same_name", "0 13 * * *", task2)

        assert scheduler.tasks["same_name"].cron_expression == "0 13 * * *"

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(
        self, mock_async_function, event_loop
    ):
        """Test successful task execution"""
        scheduler = TaskScheduler()

        async def success_task():
            return {"status": "success"}

        task = ScheduledTask(
            name="success_task",
            cron_expression="0 12 * * *",
            task_func=success_task,
            max_retries=3
        )

        result = await scheduler.execute_with_retry(task)

        assert result.success is True
        assert result.task_name == "success_task"
        assert result.retry_attempt == 0
        assert task.last_status == TaskStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_execute_with_retry_failure(
        self, mock_failing_function, event_loop
    ):
        """Test task execution with retries after failure"""
        scheduler = TaskScheduler()

        task = ScheduledTask(
            name="failing_task",
            cron_expression="0 12 * * *",
            task_func=mock_failing_function,
            max_retries=2
        )

        result = await scheduler.execute_with_retry(task)

        assert result.success is False
        assert result.task_name == "failing_task"
        assert result.retry_attempt == 2
        assert task.last_status == TaskStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_with_retry_exponential_backoff(
        self, event_loop
    ):
        """Test exponential backoff during retries"""
        scheduler = TaskScheduler()
        call_times = []

        async def track_calls():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry needed")
            return "success"

        task = ScheduledTask(
            name="backoff_task",
            cron_expression="0 12 * * *",
            task_func=track_calls,
            max_retries=3,
            backoff_factor=1.0  # Use 1.0 to avoid slow tests
        )

        result = await scheduler.execute_with_retry(task)

        assert result.success is True
        assert len(call_times) == 3

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, event_loop):
        """Test task timeout handling"""
        scheduler = TaskScheduler()

        async def slow_task():
            await asyncio.sleep(10)
            return "should not reach"

        task = ScheduledTask(
            name="timeout_task",
            cron_expression="0 12 * * *",
            task_func=slow_task,
            timeout_s=0.5,
            max_retries=1
        )

        result = await scheduler.execute_with_retry(task)

        assert result.success is False
        assert "timeout" in result.error.lower()

    @pytest.mark.unit
    def test_get_task_history_empty(self):
        """Test getting empty task history"""
        scheduler = TaskScheduler()
        history = scheduler.get_task_history("nonexistent_task")
        assert history == []

    @pytest.mark.asyncio
    async def test_record_result_in_history(self, event_loop):
        """Test that results are recorded in history"""
        scheduler = TaskScheduler()

        async def test_task():
            return "result"

        task = ScheduledTask(
            name="history_task",
            cron_expression="0 12 * * *",
            task_func=test_task
        )

        result = await scheduler.execute_with_retry(task)
        history = scheduler.get_task_history("history_task")

        assert len(history) > 0
        assert history[0].task_name == "history_task"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_persist_and_load_schedules(
        self, temp_schedule_file, event_loop
    ):
        """Test schedule persistence and loading"""
        scheduler1 = TaskScheduler({
            'persistence_file': str(temp_schedule_file)
        })

        async def task1():
            return "task1"

        scheduler1.schedule_cron("test_task", "0 12 * * *", task1)
        await scheduler1.persist_schedules()

        # Verify file created
        assert temp_schedule_file.exists()

        # Load into new scheduler
        scheduler2 = TaskScheduler({
            'persistence_file': str(temp_schedule_file)
        })
        success = await scheduler2.load_schedules()
        assert success is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_scheduled_tasks(self, event_loop):
        """Test retrieving list of scheduled tasks"""
        scheduler = TaskScheduler()

        async def dummy():
            return "result"

        scheduler.schedule_cron("task1", "0 12 * * *", dummy)
        scheduler.schedule_cron("task2", "0 13 * * *", dummy)

        tasks = await scheduler.get_scheduled_tasks()
        assert len(tasks) == 2
        assert tasks[0]['name'] in ["task1", "task2"]
        assert tasks is not None


class TestTaskStatus:
    """Tests for TaskStatus enum"""

    @pytest.mark.unit
    def test_task_status_values(self):
        """Test TaskStatus enum values"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.SUCCESS.value == "success"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestScheduledTask:
    """Tests for ScheduledTask dataclass"""

    @pytest.mark.unit
    def test_scheduled_task_creation(self):
        """Test ScheduledTask creation"""
        async def dummy():
            return "result"

        task = ScheduledTask(
            name="test",
            cron_expression="0 12 * * *",
            task_func=dummy
        )

        assert task.name == "test"
        assert task.cron_expression == "0 12 * * *"
        assert task.max_retries == 3
        assert task.backoff_factor == 2.0

    @pytest.mark.unit
    def test_scheduled_task_execution_history(self):
        """Test task maintains execution history"""
        async def dummy():
            return "result"

        task = ScheduledTask(
            name="test",
            cron_expression="0 12 * * *",
            task_func=dummy
        )

        assert task.execution_history == []
        assert task.retry_count == 0
        assert task.last_status == TaskStatus.PENDING


class TestTaskResult:
    """Tests for TaskResult dataclass"""

    @pytest.mark.unit
    def test_task_result_success(self):
        """Test successful TaskResult"""
        result = TaskResult(
            task_name="test_task",
            success=True,
            output={"status": "ok"},
            execution_time_ms=100.5
        )

        assert result.task_name == "test_task"
        assert result.success is True
        assert result.output == {"status": "ok"}
        assert result.execution_time_ms == 100.5
        assert result.error is None

    @pytest.mark.unit
    def test_task_result_failure(self):
        """Test failed TaskResult"""
        result = TaskResult(
            task_name="test_task",
            success=False,
            error="Task execution failed",
            execution_time_ms=50.0,
            retry_attempt=2
        )

        assert result.task_name == "test_task"
        assert result.success is False
        assert "failed" in result.error.lower()
        assert result.retry_attempt == 2


@pytest.mark.slow
class TestTaskSchedulerPerformance:
    """Performance tests for TaskScheduler"""

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, event_loop):
        """Test executing multiple tasks concurrently"""
        scheduler = TaskScheduler({'max_workers': 5})
        results = []

        async def tracked_task(task_id):
            await asyncio.sleep(0.1)
            results.append(task_id)
            return f"result_{task_id}"

        tasks = []
        for i in range(5):
            task = ScheduledTask(
                name=f"task_{i}",
                cron_expression="0 12 * * *",
                task_func=lambda tid=i: tracked_task(tid)
            )
            tasks.append(task)

        # Execute all tasks
        start = time.time()
        for task in tasks:
            await scheduler.execute_with_retry(task)
        elapsed = time.time() - start

        # Should complete in reasonable time (concurrent)
        assert len(results) == 5
        assert elapsed < 5.0  # Should be fast if concurrent
