"""
Command dispatcher - routes intents to handlers
"""
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass

from assistant.core.event_bus import EventBus
from assistant.engines.nlp.intent import Intent, IntentMatch
from assistant.commands.system.system_commands import SystemCommands
from assistant.commands.apps.app_commands import AppCommands
from assistant.commands.web.web_commands import WebCommands
from assistant.commands.files.file_commands import FileCommands
from assistant.commands.media.media_commands import MediaCommands
from assistant.commands.productivity.productivity_commands import ProductivityCommands

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Any = None
    error: Optional[str] = None


class CommandDispatcher:
    """Dispatches intents to appropriate command handlers"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Initialize command handlers
        self.system_commands = SystemCommands(event_bus)
        self.app_commands = AppCommands(event_bus)
        self.web_commands = WebCommands(event_bus)
        self.file_commands = FileCommands(event_bus)
        self.media_commands = MediaCommands(event_bus)
        self.productivity_commands = ProductivityCommands(event_bus)
        
        # Map intents to handlers
        self.handlers: Dict[Intent, Callable] = {
            # System commands
            Intent.SHUTDOWN: self.system_commands.shutdown,
            Intent.RESTART: self.system_commands.restart,
            Intent.SLEEP: self.system_commands.sleep,
            Intent.LOCK: self.system_commands.lock,
            Intent.LOGOUT: self.system_commands.logout,
            
            # App commands
            Intent.OPEN_APP: self.app_commands.open_app,
            Intent.CLOSE_APP: self.app_commands.close_app,
            Intent.SWITCH_APP: self.app_commands.switch_app,
            
            # Web commands
            Intent.SEARCH_WEB: self.web_commands.search,
            Intent.OPEN_WEBSITE: self.web_commands.open_website,
            Intent.OPEN_YOUTUBE: self.web_commands.open_youtube,
            
            # File commands
            Intent.CREATE_FOLDER: self.file_commands.create_folder,
            Intent.OPEN_FILE: self.file_commands.open_file,
            Intent.MOVE_FILE: self.file_commands.move_file,
            Intent.DELETE_FILE: self.file_commands.delete_file,
            
            # Media commands
            Intent.PLAY_MUSIC: self.media_commands.play,
            Intent.PAUSE_MEDIA: self.media_commands.pause,
            Intent.RESUME_MEDIA: self.media_commands.resume,
            Intent.NEXT_TRACK: self.media_commands.next_track,
            Intent.PREVIOUS_TRACK: self.media_commands.previous_track,
            Intent.VOLUME_UP: self.media_commands.volume_up,
            Intent.VOLUME_DOWN: self.media_commands.volume_down,
            Intent.MUTE: self.media_commands.mute,
            Intent.UNMUTE: self.media_commands.unmute,
            
            # Display commands
            Intent.SET_BRIGHTNESS: self.system_commands.set_brightness,
            Intent.INCREASE_BRIGHTNESS: self.system_commands.increase_brightness,
            Intent.DECREASE_BRIGHTNESS: self.system_commands.decrease_brightness,
            
            # System info
            Intent.CHECK_BATTERY: self.system_commands.check_battery,
            Intent.CHECK_CPU: self.system_commands.check_cpu,
            Intent.CHECK_RAM: self.system_commands.check_ram,
            Intent.CHECK_DISK: self.system_commands.check_disk,
            Intent.SYSTEM_INFO: self.system_commands.system_info,
            
            # Productivity
            Intent.TAKE_SCREENSHOT: self.productivity_command.take_screenshot,
            Intent.RECORD_SCREEN: self.productivity_commands.record_screen,
            Intent.SET_TIMER: self.productivity_commands.set_timer,
            Intent.SET_ALARM: self.productivity_commands.set_alarm,
            Intent.SET_REMINDER: self.productivity_commands.set_reminder,
            Intent.CREATE_NOTE: self.productivity_commands.create_note,
            
            # Communication
            Intent.SEND_EMAIL: self.productivity_commands.send_email,
            Intent.READ_EMAIL: self.productivity_commands.read_email,
            
            # Settings
            Intent.OPEN_SETTINGS: self.system_commands.open_settings,
        }
        
        logger.info(f"Command dispatcher initialized with {len(self.handlers)} handlers")
    
    def dispatch(self, intent: str, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Dispatch intent to appropriate handler"""
        try:
            # Convert string intent to enum
            intent_enum = Intent(intent)
            
            logger.info(f"Dispatching intent: {intent} with entities: {entities}")
            
            # Get handler
            handler = self.handlers.get(intent_enum)
            
            if not handler:
                logger.warning(f"No handler for intent: {intent}")
                result = CommandResult(
                    success=False,
                    message=f"I don't know how to handle that command yet.",
                    error="No handler registered"
                )
            else:
                # Execute handler
                result = handler(entities, context)
            
            # Emit result event
            self.event_bus.emit("command_executed", {
                "intent": intent,
                "entities": entities,
                "success": result.success,
                "response": result.message,
                "result": result.data,
                "error": result.error
            })
            
            return result
            
        except ValueError as e:
            logger.error(f"Invalid intent: {intent}")
            result = CommandResult(
                success=False,
                message="I don't understand that command.",
                error=str(e)
            )
            self.event_bus.emit("command_executed", {
                "intent": intent,
                "success": False,
                "response": result.message,
                "error": str(e)
            })
            return result
            
        except Exception as e:
            logger.error(f"Error dispatching command: {e}", exc_info=True)
            result = CommandResult(
                success=False,
                message="Sorry, an error occurred while executing that command.",
                error=str(e)
            )
            self.event_bus.emit("error", {
                "error": str(e),
                "component": "command_dispatcher"
            })
            return result
    
    def register_handler(self, intent: Intent, handler: Callable) -> None:
        """Register custom command handler"""
        self.handlers[intent] = handler
        logger.info(f"Registered custom handler for intent: {intent.value}")
    
    def get_available_commands(self) -> list:
        """Get list of available commands"""
        return [intent.value for intent in self.handlers.keys()]
