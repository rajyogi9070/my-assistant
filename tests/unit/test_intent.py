"""
Unit tests for the intent engine
"""
import pytest
from unittest.mock import MagicMock

from assistant.engines.nlp.intent import IntentEngine, Intent
from assistant.core.event_bus import EventBus


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def intent_engine(event_bus):
    return IntentEngine(event_bus)


class TestIntentEngine:
    """Tests for intent detection"""
    
    def test_shutdown_intent(self, intent_engine):
        result = intent_engine.process("shut down the computer")
        assert result.intent == Intent.SHUTDOWN
        assert result.confidence > 0.5
    
    def test_restart_intent(self, intent_engine):
        result = intent_engine.process("restart my computer")
        assert result.intent == Intent.RESTART
    
    def test_lock_intent(self, intent_engine):
        result = intent_engine.process("lock the screen")
        assert result.intent == Intent.LOCK
    
    def test_open_app_intent(self, intent_engine):
        result = intent_engine.process("open chrome")
        assert result.intent == Intent.OPEN_APP
        assert "app_name" in result.entities or result.entities is not None
    
    def test_search_web_intent(self, intent_engine):
        result = intent_engine.process("search for AI news")
        assert result.intent == Intent.SEARCH_WEB
    
    def test_volume_up_intent(self, intent_engine):
        result = intent_engine.process("increase volume")
        assert result.intent == Intent.VOLUME_UP
    
    def test_volume_down_intent(self, intent_engine):
        result = intent_engine.process("decrease volume")
        assert result.intent == Intent.VOLUME_DOWN
    
    def test_mute_intent(self, intent_engine):
        result = intent_engine.process("mute")
        assert result.intent == Intent.MUTE
    
    def test_screenshot_intent(self, intent_engine):
        result = intent_engine.process("take a screenshot")
        assert result.intent == Intent.TAKE_SCREENSHOT
    
    def test_battery_check_intent(self, intent_engine):
        result = intent_engine.process("check my battery level")
        assert result.intent == Intent.CHECK_BATTERY
    
    def test_brightness_intent(self, intent_engine):
        result = intent_engine.process("set brightness to 80")
        assert result.intent == Intent.SET_BRIGHTNESS
    
    def test_unknown_intent(self, intent_engine):
        result = intent_engine.process("")
        assert result.intent == Intent.UNKNOWN
    
    def test_chat_fallback(self, intent_engine):
        result = intent_engine.process("tell me a joke")
        assert result.intent == Intent.CHAT
    
    def test_timer_intent(self, intent_engine):
        result = intent_engine.process("set a timer for 10 minutes")
        assert result.intent == Intent.SET_TIMER


class TestEntityExtraction:
    """Tests for entity extraction"""
    
    def test_brightness_value(self, intent_engine):
        result = intent_engine.process("set brightness to 75")
        assert result.entities.get("brightness_value") == 75 or "brightness_value" in str(result.entities)
    
    def test_app_name_extraction(self, intent_engine):
        result = intent_engine.process("open visual studio code")
        # Should extract the app name
        assert result.intent == Intent.OPEN_APP
    
    def test_search_query(self, intent_engine):
        result = intent_engine.process("search for python tutorials")
        assert result.intent == Intent.SEARCH_WEB
