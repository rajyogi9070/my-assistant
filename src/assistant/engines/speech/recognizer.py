"""
Speech recognition engine with multiple backends
"""
import logging
import threading
import time
from typing import Optional, Callable
from enum import Enum, auto
import numpy as np

from assistant.core.event_bus import EventBus
from assistant.core.config import SpeechConfig

logger = logging.getLogger(__name__)


class RecognitionState(Enum):
    """Speech recognition states"""
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    ERROR = auto()


class SpeechRecognizer:
    """Speech recognition with multiple backend support"""
    
    def __init__(self, config: SpeechConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.state = RecognitionState.IDLE
        self.running = False
        self.active = False
        self.thread: Optional[threading.Thread] = None
        
        # Recognition settings
        self.sample_rate = config.sample_rate
        self.chunk_size = config.chunk_size
        
        # Initialize recognizer
        self.recognizer = None
        self.engine = None
        self._init_recognizer()
    
    def _init_recognizer(self) -> None:
        """Initialize speech recognition engine"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Initialize backend engine
            if self.config.engine == "vosk":
                self._init_vosk()
            elif self.config.engine == "whisper":
                self._init_whisper()
            else:
                logger.info(f"Using {self.config.engine} speech recognition")
            
            logger.info(f"Speech recognizer initialized with {self.config.engine}")
            
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {e}", exc_info=True)
    
    def _init_vosk(self) -> None:
        """Initialize Vosk offline recognition"""
        try:
            from vosk import Model, KaldiRecognizer
            import json
            
            # Try to load model
            model_path = "models/speech/vosk-model-small-en-us-0.15"
            
            try:
                self.engine = {
                    "model": Model(model_path),
                    "recognizer": None  # Will be created per session
                }
                logger.info("Vosk model loaded successfully")
            except Exception as e:
                logger.warning(f"Vosk model not found, using Google recognition: {e}")
                self.config.engine = "google"
                
        except ImportError:
            logger.warning("Vosk not installed, using Google recognition")
            self.config.engine = "google"
    
    def _init_whisper(self) -> None:
        """Initialize Whisper recognition"""
        try:
            from faster_whisper import WhisperModel
            
            # Load model (base model for speed)
            self.engine = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("Whisper model loaded successfully")
            
        except ImportError:
            logger.warning("faster-whisper not installed, using Google recognition")
            self.config.engine = "google"
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            self.config.engine = "google"
    
    def start(self) -> None:
        """Start speech recognition service"""
        logger.info("Starting speech recognition service...")
        self.running = True
        self.thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop speech recognition service"""
        logger.info("Stopping speech recognition service...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def activate(self) -> None:
        """Activate listening mode"""
        self.active = True
        self.state = RecognitionState.LISTENING
        logger.info("Speech recognition activated - listening...")
    
    def deactivate(self) -> None:
        """Deactivate listening mode"""
        self.active = False
        self.state = RecognitionState.IDLE
        logger.info("Speech recognition deactivated")
    
    def _recognition_loop(self) -> None:
        """Main recognition loop"""
        try:
            import speech_recognition as sr
            
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                logger.info("Microphone initialized")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.running:
                    if not self.active:
                        time.sleep(0.1)
                        continue
                    
                    try:
                        # Listen for speech
                        audio = self.recognizer.listen(
                            source,
                            timeout=self.config.timeout_seconds,
                            phrase_time_limit=10
                        )
                        
                        self.state = RecognitionState.PROCESSING
                        self._process_audio(audio)
                        
                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        if self.config.continuous_listening:
                            continue
                        else:
                            self.deactivate()
                    
                    except Exception as e:
                        logger.error(f"Error in recognition: {e}")
                        self.state = RecognitionState.ERROR
                        time.sleep(1)
        
        except Exception as e:
            logger.error(f"Fatal error in recognition loop: {e}", exc_info=True)
            self.event_bus.emit("error", {
                "error": str(e),
                "component": "speech_recognizer"
            })
    
    def _process_audio(self, audio) -> None:
        """Process audio through selected engine"""
        try:
            text = None
            confidence = 0.0
            
            if self.config.engine == "vosk":
                text, confidence = self._recognize_vosk(audio)
            elif self.config.engine == "whisper":
                text, confidence = self._recognize_whisper(audio)
            elif self.config.engine == "google":
                text, confidence = self._recognize_google(audio)
            
            if text and text.strip():
                logger.info(f"Recognized: {text} (confidence: {confidence:.2f})")
                
                self.event_bus.emit("speech_recognized", {
                    "text": text.strip(),
                    "confidence": confidence,
                    "engine": self.config.engine
                })
                
                # Deactivate after recognition
                self.deactivate()
            else:
                logger.debug("No speech recognized")
                self.state = RecognitionState.LISTENING
        
        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)
            self.state = RecognitionState.ERROR
    
    def _recognize_google(self, audio) -> tuple[Optional[str], float]:
        """Recognize using Google Speech Recognition"""
        try:
            import speech_recognition as sr
            
            text = self.recognizer.recognize_google(
                audio,
                language=self.config.language
            )
            
            return text, 0.85  # Google doesn't provide confidence
            
        except Exception as e:
            logger.error(f"Google recognition failed: {e}")
            return None, 0.0
    
    def _recognize_vosk(self, audio) -> tuple[Optional[str], float]:
        """Recognize using Vosk"""
        try:
            from vosk import KaldiRecognizer
            import json
            
            # Get audio data
            audio_data = audio.get_raw_data()
            
            # Create recognizer
            rec = KaldiRecognizer(self.engine["model"], self.sample_rate)
            
            # Process audio
            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                return text, 0.8
            else:
                result = json.loads(rec.PartialResult())
                text = result.get("partial", "")
                return text, 0.5
        
        except Exception as e:
            logger.error(f"Vosk recognition failed: {e}")
            return None, 0.0
    
    def _recognize_whisper(self, audio) -> tuple[Optional[str], float]:
        """Recognize using Whisper"""
        try:
            import tempfile
            import wave
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
                audio_data = audio.get_wav_data()
                f.write(audio_data)
            
            # Transcribe with Whisper
            segments, info = self.engine.transcribe(temp_path, language="en")
            
            # Combine segments
            text = " ".join([segment.text for segment in segments])
            confidence = info.language_probability
            
            # Cleanup
            import os
            os.unlink(temp_path)
            
            return text, confidence
        
        except Exception as e:
            logger.error(f"Whisper recognition failed: {e}")
            return None, 0.0
    
    def recognize_from_text(self, text: str) -> None:
        """Process text input directly (for GUI)"""
        self.event_bus.emit("speech_recognized", {
            "text": text,
            "confidence": 1.0,
            "engine": "text_input"
        })
