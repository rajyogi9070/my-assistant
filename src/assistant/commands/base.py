"""
Base command handler class
"""
from typing import Dict, Any
from dataclasses import dataclass
from abc import ABC

from assistant.core.event_bus import EventBus


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Any = None
    error: str = None


class BaseCommandHandler(ABC):
    """Base class for all command handlers"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
