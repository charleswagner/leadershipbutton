# The Leadership & EQ Coach

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Phase%201%20Complete-brightgreen.svg)](docs/plans/technical_roadmap.md)

An AI-powered leadership coaching device that provides instant, personalized guidance through natural voice interaction. Users simply hold down the spacebar (or physical button), speak their leadership challenge, and receive immediate coaching feedback through high-quality audio responses.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud account with Speech-to-Text and Text-to-Speech APIs enabled
- Microphone and speakers/headphones

### Bootstrap Development Environment

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd leadership_button
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud authentication:**

   ```bash
   gcloud auth application-default login
   ```

4. **Configure the spec-driven workflow:**
   - Open `docs/settings/spec_driven_prompt.md`
   - Copy the entire contents
   - In Cursor, open your "Spec-Driven Python" custom mode
   - Paste the contents into the "Instructions" box

5. **Start the application:**

   ```bash
   python src/main.py
   ```

6. **Use the application:**
   - Hold the spacebar to record your leadership question
   - Release to process and hear the AI response
   - Continue the conversation with follow-up questions

## 📖 Project Overview

The Leadership Button is a comprehensive AI-powered leadership coaching system that combines:

- **Voice-First Interface**: Natural hold-to-record interaction
- **Advanced AI Integration**: Gemini-powered leadership coaching (Phase 2)
- **Persistent Conversations**: Firestore-based conversation history (Phase 2)
- **Multi-User Support**: Personalized experiences for multiple users (Phase 2)
- **Robust Architecture**: Centralized, testable, and maintainable design

### Current Status

- ✅ **Phase 1 Complete**: Core functionality, testing framework, documentation
- 🔄 **Phase 2 In Progress**: AI integration, conversational features, multi-user support
- 📋 **Phase 3 Planned**: Hardware integration (Raspberry Pi)
- 📋 **Phase 4 Planned**: Enterprise deployment

## 🏗️ Architecture

### Core Components

| Component                | Purpose                                    | Status      |
| ------------------------ | ------------------------------------------ | ----------- |
| **MainLoop**             | Central orchestrator with state management | ✅ Complete |
| **AudioHandler**         | Audio recording and playback               | ✅ Complete |
| **APIManager**           | Google Cloud API integration               | ✅ Complete |
| **AudioPlaybackManager** | Centralized audio playback                 | ✅ Complete |
| **ConversationManager**  | Persistent conversations (Firestore)       | 📋 Phase 2  |
| **UserManager**          | Multi-user support and personalization     | 📋 Phase 2  |

### Application States

```
IDLE → RECORDING → PROCESSING → SPEAKING → IDLE
  ↓
ERROR → IDLE
```

### Data Flow

1. **User Input**: Spacebar press → Audio recording
2. **Speech Processing**: Audio → Google Cloud Speech-to-Text
3. **AI Processing**: Text → Gemini AI → Leadership response
4. **Audio Output**: Response → Google Cloud Text-to-Speech → Playback
5. **Conversation**: Context preserved for follow-up questions

## 📁 Project Structure

