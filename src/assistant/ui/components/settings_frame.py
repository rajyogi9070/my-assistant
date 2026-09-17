"""
Settings frame
"""
import logging
import customtkinter as ctk

logger = logging.getLogger(__name__)


class SettingsFrame(ctk.CTkFrame):
    """Settings interface"""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="w")
        
        # Scrollable frame for settings
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        
        # Create settings sections
        self._create_general_settings()
        self._create_voice_settings()
        self._create_ai_settings()
        self._create_system_settings()
    
    def _create_general_settings(self):
        """General settings section"""
        section = self._create_section("General")
        
        # Theme
        self._create_option_menu(
            section,
            "Theme",
            ["Dark", "Light", "System"],
            self._on_theme_change
        )
        
        # Language
        self._create_option_menu(
            section,
            "Language",
            ["English", "Spanish", "French", "German", "Hindi"],
            None
        )
        
        # Start with Windows
        self._create_switch(
            section,
            "Start with Windows",
            False,
            None
        )
        
        # Minimize to tray
        self._create_switch(
            section,
            "Minimize to system tray",
            True,
            None
        )
    
    def _create_voice_settings(self):
        """Voice settings section"""
        section = self._create_section("Voice & Speech")
        
        # Wake word
        self._create_option_menu(
            section,
            "Wake Word",
            ["Hey Assistant", "Hello Assistant", "Custom"],
            None
        )
        
        # Voice
        self._create_option_menu(
            section,
            "Voice",
            ["Female", "Male", "Custom"],
            None
        )
        
        # Speech rate slider
        self._create_slider(
            section,
            "Speech Rate",
            0, 200, 100,
            None
        )
        
        # Volume slider
        self._create_slider(
            section,
            "Volume",
            0, 100, 80,
            None
        )
    
    def _create_ai_settings(self):
        """AI settings section"""
        section = self._create_section("AI & Intelligence")
        
        # AI Provider
        self._create_option_menu(
            section,
            "AI Provider",
            ["OpenAI", "Anthropic", "Google", "Local"],
            None
        )
        
        # Model
        self._create_option_menu(
            section,
            "Model",
            ["GPT-4", "GPT-3.5", "Claude", "Gemini"],
            None
        )
        
        # Enable memory
        self._create_switch(
            section,
            "Enable Memory",
            True,
            None
        )
    
    def _create_system_settings(self):
        """System settings section"""
        section = self._create_section("System")
        
        # Buttons
        btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Clear History",
            command=self._clear_history
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Reset Settings",
            command=self._reset_settings,
            fg_color="darkred"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Check Updates",
            command=self._check_updates
        ).pack(side="left", padx=5)
    
    def _create_section(self, title: str):
        """Create a settings section"""
        section_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        section_frame.pack(fill="x", pady=10, padx=5)
        
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(padx=15, pady=(15, 10), anchor="w")
        
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        return content_frame
    
    def _create_option_menu(self, parent, label: str, options: list, command):
        """Create an option menu setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        label_widget = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        label_widget.pack(side="left")
        
        menu = ctk.CTkOptionMenu(
            frame,
            values=options,
            command=command,
            width=200
        )
        menu.pack(side="right")
    
    def _create_switch(self, parent, label: str, default: bool, command):
        """Create a switch setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        label_widget = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        label_widget.pack(side="left")
        
        switch = ctk.CTkSwitch(
            frame,
            text="",
            command=command,
            onvalue=True,
            offvalue=False
        )
        if default:
            switch.select()
        switch.pack(side="right")
    
    def _create_slider(self, parent, label: str, min_val: int, max_val: int, default: int, command):
        """Create a slider setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        label_widget = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        label_widget.pack(side="left")
        
        value_label = ctk.CTkLabel(frame, text=str(default), width=40)
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(
            frame,
            from_=min_val,
            to=max_val,
            number_of_steps=max_val - min_val,
            command=lambda v: self._update_slider_label(value_label, v)
        )
        slider.set(default)
        slider.pack(side="right", padx=10, fill="x", expand=True)
    
    def _update_slider_label(self, label, value):
        """Update slider value label"""
        label.configure(text=str(int(value)))
    
    def _on_theme_change(self, value):
        """Handle theme change"""
        if value == "Dark":
            ctk.set_appearance_mode("dark")
        elif value == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
    
    def _clear_history(self):
        """Clear conversation history"""
        logger.info("Clearing history")
        if self.app.engine:
            self.app.engine.memory.clear_history()
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        logger.info("Resetting settings")
        self.app.config.reset()
    
    def _check_updates(self):
        """Check for updates"""
        logger.info("Checking for updates")
        # Would implement update checking here
