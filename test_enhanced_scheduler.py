#!/usr/bin/env python3
"""
Test script for EnhancedTaskScheduler
"""
import asyncio
import sys
import os

# Add the utils directory to the path
os.chdir(os.path.join(os.path.dirname(__file__), 'utils'))

from enhanced_task_scheduler import (
    EnhancedTaskScheduler,
    TaskPriority,
    TaskResource,
    TaskDependency
)

def mock_command_handler(command: str) -> str:
    """Mock command handler for testing."""
    print(f"Executing command: {command}")
    return f"Executed: {command}"

async def test_enhanced_scheduler():
    """Test the enhanced task scheduler."""
    print("Testing EnhancedTaskScheduler...")

    # Initialize scheduler
    scheduler = EnhancedTaskScheduler()

    # Register command handler
    scheduler.register_command_handler(mock_command_handler)

    # Create a task group
    scheduler.create_task_group("test_group", "Test Group", max_concurrent=3)

    # Create resource requirements
    resources = TaskResource(cpu_percent=10, memory_mb=100)

    # Create dependencies
    dependencies = [
        TaskDependency("task1", "completion")
    ]

    # Schedule tasks
    print("\n1. Scheduling tasks...")

    # Schedule a simple task
    success1 = scheduler.schedule_enhanced_task(
        "task1",
        "echo 'Hello World'",
        {"type": "interval", "interval": {"minutes": 1}},
        priority=TaskPriority.HIGH,
        group_id="test_group",
        resource_requirements=resources,
        description="Simple echo task"
    )
    print(f"Task 1 scheduled: {success1}")

    # Schedule a dependent task
    success2 = scheduler.schedule_enhanced_task(
        "task2",
        "echo 'Dependent task'",
        {"type": "interval", "interval": {"minutes": 2}},
        priority=TaskPriority.NORMAL,
        dependencies=dependencies,
        description="Task dependent on task1"
    )
    print(f"Task 2 scheduled: {success2}")

    # Schedule a high-priority task
    success3 = scheduler.schedule_enhanced_task(
        "task3",
        "echo 'High priority task'",
        {"type": "interval", "interval": {"minutes": 1}},
        priority=TaskPriority.CRITICAL,
        description="Critical priority task"
    )
    print(f"Task 3 scheduled: {success3}")

    # Test analytics
    print("\n2. Testing analytics...")
    analytics = scheduler.get_scheduler_analytics()
    print("Scheduler Analytics:")
    print(f"  - Total tasks: {analytics['total_tasks']}")
    print(f"  - Running tasks: {analytics['running_tasks']}")
    print(f"  - Health score: {analytics['scheduler_health_score']}")

    # Test task workflow
    print("\n3. Testing task workflow...")
    workflow = scheduler.get_task_workflow("task2")
    print(f"Task 2 workflow: {len(workflow.get('dependencies', []))} dependencies")

    # Test task cancellation
    print("\n4. Testing task cancellation...")
    cancel_result = scheduler.cancel_task("task1")
    print(f"Task 1 cancelled: {cancel_result}")

    print("\n✅ EnhancedTaskScheduler test completed!")

if __name__ == "__main__":
    try:
    asyncio.run(test_enhanced_scheduler())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
