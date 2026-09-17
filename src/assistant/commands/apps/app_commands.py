"""
Application control commands
"""
import logging
import platform
import subprocess
import os
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class AppCommands(BaseCommandHandler):
    """Application control command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        
        # Application mappings
        self.app_map = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "word": "WINWORD.EXE",
            "microsoft word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "microsoft excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "microsoft powerpoint": "POWERPNT.EXE",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "terminal": "wt.exe",
            "windows terminal": "wt.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "slack": "slack.exe",
            "teams": "teams.exe",
            "microsoft teams": "teams.exe",
            "zoom": "zoom.exe",
            "skype": "skype.exe",
            "vlc": "vlc.exe",
            "obs": "obs64.exe",
            "obs studio": "obs64.exe",
            "steam": "steam.exe",
            "vscode": "Code.exe",
            "visual studio code": "Code.exe",
            "vs code": "Code.exe",
        }
    
    def open_app(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Open an application"""
        try:
            app_name = entities.get("app_name", "").lower().strip()
            
            if not app_name:
                return CommandResult(
                    success=False,
                    message="Which application would you like me to open?"
                )
            
            logger.info(f"Opening application: {app_name}")
            
            # Check if it's in our app map
            exe_name = self.app_map.get(app_name)
            
            if platform.system() == "Windows":
                if exe_name:
                    # Try to launch from app map
                    try:
                        subprocess.Popen(exe_name, shell=True)
                        return CommandResult(
                            success=True,
                            message=f"Opening {app_name.title()}."
                        )
                    except Exception as e:
                        logger.warning(f"Failed to open {exe_name}: {e}")
                
                # Try to find in start menu
                try:
                    import pyautogui
                    pyautogui.press('win')
                    import time
                    time.sleep(0.5)
                    pyautogui.typewrite(app_name, interval=0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    
                    return CommandResult(
                        success=True,
                        message=f"Opening {app_name.title()}."
                    )
                except Exception as e:
                    logger.error(f"Failed to open app via search: {e}")
            
            else:
                # Linux/Mac
                try:
                    subprocess.Popen(app_name, shell=True)
                    return CommandResult(
                        success=True,
                        message=f"Opening {app_name.title()}."
                    )
                except Exception as e:
                    logger.error(f"Failed to open {app_name}: {e}")
            
            return CommandResult(
                success=False,
                message=f"Sorry, I couldn't find {app_name}."
            )
            
        except Exception as e:
            logger.error(f"Open app failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to open the application.",
                error=str(e)
            )
    
    def close_app(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Close an application"""
        try:
            app_name = entities.get("app_name", "").lower().strip()
            
            if not app_name:
                return CommandResult(
                    success=False,
                    message="Which application would you like me to close?"
                )
            
            logger.info(f"Closing application: {app_name}")
            
            if platform.system() == "Windows":
                # Use taskkill
                exe_name = self.app_map.get(app_name, f"{app_name}.exe")
                result = os.system(f'taskkill /f /im "{exe_name}" 2>nul')
                
                if result == 0:
                    return CommandResult(
                        success=True,
                        message=f"Closed {app_name.title()}."
                    )
                else:
                    # Try with pyautogui
                    import pyautogui
                    pyautogui.hotkey('alt', 'F4')
                    
                    return CommandResult(
                        success=True,
                        message=f"Closed the active application."
                    )
            
            else:
                # Linux/Mac
                os.system(f"pkill -f {app_name}")
                
                return CommandResult(
                    success=True,
                    message=f"Closed {app_name.title()}."
                )
            
        except Exception as e:
            logger.error(f"Close app failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to close the application.",
                error=str(e)
            )
    
    def switch_app(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Switch to another application"""
        try:
            logger.info("Switching application")
            
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            
            return CommandResult(
                success=True,
                message="Switched to the previous application."
            )
            
        except Exception as e:
            logger.error(f"Switch app failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to switch applications.",
                error=str(e)
            )
