# Main Application Loop Specification

## Overview

The MainLoop class serves as the central orchestrator for the Leadership Button application. It manages the complete application lifecycle, state transitions, and coordinates all components including audio handling, API interactions, and user input processing.

## Core Architecture

### State Management

The application operates as a state machine with the following states:

- **IDLE**: Waiting for user input (spacebar press)
- **RECORDING**: Actively recording audio (spacebar held down)
- **PROCESSING**: Processing recorded audio through STT → AI → TTS pipeline
- **SPEAKING**: Playing back AI-generated audio response
- **ERROR**: Handling errors and recovering to IDLE state

### Event System

The system responds to the following events:

- **Spacebar Press**: Transitions from IDLE to RECORDING, starts audio recording
- **Spacebar Release**: Transitions from RECORDING to PROCESSING, stops recording and begins processing
- **Processing Complete**: Transitions from PROCESSING to SPEAKING, begins audio playback
- **Playback Complete**: Transitions from SPEAKING to IDLE, ready for next interaction
- **Error Occurred**: Transitions to ERROR state, handles error and returns to IDLE

### State Transitions

```
IDLE → RECORDING (spacebar press)
RECORDING → PROCESSING (spacebar release)
PROCESSING → SPEAKING (processing complete)
SPEAKING → IDLE (playback complete)
ANY_STATE → ERROR (error occurred)
ERROR → IDLE (error handled)
```

## MainLoop Class Structure

### Constructor

```python
def __init__(self, config_path: Optional[str] = "config/api_config.json"):
    """
    Initialize the main application loop.

    Args:
        config_path: Path to the API configuration file. Defaults to "config/api_config.json"
    """
```

### Core Methods

#### State Management

- `start()`: Start the main application loop and keyboard listener
- `stop()`: Stop the application and cleanup resources
- `get_state()`: Get current application state
- `_transition_state(new_state: ApplicationState)`: Internal state transition method
- `_is_valid_transition(from_state: ApplicationState, to_state: ApplicationState) -> bool`: Validate state transitions
- `get_performance_stats() -> Dict[str, Any]`: Get application performance statistics

#### Event Handling

- `_handle_spacebar_press()`: Handle spacebar press event (start recording)
- `_handle_spacebar_release()`: Handle spacebar release event (stop recording)
- `_handle_recording_complete(audio_data: bytes)`: Process completed recording
- `_handle_api_response(response: Any)`: Handle API response and initiate playback
- `_handle_audio_complete()`: Handle audio playback completion
- `_handle_error(error: Exception)`: Handle errors and recover to IDLE state

### Keyboard Input Implementation

#### pynput Integration

The MainLoop uses the `pynput` library for robust, event-driven keyboard input monitoring:

```python
from pynput import keyboard

# Keyboard listener setup in start() method
self.keyboard_listener = keyboard.Listener(
    on_press=self.on_press,
    on_release=self.on_release)
self.keyboard_listener.start()
```

#### Event-Driven Input Handling

- **Global Input Detection**: Works regardless of application focus
- **Event Callbacks**: `on_press()` and `on_release()` handle keyboard events
- **Thread Safety**: Uses `threading.Event` for spacebar state management
- **Automatic Cleanup**: Keyboard listener properly stopped on application exit

#### Hold-to-Record Behavior

```python
def on_press(self, key):
    """Callback for key press events."""
    if key == keyboard.Key.space:
        if not self.spacebar_pressed_event.is_set():
            self.spacebar_pressed_event.set()
            if self.current_state == ApplicationState.IDLE:
                self._handle_spacebar_press()

def on_release(self, key):
    """Callback for key release events."""
    if key == keyboard.Key.space:
        if self.spacebar_pressed_event.is_set():
            self.spacebar_pressed_event.clear()
            if self.current_state == ApplicationState.RECORDING:
                self._handle_spacebar_release()
```

#### Threading Model

- **Main Thread**: Blocks on `keyboard_listener.join()` waiting for events
- **Listener Thread**: Handles keyboard events in background
- **Event Synchronization**: Uses `threading.Event` for state coordination
- **Graceful Shutdown**: Properly stops listener on application termination

#### Configuration and Initialization

