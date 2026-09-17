"""
File management commands
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any

from assistant.core.event_bus import EventBus
from assistant.commands.base import BaseCommandHandler, CommandResult

logger = logging.getLogger(__name__)


class FileCommands(BaseCommandHandler):
    """File management command handlers"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
    
    def create_folder(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Create a new folder"""
        try:
            folder_name = entities.get("folder_name", "").strip()
            
            if not folder_name:
                return CommandResult(
                    success=False,
                    message="What should I name the folder?"
                )
            
            # Default to Desktop
            desktop = Path.home() / "Desktop"
            folder_path = desktop / folder_name
            
            logger.info(f"Creating folder: {folder_path}")
            
            if folder_path.exists():
                return CommandResult(
                    success=False,
                    message=f"A folder named {folder_name} already exists."
                )
            
            folder_path.mkdir(parents=True)
            
            return CommandResult(
                success=True,
                message=f"Created folder {folder_name} on your Desktop."
            )
            
        except Exception as e:
            logger.error(f"Create folder failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to create the folder.",
                error=str(e)
            )
    
    def open_file(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Open a file"""
        try:
            file_path = entities.get("file_path", "")
            
            if not file_path:
                return CommandResult(
                    success=False,
                    message="Which file would you like me to open?"
                )
            
            path = Path(file_path)
            
            if not path.exists():
                return CommandResult(
                    success=False,
                    message=f"File not found: {file_path}"
                )
            
            logger.info(f"Opening file: {path}")
            
            # Open with default application
            import platform
            if platform.system() == "Windows":
                os.startfile(str(path))
            elif platform.system() == "Darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
            
            return CommandResult(
                success=True,
                message=f"Opening {path.name}."
            )
            
        except Exception as e:
            logger.error(f"Open file failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to open the file.",
                error=str(e)
            )
    
    def move_file(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Move a file or folder"""
        try:
            source = entities.get("source_path", "")
            destination = entities.get("destination_path", "")
            
            if not source or not destination:
                return CommandResult(
                    success=False,
                    message="Please specify both source and destination paths."
                )
            
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return CommandResult(
                    success=False,
                    message=f"Source not found: {source}"
                )
            
            logger.info(f"Moving {source_path} to {dest_path}")
            
            shutil.move(str(source_path), str(dest_path))
            
            return CommandResult(
                success=True,
                message=f"Moved {source_path.name} to {dest_path}."
            )
            
        except Exception as e:
            logger.error(f"Move file failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to move the file.",
                error=str(e)
            )
    
    def delete_file(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        """Delete a file or folder"""
        try:
            file_path = entities.get("file_path", "")
            
            if not file_path:
                return CommandResult(
                    success=False,
                    message="Which file would you like me to delete?"
                )
            
            path = Path(file_path)
            
            if not path.exists():
                return CommandResult(
                    success=False,
                    message=f"File not found: {file_path}"
                )
            
            # Require confirmation for deletion
            self.event_bus.emit("confirmation_required", {
                "action": "delete",
                "message": f"Are you sure you want to delete {path.name}?"
            })
            
            logger.info(f"Deleting: {path}")
            
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(str(path))
            
            return CommandResult(
                success=True,
                message=f"Deleted {path.name}."
            )
            
        except Exception as e:
            logger.error(f"Delete file failed: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="Failed to delete the file.",
                error=str(e)
            )
