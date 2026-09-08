"""
Scheduler for UltronSysAgent
Handles task scheduling, reminders, and automated workflows
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

from ...core.event_bus import EventBus, EventTypes

@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    id: str
    name: str
    description: str
    command: str
    schedule_type: str  # 'once', 'recurring', 'interval'
    schedule_data: Dict[str, Any]  # Contains schedule-specific data
    enabled: bool = True
    created_at: str = None
    last_run: str = None
    next_run: str = None
    run_count: int = 0
    max_runs: int = None

class Scheduler:
    """Task scheduler and automation module"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Database for persistent task storage
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "scheduler"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "scheduler.db"
        self.db_connection = None
        
        # In-memory task storage
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Scheduler state
        self.is_running = False
        self.scheduler_task = None
        
        # Initialize storage
        self._initialize_database()
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _initialize_database(self):
        """Initialize SQLite database for task persistence"""
        try:
            self.db_connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.db_connection.row_factory = sqlite3.Row
            
            cursor = self.db_connection.cursor()
            
            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    command TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    schedule_data TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_run TEXT,
                    next_run TEXT,
                    run_count INTEGER DEFAULT 0,
                    max_runs INTEGER
                )
            ''')
            
            # Create task history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    execution_time TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    output TEXT,
                    error TEXT,
                    duration REAL
                )
            ''')
            
            self.db_connection.commit()
            
            # Load existing tasks
            self._load_tasks_from_database()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler database: {e}")
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        pass  # Scheduler is primarily self-managing
    
    async def start(self):
        """Start the scheduler"""
        self.logger.info("⏰ Starting Scheduler...")
        
        self.is_running = True
        
        # Start main scheduler loop
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "scheduler"}, 
                                    source="scheduler")
    
    async def stop(self):
        """Stop the scheduler"""
        self.logger.info("⏰ Stopping Scheduler...")
        
        self.is_running = False
        
        # Cancel scheduler task
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running tasks
        for task_id, task in self.running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.running_tasks.clear()
        
        # Close database
        if self.db_connection:
            self.db_connection.close()
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "scheduler"}, 
                                    source="scheduler")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check for tasks that need to run
                await self._check_and_run_tasks()
                
                # Wait before next check (check every 10 seconds)
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_and_run_tasks(self):
        """Check for tasks that need to run and execute them"""
        current_time = datetime.now()
        
        for task_id, task in self.tasks.items():
            if not task.enabled:
                continue
            
            # Check if task should run
            if await self._should_task_run(task, current_time):
                # Don't run if already running
                if task_id not in self.running_tasks:
                    self.logger.info(f"⚡ Running scheduled task: {task.name}")
                    
                    # Create and start task
                    run_task = asyncio.create_task(self._execute_task(task))
                    self.running_tasks[task_id] = run_task
                    
                    # Update next run time
                    task.next_run = self._calculate_next_run(task).isoformat()
                    self._save_task_to_database(task)
    
    async def _should_task_run(self, task: ScheduledTask, current_time: datetime) -> bool:
        """Check if a task should run at the current time"""
        try:
            # Check max runs limit
            if task.max_runs and task.run_count >= task.max_runs:
                return False
            
            # Check next run time
            if task.next_run:
                next_run = datetime.fromisoformat(task.next_run)
                if current_time < next_run:
                    return False
            
            # Check schedule type specific conditions
            if task.schedule_type == 'once':
                return task.run_count == 0
            
            elif task.schedule_type == 'interval':
                interval_seconds = task.schedule_data.get('interval_seconds', 3600)
                if task.last_run:
                    last_run = datetime.fromisoformat(task.last_run)
                    return (current_time - last_run).total_seconds() >= interval_seconds
                else:
                    return True
            
            elif task.schedule_type == 'recurring':
                # Implement cron-like scheduling
                return self._check_recurring_schedule(task, current_time)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if task should run: {e}")
            return False
    
    def _check_recurring_schedule(self, task: ScheduledTask, current_time: datetime) -> bool:
        """Check if recurring task should run"""
        try:
            schedule_data = task.schedule_data
            
            # Simple recurring schedule check
            if 'hour' in schedule_data and 'minute' in schedule_data:
                target_hour = schedule_data['hour']
                target_minute = schedule_data['minute']
                
                # Check if current time matches target time
                if (current_time.hour == target_hour and 
                    current_time.minute == target_minute):
                    
                    # Check if already ran today
                    if task.last_run:
                        last_run = datetime.fromisoformat(task.last_run)
                        if last_run.date() == current_time.date():
                            return False
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking recurring schedule: {e}")
            return False
    
    def _calculate_next_run(self, task: ScheduledTask) -> datetime:
        """Calculate the next run time for a task"""
        try:
            current_time = datetime.now()
            
            if task.schedule_type == 'once':
                return current_time + timedelta(years=10)  # Far future for one-time tasks
            
            elif task.schedule_type == 'interval':
                interval_seconds = task.schedule_data.get('interval_seconds', 3600)
                return current_time + timedelta(seconds=interval_seconds)
            
            elif task.schedule_type == 'recurring':
                # Calculate next daily occurrence
                schedule_data = task.schedule_data
                if 'hour' in schedule_data and 'minute' in schedule_data:
                    next_run = current_time.replace(
                        hour=schedule_data['hour'],
                        minute=schedule_data['minute'],
                        second=0,
                        microsecond=0
                    )
                    
                    # If time has passed today, schedule for tomorrow
                    if next_run <= current_time:
                        next_run += timedelta(days=1)
                    
                    return next_run
            
            return current_time + timedelta(hours=1)  # Default fallback
            
        except Exception as e:
            self.logger.error(f"Error calculating next run: {e}")
            return datetime.now() + timedelta(hours=1)
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        start_time = datetime.now()
        success = False
        output = ""
        error = ""
        
        try:
            # Update task run info
            task.last_run = start_time.isoformat()
            task.run_count += 1
            
            # Execute the command
            if task.command.startswith('system:'):
                # System command
                command = task.command[7:]  # Remove 'system:' prefix
                result = await self._execute_system_command(command)
                success = result.get('success', False)
                output = result.get('output', '')
                error = result.get('error', '')
                
            elif task.command.startswith('event:'):
                # Event publishing
                event_data = json.loads(task.command[6:])  # Remove 'event:' prefix
                await self.event_bus.publish(
                    event_data['type'],
                    event_data.get('data', {}),
                    source="scheduler"
                )
                success = True
                output = f"Published event: {event_data['type']}"
                
            else:
                # Default: treat as system command
                result = await self._execute_system_command(task.command)
                success = result.get('success', False)
                output = result.get('output', '')
                error = result.get('error', '')
            
            if success:
                self.logger.info(f"✅ Task '{task.name}' completed successfully")
            else:
                self.logger.warning(f"⚠️ Task '{task.name}' failed: {error}")
            
        except Exception as e:
            error = str(e)
            self.logger.error(f"❌ Error executing task '{task.name}': {e}")
        
        finally:
            # Record execution in history
            duration = (datetime.now() - start_time).total_seconds()
            
            await self._record_task_execution(
                task.id, start_time, success, output, error, duration
            )
            
            # Update task in database
            self._save_task_to_database(task)
            
            # Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def _execute_system_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command"""
        try:
            # Use the system automation module through events
            await self.event_bus.publish(EventTypes.SYSTEM_COMMAND, 
                                       {
                                           "user_input": f"scheduled: {command}",
                                           "ai_response": f"execute: {command}",
                                           "requires_admin": False
                                       }, 
                                       source="scheduler")
            
            return {
                "success": True,
                "output": f"Command scheduled for execution: {command}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_task(self, name: str, description: str, command: str, 
                         schedule_type: str, schedule_data: Dict[str, Any], 
                         max_runs: int = None) -> str:
        """Create a new scheduled task"""
        try:
            import uuid
            
            task_id = str(uuid.uuid4())
            
            task = ScheduledTask(
                id=task_id,
                name=name,
                description=description,
                command=command,
                schedule_type=schedule_type,
                schedule_data=schedule_data,
                created_at=datetime.now().isoformat(),
                max_runs=max_runs
            )
            
            # Calculate initial next run time
            task.next_run = self._calculate_next_run(task).isoformat()
            
            # Store task
            self.tasks[task_id] = task
            self._save_task_to_database(task)
            
            self.logger.info(f"✅ Created scheduled task: {name}")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a scheduled task"""
        try:
            if task_id not in self.tasks:
                return False
            
            # Cancel if running
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
            
            # Remove from memory and database
            del self.tasks[task_id]
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
            self.db_connection.commit()
            
            self.logger.info(f"✅ Deleted scheduled task: {task_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting task: {e}")
            return False
    
    async def enable_task(self, task_id: str, enabled: bool = True) -> bool:
        """Enable or disable a task"""
        try:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id].enabled = enabled
            self._save_task_to_database(self.tasks[task_id])
            
            status = "enabled" if enabled else "disabled"
            self.logger.info(f"Task {task_id} {status}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling/disabling task: {e}")
            return False
    
    def _load_tasks_from_database(self):
        """Load tasks from database into memory"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM scheduled_tasks")
            
            for row in cursor.fetchall():
                task = ScheduledTask(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    command=row['command'],
                    schedule_type=row['schedule_type'],
                    schedule_data=json.loads(row['schedule_data']),
                    enabled=bool(row['enabled']),
                    created_at=row['created_at'],
                    last_run=row['last_run'],
                    next_run=row['next_run'],
                    run_count=row['run_count'],
                    max_runs=row['max_runs']
                )
                
                self.tasks[task.id] = task
            
            self.logger.info(f"Loaded {len(self.tasks)} scheduled tasks")
            
        except Exception as e:
            self.logger.error(f"Error loading tasks from database: {e}")
    
    def _save_task_to_database(self, task: ScheduledTask):
        """Save task to database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO scheduled_tasks 
                (id, name, description, command, schedule_type, schedule_data, 
                 enabled, created_at, last_run, next_run, run_count, max_runs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id, task.name, task.description, task.command,
                task.schedule_type, json.dumps(task.schedule_data),
                task.enabled, task.created_at, task.last_run,
                task.next_run, task.run_count, task.max_runs
            ))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving task to database: {e}")
    
    async def _record_task_execution(self, task_id: str, execution_time: datetime, 
                                   success: bool, output: str, error: str, duration: float):
        """Record task execution in history"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO task_history 
                (task_id, execution_time, success, output, error, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_id, execution_time.isoformat(), success,
                output, error, duration
            ))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error recording task execution: {e}")
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all scheduled tasks"""
        return [asdict(task) for task in self.tasks.values()]
    
    def get_task_history(self, task_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task execution history"""
        try:
            cursor = self.db_connection.cursor()
            
            if task_id:
                cursor.execute('''
                    SELECT * FROM task_history 
                    WHERE task_id = ? 
                    ORDER BY execution_time DESC 
                    LIMIT ?
                ''', (task_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM task_history 
                    ORDER BY execution_time DESC 
                    LIMIT ?
                ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row['id'],
                    'task_id': row['task_id'],
                    'execution_time': row['execution_time'],
                    'success': bool(row['success']),
                    'output': row['output'],
                    'error': row['error'],
                    'duration': row['duration']
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting task history: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.is_running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": len([t for t in self.tasks.values() if t.enabled]),
            "running_tasks": len(self.running_tasks),
            "next_tasks": self._get_next_tasks(5)
        }
    
    def _get_next_tasks(self, limit: int) -> List[Dict[str, Any]]:
        """Get next tasks to run"""
        try:
            next_tasks = []
            
            for task in self.tasks.values():
                if task.enabled and task.next_run:
                    next_tasks.append({
                        'id': task.id,
                        'name': task.name,
                        'next_run': task.next_run
                    })
            
            # Sort by next run time
            next_tasks.sort(key=lambda x: x['next_run'])
            
            return next_tasks[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting next tasks: {e}")
            return []
