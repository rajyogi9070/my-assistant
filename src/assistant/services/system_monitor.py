"""
System monitoring service
"""
import logging
import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from assistant.core.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System metrics data"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    timestamp: float = 0.0


class SystemMonitor:
    """Monitor system resources and health"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.metrics = SystemMetrics()
        self.update_interval = 5.0  # seconds
        
        logger.info("System monitor initialized")
    
    def start(self) -> None:
        """Start monitoring"""
        logger.info("Starting system monitor...")
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop monitoring"""
        logger.info("Stopping system monitor...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                self._update_metrics()
                
                # Emit metrics event
                self.event_bus.emit("system_metrics_updated", {
                    "cpu_percent": self.metrics.cpu_percent,
                    "memory_percent": self.metrics.memory_percent,
                    "memory_used_gb": self.metrics.memory_used_gb,
                    "memory_total_gb": self.metrics.memory_total_gb,
                    "disk_percent": self.metrics.disk_percent,
                    "disk_free_gb": self.metrics.disk_free_gb,
                    "battery_percent": self.metrics.battery_percent,
                    "battery_plugged": self.metrics.battery_plugged,
                    "timestamp": self.metrics.timestamp
                })
                
                # Check for warnings
                self._check_warnings()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in system monitor: {e}", exc_info=True)
                time.sleep(self.update_interval)
    
    def _update_metrics(self) -> None:
        """Update system metrics"""
        try:
            import psutil
            
            # CPU
            self.metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            self.metrics.memory_percent = memory.percent
            self.metrics.memory_used_gb = memory.used / (1024**3)
            self.metrics.memory_total_gb = memory.total / (1024**3)
            
            # Disk
            disk = psutil.disk_usage('/')
            self.metrics.disk_percent = disk.percent
            self.metrics.disk_free_gb = disk.free / (1024**3)
            
            # Battery
            battery = psutil.sensors_battery()
            if battery:
                self.metrics.battery_percent = battery.percent
                self.metrics.battery_plugged = battery.power_plugged
            
            # Network
            net_io = psutil.net_io_counters()
            self.metrics.network_sent_mb = net_io.bytes_sent / (1024**2)
            self.metrics.network_recv_mb = net_io.bytes_recv / (1024**2)
            
            self.metrics.timestamp = time.time()
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def _check_warnings(self) -> None:
        """Check for system warnings"""
        # High CPU usage
        if self.metrics.cpu_percent > 90:
            self.event_bus.emit("system_warning", {
                "type": "high_cpu",
                "message": f"High CPU usage: {self.metrics.cpu_percent}%"
            })
        
        # High memory usage
        if self.metrics.memory_percent > 90:
            self.event_bus.emit("system_warning", {
                "type": "high_memory",
                "message": f"High memory usage: {self.metrics.memory_percent}%"
            })
        
        # Low disk space
        if self.metrics.disk_percent > 90:
            self.event_bus.emit("system_warning", {
                "type": "low_disk",
                "message": f"Low disk space: {self.metrics.disk_free_gb:.1f} GB free"
            })
        
        # Low battery
        if (self.metrics.battery_percent is not None and 
            self.metrics.battery_percent < 20 and 
            not self.metrics.battery_plugged):
            self.event_bus.emit("system_warning", {
                "type": "low_battery",
                "message": f"Low battery: {self.metrics.battery_percent}%"
            })
    
    def get_metrics(self) -> SystemMetrics:
        """Get current metrics"""
        return self.metrics
    
    def get_cpu_percent(self) -> float:
        """Get CPU usage percentage"""
        return self.metrics.cpu_percent
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        return {
            "percent": self.metrics.memory_percent,
            "used_gb": self.metrics.memory_used_gb,
            "total_gb": self.metrics.memory_total_gb
        }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        return {
            "percent": self.metrics.disk_percent,
            "free_gb": self.metrics.disk_free_gb
        }
    
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Get battery information"""
        if self.metrics.battery_percent is not None:
            return {
                "percent": self.metrics.battery_percent,
                "plugged": self.metrics.battery_plugged
            }
        return None
