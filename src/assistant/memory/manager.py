"""
Memory and conversation management
"""
import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from assistant.core.event_bus import EventBus
from assistant.core.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class Interaction:
    """User interaction record"""
    timestamp: str
    user_input: str
    intent: str
    response: str
    success: bool
    entities: Dict[str, Any] = None


class MemoryManager:
    """Manages conversation history and user preferences"""
    
    def __init__(self, config: ConfigManager, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        
        # Database setup
        self.db_path = self._get_db_path()
        self._init_database()
        
        # In-memory cache
        self.recent_interactions: List[Interaction] = []
        self.user_preferences: Dict[str, Any] = {}
        
        logger.info("Memory manager initialized")
    
    def _get_db_path(self) -> Path:
        """Get database path"""
        import os
        if os.name == 'nt':
            data_dir = Path(os.environ.get('APPDATA', Path.home())) / 'MyAssistant'
        else:
            data_dir = Path.home() / '.myassistant'
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / 'memory.db'
    
    def _init_database(self) -> None:
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    intent TEXT,
                    response TEXT,
                    success BOOLEAN,
                    entities TEXT
                )
            ''')
            
            # Create preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
    
    def start(self) -> None:
        """Start memory manager"""
        self._load_preferences()
        self._load_recent_interactions()
        logger.info("Memory manager started")
    
    def stop(self) -> None:
        """Stop memory manager"""
        logger.info("Memory manager stopped")
    
    def save_interaction(self, context: Any, result: Any) -> None:
        """Save interaction to database"""
        try:
            interaction = Interaction(
                timestamp=datetime.now().isoformat(),
                user_input=context.user_input if hasattr(context, 'user_input') else "",
                intent=context.intent if hasattr(context, 'intent') else "",
                response=result.message if hasattr(result, 'message') else "",
                success=result.success if hasattr(result, 'success') else False,
                entities=context.entities if hasattr(context, 'entities') else {}
            )
            
            # Add to cache
            self.recent_interactions.append(interaction)
            if len(self.recent_interactions) > 100:
                self.recent_interactions.pop(0)
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interactions (timestamp, user_input, intent, response, success, entities)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                interaction.timestamp,
                interaction.user_input,
                interaction.intent,
                interaction.response,
                interaction.success,
                json.dumps(interaction.entities)
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Saved interaction: {interaction.intent}")
            
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}", exc_info=True)
    
    def _load_recent_interactions(self) -> None:
        """Load recent interactions from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_input, intent, response, success, entities
                FROM interactions
                ORDER BY id DESC
                LIMIT 100
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            self.recent_interactions = [
                Interaction(
                    timestamp=row[0],
                    user_input=row[1],
                    intent=row[2],
                    response=row[3],
                    success=bool(row[4]),
                    entities=json.loads(row[5]) if row[5] else {}
                )
                for row in reversed(rows)
            ]
            
            logger.info(f"Loaded {len(self.recent_interactions)} recent interactions")
            
        except Exception as e:
            logger.error(f"Failed to load interactions: {e}")
    
    def get_recent_interactions(self, limit: int = 10) -> List[Interaction]:
        """Get recent interactions"""
        return self.recent_interactions[-limit:]
    
    def get_interaction_history(self, days: int = 7) -> List[Interaction]:
        """Get interaction history for specified days"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_input, intent, response, success, entities
                FROM interactions
                WHERE timestamp >= datetime('now', ? || ' days')
                ORDER BY id DESC
            ''', (f"-{days}",))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                Interaction(
                    timestamp=row[0],
                    user_input=row[1],
                    intent=row[2],
                    response=row[3],
                    success=bool(row[4]),
                    entities=json.loads(row[5]) if row[5] else {}
                )
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get interaction history: {e}")
            return []
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference"""
        try:
            self.user_preferences[key] = value
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Set preference: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set preference: {e}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.user_preferences.get(key, default)
    
    def _load_preferences(self) -> None:
        """Load preferences from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM preferences')
            rows = cursor.fetchall()
            conn.close()
            
            for key, value in rows:
                try:
                    self.user_preferences[key] = json.loads(value)
                except:
                    self.user_preferences[key] = value
            
            logger.info(f"Loaded {len(self.user_preferences)} preferences")
            
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
    
    def get_frequent_intents(self, limit: int = 5) -> List[str]:
        """Get most frequently used intents"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT intent, COUNT(*) as count
                FROM interactions
                WHERE intent IS NOT NULL
                GROUP BY intent
                ORDER BY count DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get frequent intents: {e}")
            return []
    
    def clear_history(self) -> None:
        """Clear all interaction history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM interactions')
            
            conn.commit()
            conn.close()
            
            self.recent_interactions.clear()
            
            logger.info("Interaction history cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