```
leadershipbutton/
├── config/                          # Configuration files
│   ├── api_config.json             # Main API configuration
│   ├── api_config.development.json # Development settings
│   └── api_config.production.json  # Production settings
├── docs/                           # Documentation
│   ├── logs/                       # Build logs
│   │   └── buildlog.log           # Development activity log
│   ├── plans/                      # Project planning
│   │   ├── product_roadmap.md     # Product development roadmap
│   │   └── technical_roadmap.md   # Technical implementation roadmap
│   ├── settings/                   # Project settings
│   │   ├── spec_driven_prompt.md  # AI development workflow
│   │   └── bootstrap_py.md        # Bootstrap instructions
│   └── specs/                      # Feature specifications
│       └── leadership_button/      # Module specifications
│           ├── spec_api_client.md      # API client specification
│           ├── spec_audio_handler.md   # Audio handling specification
│           ├── spec_audio_playback.md  # Audio playback specification
│           ├── spec_conversation_manager.md # Conversation management
│           └── spec_main_loop.md       # Main loop specification
├── src/                           # Source code
│   ├── main.py                    # Application entry point
│   └── leadership_button/         # Main application modules
│       ├── __init__.py
│       ├── api_client.py          # Google Cloud API integration
│       ├── audio_handler.py       # Audio recording and playback
│       ├── audio_playback.py      # Centralized audio playback
│       └── main_loop.py           # Main application orchestrator
├── tests/                         # Test files and data
│   ├── data/                      # Test data files
│   ├── audio_test_utils.py        # Audio testing utilities
│   ├── test_audio_workflow.py     # Audio workflow tests
│   ├── test_main_loop.py          # Main loop tests
│   ├── test_main_loop_steps.py    # Step-by-step tests
│   └── test_main_loop_keyboard_emulator.py # Keyboard emulation tests
├── requirements.txt               # Python dependencies
├── service-account.json           # Google Cloud credentials
├── .cursor-rules.json             # Cursor IDE configuration
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 Installation

### System Requirements

- **Operating System**: macOS, Linux, Windows
- **Python**: 3.9 or higher
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB free space
- **Audio**: Microphone and speakers/headphones

### Dependencies

#### Core Dependencies

```bash
# Audio handling
pyaudio>=0.2.11

# Google Cloud APIs
google-cloud-speech>=2.0.0
google-cloud-texttospeech>=2.0.0
google-auth>=2.0.0

# Configuration and environment
python-dotenv>=1.0.0

# Retry logic and reliability
tenacity>=8.0.0

# Keyboard input
pynput
```

#### Development Dependencies

```bash
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Logging
coloredlogs>=15.0
```

#### Optional Dependencies

```bash
# Raspberry Pi GPIO (only needed on Pi)
# RPi.GPIO>=0.7.1
```

### Installation Steps

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd leadership_button
   ```

2. **Create virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud:**

   ```bash
   # Install Google Cloud CLI
   # Follow: https://cloud.google.com/sdk/docs/install

   # Authenticate
   gcloud auth application-default login

   # Enable required APIs
   gcloud services enable speech.googleapis.com
   gcloud services enable texttospeech.googleapis.com
   ```

5. **Configure the application:**
   ```bash
   # Copy and edit configuration
   cp config/api_config.development.json config/api_config.json
   # Edit config/api_config.json with your settings
   ```

## ⚙️ Configuration

### Configuration Files

| File                                 | Purpose              | Environment      |
| ------------------------------------ | -------------------- | ---------------- |
| `config/api_config.json`             | Main configuration   | All environments |
| `config/api_config.development.json` | Development settings | Development only |
| `config/api_config.production.json`  | Production settings  | Production only  |

### Configuration Sections

#### API Settings

```json
{
  "api_settings": {
    "timeout_seconds": 30,
    "retry_max_attempts": 3,
    "retry_delay_seconds": 1.0,
    "enable_logging": true,
    "log_level": "INFO"
  }
}
```

#### Google Cloud Speech-to-Text

```json
{
  "google_cloud": {
    "speech_to_text": {
      "model": "latest_long",
      "language_code": "en-US",
      "sample_rate_hertz": 16000,
      "enable_automatic_punctuation": true,
      "audio_encoding": "LINEAR16"
    }
  }
}
```

#### Google Cloud Text-to-Speech

```json
{
  "google_cloud": {
    "text_to_speech": {
      "voice_name": "en-US-Wavenet-D",
      "language_code": "en-US",
      "speaking_rate": 1.0,
      "pitch": 0.0,
      "volume_gain_db": 0.0
    }
  }
}
```

#### Audio Settings

```json
{
  "audio_settings": {
    "input_sample_rate": 16000,
    "output_sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "max_recording_duration": 30
  }
}
```

#### Performance Settings

```json
{
  "performance": {
    "max_audio_buffer_mb": 100,
    "concurrent_requests_limit": 3,
    "cache_tts_responses": true,
    "cache_duration_seconds": 3600
  }
}
```

