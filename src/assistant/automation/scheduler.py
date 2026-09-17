"""
Task scheduling and automation
"""
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import schedule

from assistant.core.event_bus import EventBus
from assistant.core.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    id: str
    name: str
    action: str
    schedule_type: str  # daily, weekly, hourly, once
    schedule_time: str
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    parameters: Dict[str, Any] = None


class TaskScheduler:
    """Manages scheduled tasks and automation"""
    
    def __init__(self, config: ConfigManager, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        logger.info("Task scheduler initialized")
    
    def start(self) -> None:
        """Start the scheduler"""
        logger.info("Starting task scheduler...")
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler"""
        logger.info("Stopping task scheduler...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(5)
    
    def add_task(self, task: ScheduledTask) -> bool:
        """Add a scheduled task"""
        try:
            self.tasks[task.id] = task
            
            # Schedule based on type
            if task.schedule_type == "daily":
                schedule.every().day.at(task.schedule_time).do(
                    self._execute_task, task_id=task.id
                )
            elif task.schedule_type == "hourly":
                schedule.every().hour.do(self._execute_task, task_id=task.id)
            elif task.schedule_type == "weekly":
                schedule.every().monday.at(task.schedule_time).do(
                    self._execute_task, task_id=task.id
                )
            
            logger.info(f"Added scheduled task: {task.name}")
            
            self.event_bus.emit("task_added", {
                "id": task.id,
                "name": task.name,
                "schedule": task.schedule_type
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}", exc_info=True)
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            # Note: schedule library doesn't support removing specific jobs easily
            # Would need to clear and reschedule all
            logger.info(f"Removed task: {task_id}")
            return True
        return False
    
    def _execute_task(self, task_id: str) -> None:
        """Execute a scheduled task"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        
        if not task.enabled:
            return
        
        logger.info(f"Executing scheduled task: {task.name}")
        
        try:
            # Emit task execution event
            self.event_bus.emit("task_executed", {
                "id": task.id,
                "name": task.name,
                "action": task.action,
                "parameters": task.parameters
            })
            
            # Update last run time
            task.last_run = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.name}: {e}", exc_info=True)
    
    def get_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks"""
        return list(self.tasks.values())
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            return True
        return False
