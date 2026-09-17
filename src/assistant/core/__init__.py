"""
Configuration management system
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class WakeWordConfig(BaseModel):
    """Wake word detection configuration"""
    enabled: bool = True
    wake_words: list[str] = Field(default_factory=lambda: ["hey_assistant", "hello_assistant"])
    sensitivity: float = 0.5
    timeout_seconds: float = 3.0
    false_activation_prevention: bool = True
    custom_wake_word: Optional[str] = None


class SpeechConfig(BaseModel):
    """Speech recognition configuration"""
    engine: str = "vosk"  # vosk, google, whisper
    language: str = "en-US"
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 4000
    noise_suppression: bool = True
    echo_cancellation: bool = True
    auto_punctuation: bool = True
    continuous_listening: bool = True
    timeout_seconds: float = 5.0


class TTSConfig(BaseModel):
    """Text-to-speech configuration"""
    engine: str = "pyttsx3"  # pyttsx3, edge, google
    voice_id: Optional[str] = None
    rate: int = 175
    volume: float = 1.0
    pitch: int = 100
    gender: str = "female"  # male, female
    streaming: bool = True


class UIConfig(BaseModel):
    """User interface configuration"""
    theme: str = "dark"  # dark, light, auto
    language: str = "en"
    animations_enabled: bool = True
    window_width: int = 1200
    window_height: int = 800
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    always_on_top: bool = False
    start_minimized: bool = False
    show_system_tray: bool = True
    dashboard_enabled: bool = True


class AIConfig(BaseModel):
    """AI/LLM configuration"""
    provider: str = "openai"  # openai, anthropic, local
    model: str = "gpt-4"
    api_key: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout_seconds: int = 30
    fallback_to_offline: bool = True


class SecurityConfig(BaseModel):
    """Security configuration"""
    voice_authentication: bool = False
    face_authentication: bool = False
    pin_code: Optional[str] = None
    require_confirmation: list[str] = Field(
        default_factory=lambda: ["shutdown", "restart", "delete", "format"]
    )
    encryption_enabled: bool = True
    audit_logging: bool = True


class PerformanceConfig(BaseModel):
    """Performance configuration"""
    cpu_optimization: bool = True
    gpu_acceleration: bool = False
    lazy_loading: bool = True
    caching_enabled: bool = True
    max_memory_mb: int = 512
    background_mode: bool = True
    low_power_mode: bool = False


class UpdateConfig(BaseModel):
    """Update system configuration"""
    auto_check: bool = True
    auto_download: bool = False
    auto_install: bool = False
    check_interval_hours: int = 24
    channel: str = "stable"  # stable, beta, dev
    last_check: Optional[str] = None


class AssistantConfig(BaseModel):
    """Main assistant configuration"""
    version: str = "1.0.0"
    wake_word: WakeWordConfig = Field(default_factory=WakeWordConfig)
    speech: SpeechConfig = Field(default_factory=SpeechConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    updates: UpdateConfig = Field(default_factory=UpdateConfig)
    
    # Feature flags
    plugins_enabled: bool = True
    automation_enabled: bool = True
    memory_enabled: bool = True
    notifications_enabled: bool = True
    
    # User preferences
    user_name: Optional[str] = None
    timezone: str = "UTC"
    units: str = "metric"  # metric, imperial


class ConfigManager:
    """Manages application configuration with persistence"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = self._get_default_config_path()
        
        self.config_path = config_path
        self.config = self._load_or_create()
        
        logger.info(f"Configuration loaded from {self.config_path}")
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path"""
        if os.name == 'nt':
            config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'MyAssistant'
        else:
            config_dir = Path.home() / '.myassistant'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'
    
    def _load_or_create(self) -> AssistantConfig:
        """Load existing config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AssistantConfig(**data)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                logger.info("Creating default configuration")
        
        config = AssistantConfig()
        self._save(config)
        return config
    
    def _save(self, config: AssistantConfig) -> None:
        """Save configuration to disk"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(), f, indent=2)
            logger.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def save(self) -> None:
        """Save current configuration"""
        self._save(self.config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        obj = self.config
        
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            elif isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                raise KeyError(f"Configuration key not found: {k}")
        
        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise KeyError(f"Configuration key not found: {final_key}")
        
        self.save()
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = AssistantConfig()
        self.save()
        logger.info("Configuration reset to defaults")
    
    def export(self, path: Path) -> None:
        """Export configuration to file"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.config.model_dump(), f, indent=2)
    
    def import_config(self, path: Path) -> None:
        """Import configuration from file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.config = AssistantConfig(**data)
        self.save()
