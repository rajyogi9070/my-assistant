"""
Unit tests for configuration management
"""
import pytest
import json
import tempfile
from pathlib import Path

from assistant.core.config import ConfigManager, AssistantConfig


class TestAssistantConfig:
    """Tests for configuration model"""
    
    def test_default_config(self):
        config = AssistantConfig()
        assert config.version == "1.0.0"
        assert config.wake_word.enabled is True
        assert config.speech.engine == "vosk"
        assert config.tts.engine == "pyttsx3"
        assert config.ui.theme == "dark"
    
    def test_wake_word_config(self):
        config = AssistantConfig()
        assert "hey_assistant" in config.wake_word.wake_words
        assert 0 <= config.wake_word.sensitivity <= 1
    
    def test_speech_config(self):
        config = AssistantConfig()
        assert config.speech.sample_rate == 16000
        assert config.speech.channels == 1
    
    def test_security_config(self):
        config = AssistantConfig()
        assert "shutdown" in config.security.require_confirmation
        assert "delete" in config.security.require_confirmation


class TestConfigManager:
    """Tests for configuration manager"""
    
    def test_create_default_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(config_path)
            
            assert config_path.exists()
            assert manager.config.version == "1.0.0"
    
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            # Create and save
            manager1 = ConfigManager(config_path)
            manager1.config.ui.theme = "light"
            manager1.save()
            
            # Load again
            manager2 = ConfigManager(config_path)
            assert manager2.config.ui.theme == "light"
    
    def test_get_nested_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(config_path)
            
            value = manager.get("ui.theme")
            assert value == "dark"
    
    def test_set_nested_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(config_path)
            
            manager.set("ui.theme", "light")
            assert manager.config.ui.theme == "light"
    
    def test_reset_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(config_path)
            
            manager.config.ui.theme = "light"
            manager.reset()
            
            assert manager.config.ui.theme == "dark"
    
    def test_export_import(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            export_path = Path(tmpdir) / "export.json"
            
            # Create and export
            manager1 = ConfigManager(config_path)
            manager1.config.ui.theme = "light"
            manager1.save()
            manager1.export(export_path)
            
            assert export_path.exists()
            
            # Import into new manager
            manager2 = ConfigManager(Path(tmpdir) / "config2.json")
            manager2.import_config(export_path)
            
            assert manager2.config.ui.theme == "light"
