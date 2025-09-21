#!/usr/bin/env python3
"""
Simple test for EnhancedTaskScheduler
"""
import asyncio
from enhanced_task_scheduler import EnhancedTaskScheduler, TaskPriority, TaskResource

def mock_handler(command: str) -> str:
    """Mock command handler."""
    return f"Executed: {command}"

async def test_basic():
    """Basic test of enhanced scheduler."""
    print("Testing EnhancedTaskScheduler...")

    scheduler = EnhancedTaskScheduler()
    scheduler.register_command_handler(mock_handler)

    # Create task group
    scheduler.create_task_group("test", "Test Group")

    # Schedule a task
    resources = TaskResource(cpu_percent=5, memory_mb=50)
    success = scheduler.schedule_enhanced_task(
        "test_task",
        "echo hello",
        {"type": "interval", "interval": {"minutes": 1}},
        priority=TaskPriority.HIGH,
        group_id="test",
        resource_requirements=resources
    )

    print(f"Task scheduled: {success}")

    # Get analytics
    analytics = scheduler.get_scheduler_analytics()
    print(f"Total tasks: {analytics['total_tasks']}")
    print(f"Health score: {analytics['scheduler_health_score']}")

    print("✅ Enhanced scheduler test completed!")

if __name__ == "__main__":
    asyncio.run(test_basic())