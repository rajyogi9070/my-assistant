"""
Main entry point for My Assistant
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from assistant.core.engine import AssistantEngine
from assistant.core.config import ConfigManager
from assistant.utils.logger import setup_logging


def main():
    """Main entry point for CLI mode"""
    setup_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting My Assistant...")
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Create and run engine
        engine = AssistantEngine(config)
        engine.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def main_gui():
    """Main entry point for GUI mode"""
    setup_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting My Assistant GUI...")
    
    try:
        # Import GUI components
        from assistant.ui.app import AssistantApp
        
        # Create and run GUI
        app = AssistantApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Default to GUI mode
    if "--cli" in sys.argv:
        main()
    else:
        main_gui()
