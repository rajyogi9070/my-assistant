"""
Entity extraction from natural language
"""
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Extracted entity"""
    name: str
    value: Any
    confidence: float = 1.0
    start: int = 0
    end: int = 0


class EntityExtractor:
    """Extract entities from natural language text"""
    
    def __init__(self):
        self.extractors = {
            'number': self._extract_numbers,
            'percentage': self._extract_percentages,
            'time': self._extract_time,
            'date': self._extract_dates,
            'email': self._extract_emails,
            'url': self._extract_urls,
            'app_name': self._extract_app_names,
            'file_path': self._extract_file_paths,
        }
        
        # Common application names
        self.app_aliases = {
            'chrome': 'Google Chrome',
            'firefox': 'Mozilla Firefox',
            'edge': 'Microsoft Edge',
            'explorer': 'Internet Explorer',
            'vscode': 'Visual Studio Code',
            'vs code': 'Visual Studio Code',
            'notepad': 'Notepad',
            'word': 'Microsoft Word',
            'excel': 'Microsoft Excel',
            'powerpoint': 'Microsoft PowerPoint',
            'spotify': 'Spotify',
            'discord': 'Discord',
            'slack': 'Slack',
            'teams': 'Microsoft Teams',
            'zoom': 'Zoom',
            'skype': 'Skype',
            'vlc': 'VLC Media Player',
            'obs': 'OBS Studio',
            'steam': 'Steam',
            'calculator': 'Calculator',
            'paint': 'Paint',
            'cmd': 'Command Prompt',
            'terminal': 'Windows Terminal',
            'powershell': 'PowerShell',
        }
        
        logger.info("Entity extractor initialized")
    
    def extract(self, text: str, entity_types: List[str] = None) -> Dict[str, Any]:
        """Extract entities from text"""
        if entity_types is None:
            entity_types = list(self.extractors.keys())
        
        entities = {}
        
        for entity_type in entity_types:
            if entity_type in self.extractors:
                result = self.extractors[entity_type](text)
                if result:
                    entities[entity_type] = result
        
        return entities
    
    def _extract_numbers(self, text: str) -> Optional[List[int]]:
        """Extract numbers from text"""
        numbers = re.findall(r'\b\d+\b', text)
        return [int(n) for n in numbers] if numbers else None
    
    def _extract_percentages(self, text: str) -> Optional[List[int]]:
        """Extract percentages from text"""
        percentages = re.findall(r'(\d+)\s*%', text)
        return [int(p) for p in percentages] if percentages else None
    
    def _extract_time(self, text: str) -> Optional[Dict[str, int]]:
        """Extract time from text"""
        # Match patterns like "10 minutes", "2 hours", "30 seconds"
        patterns = [
            r'(\d+)\s*(minute|minutes|min)',
            r'(\d+)\s*(hour|hours|hr)',
            r'(\d+)\s*(second|seconds|sec)',
        ]
        
        time_dict = {}
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                unit = match.group(2).lower()
                
                if 'minute' in unit or 'min' in unit:
                    time_dict['minutes'] = value
                elif 'hour' in unit or 'hr' in unit:
                    time_dict['hours'] = value
                elif 'second' in unit or 'sec' in unit:
                    time_dict['seconds'] = value
        
        return time_dict if time_dict else None
    
    def _extract_dates(self, text: str) -> Optional[str]:
        """Extract dates from text"""
        # Simple date patterns
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_emails(self, text: str) -> Optional[List[str]]:
        """Extract email addresses from text"""
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return emails if emails else None
    
    def _extract_urls(self, text: str) -> Optional[List[str]]:
        """Extract URLs from text"""
        urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            text
        )
        
        # Also match domain names
        domains = re.findall(r'\b[\w-]+\.(com|org|net|io|co|edu|gov)\b', text, re.IGNORECASE)
        if domains:
            for match in re.finditer(r'\b[\w-]+\.(com|org|net|io|co|edu|gov)\b', text, re.IGNORECASE):
                urls.append(match.group(0))
        
        return urls if urls else None
    
    def _extract_app_names(self, text: str) -> Optional[str]:
        """Extract application names from text"""
        text_lower = text.lower()
        
        # Check against known app aliases
        for alias, full_name in self.app_aliases.items():
            if alias in text_lower:
                return full_name
        
        # Try to extract from common patterns
        patterns = [
            r'\b(open|launch|start|run)\b\s+(.+?)(?:\s+and|\s+then|\.|$)',
            r'\b(close|quit|exit)\b\s+(.+?)(?:\s+and|\s+then|\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match and len(match.groups()) > 1:
                app_name = match.group(2).strip()
                # Clean up common words
                app_name = re.sub(r'\b(the|my|a|an)\b', '', app_name).strip()
                if app_name:
                    return app_name.title()
        
        return None
    
    def _extract_file_paths(self, text: str) -> Optional[str]:
        """Extract file paths from text"""
        # Windows paths
        windows_paths = re.findall(r'[A-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*', text)
        if windows_paths:
            return windows_paths[0]
        
        # Unix paths
        unix_paths = re.findall(r'(?:/[^/\s]+)+', text)
        if unix_paths:
            return unix_paths[0]
        
        return None
    
    def normalize_app_name(self, name: str) -> str:
        """Normalize application name to standard form"""
        name_lower = name.lower().strip()
        return self.app_aliases.get(name_lower, name)
    
    def extract_duration_seconds(self, text: str) -> Optional[int]:
        """Extract duration in seconds from text"""
        time_dict = self._extract_time(text)
        
        if not time_dict:
            return None
        
        total_seconds = 0
        total_seconds += time_dict.get('hours', 0) * 3600
        total_seconds += time_dict.get('minutes', 0) * 60
        total_seconds += time_dict.get('seconds', 0)
        
        return total_seconds if total_seconds > 0 else None
