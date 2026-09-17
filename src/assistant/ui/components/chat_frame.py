"""
Chat interface frame
"""
import logging
import customtkinter as ctk
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatFrame(ctk.CTkFrame):
    """Chat interface for text interaction"""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Chat",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Chat display area
        self.chat_display = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(size=14),
            state="disabled"
        )
        self.chat_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Input area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Text input
        self.text_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message or command...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.text_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.text_input.bind("<Return>", self._on_enter)
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=80,
            height=40,
            command=self._send_message
        )
        self.send_button.grid(row=0, column=1)
        
        # Microphone button
        self.mic_button = ctk.CTkButton(
            self.input_frame,
            text="🎤",
            width=40,
            height=40,
            command=self._toggle_microphone
        )
        self.mic_button.grid(row=0, column=2, padx=(10, 0))
        
        # Welcome message
        self.add_assistant_message("Hello! I'm your AI Assistant. How can I help you today?")
    
    def _on_enter(self, event):
        """Handle enter key press"""
        self._send_message()
    
    def _send_message(self):
        """Send message"""
        text = self.text_input.get().strip()
        
        if not text:
            return
        
        # Add user message to chat
        self.add_user_message(text)
        
        # Clear input
        self.text_input.delete(0, "end")
        
        # Process command
        self.app.process_command(text)
    
    def _toggle_microphone(self):
        """Toggle microphone"""
        logger.info("Microphone toggle requested")
        # This would activate the wake word/speech recognition
        if self.app.engine:
            self.app.engine.speech_recognizer.activate()
    
    def add_user_message(self, text: str):
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        message = f"\n[{timestamp}] You: {text}\n"
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def add_assistant_message(self, text: str):
        """Add assistant message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        message = f"\n[{timestamp}] Assistant: {text}\n"
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.add_assistant_message("Chat cleared. How can I help you?")
