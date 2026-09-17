"""
Notification management system
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from assistant.core.event_bus import EventBus
from assistant.core.config import ConfigManager

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class Notification:
    """Notification data"""
    id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    timestamp: str = ""
    read: bool = False
    action: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class NotificationManager:
    """Manages notifications and alerts"""
    
    def __init__(self, config: ConfigManager, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.notifications: List[Notification] = []
        self.max_notifications = 100
        self.do_not_disturb = False
        
        # Register event handlers
        self.event_bus.on("timer_completed", self._on_timer_completed)
        self.event_bus.on("system_warning", self._on_system_warning)
        
        logger.info("Notification manager initialized")
    
    def notify(self, title: str, message: str, priority: NotificationPriority = NotificationPriority.NORMAL,
               action: Optional[Dict[str, Any]] = None) -> str:
        """Create a notification"""
        if self.do_not_disturb and priority != NotificationPriority.CRITICAL:
            logger.debug("Notification suppressed (DND mode)")
            return ""
        
        notification = Notification(
            id=f"notif_{len(self.notifications)}_{datetime.now().timestamp()}",
            title=title,
            message=message,
            priority=priority,
            action=action
        )
        
        self.notifications.append(notification)
        
        # Trim old notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        logger.info(f"Notification: {title} - {message}")
        
        # Emit event
        self.event_bus.emit("notification_created", {
            "id": notification.id,
            "title": title,
            "message": message,
            "priority": priority.name
        })
        
        # Try to show system notification
        self._show_system_notification(notification)
        
        return notification.id
    
    def _show_system_notification(self, notification: Notification) -> None:
        """Show system notification"""
        try:
            # Try plyer for cross-platform notifications
            from plyer import notification as plyer_notif
            
            plyer_notif.notify(
                title=notification.title,
                message=notification.message,
                app_name="My Assistant",
                timeout=10
            )
            
        except ImportError:
            logger.debug("plyer not available for system notifications")
        except Exception as e:
            logger.error(f"Failed to show system notification: {e}")
    
    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """Get notifications"""
        if unread_only:
            return [n for n in self.notifications if not n.read]
        return self.notifications.copy()
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.read = True
                return True
        return False
    
    def mark_all_as_read(self) -> None:
        """Mark all notifications as read"""
        for notif in self.notifications:
            notif.read = True
    
    def clear_all(self) -> None:
        """Clear all notifications"""
        self.notifications.clear()
        logger.info("All notifications cleared")
    
    def delete(self, notification_id: str) -> bool:
        """Delete a notification"""
        for i, notif in enumerate(self.notifications):
            if notif.id == notification_id:
                del self.notifications[i]
                return True
        return False
    
    def set_do_not_disturb(self, enabled: bool) -> None:
        """Set do not disturb mode"""
        self.do_not_disturb = enabled
        logger.info(f"Do not disturb: {enabled}")
    
    def _on_timer_completed(self, event: Any) -> None:
        """Handle timer completion"""
        label = event.data.get("label", "Timer")
        message = event.data.get("message", "Timer completed!")
        
        self.notify(
            title="⏰ Timer Completed",
            message=message,
            priority=NotificationPriority.HIGH
        )
    
    def _on_system_warning(self, event: Any) -> None:
        """Handle system warnings"""
        warning_type = event.data.get("type", "warning")
        message = event.data.get("message", "System warning")
        
        self.notify(
            title="⚠️ System Warning",
            message=message,
            priority=NotificationPriority.HIGH
        )