#### Development Settings

```json
{
  "development": {
    "mock_api_calls": false,
    "save_debug_audio": false,
    "verbose_logging": false,
    "simulate_network_delays": false
  }
}
```

### Environment Variables

| Variable                         | Purpose                     | Required |
| -------------------------------- | --------------------------- | -------- |
| `GOOGLE_CLOUD_PROJECT`           | Google Cloud project ID     | Yes      |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key | Yes      |
| `LEADERSHIP_BUTTON_CONFIG`       | Path to config file         | No       |

## 🎮 Usage

### Command Line Interface

The application provides a comprehensive CLI with multiple modes and options:

#### Basic Usage

```bash
# Start in development mode (default)
python src/main.py

# Start in production mode
python src/main.py --mode production

# Use custom configuration file
python src/main.py --config /path/to/config.json
```

#### Testing and Debugging

```bash
# Run all tests
python src/main.py --test

# Show application status
python src/main.py --status

# Record audio to file for testing
python src/main.py --record test_audio.wav

# Show version information
python src/main.py --version
```

#### Complete Command Reference

| Command         | Description      | Example                |
| --------------- | ---------------- | ---------------------- |
| `--mode, -m`    | Application mode | `--mode production`    |
| `--config, -c`  | Config file path | `--config custom.json` |
| `--test, -t`    | Run tests        | `--test`               |
| `--status, -s`  | Show status      | `--status`             |
| `--record, -r`  | Record audio     | `--record test.wav`    |
| `--version, -v` | Show version     | `--version`            |

### Application Modes

#### Development Mode

- Enhanced logging and debugging
- Mock AI provider for testing
- Verbose error messages
- Debug audio file saving

#### Production Mode

- Optimized performance
- Minimal logging
- Real AI integration
- Error recovery

### Interactive Usage

1. **Start the application:**

   ```bash
   python src/main.py
   ```

2. **Wait for initialization:**

   ```
   🎯 Leadership & EQ Coach v1.0
   Mode: Development
   Press Ctrl+C to stop
   ```

3. **Record your question:**
   - Hold the spacebar down
   - Speak your leadership challenge
   - Release the spacebar

4. **Listen to the response:**
   - The AI will process your question
   - You'll hear the coaching response
   - Follow-up questions may be asked

5. **Continue the conversation:**
   - Hold spacebar again for follow-up
   - Continue the coaching session
   - Press Ctrl+C to exit

## 🔌 API Reference

### Core Classes

#### MainLoop

Central orchestrator for the application.

```python
from src.leadership_button.main_loop import MainLoop

# Initialize
main_loop = MainLoop(config_path="config/api_config.json")

# Start the application
main_loop.start()

# Get current state
state = main_loop.get_state()

# Get performance stats
stats = main_loop.get_performance_stats()

# Stop the application
main_loop.stop()
```

**Key Methods:**

- `start()`: Start the main application loop
- `stop()`: Stop the application and cleanup
- `get_state()`: Get current application state
- `get_performance_stats()`: Get performance statistics

#### APIManager

Manages Google Cloud API interactions.

```python
from src.leadership_button.api_client import APIManager, APIConfig

# Initialize
config = APIConfig("config/api_config.json")
api_manager = APIManager(config)

# Initialize the manager
api_manager.initialize()

# Speech to text
text = api_manager.speech_to_text(audio_data)

# Text to speech
audio_response = api_manager.text_to_speech("Hello, world!")

# Process conversation turn
response = api_manager.process_conversation_turn(audio_data)

# Get API status
status = api_manager.get_api_status()
```

**Key Methods:**

- `speech_to_text(audio_data)`: Convert audio to text
- `text_to_speech(text)`: Convert text to speech
- `process_conversation_turn(audio_data)`: Complete conversation processing
- `get_api_status()`: Get API health status

#### AudioHandler

Handles audio recording and playback.

