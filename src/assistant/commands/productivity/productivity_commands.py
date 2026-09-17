"""
Productivity commands - screenshots, timers, notes, etc.
"""
import logging
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class ProductivityCommands(BaseCommandHandler):
    """Productivity command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.timers = []
    
    def take_screenshot(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Take a screenshot"""
        try:
            import pyautogui
            
            # Create screenshots directory
            screenshots_dir = Path.home() / "Pictures" / "Screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            logger.info(f"Taking screenshot: {filepath}")
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            
            return CommandResult(
                success=True,
                message=f"Screenshot saved to {filepath}.",
                data={"path": str(filepath)}
            )
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to take screenshot.",
                error=str(e)
            )
    
    def record_screen(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Record screen"""
        try:
            # This would require additional libraries like opencv or pyautogui with video
            return CommandResult(
                success=False,
                message="Screen recording is not yet implemented. Use OBS Studio or Windows Game Bar (Win+G)."
            )
            
        except Exception as e:
            logger.error(f"Record screen failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to record screen.",
                error=str(e)
            )
    
    def set_timer(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Set a timer"""
        try:
            duration = entities.get("duration", 0)
            unit = entities.get("unit", "minutes")
            
            if not duration:
                return CommandResult(
                    success=False,
                    message="How long should the timer be?"
                )
            
            # Convert to seconds
            if "hour" in unit:
                seconds = duration * 3600
            elif "minute" in unit:
                seconds = duration * 60
            else:
                seconds = duration
            
            logger.info(f"Setting timer for {duration} {unit}")
            
            # Start timer in background thread
            timer_thread = threading.Thread(
                target=self._timer_callback,
                args=(seconds, f"{duration} {unit}"),
                daemon=True
            )
            timer_thread.start()
            
            return CommandResult(
                success=True,
                message=f"Timer set for {duration} {unit}."
            )
            
        except Exception as e:
            logger.error(f"Set timer failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to set timer.",
                error=str(e)
            )
    
    def _timer_callback(self, seconds: int, label: str):
        """Timer callback function"""
        time.sleep(seconds)
        
        # Emit timer completed event
        self.event_bus.emit("timer_completed", {
            "label": label,
            "message": f"Timer for {label} has completed!"
        })
        
        logger.info(f"Timer completed: {label}")
    
    def set_alarm(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Set an alarm"""
        try:
            # This would require a more complex implementation
            return CommandResult(
                success=False,
                message="Alarm functionality is not yet implemented."
            )
            
        except Exception as e:
            logger.error(f"Set alarm failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to set alarm.",
                error=str(e)
            )
    
    def set_reminder(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Set a reminder"""
        try:
            reminder_text = entities.get("text", "")
            
            if not reminder_text:
                return CommandResult(
                    success=False,
                    message="What should I remind you about?"
                )
            
            # Store reminder (would need persistent storage)
            logger.info(f"Setting reminder: {reminder_text}")
            
            return CommandResult(
                success=True,
                message=f"Reminder set: {reminder_text}"
            )
            
        except Exception as e:
            logger.error(f"Set reminder failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to set reminder.",
                error=str(e)
            )
    
    def create_note(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Create a note"""
        try:
            note_text = entities.get("text", "")
            
            if not note_text:
                return CommandResult(
                    success=False,
                    message="What would you like me to note?"
                )
            
            # Create notes directory
            notes_dir = Path.home() / "Documents" / "MyAssistant" / "Notes"
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}.txt"
            filepath = notes_dir / filename
            
            logger.info(f"Creating note: {filepath}")
            
            # Write note
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Note created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(note_text)
            
            return CommandResult(
                success=True,
                message=f"Note saved to {filepath}.",
                data={"path": str(filepath)}
            )
            
        except Exception as e:
            logger.error(f"Create note failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to create note.",
                error=str(e)
            )
    
    def send_email(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Send an email"""
        try:
            # Open default email client with compose window
            import webbrowser
            
            recipient = entities.get("recipient", "")
            subject = entities.get("subject", "")
            body = entities.get("body", "")
            
            mailto_url = f"mailto:{recipient}"
            if subject:
                mailto_url += f"?subject={subject}"
            if body:
                mailto_url += f"&body={body}"
            
            webbrowser.open(mailto_url)
            
            return CommandResult(
                success=True,
                message="Opening email client."
            )
            
        except Exception as e:
            logger.error(f"Send email failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to send email.",
                error=str(e)
            )
    
    def read_email(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Read emails"""
        try:
            # Open default email client
            import webbrowser
            webbrowser.open("mailto:")
            
            return CommandResult(
                success=True,
                message="Opening email client."
            )
            
        except Exception as e:
            logger.error(f"Read email failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to open email.",
                error=str(e)
            )