- `_load_config(config_path: Optional[str]) -> Dict[str, Any]`: Load configuration from JSON file
- `_get_default_config() -> Dict[str, Any]`: Provide default configuration values
- `_initialize_components()`: Initialize audio handler, API client, and playback manager
- `_setup_mock_ai_provider()`: Set up mock AI provider for development/testing
- `_cleanup()`: Cleanup resources and stop background threads

## Component Integration

### AudioHandler Integration

- Manages audio recording and playback
- Provides AudioData objects with metadata
- Handles hardware-specific audio operations
- Supports both development and production audio configurations

### APIManager Integration

- Handles Google Cloud Speech-to-Text API calls
- Manages Google Cloud Text-to-Speech API calls
- Provides secure credential management
- Implements retry logic and error handling
- Supports LLM integration for AI processing

### AudioPlaybackManager Integration

- Centralized audio playback functionality
- Handles multiple audio formats and sources
- Provides consistent playback interface
- Supports debugging and audio saving

## Error Handling

### Error Recovery Strategy

1. **Immediate Error Capture**: All errors are logged with context
2. **State Recovery**: System attempts to return to IDLE state
3. **Resource Cleanup**: All resources are properly cleaned up
4. **User Feedback**: Clear error messages are provided
5. **Graceful Degradation**: System continues operating despite errors

### Error Types Handled

- **Audio Recording Errors**: Microphone access, hardware failures
- **API Errors**: Network issues, authentication failures, quota limits
- **Processing Errors**: Invalid audio data, transcription failures
- **Playback Errors**: Speaker access, audio format issues
- **Input Errors**: Keyboard listener failures, pynput initialization issues

## Configuration Management

### Configuration Sources

- **API Configuration**: Google Cloud credentials and settings
- **Audio Configuration**: Recording and playback parameters
- **Application Configuration**: Logging, performance, and behavior settings

### Environment Support

- **Development Mode**: Enhanced logging, debug features, test integration
- **Production Mode**: Optimized performance, minimal logging, error recovery
- **Test Mode**: Mock components, isolated testing, validation features

## Performance Considerations

### Optimization Strategies

- **Asynchronous Processing**: Non-blocking audio and API operations
- **Resource Management**: Efficient memory and CPU usage
- **Caching**: Audio data and API responses where appropriate
- **Background Threads**: Keyboard event listener and processing operations

### Monitoring and Metrics

- **Response Time**: Audio processing pipeline performance
- **Error Rates**: API and audio operation success rates
- **Resource Usage**: Memory and CPU consumption
- **User Interaction**: Spacebar press/release patterns

## Testing Integration

### Test Orchestration

- **Centralized Methods**: All business logic accessible via test methods
- **State Validation**: Test methods can verify application state
- **Component Isolation**: Individual components can be tested independently
- **Pipeline Validation**: Complete audio pipeline can be tested end-to-end

### Mock Support

- **LLM Mocking**: AI processing can be bypassed for audio pipeline testing
- **API Mocking**: External APIs can be mocked for isolated testing
- **Audio Mocking**: Audio hardware can be simulated for testing
- **Input Mocking**: Spacebar events can be simulated programmatically

## Security Considerations

### Credential Management

- **Environment Variables**: Secure storage of API credentials
- **Configuration Files**: Encrypted or protected configuration storage
- **Access Control**: Proper file permissions and access restrictions
- **Credential Rotation**: Support for credential updates and rotation

### Data Privacy

- **Audio Data**: Temporary storage and secure deletion
- **API Communications**: Encrypted transmission of audio data
- **Logging**: Sensitive data exclusion from logs
- **User Privacy**: No persistent storage of user interactions

## Future Extensibility

### Plugin Architecture

- **Component Plugins**: Modular audio and API components
- **Processing Plugins**: Extensible audio processing pipeline
- **Interface Plugins**: Alternative input methods (buttons, voice commands)
- **Output Plugins**: Multiple output formats and destinations

### Feature Additions

- **Multi-language Support**: Internationalization and localization
- **Voice Recognition**: Speaker identification and personalization
- **Advanced AI**: Enhanced conversation capabilities
- **Analytics**: Usage tracking and performance optimization
