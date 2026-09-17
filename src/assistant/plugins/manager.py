"""
Plugin management system
"""
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from assistant.core.event_bus import EventBus
from assistant.core.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Plugin information"""
    name: str
    version: str
    author: str
    description: str
    enabled: bool
    path: str
    module: Any = None


class PluginManager:
    """Manages plugin loading and lifecycle"""
    
    def __init__(self, config: ConfigManager, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugins_dir = Path(__file__).parent.parent / "plugins"
        
        logger.info("Plugin manager initialized")
    
    def load_all(self) -> None:
        """Load all enabled plugins"""
        if not self.config.config.plugins_enabled:
            logger.info("Plugins disabled in configuration")
            return
        
        logger.info("Loading plugins...")
        
        # Scan plugins directory
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created plugins directory: {self.plugins_dir}")
            return
        
        # Load builtin plugins
        builtin_dir = self.plugins_dir / "builtin"
        if builtin_dir.exists():
            for plugin_path in builtin_dir.glob("*/__init__.py"):
                self._load_plugin(plugin_path.parent)
        
        # Load user plugins
        for plugin_path in self.plugins_dir.glob("*/__init__.py"):
            if "builtin" not in str(plugin_path):
                self._load_plugin(plugin_path.parent)
        
        logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def _load_plugin(self, plugin_dir: Path) -> bool:
        """Load a single plugin"""
        try:
            plugin_name = plugin_dir.name
            
            # Check if already loaded
            if plugin_name in self.plugins:
                logger.warning(f"Plugin already loaded: {plugin_name}")
                return False
            
            # Load plugin module
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                plugin_dir / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"Failed to load plugin spec: {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin metadata
            plugin_info = PluginInfo(
                name=getattr(module, '__plugin_name__', plugin_name),
                version=getattr(module, '__version__', '1.0.0'),
                author=getattr(module, '__author__', 'Unknown'),
                description=getattr(module, '__description__', 'No description'),
                enabled=True,
                path=str(plugin_dir),
                module=module
            )
            
            # Initialize plugin
            if hasattr(module, 'setup'):
                module.setup(self.event_bus, self.config)
            
            self.plugins[plugin_name] = plugin_info
            
            logger.info(f"Loaded plugin: {plugin_info.name} v{plugin_info.version}")
            
            self.event_bus.emit("plugin_loaded", {
                "name": plugin_info.name,
                "version": plugin_info.version
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_dir}: {e}", exc_info=True)
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        try:
            if plugin_name not in self.plugins:
                logger.warning(f"Plugin not loaded: {plugin_name}")
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Call cleanup if available
            if plugin.module and hasattr(plugin.module, 'cleanup'):
                plugin.module.cleanup()
            
            del self.plugins[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            
            self.event_bus.emit("plugin_unloaded", {
                "name": plugin_name
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}", exc_info=True)
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        if plugin_name in self.plugins:
            plugin_path = Path(self.plugins[plugin_name].path)
            self.unload_plugin(plugin_name)
            return self._load_plugin(plugin_path)
        return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all loaded plugins"""
        return list(self.plugins.values())
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Get all enabled plugins"""
        return [p for p in self.plugins.values() if p.enabled]
