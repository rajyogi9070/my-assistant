"""
Event bus for component communication
"""
import logging
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from threading import Lock
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event data structure"""
    name: str
    data: Dict[str, Any]
    source: str = "system"
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            import time
            self.timestamp = time.time()


class EventBus:
    """Central event bus for decoupled component communication"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        self._async_loop: asyncio.AbstractEventLoop = None
    
    def on(self, event_name: str, handler: Callable) -> None:
        """Register event handler"""
        with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(handler)
            logger.debug(f"Registered handler for event: {event_name}")
    
    def off(self, event_name: str, handler: Callable = None) -> None:
        """Unregister event handler"""
        with self._lock:
            if event_name in self._handlers:
                if handler is None:
                    # Remove all handlers for this event
                    del self._handlers[event_name]
                else:
                    # Remove specific handler
                    self._handlers[event_name] = [
                        h for h in self._handlers[event_name] if h != handler
                    ]
                logger.debug(f"Unregistered handler for event: {event_name}")
    
    def emit(self, event_name: str, data: Dict[str, Any] = None, source: str = "system") -> None:
        """Emit event to all registered handlers"""
        if data is None:
            data = {}
        
        event = Event(name=event_name, data=data, source=source)
        
        with self._lock:
            handlers = self._handlers.get(event_name, []).copy()
        
        for handler in handlers:
            try:
                # Check if handler is async
                if asyncio.iscoroutinefunction(handler):
                    # Schedule async handler
                    if self._async_loop and self._async_loop.is_running():
                        asyncio.run_coroutine_threadsafe(handler(event), self._async_loop)
                    else:
                        logger.warning(f"No async loop available for handler: {handler}")
                else:
                    # Call sync handler
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler} for {event_name}: {e}", exc_info=True)
    
    async def emit_async(self, event_name: str, data: Dict[str, Any] = None, source: str = "system") -> None:
        """Emit event asynchronously"""
        if data is None:
            data = {}
        
        event = Event(name=event_name, data=data, source=source)
        
        with self._lock:
            handlers = self._handlers.get(event_name, []).copy()
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in async event handler {handler} for {event_name}: {e}", exc_info=True)
    
    def once(self, event_name: str, handler: Callable) -> None:
        """Register one-time event handler"""
        def wrapper(event: Event):
            self.off(event_name, wrapper)
            handler(event)
        
        self.on(event_name, wrapper)
    
    def set_async_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set async event loop for async handlers"""
        self._async_loop = loop
    
    def clear(self) -> None:
        """Clear all event handlers"""
        with self._lock:
            self._handlers.clear()
        logger.info("All event handlers cleared")
    
    def get_registered_events(self) -> List[str]:
        """Get list of registered event names"""
        with self._lock:
            return list(self._handlers.keys())