```python
from src.leadership_button.audio_handler import AudioHandler, AudioConfig

# Initialize
config = AudioConfig()
audio_handler = AudioHandler(config)

# Start recording
success = audio_handler.start_recording()

# Stop recording and get audio data
audio_data = audio_handler.stop_recording()

# Play audio
success = audio_handler.play_audio(audio_bytes)

# Check status
is_recording = audio_handler.is_recording()
is_playing = audio_handler.is_playing()
```

**Key Methods:**

- `start_recording()`: Start audio recording
- `stop_recording()`: Stop recording and return audio data
- `play_audio(audio_data)`: Play audio data
- `is_recording()`: Check if currently recording
- `is_playing()`: Check if currently playing

#### AudioPlaybackManager

Centralized audio playback management.

```python
from src.leadership_button.audio_playback import AudioPlaybackManager

# Initialize
playback_manager = AudioPlaybackManager()

# Play audio response
success = playback_manager.play_audio_response(audio_response, "description")

# Play and wait for completion
success = playback_manager.play_audio_and_wait(audio_response, "description")

# Get audio information
info = playback_manager.get_audio_info(audio_response)

# Save debug audio
success = playback_manager.save_audio_debug(audio_response, "debug.raw")
```

**Key Methods:**

- `play_audio_response(audio_response, description)`: Play audio without waiting
- `play_audio_and_wait(audio_response, description)`: Play audio and wait for completion
- `get_audio_info(audio_response)`: Get audio metadata
- `save_audio_debug(audio_response, filepath)`: Save audio for debugging

### Data Models

#### AudioData

Container for audio data with metadata.

```python
from src.leadership_button.audio_handler import AudioData

# Create audio data
audio_data = AudioData(
    data=audio_bytes,
    format="wav",
    sample_rate=16000,
    channels=1
)

# Access properties
duration = audio_data.duration
file_size = audio_data.get_file_size()

# Save to file
success = audio_data.save_to_file("output.wav")
```

#### TranscriptionResult

Result from speech-to-text processing.

```python
from src.leadership_button.api_client import TranscriptionResult

# Create result
result = TranscriptionResult(
    text="Hello, world!",
    confidence=0.95,
    alternatives=["Hello world", "Hello, world"]
)

# Check confidence
is_high_confidence = result.is_high_confidence(threshold=0.8)

# Get best alternative
best_text = result.get_best_alternative()
```

#### VoiceConfig

Configuration for text-to-speech voice.

```python
from src.leadership_button.api_client import VoiceConfig

# Create voice config
voice_config = VoiceConfig(
    name="en-US-Wavenet-D",
    language_code="en-US"
)

# Convert to dictionary
config_dict = voice_config.to_dict()
```

### Application States

```python
from src.leadership_button.main_loop import ApplicationState

# Available states
ApplicationState.IDLE        # Waiting for input
ApplicationState.RECORDING   # Recording audio
ApplicationState.PROCESSING  # Processing audio/API
ApplicationState.SPEAKING    # Playing response
ApplicationState.ERROR       # Error state
```

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**

   ```bash
   git clone <your-repo-url>
   cd leadership_button
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure spec-driven workflow:**
   - Open `docs/settings/spec_driven_prompt.md`
   - Copy the entire contents
   - In Cursor, create a new custom mode called "Spec-Driven Python"
   - Paste the contents into the "Instructions" box

3. **Set up Google Cloud:**

   ```bash
   gcloud auth application-default login
   gcloud services enable speech.googleapis.com
   gcloud services enable texttospeech.googleapis.com
   ```

4. **Configure development settings:**
   ```bash
   cp config/api_config.development.json config/api_config.json
   # Edit config/api_config.json as needed
   ```

### Development Workflow

This project follows a **spec-driven development approach**:

1. **Write Specifications**: Create `.md` files in `docs/specs/`
2. **Implement Code**: Write code in `src/leadership_button/`
3. **Write Tests**: Create tests in `tests/`
4. **Update Documentation**: Keep specs and code in sync

### Key Development Files

| File                                  | Purpose                       |
| ------------------------------------- | ----------------------------- |
| `docs/settings/spec_driven_prompt.md` | AI development workflow       |
| `docs/plans/technical_roadmap.md`     | Technical implementation plan |
| `docs/plans/product_roadmap.md`       | Product development plan      |
| `docs/specs/`                         | Feature specifications        |
| `.cursor-rules.json`                  | Cursor IDE configuration      |

### Code Style and Standards

- **Python**: PEP 8 compliance
- **Documentation**: Comprehensive docstrings
- **Testing**: 100% test coverage for business logic
- **Error Handling**: Graceful degradation and recovery
- **Logging**: Structured logging with appropriate levels

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_main_loop.py

# Run with coverage
python -m pytest tests/ --cov=src/leadership_button

# Run with verbose output
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_main_loop.py::TestMainLoop::test_initialization
```

