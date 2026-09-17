"""
Core assistant engine - orchestrates all components
"""
import asyncio
import logging
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto

from assistant.core.config import ConfigManager
from assistant.core.event_bus import EventBus, Event
from assistant.engines.speech.wake_word import WakeWordEngine
from assistant.engines.speech.recognizer import SpeechRecognizer
from assistant.engines.speech.synthesizer import TextToSpeech
from assistant.engines.nlp.intent import IntentEngine
from assistant.engines.ai.llm import AIEngine
from assistant.commands.dispatcher import CommandDispatcher
from assistant.services.system_monitor import SystemMonitor
from assistant.memory.manager import MemoryManager
from assistant.plugins.manager import PluginManager
from assistant.notifications.manager import NotificationManager
from assistant.automation.scheduler import TaskScheduler

logger = logging.getLogger(__name__)


class AssistantState(Enum):
    """Assistant operational states"""
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    SPEAKING = auto()
    SLEEPING = auto()
    ERROR = auto()


@dataclass
class AssistantContext:
    """Context for current interaction"""
    user_input: str = ""
    intent: Optional[str] = None
    entities: dict = None
    confidence: float = 0.0
    timestamp: float = 0.0
    source: str = "voice"  # voice, text, automation
    session_id: str = ""
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class AssistantEngine:
    """Main engine that coordinates all assistant components"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.state = AssistantState.IDLE
        self.running = False
        self.context = AssistantContext()
        
        # Event bus for component communication
        self.event_bus = EventBus()
        
        # Initialize components
        self._init_components()
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("Assistant engine initialized")
    
    def _init_components(self) -> None:
        """Initialize all engine components"""
        logger.info("Initializing components...")
        
        # Core engines
        self.wake_word = WakeWordEngine(self.config.config.wake_word, self.event_bus)
        self.speech_recognizer = SpeechRecognizer(self.config.config.speech, self.event_bus)
        self.tts = TextToSpeech(self.config.config.tts, self.event_bus)
        self.intent_engine = IntentEngine(self.event_bus)
        self.ai_engine = AIEngine(self.config.config.ai, self.event_bus)
        
        # Command system
        self.command_dispatcher = CommandDispatcher(self.event_bus)
        
        # Services
        self.system_monitor = SystemMonitor(self.event_bus)
        self.memory = MemoryManager(self.config, self.event_bus)
        self.plugins = PluginManager(self.config, self.event_bus)
        self.notifications = NotificationManager(self.config, self.event_bus)
        self.scheduler = TaskScheduler(self.config, self.event_bus)
        
        logger.info("All components initialized")
    
    def _register_handlers(self) -> None:
        """Register event handlers"""
        self.event_bus.on("wake_word_detected", self._on_wake_word)
        self.event_bus.on("speech_recognized", self._on_speech_recognized)
        self.event_bus.on("intent_detected", self._on_intent_detected)
        self.event_bus.on("command_executed", self._on_command_executed)
        self.event_bus.on("error", self._on_error)
    
    def start(self) -> None:
        """Start the assistant engine"""
        logger.info("Starting assistant engine...")
        self.running = True
        
        # Start components in separate threads
        threads = [
            threading.Thread(target=self.wake_word.start, daemon=True),
            threading.Thread(target=self.speech_recognizer.start, daemon=True),
            threading.Thread(target=self.system_monitor.start, daemon=True),
            threading.Thread(target=self.scheduler.start, daemon=True),
        ]
        
        for thread in threads:
            thread.start()
        
        # Load plugins
        self.plugins.load_all()
        
        # Start memory manager
        self.memory.start()
        
        self.event_bus.emit("assistant_started", {"state": self.state.name})
        logger.info("Assistant engine started successfully")
        
        # Main loop
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def stop(self) -> None:
        """Stop the assistant engine"""
        logger.info("Stopping assistant engine...")
        self.running = False
        
        # Stop components
        self.wake_word.stop()
        self.speech_recognizer.stop()
        self.tts.stop()
        self.system_monitor.stop()
        self.scheduler.stop()
        self.memory.stop()
        
        self.event_bus.emit("assistant_stopped", {})
        logger.info("Assistant engine stopped")
    
    def _on_wake_word(self, event: Event) -> None:
        """Handle wake word detection"""
        logger.info(f"Wake word detected: {event.data.get('wake_word')}")
        self.state = AssistantState.LISTENING
        self.event_bus.emit("state_changed", {"state": self.state.name})
        
        # Activate speech recognition
        self.speech_recognizer.activate()
        
        # Play acknowledgment sound or visual cue
        self.tts.speak("Yes?")
    
    def _on_speech_recognized(self, event: Event) -> None:
        """Handle speech recognition result"""
        text = event.data.get("text", "")
        confidence = event.data.get("confidence", 0.0)
        
        if not text or confidence < 0.5:
            logger.debug(f"Low confidence speech: {text} ({confidence})")
            return
        
        logger.info(f"Speech recognized: {text} (confidence: {confidence:.2f})")
        
        self.context = AssistantContext(
            user_input=text,
            confidence=confidence,
            source="voice"
        )
        
        self.state = AssistantState.PROCESSING
        self.event_bus.emit("state_changed", {"state": self.state.name})
        
        # Process through NLP
        self.intent_engine.process(text, self.context)
    
    def _on_intent_detected(self, event: Event) -> None:
        """Handle intent detection"""
        intent = event.data.get("intent")
        entities = event.data.get("entities", {})
        confidence = event.data.get("confidence", 0.0)
        
        logger.info(f"Intent detected: {intent} (confidence: {confidence:.2f})")
        
        self.context.intent = intent
        self.context.entities = entities
        self.context.confidence = confidence
        
        # Dispatch command
        self.command_dispatcher.dispatch(intent, entities, self.context)
    
    def _on_command_executed(self, event: Event) -> None:
        """Handle command execution result"""
        result = event.data.get("result")
        response = event.data.get("response", "")
        success = event.data.get("success", True)
        
        logger.info(f"Command executed: success={success}")
        
        # Save to memory
        if self.config.config.memory_enabled:
            self.memory.save_interaction(self.context, result)
        
        # Speak response if available
        if response:
            self.state = AssistantState.SPEAKING
            self.event_bus.emit("state_changed", {"state": self.state.name})
            self.tts.speak(response)
        
        # Return to idle
        self.state = AssistantState.IDLE
        self.event_bus.emit("state_changed", {"state": self.state.name})
    
    def _on_error(self, event: Event) -> None:
        """Handle errors"""
        error = event.data.get("error")
        component = event.data.get("component", "unknown")
        
        logger.error(f"Error in {component}: {error}")
        
        self.state = AssistantState.ERROR
        self.event_bus.emit("state_changed", {"state": self.state.name})
        
        # Notify user
        self.tts.speak("I encountered an error. Please try again.")
        
        # Return to idle after error
        time.sleep(2)
        self.state = AssistantState.IDLE
        self.event_bus.emit("state_changed", {"state": self.state.name})
    
    def process_text(self, text: str) -> None:
        """Process text input directly (for GUI)"""
        logger.info(f"Processing text input: {text}")
        
        self.context = AssistantContext(
            user_input=text,
            confidence=1.0,
            source="text"
        )
        
        self.state = AssistantState.PROCESSING
        self.event_bus.emit("state_changed", {"state": self.state.name})
        
        # Process through NLP
        self.intent_engine.process(text, self.context)
    
    def get_state(self) -> AssistantState:
        """Get current assistant state"""
        return self.state
    
    def set_state(self, state: AssistantState) -> None:
        """Set assistant state"""
        self.state = state
        self.event_bus.emit("state_changed", {"state": state.name})
