"""
Dashboard frame - main overview
"""
import logging
import customtkinter as ctk
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DashboardFrame(ctk.CTkFrame):
    """Dashboard showing system metrics and quick actions"""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Greeting
        self.greeting_label = ctk.CTkLabel(
            self,
            text="Hello! How can I help you today?",
            font=ctk.CTkFont(size=16)
        )
        self.greeting_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="w")
        
        # Metrics cards
        self._create_metrics_cards()
        
        # Quick actions
        self._create_quick_actions()
    
    def _create_metrics_cards(self):
        """Create system metrics cards"""
        # CPU Card
        self.cpu_card = self._create_metric_card(
            row=2, col=0,
            title="CPU Usage",
            icon="💻",
            value="0%"
        )
        
        # Memory Card
        self.memory_card = self._create_metric_card(
            row=2, col=1,
            title="Memory",
            icon="🧠",
            value="0%"
        )
        
        # Disk Card
        self.disk_card = self._create_metric_card(
            row=2, col=2,
            title="Disk Space",
            icon="💾",
            value="0 GB"
        )
        
        # Battery Card
        self.battery_card = self._create_metric_card(
            row=3, col=0,
            title="Battery",
            icon="🔋",
            value="N/A"
        )
        
        # Network Card
        self.network_card = self._create_metric_card(
            row=3, col=1,
            title="Network",
            icon="🌐",
            value="0 MB"
        )
        
        # Uptime Card
        self.uptime_card = self._create_metric_card(
            row=3, col=2,
            title="Uptime",
            icon="⏱️",
            value="0h"
        )
    
    def _create_metric_card(self, row: int, col: int, title: str, icon: str, value: str):
        """Create a metric card"""
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Icon and title
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=(10, 0))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack(padx=15, pady=(5, 15))
        
        return {"card": card, "value_label": value_label}
    
    def _create_quick_actions(self):
        """Create quick action buttons"""
        actions_frame = ctk.CTkFrame(self, corner_radius=10)
        actions_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=15, pady=(15, 10), anchor="w")
        
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        actions = [
            ("📸", "Screenshot"),
            ("🔍", "Search"),
            ("📝", "Note"),
            ("⏰", "Timer"),
            ("🎵", "Music"),
        ]
        
        for i, (icon, text) in enumerate(actions):
            btn = ctk.CTkButton(
                buttons_frame,
                text=f"{icon} {text}",
                width=120,
                height=40,
                command=lambda t=text: self._quick_action(t)
            )
            btn.pack(side="left", padx=5, pady=5)
    
    def _quick_action(self, action: str):
        """Handle quick action"""
        logger.info(f"Quick action: {action}")
        
        action_commands = {
            "Screenshot": "take a screenshot",
            "Search": "search the web",
            "Note": "create a note",
            "Timer": "set a timer",
            "Music": "play music",
        }
        
        command = action_commands.get(action, action.lower())
        self.app.process_command(command)
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update metrics display"""
        try:
            # CPU
            cpu = metrics.get("cpu_percent", 0)
            self.cpu_card["value_label"].configure(text=f"{cpu:.1f}%")
            
            # Memory
            memory = metrics.get("memory_percent", 0)
            memory_used = metrics.get("memory_used_gb", 0)
            self.memory_card["value_label"].configure(text=f"{memory:.1f}%")
            
            # Disk
            disk_free = metrics.get("disk_free_gb", 0)
            self.disk_card["value_label"].configure(text=f"{disk_free:.1f} GB")
            
            # Battery
            battery = metrics.get("battery_percent")
            if battery is not None:
                plugged = metrics.get("battery_plugged", False)
                icon = "🔌" if plugged else "🔋"
                self.battery_card["value_label"].configure(text=f"{battery:.0f}%")
            else:
                self.battery_card["value_label"].configure(text="N/A")
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
