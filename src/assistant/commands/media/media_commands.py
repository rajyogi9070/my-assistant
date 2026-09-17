"""
Media control commands
"""
import logging
import platform
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class MediaCommands(BaseCommandHandler):
    """Media control command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
    
    def play(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Play media"""
        try:
            import pyautogui
            pyautogui.press('playpause')
            
            return CommandResult(
                success=True,
                message="Playing media."
            )
            
        except Exception as e:
            logger.error(f"Play failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to play media.",
                error=str(e)
            )
    
    def pause(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Pause media"""
        try:
            import pyautogui
            pyautogui.press('playpause')
            
            return CommandResult(
                success=True,
                message="Paused media."
            )
            
        except Exception as e:
            logger.error(f"Pause failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to pause media.",
                error=str(e)
            )
    
    def resume(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Resume media"""
        return self.play(entities, context)
    
    def next_track(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Next track"""
        try:
            import pyautogui
            pyautogui.press('nexttrack')
            
            return CommandResult(
                success=True,
                message="Skipping to next track."
            )
            
        except Exception as e:
            logger.error(f"Next track failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to skip to next track.",
                error=str(e)
            )
    
    def previous_track(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Previous track"""
        try:
            import pyautogui
            pyautogui.press('prevtrack')
            
            return CommandResult(
                success=True,
                message="Going to previous track."
            )
            
        except Exception as e:
            logger.error(f"Previous track failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to go to previous track.",
                error=str(e)
            )
    
    def volume_up(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Increase volume"""
        try:
            import pyautogui
            
            # Press volume up key multiple times
            for _ in range(5):
                pyautogui.press('volumeup')
            
            return CommandResult(
                success=True,
                message="Volume increased."
            )
            
        except Exception as e:
            logger.error(f"Volume up failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to increase volume.",
                error=str(e)
            )
    
    def volume_down(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Decrease volume"""
        try:
            import pyautogui
            
            # Press volume down key multiple times
            for _ in range(5):
                pyautogui.press('volumedown')
            
            return CommandResult(
                success=True,
                message="Volume decreased."
            )
            
        except Exception as e:
            logger.error(f"Volume down failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to decrease volume.",
                error=str(e)
            )
    
    def mute(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Mute audio"""
        try:
            import pyautogui
            pyautogui.press('volumemute')
            
            return CommandResult(
                success=True,
                message="Audio muted."
            )
            
        except Exception as e:
            logger.error(f"Mute failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to mute audio.",
                error=str(e)
            )
    
    def unmute(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Unmute audio"""
        try:
            import pyautogui
            pyautogui.press('volumemute')
            
            return CommandResult(
                success=True,
                message="Audio unmuted."
            )
            
        except Exception as e:
            logger.error(f"Unmute failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to unmute audio.",
                error=str(e)
            )
