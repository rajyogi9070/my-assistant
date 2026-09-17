"""
Intent detection and natural language understanding
"""
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum, auto
import json

from assistant.core.event_bus import EventBus

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Available intents"""
    # System control
    SHUTDOWN = "shutdown"
    RESTART = "restart"
    SLEEP = "sleep"
    LOCK = "lock"
    LOGOUT = "logout"
    
    # Application control
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SWITCH_APP = "switch_app"
    
    # Web operations
    SEARCH_WEB = "search_web"
    OPEN_WEBSITE = "open_website"
    OPEN_YOUTUBE = "open_youtube"
    
    # File operations
    CREATE_FOLDER = "create_folder"
    OPEN_FILE = "open_file"
    MOVE_FILE = "move_file"
    DELETE_FILE = "delete_file"
    
    # Media control
    PLAY_MUSIC = "play_music"
    PAUSE_MEDIA = "pause_media"
    RESUME_MEDIA = "resume_media"
    NEXT_TRACK = "next_track"
    PREVIOUS_TRACK = "previous_track"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE = "mute"
    UNMUTE = "unmute"
    
    # Display control
    SET_BRIGHTNESS = "set_brightness"
    INCREASE_BRIGHTNESS = "increase_brightness"
    DECREASE_BRIGHTNESS = "decrease_brightness"
    
    # System information
    CHECK_BATTERY = "check_battery"
    CHECK_CPU = "check_cpu"
    CHECK_RAM = "check_ram"
    CHECK_DISK = "check_disk"
    SYSTEM_INFO = "system_info"
    
    # Productivity
    TAKE_SCREENSHOT = "take_screenshot"
    RECORD_SCREEN = "record_screen"
    SET_TIMER = "set_timer"
    SET_ALARM = "set_alarm"
    SET_REMINDER = "set_reminder"
    CREATE_NOTE = "create_note"
    
    # Communication
    SEND_EMAIL = "send_email"
    READ_EMAIL = "read_email"
    
    # AI/Chat
    CHAT = "chat"
    ASK_QUESTION = "ask_question"
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"
    
    # Settings
    OPEN_SETTINGS = "open_settings"
    CHANGE_THEME = "change_theme"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class IntentMatch:
    """Intent match result"""
    intent: Intent
    confidence: float
    entities: Dict[str, Any]
    pattern: str = ""


class IntentEngine:
    """Intent detection using pattern matching and NLP"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.patterns: List[Dict[str, Any]] = []
        self._load_patterns()
        
        logger.info("Intent engine initialized")
    
    def _load_patterns(self) -> None:
        """Load intent patterns"""
        self.patterns = [
            # System control
            {
                "intent": Intent.SHUTDOWN,
                "patterns": [
                    r"\b(shut\s*down|power\s*off|turn\s*off)\b.*\b(computer|pc|system|laptop)\b",
                    r"\b(shutdown|poweroff)\b"
                ],
                "priority": 10
            },
            {
                "intent": Intent.RESTART,
                "patterns": [
                    r"\b(restart|reboot)\b.*\b(computer|pc|system|laptop)\b",
                    r"\b(restart|reboot)\b"
                ],
                "priority": 10
            },
            {
                "intent": Intent.SLEEP,
                "patterns": [
                    r"\b(sleep|hibernate|suspend)\b.*\b(computer|pc|system|laptop)\b",
                    r"\b(sleep|hibernate)\b"
                ],
                "priority": 10
            },
            {
                "intent": Intent.LOCK,
                "patterns": [
                    r"\block\b.*\b(computer|pc|screen|system)\b",
                    r"\block\b"
                ],
                "priority": 10
            },
            {
                "intent": Intent.LOGOUT,
                "patterns": [
                    r"\b(log\s*out|sign\s*out)\b",
                ],
                "priority": 10
            },
            
            # Application control
            {
                "intent": Intent.OPEN_APP,
                "patterns": [
                    r"\b(open|launch|start|run)\b\s+(.+)",
                    r"\b(open|launch|start)\b\s+the\s+(.+)",
                ],
                "entity_extractors": ["app_name"],
                "priority": 8
            },
            {
                "intent": Intent.CLOSE_APP,
                "patterns": [
                    r"\b(close|quit|exit|kill|stop)\b\s+(.+)",
                    r"\b(close|quit|exit)\b\s+the\s+(.+)",
                ],
                "entity_extractors": ["app_name"],
                "priority": 8
            },
            
            # Web operations
            {
                "intent": Intent.SEARCH_WEB,
                "patterns": [
                    r"\b(search|google|look\s*up)\b.*\b(for|about)?\b\s*(.+)",
                    r"\bsearch\b\s+(.+)\b(on|in)\b\s+(google|bing|web|internet)",
                ],
                "entity_extractors": ["search_query"],
                "priority": 7
            },
            {
                "intent": Intent.OPEN_WEBSITE,
                "patterns": [
                    r"\b(open|go\s*to|visit)\b\s+(.+)\.(com|org|net|io|co)",
                    r"\b(open|go\s*to)\b\s+website\s+(.+)",
                ],
                "entity_extractors": ["url"],
                "priority": 7
            },
            {
                "intent": Intent.OPEN_YOUTUBE,
                "patterns": [
                    r"\b(open|go\s*to)\b.*youtube\b",
                    r"\bplay\b.*\bon\b.*youtube\b",
                ],
                "priority": 7
            },
            
            # File operations
            {
                "intent": Intent.CREATE_FOLDER,
                "patterns": [
                    r"\b(create|make|new)\b.*\b(folder|directory)\b.*\b(name[ds]?)?\b\s*(.+)",
                    r"\b(create|make)\b\s+a\s+(folder|directory)\b.*\b(name[ds]?)?\b\s*(.+)",
                ],
                "entity_extractors": ["folder_name"],
                "priority": 6
            },
            
            # Media control
            {
                "intent": Intent.PLAY_MUSIC,
                "patterns": [
                    r"\b(play|start)\b.*\b(music|song|playlist)\b",
                    r"\bplay\b\s+(.+)",
                ],
                "priority": 7
            },
            {
                "intent": Intent.PAUSE_MEDIA,
                "patterns": [
                    r"\bpause\b",
                    r"\bstop\b.*\b(music|video|playing)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.RESUME_MEDIA,
                "patterns": [
                    r"\b(resume|continue|unpause)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.NEXT_TRACK,
                "patterns": [
                    r"\bnext\b.*\b(song|track)\b",
                    r"\bskip\b.*\b(song|track)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.PREVIOUS_TRACK,
                "patterns": [
                    r"\b(previous|last|back)\b.*\b(song|track)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.VOLUME_UP,
                "patterns": [
                    r"\b(increase|raise|turn\s*up)\b.*\bvolume\b",
                    r"\bvolume\s*up\b",
                    r"\b(turn\s*up|increase)\b.*\b(sound|audio)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.VOLUME_DOWN,
                "patterns": [
                    r"\b(decrease|lower|turn\s*down)\b.*\bvolume\b",
                    r"\bvolume\s*down\b",
                    r"\b(turn\s*down|decrease)\b.*\b(sound|audio)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.MUTE,
                "patterns": [
                    r"\bmute\b",
                    r"\bturn\s*off\b.*\b(sound|audio|volume)\b",
                ],
                "priority": 7
            },
            {
                "intent": Intent.UNMUTE,
                "patterns": [
                    r"\bunmute\b",
                    r"\bturn\s*on\b.*\b(sound|audio|volume)\b",
                ],
                "priority": 7
            },
            
            # Display control
            {
                "intent": Intent.SET_BRIGHTNESS,
                "patterns": [
                    r"\b(set|change|adjust)\b.*\bbrightness\b.*\b(to)\b\s*(\d+)",
                    r"\bbrightness\b.*\b(to)\b\s*(\d+)",
                ],
                "entity_extractors": ["brightness_value"],
                "priority": 6
            },
            {
                "intent": Intent.INCREASE_BRIGHTNESS,
                "patterns": [
                    r"\b(increase|raise|turn\s*up)\b.*\bbrightness\b",
                    r"\bbrightness\s*up\b",
                ],
                "priority": 6
            },
            {
                "intent": Intent.DECREASE_BRIGHTNESS,
                "patterns": [
                    r"\b(decrease|lower|turn\s*down)\b.*\bbrightness\b",
                    r"\bbrightness\s*down\b",
                ],
                "priority": 6
            },
            
            # System information
            {
                "intent": Intent.CHECK_BATTERY,
                "patterns": [
                    r"\b(battery|power)\b.*\b(level|status|percentage|health)\b",
                    r"\b(check|what|how)\b.*\bbattery\b",
                ],
                "priority": 5
            },
            {
                "intent": Intent.CHECK_CPU,
                "patterns": [
                    r"\bcpu\b.*\b(usage|temperature|load)\b",
                    r"\b(check|what)\b.*\bcpu\b",
                ],
                "priority": 5
            },
            {
                "intent": Intent.CHECK_RAM,
                "patterns": [
                    r"\b(ram|memory)\b.*\b(usage|available|free)\b",
                    r"\b(check|how\s*much)\b.*\b(ram|memory)\b",
                ],
                "priority": 5
            },
            
            # Productivity
            {
                "intent": Intent.TAKE_SCREENSHOT,
                "patterns": [
                    r"\b(take|capture|snap)\b.*\b(screenshot|screen\s*shot|picture)\b",
                    r"\bscreenshot\b",
                ],
                "priority": 6
            },
            {
                "intent": Intent.SET_TIMER,
                "patterns": [
                    r"\b(set|start|create)\b.*\btimer\b.*\b(for)\b\s*(\d+)",
                    r"\btimer\b.*\b(for)\b\s*(\d+)\s*(minute|second|hour)",
                ],
                "entity_extractors": ["duration", "unit"],
                "priority": 6
            },
            {
                "intent": Intent.CREATE_NOTE,
                "patterns": [
                    r"\b(create|make|write)\b.*\b(note|memo)\b",
                    r"\bnote\b.*\b(about|that)\b",
                ],
                "priority": 6
            },
            
            # Communication
            {
                "intent": Intent.SEND_EMAIL,
                "patterns": [
                    r"\b(send|write|compose)\b.*\b(email|mail)\b",
                    r"\bemail\b.*\b(to)\b",
                ],
                "priority": 6
            },
            
            # Settings
            {
                "intent": Intent.OPEN_SETTINGS,
                "patterns": [
                    r"\b(open|show)\b.*\bsettings\b",
                    r"\bsettings\b",
                ],
                "priority": 5
            },
            
            # AI/Chat - default fallback
            {
                "intent": Intent.CHAT,
                "patterns": [
                    r".+",  # Matches anything
                ],
                "priority": 1
            },
        ]
        
        logger.info(f"Loaded {len(self.patterns)} intent patterns")
    
    def process(self, text: str, context: Any = None) -> IntentMatch:
        """Process text and detect intent"""
        logger.debug(f"Processing text: {text}")
        
        text_lower = text.lower().strip()
        
        matches = []
        
        # Check all patterns
        for pattern_def in self.patterns:
            intent = pattern_def["intent"]
            priority = pattern_def.get("priority", 1)
            
            for pattern in pattern_def["patterns"]:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    confidence = min(0.95, 0.5 + (priority / 20))
                    
                    # Extract entities
                    entities = self._extract_entities(text, match, pattern_def)
                    
                    matches.append(IntentMatch(
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        pattern=pattern
                    ))
        
        # Sort by confidence and priority
        if matches:
            matches.sort(key=lambda m: m.confidence, reverse=True)
            best_match = matches[0]
            
            logger.info(f"Intent detected: {best_match.intent.value} (confidence: {best_match.confidence:.2f})")
            
            # Emit event
            self.event_bus.emit("intent_detected", {
                "intent": best_match.intent.value,
                "entities": best_match.entities,
                "confidence": best_match.confidence,
                "text": text
            })
            
            return best_match
        
        # No match found
        logger.warning(f"No intent matched for: {text}")
        
        unknown_match = IntentMatch(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            entities={}
        )
        
        self.event_bus.emit("intent_detected", {
            "intent": Intent.UNKNOWN.value,
            "entities": {},
            "confidence": 0.0,
            "text": text
        })
        
        return unknown_match
    
    def _extract_entities(self, text: str, match, pattern_def: Dict) -> Dict[str, Any]:
        """Extract entities from matched pattern"""
        entities = {}
        
        extractors = pattern_def.get("entity_extractors", [])
        groups = match.groups()
        
        # Map groups to entity names
        for i, extractor in enumerate(extractors):
            if i < len(groups) and groups[i]:
                entities[extractor] = groups[i].strip()
        
        # Special handling for specific intents
        intent = pattern_def["intent"]
        
        if intent == Intent.OPEN_APP and "app_name" not in entities:
            # Try to extract app name
            if groups:
                entities["app_name"] = groups[-1].strip()
        
        elif intent == Intent.SEARCH_WEB and "search_query" not in entities:
            # Extract search query
            if groups:
                entities["search_query"] = groups[-1].strip()
        
        elif intent == Intent.SET_BRIGHTNESS:
            # Extract numeric value
            for group in groups:
                if group and group.isdigit():
                    entities["brightness_value"] = int(group)
                    break
        
        elif intent == Intent.SET_TIMER:
            # Extract duration and unit
            for group in groups:
                if group and group.isdigit():
                    entities["duration"] = int(group)
                elif group and group in ["minute", "second", "hour", "minutes", "seconds", "hours"]:
                    entities["unit"] = group
        
        return entities
    
    def add_pattern(self, intent: Intent, pattern: str, priority: int = 5) -> None:
        """Add custom intent pattern"""
        self.patterns.append({
            "intent": intent,
            "patterns": [pattern],
            "priority": priority
        })
        logger.info(f"Added custom pattern for intent: {intent.value}")
    
    def get_available_intents(self) -> List[Intent]:
        """Get list of available intents"""
        return [p["intent"] for p in self.patterns]
