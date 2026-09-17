# My Assistant

A production-grade AI-powered Windows desktop voice assistant with full system control, natural language understanding, and enterprise-level architecture.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)

## ✨ Features

### 🎤 Voice Control
- **Wake Word Detection**: "Hey Assistant" or custom wake words
- **Real-time Speech Recognition**: Multiple backends (Vosk offline, Google, Whisper)
- **Natural Text-to-Speech**: Multiple voice options with speed/pitch control
- **Noise Suppression**: Works in noisy environments

### 🖥️ System Control
- Power management (shutdown, restart, sleep, lock)
- Display control (brightness, resolution)
- System monitoring (CPU, RAM, disk, battery)
- Windows settings access

### 📱 Application Control
- Launch/close applications
- Window management
- Process management
- Application switching

### 🌐 Web Operations
- Web search
- Website navigation
- YouTube integration
- Browser control

### 📁 File Management
- Create/move/delete files and folders
- File search
- Document operations

### 🎵 Media Control
- Play/pause/skip media
- Volume control
- Media key integration

### 📸 Productivity
- Screenshots
- Timers and reminders
- Notes
- Screen recording

### 🤖 AI Features
- Chat with AI (OpenAI, Anthropic, Google, Local)
- Context-aware conversations
- Smart memory and learning
- Task automation

### 🔌 Plugin System
- Extensible architecture
- Third-party plugins
- Plugin marketplace support

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.10+
- Microphone
- Internet connection (for online features)

### Installation

#### From Source
```bash
# Clone the repository
git clone https://github.com/rajyogi9070/my-assistant.git
cd my-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the assistant
python -m assistant
```

#### Using the Installer
1. Download `MyAssistant-Setup-1.0.0.exe` from [Releases](https://github.com/rajyogi9070/my-assistant/releases)
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu or Desktop

## 📖 Usage

### Wake Word
Say **"Hey Assistant"** or **"Hello Assistant"** to activate the assistant.

### Voice Commands

#### System Control
- "Shut down the computer"
- "Restart the computer"
- "Lock the screen"
- "Increase brightness to 80%"
- "What's my battery level?"

#### Applications
- "Open Chrome"
- "Close Spotify"
- "Open Visual Studio Code"
- "Switch applications"

#### Web
- "Search for AI news"
- "Open YouTube"
- "Go to github.com"

#### Files
- "Create a folder named Projects"
- "Take a screenshot"
- "Open my Documents folder"

#### Media
- "Play music"
- "Pause"
- "Volume up"
- "Next track"

#### Productivity
- "Set a timer for 10 minutes"
- "Create a note"
- "Take a screenshot"

### Text Input
You can also type commands in the chat interface.

## 🏗️ Architecture

```
src/assistant/
├── core/              # Core engine and configuration
├── engines/           # Speech, NLP, and AI engines
│   ├── speech/       # Wake word, STT, TTS
│   ├── nlp/          # Intent detection, entity extraction
│   └── ai/           # LLM integration
├── commands/          # Command handlers
│   ├── system/       # System control
│   ├── apps/         # Application control
│   ├── web/          # Web operations
│   ├── files/        # File management
│   ├── media/        # Media control
│   └── productivity/ # Productivity features
├── ui/               # User interface
├── services/         # Background services
├── plugins/          # Plugin system
├── memory/           # Conversation memory
├── automation/       # Task scheduling
└── utils/            # Utilities
```

## 🔧 Configuration

Configuration is stored in `%APPDATA%\MyAssistant\config.json`.

### Key Settings
- **Wake Word**: Customize wake word and sensitivity
- **Voice**: Select voice, speed, and pitch
- **AI Provider**: Choose between OpenAI, Anthropic, Google, or local models
- **Theme**: Dark, light, or system theme
- **Privacy**: Control data collection and storage

## 🧪 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linters
black src/
ruff check src/
```

### Build Executable
```bash
# Build with PyInstaller
python scripts/build.py build

# Create installer
python scripts/build.py installer

# Full build pipeline
python scripts/build.py all
```

### Creating Plugins
See [Plugin Development Guide](docs/PLUGINS.md) for creating custom plugins.

## 📚 Documentation

- [User Manual](docs/USER_MANUAL.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Plugin Development](docs/PLUGINS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition
- [OpenWakeWord](https://github.com/dscripka/openWakeWord) - Wake word detection
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - GUI automation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/rajyogi9070/my-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rajyogi9070/my-assistant/discussions)
- **Email**: dev@myassistant.app

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Advanced automation workflows
- [ ] Voice biometrics
- [ ] Cloud sync
- [ ] Mobile companion app
- [ ] Smart home integration
- [ ] More AI providers
- [ ] Plugin marketplace

---

Built with ❤️ by the My Assistant Team
