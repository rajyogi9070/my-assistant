"""
Sidebar navigation component
"""
import logging
import customtkinter as ctk
from typing import Callable

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation"""
    
    def __init__(self, parent, command: Callable):
        super().__init__(parent, width=200, corner_radius=0)
        self.command = command
        
        self.grid_columnconfigure(0, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self,
            text="My Assistant",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Version
        self.version_label = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            text_color="gray",
            font=ctk.CTkFont(size=14)
        )
        self.status_indicator.pack(side="left", padx=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Idle",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left")
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("chat", "💬", "Chat"),
            ("settings", "⚙️", "Settings"),
        ]
        
        for i, (key, icon, text) in enumerate(nav_items, start=3):
            btn = ctk.CTkButton(
                self,
                text=f"{icon}  {text}",
                command=lambda k=key: self.command(k),
                anchor="w",
                height=40
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Spacer
        self.spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.spacer.grid(row=10, column=0, sticky="nsew")
        self.grid_rowconfigure(10, weight=1)
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(
            self,
            text="🌓  Toggle Theme",
            command=self._toggle_theme,
            height=35
        )
        self.theme_button.grid(row=11, column=0, padx=20, pady=10, sticky="ew")
        
        # Quit button
        self.quit_button = ctk.CTkButton(
            self,
            text="❌  Quit",
            command=self._quit,
            height=35,
            fg_color="darkred",
            hover_color="red"
        )
        self.quit_button.grid(row=12, column=0, padx=20, pady=(10, 20), sticky="ew")
    
    def update_state(self, state: str):
        """Update status indicator"""
        state_colors = {
            "IDLE": ("gray", "Idle"),
            "LISTENING": ("blue", "Listening..."),
            "PROCESSING": ("orange", "Processing..."),
            "SPEAKING": ("green", "Speaking..."),
            "ERROR": ("red", "Error"),
        }
        
        color, text = state_colors.get(state, ("gray", state))
        
        self.status_indicator.configure(text_color=color)
        self.status_label.configure(text=text)
    
    def _toggle_theme(self):
        """Toggle theme"""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
    
    def _quit(self):
        """Quit application"""
        self.winfo_toplevel().destroy()
