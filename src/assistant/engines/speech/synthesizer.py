"""
Text-to-speech synthesis engine
"""
import logging
import threading
import time
from typing import Optional
from queue import Queue
from enum import Enum, auto

from assistant.core.event_bus import EventBus
from assistant.core.config import TTSConfig

logger = logging.getLogger(__name__)


class TTSState(Enum):
    """TTS engine states"""
    IDLE = auto()
    SPEAKING = auto()
    PAUSED = auto()
    ERROR = auto()


class TextToSpeech:
    """Text-to-speech synthesis with multiple backends"""
    
    def __init__(self, config: TTSConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = EventBus
        self.state = TTSState.IDLE
        self.running = True
        self.speaking = False
        
        # Speech queue for streaming
        self.queue: Queue = Queue()
        self.thread: Optional[threading.Thread] = None
        
        # Initialize TTS engine
        self.engine = None
        self._init_engine()
        
        # Start speech thread
        self._start_speech_thread()
    
    def _init_engine(self) -> None:
        """Initialize TTS engine"""
        try:
            if self.config.engine == "pyttsx3":
                self._init_pyttsx3()
            elif self.config.engine == "edge":
                self._init_edge_tts()
            else:
                logger.warning(f"Unknown TTS engine: {self.config.engine}, using pyttsx3")
                self._init_pyttsx3()
        
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}", exc_info=True)
            self.state = TTSState.ERROR
    
    def _init_pyttsx3(self) -> None:
        """Initialize pyttsx3 offline TTS"""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            self.engine.setProperty('rate', self.config.rate)
            self.engine.setProperty('volume', self.config.volume)
            
            # Set voice based on gender preference
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find voice matching gender preference
                for voice in voices:
                    if self.config.gender.lower() in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
            
            logger.info("pyttsx3 TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def _init_edge_tts(self) -> None:
        """Initialize Edge TTS (online)"""
        try:
            # Edge TTS will be used on-demand (async)
            import edge_tts
            self.engine = "edge"
            logger.info("Edge TTS engine initialized")
            
        except ImportError:
            logger.warning("edge-tts not installed, falling back to pyttsx3")
            self._init_pyttsx3()
    
    def _start_speech_thread(self) -> None:
        """Start background speech thread"""
        self.thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.thread.start()
    
    def _speech_loop(self) -> None:
        """Background speech processing loop"""
        while self.running:
            try:
                # Get next speech request
                text = self.queue.get(timeout=1.0)
                
                if text is None:
                    break
                
                self._speak_text(text)
                self.queue.task_done()
                
            except Exception as e:
                if "Empty" not in str(type(e).__name__):
                    logger.error(f"Error in speech loop: {e}")
                time.sleep(0.1)
    
    def _speak_text(self, text: str) -> None:
        """Speak text using configured engine"""
        try:
            self.speaking = True
            self.state = TTSState.SPEAKING
            
            self.event_bus.emit("tts_started", {"text": text})
            
            if self.config.engine == "pyttsx3" or self.engine != "edge":
                self._speak_pyttsx3(text)
            elif self.config.engine == "edge":
                self._speak_edge(text)
            
            self.event_bus.emit("tts_completed", {"text": text})
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}", exc_info=True)
            self.state = TTSState.ERROR
            self.event_bus.emit("tts_error", {"error": str(e), "text": text})
        
        finally:
            self.speaking = False
            self.state = TTSState.IDLE
    
    def _speak_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"pyttsx3 speech failed: {e}")
            raise
    
    def _speak_edge(self, text: str) -> None:
        """Speak using Edge TTS"""
        try:
            import asyncio
            import edge_tts
            import tempfile
            import os
            
            # Create async function
            async def synthesize():
                communicate = edge_tts.Communicate(text, self.config.voice_id or "en-US-AriaNeural")
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    temp_path = f.name
                
                await communicate.save(temp_path)
                return temp_path
            
            # Run async synthesis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            temp_path = loop.run_until_complete(synthesize())
            loop.close()
            
            # Play audio file
            self._play_audio_file(temp_path)
            
            # Cleanup
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Edge TTS speech failed: {e}")
            # Fallback to pyttsx3
            self._speak_pyttsx3(text)
    
    def _play_audio_file(self, file_path: str) -> None:
        """Play audio file"""
        try:
            # Try pygame mixer
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.quit()
            
        except ImportError:
            # Fallback: use system player
            import platform
            import subprocess
            
            system = platform.system()
            if system == "Windows":
                # Use Windows Media Player
                import winsound
                # winsound doesn't support MP3, so we'd need another approach
                # For now, fall back to pyttsx3
                logger.warning("No audio player available, falling back to pyttsx3")
                self._init_pyttsx3()
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        """Queue text for speech synthesis"""
        if not text or not text.strip():
            return
        
        if interrupt and self.speaking:
            self.interrupt()
        
        # Split long text into chunks for streaming
        if self.config.streaming and len(text) > 200:
            chunks = self._split_text(text)
            for chunk in chunks:
                self.queue.put(chunk)
        else:
            self.queue.put(text)
        
        logger.debug(f"Queued speech: {text[:50]}...")
    
    def _split_text(self, text: str) -> list[str]:
        """Split text into speakable chunks"""
        # Split on sentence boundaries
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 200:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def interrupt(self) -> None:
        """Interrupt current speech"""
        if self.speaking:
            try:
                if self.config.engine == "pyttsx3":
                    self.engine.stop()
                
                # Clear queue
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                    except:
                        break
                
                logger.info("Speech interrupted")
                self.speaking = False
                self.state = TTSState.IDLE
                
            except Exception as e:
                logger.error(f"Error interrupting speech: {e}")
    
    def pause(self) -> None:
        """Pause speech"""
        if self.speaking:
            try:
                if self.config.engine == "pyttsx3":
                    self.engine.stop()
                
                self.state = TTSState.PAUSED
                logger.info("Speech paused")
                
            except Exception as e:
                logger.error(f"Error pausing speech: {e}")
    
    def resume(self) -> None:
        """Resume paused speech"""
        if self.state == TTSState.PAUSED:
            self.state = TTSState.IDLE
            logger.info("Speech resumed")
    
    def stop(self) -> None:
        """Stop TTS engine"""
        logger.info("Stopping TTS engine...")
        self.running = False
        self.queue.put(None)  # Signal thread to stop
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.engine and self.config.engine == "pyttsx3":
            try:
                self.engine.stop()
            except:
                pass
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)"""
        self.config.rate = rate
        if self.config.engine == "pyttsx3" and self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float) -> None:
        """Set speech volume (0.0 to 1.0)"""
        self.config.volume = max(0.0, min(1.0, volume))
        if self.config.engine == "pyttsx3" and self.engine:
            self.engine.setProperty('volume', self.config.volume)
    
    def set_voice(self, voice_id: str) -> None:
        """Set voice by ID"""
        self.config.voice_id = voice_id
        if self.config.engine == "pyttsx3" and self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def get_voices(self) -> list[dict]:
        """Get available voices"""
        voices = []
        
        if self.config.engine == "pyttsx3" and self.engine:
            for voice in self.engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': 'unknown'
                })
        
        return voices
