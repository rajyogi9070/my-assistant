"""
Web browser commands
"""
import logging
import webbrowser
import urllib.parse
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class WebCommands(BaseCommandHandler):
    """Web browser command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
    
    def search(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Search the web"""
        try:
            query = entities.get("search_query", "")
            
            if not query:
                return CommandResult(
                    success=False,
                    message="What would you like me to search for?"
                )
            
            logger.info(f"Searching for: {query}")
            
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open in default browser
            webbrowser.open(search_url)
            
            return CommandResult(
                success=True,
                message=f"Searching for {query}."
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to perform web search.",
                error=str(e)
            )
    
    def open_website(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Open a website"""
        try:
            url = entities.get("url", "")
            
            if not url:
                return CommandResult(
                    success=False,
                    message="Which website would you like me to open?"
                )
            
            # Add https if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Opening website: {url}")
            
            webbrowser.open(url)
            
            return CommandResult(
                success=True,
                message=f"Opening {url}."
            )
            
        except Exception as e:
            logger.error(f"Open website failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to open the website.",
                error=str(e)
            )
    
    def open_youtube(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Open YouTube"""
        try:
            query = entities.get("search_query", "")
            
            if query:
                # Search on YouTube
                encoded_query = urllib.parse.quote_plus(query)
                url = f"https://www.youtube.com/results?search_query={encoded_query}"
                message = f"Searching YouTube for {query}."
            else:
                # Open YouTube homepage
                url = "https://www.youtube.com"
                message = "Opening YouTube."
            
            logger.info(f"Opening YouTube: {url}")
            
            webbrowser.open(url)
            
            return CommandResult(
                success=True,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Open YouTube failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to open YouTube.",
                error=str(e)
            )
