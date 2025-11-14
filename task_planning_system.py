#!/usr/bin/env python3
"""Task Planning & Execution System"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from utils.ultron_logger import log_info, log_ai_decision

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    def __init__(self, description: str, task_type: str = "general", priority: int = 1):
        self.id = str(uuid.uuid4())
        self.description = description
        self.task_type = task_type
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.subtasks = []
        self.dependencies = []
        self.result = None
        self.error = None
        self.progress = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "dependencies": self.dependencies,
            "result": self.result,
            "error": self.error,
            "progress": self.progress
        }

class TaskPlanner:
    def __init__(self):
        self.tasks = {}
        self.execution_history = []
    
    def create_task(self, description: str, task_type: str = "general", priority: int = 1) -> Task:
        """Create a new task"""
        task = Task(description, task_type, priority)
        self.tasks[task.id] = task
        log_info("task_planner", f"Created task: {description}")
        return task
    
    def break_down_task(self, task_id: str, subtask_descriptions: List[str]) -> List[Task]:
        """Break down a complex task into subtasks"""
        parent_task = self.tasks.get(task_id)
        if not parent_task:
            return []
        
        subtasks = []
        for desc in subtask_descriptions:
            subtask = Task(desc, parent_task.task_type, parent_task.priority)
            subtasks.append(subtask)
            parent_task.subtasks.append(subtask)
            self.tasks[subtask.id] = subtask
        
        log_info("task_planner", f"Broke down task {task_id} into {len(subtasks)} subtasks")
        return subtasks
    
    def add_dependency(self, task_id: str, dependency_id: str):
        """Add dependency between tasks"""
        task = self.tasks.get(task_id)
        if task and dependency_id in self.tasks:
            task.dependencies.append(dependency_id)
            log_info("task_planner", f"Added dependency: {task_id} depends on {dependency_id}")
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (no pending dependencies)"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_met = all(
                    self.tasks.get(dep_id, Task("")).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if dependencies_met:
                    ready_tasks.append(task)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        return ready_tasks
    
    def start_task(self, task_id: str):
        """Mark task as started"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            log_ai_decision("task_planner", f"Started task: {task.description}", ai_model="task_planner")
    
    def complete_task(self, task_id: str, result: Any = None):
        """Mark task as completed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 1.0
            
            # Add to execution history
            self.execution_history.append({
                "task_id": task_id,
                "description": task.description,
                "completed_at": task.completed_at.isoformat(),
                "result": result
            })
            
            log_info("task_planner", f"Completed task: {task.description}")
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            log_info("task_planner", f"Failed task: {task.description} - {error}")
    
    def update_progress(self, task_id: str, progress: float):
        """Update task progress (0.0 to 1.0)"""
        task = self.tasks.get(task_id)
        if task:
            task.progress = max(0.0, min(1.0, progress))
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get overall workflow status"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        in_progress_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "ready_tasks": len(self.get_ready_tasks())
        }

class WorkflowExecutor:
    def __init__(self, planner: TaskPlanner):
        self.planner = planner
        self.rollback_stack = []
    
    async def execute_workflow(self, workflow_description: str) -> Dict[str, Any]:
        """Execute a complete workflow"""
        log_info("workflow_executor", f"Starting workflow: {workflow_description}")
        
        # Simple workflow breakdown (in production, use LLM for this)
        subtasks = self._break_down_workflow(workflow_description)
        
        # Create main task
        main_task = self.planner.create_task(workflow_description, "workflow", priority=5)
        
        # Create subtasks
        subtask_objects = self.planner.break_down_task(main_task.id, subtasks)
        
        # Execute subtasks in order
        results = []
        for subtask in subtask_objects:
            try:
                self.planner.start_task(subtask.id)
                
                # Simulate task execution
                result = await self._execute_single_task(subtask)
                
                self.planner.complete_task(subtask.id, result)
                results.append(result)
                
                # Add to rollback stack
                self.rollback_stack.append({
                    "task_id": subtask.id,
                    "action": "complete",
                    "result": result
                })
                
            except Exception as e:
                self.planner.fail_task(subtask.id, str(e))
                log_info("workflow_executor", f"Task failed: {subtask.description} - {e}")
                
                # Rollback on failure
                await self._rollback_workflow()
                return {
                    "success": False,
                    "error": str(e),
                    "completed_subtasks": len(results),
                    "total_subtasks": len(subtask_objects)
                }
        
        # Complete main task
        self.planner.complete_task(main_task.id, results)
        
        return {
            "success": True,
            "main_task_id": main_task.id,
            "subtasks_completed": len(results),
            "results": results
        }
    
    def _break_down_workflow(self, description: str) -> List[str]:
        """Break down workflow into subtasks"""
        # Simple rule-based breakdown
        if "research" in description.lower():
            return [
                "Identify research topics",
                "Gather information",
                "Analyze findings",
                "Compile report"
            ]
        elif "code" in description.lower():
            return [
                "Analyze requirements",
                "Design solution",
                "Implement code",
                "Test functionality"
            ]
        else:
            return [
                "Analyze task requirements",
                "Execute main task",
                "Verify results"
            ]
    
    async def _execute_single_task(self, task: Task) -> str:
        """Execute a single task"""
        # Simulate task execution
        import asyncio
        await asyncio.sleep(0.1)  # Simulate work
        
        return f"Task '{task.description}' completed successfully"
    
    async def _rollback_workflow(self):
        """Rollback workflow changes"""
        log_info("workflow_executor", "Rolling back workflow changes")
        
        while self.rollback_stack:
            rollback_item = self.rollback_stack.pop()
            task_id = rollback_item["task_id"]
            
            # Mark task as cancelled
            task = self.planner.tasks.get(task_id)
            if task:
                task.status = TaskStatus.CANCELLED
        
        log_info("workflow_executor", "Rollback completed")

# Global instances
task_planner = TaskPlanner()
workflow_executor = WorkflowExecutor(task_planner)