### Test Categories

| Category              | Files                                 | Purpose                      |
| --------------------- | ------------------------------------- | ---------------------------- |
| **Unit Tests**        | `test_main_loop_steps.py`             | Individual component testing |
| **Integration Tests** | `test_audio_workflow.py`              | End-to-end workflow testing  |
| **Keyboard Tests**    | `test_main_loop_keyboard_emulator.py` | Input simulation testing     |
| **Utility Tests**     | `audio_test_utils.py`                 | Audio testing utilities      |

### Test Utilities

#### AudioTestUtils

```python
from tests.audio_test_utils import AudioTestUtils

# Generate test tone
test_audio = AudioTestUtils.generate_test_tone(duration=3.0, frequency=440)

# Get system audio devices
devices = AudioTestUtils.get_system_audio_devices()

# Test audio playback
success = AudioTestUtils.test_audio_playback(audio_data)
```

#### Keyboard Emulator

```python
from tests.test_main_loop_keyboard_emulator import KeyboardEmulator

# Create emulator
emulator = KeyboardEmulator()

# Simulate spacebar press
emulator.press_spacebar()

# Simulate spacebar release
emulator.release_spacebar()

# Simulate conversation
emulator.simulate_conversation("Hello, how are you?")
```

### Debug Tools

#### Audio Recording

```bash
# Record test audio
python src/main.py --record test_audio.wav
```

#### Debug Audio Playback

```bash
# Test audio playback
python tests/debug_audio_playback.py
```

#### Debug Recording

```bash
# Test audio recording
python tests/debug_recording.py
```

## 🔧 Troubleshooting

### Common Issues

#### Audio Issues

**Problem**: "PyAudio not available"

```bash
# Install PyAudio
pip install pyaudio

# On macOS with Homebrew
brew install portaudio
pip install pyaudio

# On Ubuntu/Debian
sudo apt-get install python3-pyaudio
```

**Problem**: "No audio input device found"

```bash
# Check available devices
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i) for i in range(p.get_device_count())])"

# Set device index in config
# Edit config/api_config.json and set "device_index": 0
```

**Problem**: "Audio playback not working"

```bash
# Test audio system
python tests/debug_audio_playback.py

# Check volume settings
# Ensure speakers/headphones are connected and unmuted
```

#### Google Cloud Issues

**Problem**: "Authentication failed"

```bash
# Re-authenticate
gcloud auth application-default login

# Check credentials
gcloud auth list

# Set project
gcloud config set project YOUR_PROJECT_ID
```

**Problem**: "API not enabled"

```bash
# Enable required APIs
gcloud services enable speech.googleapis.com
gcloud services enable texttospeech.googleapis.com

# Check enabled APIs
gcloud services list --enabled
```

**Problem**: "Quota exceeded"

```bash
# Check quota usage
gcloud compute regions describe us-central1

# Request quota increase
# Go to Google Cloud Console > APIs & Services > Quotas
```

#### Application Issues

**Problem**: "Configuration file not found"

```bash
# Check config file exists
ls -la config/

# Copy default config
cp config/api_config.development.json config/api_config.json
```

