# User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Voice Commands](#voice-commands)
3. [Settings](#settings)
4. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch
1. Launch My Assistant from the Start Menu or Desktop shortcut
2. Grant microphone permissions when prompted
3. The assistant will start in the system tray
4. Say "Hey Assistant" to activate

### Interface Overview
- **Sidebar**: Navigation between Dashboard, Chat, and Settings
- **Dashboard**: System metrics and quick actions
- **Chat**: Text and voice interaction
- **Settings**: Customize the assistant

## Voice Commands

### Activation
- "Hey Assistant" - Activate the assistant
- "Hello Assistant" - Alternative wake word

### System Commands
| Command | Action |
|---------|--------|
| "Shut down the computer" | Power off (with confirmation) |
| "Restart the computer" | Reboot system |
| "Lock the screen" | Lock Windows |
| "Go to sleep" | Sleep mode |

### Application Control
| Command | Action |
|---------|--------|
| "Open Chrome" | Launch browser |
| "Open Visual Studio Code" | Launch VS Code |
| "Close Spotify" | Terminate app |
| "Switch applications" | Alt+Tab |

### Media Control
| Command | Action |
|---------|--------|
| "Play music" | Resume playback |
| "Pause" | Pause playback |
| "Volume up" | Increase volume |
| "Volume down" | Decrease volume |
| "Mute" | Mute audio |
| "Next track" | Skip forward |

### Web Operations
| Command | Action |
|---------|--------|
| "Search for [query]" | Google search |
| "Open YouTube" | Launch YouTube |
| "Go to [website]" | Open website |

### System Information
| Command | Action |
|---------|--------|
| "What's my battery level?" | Battery status |
| "Check CPU usage" | CPU information |
| "How much RAM do I have?" | Memory info |
| "System information" | Full system specs |

### Productivity
| Command | Action |
|---------|--------|
| "Take a screenshot" | Capture screen |
| "Set a timer for 10 minutes" | Start timer |
| "Create a note" | New note |

## Settings

### General
- **Theme**: Dark, Light, or System
- **Language**: Interface language
- **Start with Windows**: Auto-launch on boot
- **Minimize to tray**: Hide in system tray

### Voice & Speech
- **Wake Word**: Choose activation phrase
- **Voice**: Select TTS voice
- **Speech Rate**: Adjust speaking speed
- **Volume**: Set voice volume

### AI & Intelligence
- **AI Provider**: OpenAI, Anthropic, Google, or Local
- **Model**: Choose AI model
- **Memory**: Enable conversation memory

## Troubleshooting

### Microphone Not Working
1. Check Windows Sound Settings
2. Ensure microphone is selected as default
3. Grant microphone permissions to My Assistant
4. Restart the application

### Wake Word Not Responding
1. Increase wake word sensitivity in Settings
2. Reduce background noise
3. Speak clearly and directly into microphone
4. Check that wake word detection is enabled

### Commands Not Recognized
1. Speak slowly and clearly
2. Try rephrasing the command
3. Check internet connection (for online recognition)
4. Switch to offline mode (Vosk) if needed

### Performance Issues
1. Close unnecessary applications
2. Disable unused features in Settings
3. Switch to offline speech recognition
4. Reduce animation effects

### Application Crashes
1. Check log files in `%APPDATA%\MyAssistant\logs\`
2. Update to the latest version
3. Reset settings to defaults
4. Reinstall the application

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Space` | Activate assistant |
| `Ctrl+Shift+M` | Mute microphone |
| `Ctrl+Q` | Quit application |
| `Esc` | Cancel current operation |

## Privacy & Security

- All voice processing can be done offline
- Conversation history is stored locally
- AI API keys are encrypted
- No data is shared without consent
- You can delete all data in Settings

## Getting Help

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/rajyogi9070/my-assistant/issues)
- **Email**: support@myassistant.app
