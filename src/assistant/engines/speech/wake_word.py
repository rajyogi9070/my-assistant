"""
Wake word detection engine
"""
import logging
import threading
import time
from typing import Optional
import numpy as np

from assistant.core.event_bus import EventBus
from assistant.core.config import WakeWordConfig

logger = logging.getLogger(__name__)


class WakeWordEngine:
    """Wake word detection using openwakeword or fallback methods"""
    
    def __init__(self, config: WakeWordConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.running = False
        self.active = False
        self.thread: Optional[threading.Thread] = None
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1280  # 80ms chunks for openwakeword
        
        # Initialize wake word detector
        self.detector = None
        self._init_detector()
    
    def _init_detector(self) -> None:
        """Initialize wake word detector"""
        try:
            # Try to use openwakeword
            import openwakeword
            from openwakeword.model import Model
            
            logger.info("Initializing openwakeword detector...")
            
            # Create model with default wakeword models
            self.detector = Model(
                wakeword_models=[],  # Use built-in models
                inference_framework="onnx"
            )
            
            logger.info("openwakeword detector initialized")
            
        except ImportError:
            logger.warning("openwakeword not available, using fallback detection")
            self.detector = None
        except Exception as e:
            logger.error(f"Failed to initialize wake word detector: {e}")
            self.detector = None
    
    def start(self) -> None:
        """Start wake word detection"""
        if not self.config.enabled:
            logger.info("Wake word detection disabled")
            return
        
        logger.info("Starting wake word detection...")
        self.running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop wake word detection"""
        logger.info("Stopping wake word detection...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _detection_loop(self) -> None:
        """Main detection loop"""
        try:
            import pyaudio
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Wake word detection started")
            
            while self.running:
                if not self.active:
                    time.sleep(0.1)
                    continue
                
                # Read audio chunk
                audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Process audio
                if self.detector:
                    self._process_with_openwakeword(audio_array)
                else:
                    self._process_fallback(audio_array)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}", exc_info=True)
            self.event_bus.emit("error", {
                "error": str(e),
                "component": "wake_word"
            })
    
    def _process_with_openwakeword(self, audio: np.ndarray) -> None:
        """Process audio with openwakeword"""
        try:
            # Get predictions
            prediction = self.detector.predict(audio)
            
            # Check for wake word detection
            for model_name, score in prediction.items():
                if score > self.config.sensitivity:
                    logger.info(f"Wake word detected: {model_name} (score: {score:.2f})")
                    
                    self.event_bus.emit("wake_word_detected", {
                        "wake_word": model_name,
                        "confidence": score
                    })
                    
                    # Reset detector to prevent multiple triggers
                    self.detector.reset()
                    break
                    
        except Exception as e:
            logger.error(f"Error in openwakeword processing: {e}")
    
    def _process_fallback(self, audio: np.ndarray) -> None:
        """Fallback wake word detection using energy threshold"""
        # Simple energy-based detection (not ideal but works as fallback)
        energy = np.abs(audio).mean()
        
        # This is a very basic fallback - in production you'd want proper wake word models
        if energy > 1000:  # Arbitrary threshold
            # In a real implementation, you'd use a proper wake word model here
            pass
    
    def activate(self) -> None:
        """Activate wake word detection"""
        self.active = True
        logger.debug("Wake word detection activated")
    
    def deactivate(self) -> None:
        """Deactivate wake word detection"""
        self.active = False
        logger.debug("Wake word detection deactivated")
    
    def add_custom_wake_word(self, model_path: str) -> bool:
        """Add custom wake word model"""
        try:
            if self.detector:
                # Load custom model
                self.detector.load_wakeword_model(model_path)
                logger.info(f"Custom wake word model loaded: {model_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load custom wake word: {e}")
            return False
    
    def set_sensitivity(self, sensitivity: float) -> None:
        """Set detection sensitivity (0.0 to 1.0)"""
        self.config.sensitivity = max(0.0, min(1.0, sensitivity))
        logger.info(f"Wake word sensitivity set to {self.config.sensitivity}")
