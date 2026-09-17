"""
Main assistant application UI
"""
import logging
import threading
import customtkinter as ctk
from typing import Optional
from PIL import Image, ImageDraw
import os

from assistant.core.config import ConfigManager, AssistantConfig
from assistant.core.engine import AssistantEngine, AssistantState
from assistant.core.event_bus import Event
from assistant.ui.components.dashboard import DashboardFrame
from assistant.ui.components.chat_frame import ChatFrame
from assistant.ui.components.settings_frame import SettingsFrame
from assistant.ui.components.sidebar import Sidebar

logger = logging.getLogger(__name__)


# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AssistantApp:
    """Main assistant application window"""
    
    def __init__(self):
        # Initialize config
        self.config = ConfigManager()
        
        # Set appearance mode
        appearance = self.config.config.ui.theme
        ctk.set_appearance_mode(appearance)
        
        # Create main window
        self.window = ctk.CTk()
        self.window.title("My Assistant")
        self.window.geometry(
            f"{self.config.config.ui.window_width}x{self.config.config.ui.window_height}"
        )
        self.window.minsize(900, 600)
        
        # Configure grid layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Initialize engine in background
        self.engine: Optional[AssistantEngine] = None
        self._init_engine_background()
        
        # Create UI components
        self._create_ui()
        
        # Register event handlers
        self._register_handlers()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.info("UI initialized")
    
    def _init_engine_background(self):
        """Initialize engine in background thread"""
        def init():
            try:
                self.engine = AssistantEngine(self.config)
                logger.info("Engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize engine: {e}")
        
        thread = threading.Thread(target=init, daemon=True)
        thread.start()
    
    def _create_ui(self):
        """Create UI components"""
        # Sidebar
        self.sidebar = Sidebar(
            self.window,
            command=self._on_sidebar_select
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create frames
        self.frames = {}
        
        # Dashboard (default)
        self.frames["dashboard"] = DashboardFrame(self.content_frame, self)
        self.frames["dashboard"].grid(row=0, column=0, sticky="nsew")
        
        # Chat
        self.frames["chat"] = ChatFrame(self.content_frame, self)
        
        # Settings
        self.frames["settings"] = SettingsFrame(self.content_frame, self)
        
        # Show dashboard by default
        self.current_frame = "dashboard"
    
    def _register_handlers(self):
        """Register event handlers"""
        if self.engine:
            self.engine.event_bus.on("state_changed", self._on_state_changed)
            self.engine.event_bus.on("speech_recognized", self._on_speech_recognized)
            self.engine.event_bus.on("command_executed", self._on_command_executed)
            self.engine.event_bus.on("system_metrics_updated", self._on_metrics_updated)
    
    def _on_sidebar_select(self, selection: str):
        """Handle sidebar selection"""
        logger.info(f"Sidebar selection: {selection}")
        
        # Hide current frame
        if self.current_frame in self.frames:
            self.frames[self.current_frame].grid_forget()
        
        # Show selected frame
        if selection in self.frames:
            self.frames[selection].grid(row=0, column=0, sticky="nsew")
            self.current_frame = selection
        elif selection == "chat":
            self.frames["chat"].grid(row=0, column=0, sticky="nsew")
            self.current_frame = "chat"
        elif selection == "settings":
            self.frames["settings"].grid(row=0, column=0, sticky="nsew")
            self.current_frame = "settings"
    
    def _on_state_changed(self, event: Event):
        """Handle assistant state changes"""
        state = event.data.get("state", "IDLE")
        self.window.after(0, lambda: self.sidebar.update_state(state))
    
    def _on_speech_recognized(self, event: Event):
        """Handle speech recognition"""
        text = event.data.get("text", "")
        if self.current_frame == "chat":
            self.window.after(0, lambda: self.frames["chat"].add_user_message(text))
    
    def _on_command_executed(self, event: Event):
        """Handle command execution"""
        response = event.data.get("response", "")
        success = event.data.get("success", False)
        
        if response and self.current_frame == "chat":
            self.window.after(0, lambda: self.frames["chat"].add_assistant_message(response))
    
    def _on_metrics_updated(self, event: Event):
        """Handle system metrics updates"""
        if self.current_frame == "dashboard":
            self.window.after(0, lambda: self.frames["dashboard"].update_metrics(event.data))
    
    def _on_close(self):
        """Handle window close"""
        logger.info("Closing application...")
        
        # Save window position
        self.config.config.ui.window_width = self.window.winfo_width()
        self.config.config.ui.window_height = self.window.winfo_height()
        self.config.save()
        
        # Stop engine
        if self.engine:
            self.engine.stop()
        
        self.window.destroy()
    
    def run(self):
        """Run the application"""
        logger.info("Starting UI main loop...")
        self.window.mainloop()
    
    def process_command(self, text: str):
        """Process a text command"""
        if self.engine:
            self.engine.process_text(text)
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.config.config.ui.theme = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.config.config.ui.theme = "dark"
        self.config.save()
