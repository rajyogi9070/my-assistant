# Developer Guide

## Architecture Overview

My Assistant follows a modular, event-driven architecture with clear separation of concerns.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer (CustomTkinter)              │
├─────────────────────────────────────────────────────────────┤
│                      Event Bus (Pub/Sub)                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Wake Word   │    Speech    │     NLP      │      AI        │
│   Engine     │  Recognition │    Engine    │    Engine      │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                    Command Dispatcher                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   System     │     App      │     Web      │    Media       │
│   Commands   │   Commands   │   Commands   │   Commands     │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                     Services Layer                           │
│  (Memory, Plugins, Notifications, Scheduler, Monitor)       │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Event-Driven**: Components communicate through events
2. **Modular**: Each feature is a separate module
3. **Extensible**: Plugin system for custom features
4. **Testable**: Dependency injection and interfaces
5. **Async-Ready**: Support for asynchronous operations

## Project Structure

```
src/assistant/
├── __init__.py          # Package metadata
├── __main__.py          # Entry point
├── core/                # Core components
│   ├── engine.py       # Main assistant engine
│   ├── config.py       # Configuration management
│   └── event_bus.py    # Event system
├── engines/            # Processing engines
│   ├── speech/         # Audio processing
│   │   ├── wake_word.py
│   │   ├── recognizer.py
│   │   └── synthesizer.py
│   ├── nlp/            # Natural language
│   │   ├── intent.py
│   │   └── entities.py
│   └── ai/             # AI integration
│       └── llm.py
├── commands/           # Command handlers
│   ├── base.py
│   ├── dispatcher.py
│   ├── system/
│   ├── apps/
│   ├── web/
│   ├── files/
│   ├── media/
│   └── productivity/
├── ui/                 # User interface
│   ├── app.py
│   └── components/
├── services/           # Background services
│   └── system_monitor.py
├── plugins/            # Plugin system
│   └── manager.py
├── memory/             # Data persistence
│   └── manager.py
├── automation/         # Task scheduling
│   └── scheduler.py
├── notifications/      # Alert system
│   └── manager.py
└── utils/              # Utilities
    └── logger.py
```

## Development Setup

### Prerequisites
- Python 3.10+
- Windows 10/11 (for full functionality)
- Git

### Environment Setup

```bash
# Clone repository
git clone https://github.com/rajyogi9070/my-assistant.git
cd my-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=assistant --cov-report=html

# Run specific test file
pytest tests/unit/test_intent.py -v
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Adding New Features

### 1. Adding a New Intent

Edit `src/assistant/engines/nlp/intent.py`:

```python
class Intent(Enum):
    # ... existing intents ...
    MY_NEW_INTENT = "my_new_intent"

# Add pattern
{
    "intent": Intent.MY_NEW_INTENT,
    "patterns": [
        r"\b(do|execute)\b.*\b(something)\b",
    ],
    "priority": 7
}
```

### 2. Creating a Command Handler

Create `src/assistant/commands/my_feature/my_commands.py`:

```python
from assistant.commands.base import BaseCommandHandler, CommandResult

class MyCommands(BaseCommandHandler):
    def my_action(self, entities: Dict[str, Any], context: Any = None) -> CommandResult:
        try:
            # Your logic here
            return CommandResult(
                success=True,
                message="Action completed successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message="Action failed",
                error=str(e)
            )
```

### 3. Registering the Handler

Edit `src/assistant/commands/dispatcher.py`:

```python
from assistant.commands.my_feature.my_commands import MyCommands

class CommandDispatcher:
    def __init__(self, event_bus: EventBus):
        # ...
        self.my_commands = MyCommands(event_bus)
        
        self.handlers = {
            # ...
            Intent.MY_NEW_INTENT: self.my_commands.my_action,
        }
```

## Plugin Development

### Plugin Structure

```
plugins/
└── my_plugin/
    ├── __init__.py
    └── README.md
```

### Plugin Template

```python
# plugins/my_plugin/__init__.py

__plugin_name__ = "My Plugin"
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "A custom plugin for My Assistant"

def setup(event_bus, config):
    """Called when plugin is loaded"""
    # Register event handlers
    event_bus.on("wake_word_detected", on_wake_word)
    
    # Register commands
    # ...

def cleanup():
    """Called when plugin is unloaded"""
    # Cleanup resources
    pass

def on_wake_word(event):
    """Handle wake word detection"""
    print("Wake word detected!")
```

## Building & Distribution

### Build Executable

```bash
# Using build script
python scripts/build.py build

# Or directly with PyInstaller
pyinstaller build/assistant.spec --clean
```

### Create Installer

1. Install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Open `installer/setup.iss`
3. Compile the script
4. Installer will be in `dist/`

## Debugging

### Logging

Logs are written to `%APPDATA%\MyAssistant\logs\`

Enable debug logging:
```python
from assistant.utils.logger import setup_logging
import logging

setup_logging(level=logging.DEBUG)
```

### Common Issues

**Import Errors**: Ensure you're running from the project root with `python -m assistant`

**Audio Issues**: Check PyAudio installation and microphone permissions

**UI Issues**: Ensure CustomTkinter is properly installed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused
- Write tests for new features

## Questions?

- Check existing issues on GitHub
- Read the documentation
- Ask in GitHub Discussions