**Problem**: "Tests failing"

```bash
# Run tests with verbose output
python -m pytest tests/ -v

# Check test dependencies
pip install pytest pytest-cov

# Run specific failing test
python -m pytest tests/test_main_loop.py::TestMainLoop::test_initialization -v
```

**Problem**: "Application stuck in processing"

```bash
# Check logs
tail -f logs/application.log

# Restart application
# Press Ctrl+C and restart

# Check API connectivity
python -c "from src.leadership_button.api_client import test_google_cloud_connection; print(test_google_cloud_connection())"
```

### Debug Commands

#### System Diagnostics

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i) for i in range(p.get_device_count())])"

# Check Google Cloud authentication
gcloud auth list

# Check API status
python src/main.py --status
```

#### Performance Monitoring

```bash
# Monitor CPU and memory
top -p $(pgrep -f "python src/main.py")

# Monitor disk usage
du -sh logs/ config/

# Monitor network connections
netstat -an | grep :443
```

#### Log Analysis

```bash
# View recent logs
tail -f logs/application.log

# Search for errors
grep ERROR logs/application.log

# Search for specific user
grep "user_id" logs/application.log

# Monitor API calls
grep "API" logs/application.log
```

### Performance Tuning

#### Audio Optimization

```json
{
  "audio_settings": {
    "chunk_size": 2048, // Increase for better performance
    "max_recording_duration": 60, // Increase for longer recordings
    "input_sample_rate": 8000 // Decrease for faster processing
  }
}
```

#### API Optimization

```json
{
  "api_settings": {
    "timeout_seconds": 60, // Increase for slow connections
    "retry_max_attempts": 5, // Increase for reliability
    "retry_delay_seconds": 2.0 // Increase for rate limiting
  }
}
```

#### Performance Settings

```json
{
  "performance": {
    "max_audio_buffer_mb": 200, // Increase for large audio files
    "concurrent_requests_limit": 5, // Increase for multiple users
    "cache_tts_responses": true, // Enable for faster responses
    "cache_duration_seconds": 7200 // Increase cache duration
  }
}
```

## 🤝 Contributing

### Development Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow spec-driven development**:
   - Write/update specifications in `docs/specs/`
   - Implement code in `src/leadership_button/`
   - Write tests in `tests/`
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Code Standards

- **Python**: Follow PEP 8 style guide
- **Documentation**: Include comprehensive docstrings
- **Testing**: Maintain 100% test coverage
- **Error Handling**: Implement graceful error recovery
- **Logging**: Use appropriate log levels

### Specification Guidelines

All new features must have corresponding specifications:

1. **Create spec file**: `docs/specs/leadership_button/spec_feature_name.md`
2. **Follow spec template**: Use existing specs as templates
3. **Include all sections**: Overview, architecture, API, testing
4. **Keep specs updated**: Ensure code matches specifications

### Testing Requirements

- **Unit Tests**: Test individual components
- **Integration Tests**: Test complete workflows
- **Performance Tests**: Test under load
- **Error Tests**: Test error conditions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check `docs/` directory for detailed documentation
- **Specifications**: Review `docs/specs/` for feature details
- **Roadmaps**: Check `docs/plans/` for development plans
- **Issues**: Create an issue on GitHub for bugs or feature requests

### Community

- **Discussions**: Use GitHub Discussions for questions
- **Contributions**: Follow the contributing guidelines
- **Feedback**: Share your experience and suggestions

### Resources

- **Google Cloud Speech-to-Text**: [Documentation](https://cloud.google.com/speech-to-text)
- **Google Cloud Text-to-Speech**: [Documentation](https://cloud.google.com/text-to-speech)
- **PyAudio**: [Documentation](https://people.csail.mit.edu/hubert/pyaudio/)
- **Python Testing**: [pytest Documentation](https://docs.pytest.org/)

---

**The Leadership Button** - Transforming leadership development through AI-powered voice coaching.

_Built with ❤️ using Python, Google Cloud, and spec-driven development._
