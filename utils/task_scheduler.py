import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
import logging
import json
from pathlib import Path

class TaskScheduler:
    def __init__(self, save_file: str = "scheduled_tasks.json"):
        self.tasks: Dict[str, Dict] = {}
        self.save_file = Path(save_file)
        self.running = False
        self._load_tasks()

    def _load_tasks(self):
        """Load scheduled tasks from file."""
        try:
            if self.save_file.exists():
                with open(self.save_file, 'r') as f:
                    saved_tasks = json.load(f)
                for task_id, task in saved_tasks.items():
                    # Convert stored datetime strings back to datetime objects
                    if task.get('next_run'):
                        task['next_run'] = datetime.fromisoformat(task['next_run'])
                    self.tasks[task_id] = task
                logging.info(f"Loaded {len(self.tasks)} scheduled tasks - task_scheduler.py:26")
        except Exception as e:
            logging.error(f"Error loading scheduled tasks: {e} - task_scheduler.py:28")

    def _save_tasks(self):
        """Save scheduled tasks to file."""
        try:
            tasks_to_save = {}
            for task_id, task in self.tasks.items():
                task_copy = task.copy()
                # Convert datetime objects to ISO format strings for JSON serialization
                if task_copy.get('next_run'):
                    task_copy['next_run'] = task_copy['next_run'].isoformat()
                tasks_to_save[task_id] = task_copy
            
            with open(self.save_file, 'w') as f:
                json.dump(tasks_to_save, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving scheduled tasks: {e} - task_scheduler.py:44")

    def schedule_task(self, task_id: str, command: str, schedule: Dict[str, Any], description: str = "") -> bool:
        """Schedule a new task."""
        try:
            if task_id in self.tasks:
                return False

            task = {
                'command': command,
                'schedule': schedule,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'last_run': None,
                'next_run': self._calculate_next_run(schedule),
                'enabled': True,
                'runs': 0,
                'failures': 0,
                'last_error': None
            }
            
            self.tasks[task_id] = task
            self._save_tasks()
            logging.info(f"Scheduled new task: {task_id} - task_scheduler.py:67")
            return True
        except Exception as e:
            logging.error(f"Error scheduling task {task_id}: {e} - task_scheduler.py:70")
            return False

    def _calculate_next_run(self, schedule: Dict[str, Any]) -> Optional[datetime]:
        """Calculate the next run time based on schedule configuration."""
        try:
            now = datetime.now()
            if schedule.get('type') == 'interval':
                interval = timedelta(**schedule['interval'])
                return now + interval
            elif schedule.get('type') == 'daily':
                time = schedule['time']
                next_run = now.replace(
                    hour=time['hour'],
                    minute=time.get('minute', 0),
                    second=time.get('second', 0)
                )
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
            elif schedule.get('type') == 'weekly':
                days = schedule['days']
                time = schedule['time']
                next_run = now
                while next_run.weekday() not in days:
                    next_run += timedelta(days=1)
                next_run = next_run.replace(
                    hour=time['hour'],
                    minute=time.get('minute', 0),
                    second=time.get('second', 0)
                )
                if next_run <= now:
                    next_run += timedelta(days=1)
                    while next_run.weekday() not in days:
                        next_run += timedelta(days=1)
                return next_run
            elif schedule.get('type') == 'monthly':
                time = schedule['time']
                day = schedule.get('day', 1)
                next_run = now.replace(
                    day=day,
                    hour=time['hour'],
                    minute=time.get('minute', 0),
                    second=time.get('second', 0)
                )
                if next_run <= now:
                    # Move to next month
                    if next_run.month == 12:
                        next_run = next_run.replace(year=next_run.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=next_run.month + 1)
                return next_run
            elif schedule.get('type') == 'cron':
                # Basic cron-like scheduling
                cron = schedule['cron']
                return self._calculate_cron_next_run(cron, now)
            elif schedule.get('type') == 'conditional':
                # Conditional scheduling based on system state
                condition = schedule['condition']
                return self._calculate_conditional_next_run(condition, now)
        except Exception as e:
            logging.error(f"Error calculating next run time: {e} - task_scheduler.py:130")
            return None

    def _calculate_cron_next_run(self, cron_expr: str, now: datetime) -> Optional[datetime]:
        """Calculate next run time based on cron expression (basic implementation)."""
        try:
            # Basic cron: minute hour day month weekday
            parts = cron_expr.split()
            if len(parts) != 5:
                return None
            
            minute, hour, day, month, weekday = parts
            
            next_run = now.replace(second=0, microsecond=0)
            
            # Simple implementation - full cron would be more complex
            if minute != '*':
                next_run = next_run.replace(minute=int(minute))
            if hour != '*':
                next_run = next_run.replace(hour=int(hour))
            
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        except Exception as e:
            logging.error(f"Error parsing cron expression {cron_expr}: {e}")
            return None

    def _calculate_conditional_next_run(self, condition: Dict, now: datetime) -> Optional[datetime]:
        """Calculate next run based on system conditions."""
        try:
            # Check conditions like CPU usage, memory usage, etc.
            check_interval = condition.get('check_interval', {'minutes': 5})
            return now + timedelta(**check_interval)
        except Exception as e:
            logging.error(f"Error calculating conditional run time: {e}")
            return None

    def get_task_analytics(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analytics for a specific task."""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Calculate success rate
        total_runs = task.get('runs', 0)
        failures = task.get('failures', 0)
        success_rate = ((total_runs - failures) / total_runs * 100) if total_runs > 0 else 0
        
        # Get execution history statistics
        history = task.get('execution_history', [])
        if history:
            durations = [h['duration'] for h in history if 'duration' in h]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
        else:
            avg_duration = min_duration = max_duration = 0
        
        # Calculate reliability score (based on success rate and consistency)
        reliability_score = success_rate * 0.7 + (100 - (max_duration - min_duration) / max(avg_duration, 1) * 100) * 0.3
        
        return {
            'task_id': task_id,
            'total_runs': total_runs,
            'failures': failures,
            'success_rate': round(success_rate, 2),
            'reliability_score': round(reliability_score, 2),
            'avg_execution_time': round(avg_duration, 3),
            'min_execution_time': round(min_duration, 3),
            'max_execution_time': round(max_duration, 3),
            'last_run': task.get('last_run'),
            'next_run': task.get('next_run').isoformat() if task.get('next_run') else None,
            'enabled': task.get('enabled', True),
            'error_history': task.get('error_history', []),
            'execution_trend': self._calculate_execution_trend(history)
        }

    def _calculate_execution_trend(self, history: List[Dict]) -> str:
        """Calculate execution time trend."""
        if len(history) < 3:
            return "insufficient_data"
        
        recent = history[-5:]  # Last 5 executions
        older = history[-10:-5] if len(history) >= 10 else history[:-5]
        
        if not older:
            return "insufficient_data"
        
        recent_avg = sum(h.get('duration', 0) for h in recent) / len(recent)
        older_avg = sum(h.get('duration', 0) for h in older) / len(older)
        
        if recent_avg > older_avg * 1.1:
            return "degrading"
        elif recent_avg < older_avg * 0.9:
            return "improving"
        else:
            return "stable"

    def get_system_analytics(self) -> Dict[str, Any]:
        """Get overall system task analytics."""
        total_tasks = len(self.tasks)
        enabled_tasks = sum(1 for t in self.tasks.values() if t.get('enabled', True))
        total_runs = sum(t.get('runs', 0) for t in self.tasks.values())
        total_failures = sum(t.get('failures', 0) for t in self.tasks.values())
        
        # Calculate system health score
        if total_runs > 0:
            system_success_rate = ((total_runs - total_failures) / total_runs) * 100
        else:
            system_success_rate = 100
        
        # Get task performance distribution
        performance_levels = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        for task_id in self.tasks:
            analytics = self.get_task_analytics(task_id)
            if analytics:
                score = analytics['reliability_score']
                if score >= 90:
                    performance_levels['excellent'] += 1
                elif score >= 70:
                    performance_levels['good'] += 1
                elif score >= 50:
                    performance_levels['fair'] += 1
                else:
                    performance_levels['poor'] += 1
        
        return {
            'total_tasks': total_tasks,
            'enabled_tasks': enabled_tasks,
            'disabled_tasks': total_tasks - enabled_tasks,
            'total_runs': total_runs,
            'total_failures': total_failures,
            'system_success_rate': round(system_success_rate, 2),
            'performance_distribution': performance_levels,
            'system_health_score': round(system_success_rate * 0.8 + (enabled_tasks / max(total_tasks, 1)) * 20, 2)
        }

    async def start(self):
        """Start the task scheduler."""
        self.running = True
        while self.running:
            try:
                now = datetime.now()
                for task_id, task in self.tasks.items():
                    if (task['enabled'] and task['next_run'] 
                        and task['next_run'] <= now):
                        await self._execute_task(task_id)
                        
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error in task scheduler main loop: {e} - task_scheduler.py:123")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the task scheduler."""
        self.running = False
        self._save_tasks()

    def register_command_handler(self, handler: Callable[[str], Any]):
        """Register a command handler function that will execute task commands."""
        self.command_handler = handler
        logging.info("Command handler registered with TaskScheduler - task_scheduler.py:134")

    async def _execute_task(self, task_id: str):
        """Execute a scheduled task with full integration."""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        start_time = datetime.now()
        
        try:
            # Execute the command through the registered handler
            if hasattr(self, 'command_handler'):
                logging.info(f"Executing task {task_id}: {task['command']} - task_scheduler.py:147")
                
                if asyncio.iscoroutinefunction(self.command_handler):
                    result = await self.command_handler(task['command'])
                else:
                    result = self.command_handler(task['command'])
                
                # Update task metrics
                task['last_run'] = start_time.isoformat()
                task['runs'] += 1
                task['next_run'] = self._calculate_next_run(task['schedule'])
                task['last_error'] = None
                task['last_result'] = str(result)
                task['last_execution_time'] = (datetime.now() - start_time).total_seconds()
                
                # Update task statistics
                if 'statistics' not in task:
                    task['statistics'] = {
                        'avg_execution_time': task['last_execution_time'],
                        'min_execution_time': task['last_execution_time'],
                        'max_execution_time': task['last_execution_time'],
                        'total_execution_time': task['last_execution_time']
                    }
                else:
                    stats = task['statistics']
                    n = task['runs']
                    execution_time = task['last_execution_time']
                    
                    # Update running average
                    stats['avg_execution_time'] = (stats['avg_execution_time'] * (n-1) + execution_time) / n
                    stats['min_execution_time'] = min(stats['min_execution_time'], execution_time)
                    stats['max_execution_time'] = max(stats['max_execution_time'], execution_time)
                    stats['total_execution_time'] += execution_time
                
            else:
                raise RuntimeError("No command handler registered")
            
        except Exception as e:
            task['failures'] += 1
            task['last_error'] = str(e)
            task['last_error_time'] = datetime.now().isoformat()
            
            # Update error statistics
            if 'error_history' not in task:
                task['error_history'] = []
            
            task['error_history'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'command': task['command']
            })
            
            # Keep only last 10 errors
            task['error_history'] = task['error_history'][-10:]
            
            logging.error(f"Error executing task {task_id}: {e} - task_scheduler.py:202")
        
        finally:
            # Update task execution history
            if 'execution_history' not in task:
                task['execution_history'] = []
            
            task['execution_history'].append({
                'timestamp': start_time.isoformat(),
                'duration': (datetime.now() - start_time).total_seconds(),
                'success': 'last_error' not in task or task['last_error'] is None,
                'error': task.get('last_error'),
                'result': task.get('last_result', '')
            })
            
            # Keep only last 10 executions
            task['execution_history'] = task['execution_history'][-10:]
            
            # Save task state
            self._save_tasks()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task details by ID."""
        return self.tasks.get(task_id)

    def list_tasks(self) -> List[Dict]:
        """List all scheduled tasks."""
        return [{'id': k, **v} for k, v in self.tasks.items()]

    def enable_task(self, task_id: str) -> bool:
        """Enable a task."""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = True
            self._save_tasks()
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """Disable a task."""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = False
            self._save_tasks()
            return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False

    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update task configuration."""
        if task_id not in self.tasks:
            return False
        
        try:
            task = self.tasks[task_id]
            for key, value in updates.items():
                if key == 'schedule':
                    task['next_run'] = self._calculate_next_run(value)
                task[key] = value
            
            self._save_tasks()
            return True
        except Exception as e:
            logging.error(f"Error updating task {task_id}: {e} - task_scheduler.py:270")
            return False
