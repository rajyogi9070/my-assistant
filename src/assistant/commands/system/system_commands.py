"""
System control commands - shutdown, restart, settings, etc.
"""
import logging
import platform
import os
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class SystemCommands(BaseCommandHandler):
    """System control command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
    
    def shutdown(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Shutdown the computer"""
        try:
            logger.info("Executing shutdown command")
            
            # Confirmation required
            self.event_bus.emit("confirmation_required", {
                "action": "shutdown",
                "message": "Are you sure you want to shut down the computer?"
            })
            
            # Execute shutdown
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("shutdown -h now")
            
            return CommandResult(
                success=True,
                message="Shutting down the computer in 5 seconds."
            )
            
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to shut down the computer.",
                error=str(e)
            )
    
    def restart(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Restart the computer"""
        try:
            logger.info("Executing restart command")
            
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("reboot")
            
            return CommandResult(
                success=True,
                message="Restarting the computer in 5 seconds."
            )
            
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to restart the computer.",
                error=str(e)
            )
    
    def sleep(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Put computer to sleep"""
        try:
            logger.info("Executing sleep command")
            
            if platform.system() == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                os.system("systemctl suspend")
            
            return CommandResult(
                success=True,
                message="Putting the computer to sleep."
            )
            
        except Exception as e:
            logger.error(f"Sleep failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to put computer to sleep.",
                error=str(e)
            )
    
    def lock(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Lock the computer"""
        try:
            logger.info("Executing lock command")
            
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            else:
                os.system("loginctl lock-session")
            
            return CommandResult(
                success=True,
                message="Locking the computer."
            )
            
        except Exception as e:
            logger.error(f"Lock failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to lock the computer.",
                error=str(e)
            )
    
    def logout(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Log out current user"""
        try:
            logger.info("Executing logout command")
            
            if platform.system() == "Windows":
                os.system("shutdown /l")
            else:
                os.system("loginctl terminate-user $USER")
            
            return CommandResult(
                success=True,
                message="Logging out."
            )
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to log out.",
                error=str(e)
            )
    
    def set_brightness(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Set screen brightness"""
        try:
            brightness = entities.get("brightness_value", 50)
            logger.info(f"Setting brightness to {brightness}%")
            
            # Try to use screen_brightness_control
            try:
                import screen_brightness_control as sbc
                sbc.set_brightness(brightness)
                
                return CommandResult(
                    success=True,
                    message=f"Brightness set to {brightness}%."
                )
            except ImportError:
                # Fallback to Windows WMI
                if platform.system() == "Windows":
                    import wmi
                    c = wmi.WMI(namespace='wmi')
                    methods = c.WmiMonitorBrightnessMethods()[0]
                    methods.WmiSetBrightness(brightness, 0)
                    
                    return CommandResult(
                        success=True,
                        message=f"Brightness set to {brightness}%."
                    )
            
            return CommandResult(
                success=False,
                message="Unable to control brightness on this system."
            )
            
        except Exception as e:
            logger.error(f"Set brightness failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to set brightness.",
                error=str(e)
            )
    
    def increase_brightness(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Increase screen brightness"""
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            new_brightness = min(100, current + 10)
            sbc.set_brightness(new_brightness)
            
            return CommandResult(
                success=True,
                message=f"Brightness increased to {new_brightness}%."
            )
            
        except Exception as e:
            logger.error(f"Increase brightness failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to increase brightness.",
                error=str(e)
            )
    
    def decrease_brightness(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Decrease screen brightness"""
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            new_brightness = max(0, current - 10)
            sbc.set_brightness(new_brightness)
            
            return CommandResult(
                success=True,
                message=f"Brightness decreased to {new_brightness}%."
            )
            
        except Exception as e:
            logger.error(f"Decrease brightness failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to decrease brightness.",
                error=str(e)
            )
    
    def check_battery(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Check battery status"""
        try:
            import psutil
            
            battery = psutil.sensors_battery()
            
            if battery is None:
                return CommandResult(
                    success=True,
                    message="No battery detected. This device is plugged in."
                )
            
            percent = battery.percent
            plugged = battery.power_plugged
            secsleft = battery.secsleft
            
            message = f"Battery is at {percent}%."
            if plugged:
                message += " It's currently charging."
            elif secsleft > 0:
                hours = secsleft // 3600
                minutes = (secsleft % 3600) // 60
                message += f" About {hours} hours and {minutes} minutes remaining."
            
            return CommandResult(
                success=True,
                message=message,
                data={
                    "percent": percent,
                    "plugged": plugged,
                    "secsleft": secsleft
                }
            )
            
        except Exception as e:
            logger.error(f"Check battery failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to check battery status.",
                error=str(e)
            )
    
    def check_cpu(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Check CPU usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            return CommandResult(
                success=True,
                message=f"CPU usage is at {cpu_percent}% with {cpu_count} cores.",
                data={
                    "percent": cpu_percent,
                    "cores": cpu_count
                }
            )
            
        except Exception as e:
            logger.error(f"Check CPU failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to check CPU status.",
                error=str(e)
            )
    
    def check_ram(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Check RAM usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            used_gb = memory.used / (1024**3)
            percent = memory.percent
            
            return CommandResult(
                success=True,
                message=f"RAM usage is at {percent}%. Using {used_gb:.1f} GB out of {total_gb:.1f} GB.",
                data={
                    "percent": percent,
                    "used_gb": used_gb,
                    "total_gb": total_gb
                }
            )
            
        except Exception as e:
            logger.error(f"Check RAM failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to check RAM status.",
                error=str(e)
            )
    
    def check_disk(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Check disk usage"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
            free_gb = disk.free / (1024**3)
            percent = disk.percent
            
            return CommandResult(
                success=True,
                message=f"Disk usage is at {percent}%. {free_gb:.1f} GB free out of {total_gb:.1f} GB.",
                data={
                    "percent": percent,
                    "used_gb": used_gb,
                    "free_gb": free_gb,
                    "total_gb": total_gb
                }
            )
            
        except Exception as e:
            logger.error(f"Check disk failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to check disk status.",
                error=str(e)
            )
    
    def system_info(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Get system information"""
        try:
            import psutil
            import platform
            
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            }
            
            message = f"Running {info['system']} {info['release']} on {info['processor']} with {info['cpu_count']} cores and {info['memory_total_gb']:.1f} GB RAM."
            
            return CommandResult(
                success=True,
                message=message,
                data=info
            )
            
        except Exception as e:
            logger.error(f"System info failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to get system information.",
                error=str(e)
            )
    
    def open_settings(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Open system settings"""
        try:
            if platform.system() == "Windows":
                os.startfile("ms-settings:")
            else:
                os.system("gnome-control-center")
            
            return CommandResult(
                success=True,
                message="Opening settings."
            )
            
        except Exception as e:
            logger.error(f"Open settings failed: {e}")
            return CommandResult(
                success=False,
                message="Failed to open settings.",
                error=str(e)
            )
