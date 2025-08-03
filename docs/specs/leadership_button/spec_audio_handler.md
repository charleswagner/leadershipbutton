# Audio Handler Specification

## Overview

The AudioHandler module provides comprehensive audio recording and playback capabilities for the Leadership Button application. It manages all audio hardware interactions, supports both development and production environments, and integrates seamlessly with the centralized AudioPlaybackManager for consistent audio operations.

## Core Architecture

### AudioHandler Class

The primary class that manages all audio operations including recording, playback, and hardware integration.

### AudioConfig Class

Configuration class that defines audio parameters for recording and playback operations.

### AudioData Class

Data structure that encapsulates audio data with metadata including sample rate, channels, format, and duration.

## AudioHandler Class Structure

### Constructor

```python
def __init__(self, config: AudioConfig = None):
    """
    Initialize the audio handler with configuration.

    Args:
        config: Audio configuration parameters. If None, uses default config.
    """
```

### Core Recording Methods

```python
def start_recording(self) -> bool:
    """
    Start audio recording from the microphone.

    Returns:
        True if recording started successfully, False otherwise
    """

def stop_recording(self) -> Optional[AudioData]:
    """
    Stop audio recording and return the recorded audio data.

    Returns:
        AudioData object containing the recorded audio, or None if failed
    """

def is_recording(self) -> bool:
    """
    Check if currently recording audio.

    Returns:
        True if recording, False otherwise
    """
```

### Core Playback Methods

```python
def play_audio(self, audio_data: bytes) -> bool:
    """
    Play audio data through the speakers.

    Args:
        audio_data: Raw audio bytes to play

    Returns:
        True if playback started successfully, False otherwise
    """

def is_playing(self) -> bool:
    """
    Check if currently playing audio.

    Returns:
        True if playing, False otherwise
    """

def stop_playback(self) -> bool:
    """
    Stop current audio playback.

    Returns:
        True if playback stopped successfully, False otherwise
    """
```

### Hardware Integration Methods

```python
def get_available_devices(self) -> Dict[str, List[str]]:
    """
    Get list of available audio input and output devices.

    Returns:
        Dictionary with 'input' and 'output' device lists
    """

def set_input_device(self, device_name: str) -> bool:
    """
    Set the audio input device for recording.

    Args:
        device_name: Name of the input device

    Returns:
        True if device set successfully, False otherwise
    """

def set_output_device(self, device_name: str) -> bool:
    """
    Set the audio output device for playback.

    Args:
        device_name: Name of the output device

    Returns:
        True if device set successfully, False otherwise
    """
```

### Utility Methods

```python
def get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
    """
    Get information about audio data.

    Args:
        audio_data: Raw audio bytes

    Returns:
        Dictionary with audio information (sample_rate, channels, duration, etc.)
    """

def save_audio(self, audio_data: bytes, filepath: str) -> bool:
    """
    Save audio data to a file.

    Args:
        audio_data: Raw audio bytes to save
        filepath: Path to save the audio file

    Returns:
        True if saved successfully, False otherwise
    """

def load_audio(self, filepath: str) -> Optional[bytes]:
    """
    Load audio data from a file.

    Args:
        filepath: Path to the audio file

    Returns:
        Raw audio bytes or None if failed
    """

def cleanup(self) -> None:
    """
    Clean up audio resources and close connections.
    """
```

## AudioConfig Class Structure

### Constructor

```python
def __init__(self,
             sample_rate: int = 16000,
             channels: int = 1,
             format: int = pyaudio.paInt16,
             chunk_size: int = 1024,
             input_device: Optional[str] = None,
             output_device: Optional[str] = None):
    """
    Initialize audio configuration.

    Args:
        sample_rate: Audio sample rate in Hz (default: 16000)
        channels: Number of audio channels (default: 1 for mono)
        format: Audio format (default: 16-bit integer)
        chunk_size: Audio processing chunk size (default: 1024)
        input_device: Specific input device name (default: system default)
        output_device: Specific output device name (default: system default)
    """
```

### Configuration Properties

- `sample_rate`: Audio sample rate in Hz
- `channels`: Number of audio channels (1=mono, 2=stereo)
- `format`: Audio format (paInt16, paFloat32, etc.)
- `chunk_size`: Audio processing chunk size
- `input_device`: Audio input device name
- `output_device`: Audio output device name
- `recording_timeout`: Maximum recording duration in seconds
- `playback_timeout`: Maximum playback duration in seconds

## AudioData Class Structure

### Constructor

```python
def __init__(self,
             data: bytes,
             sample_rate: int,
             channels: int,
             format: int,
             duration: Optional[float] = None):
    """
    Initialize audio data object.

    Args:
        data: Raw audio bytes
        sample_rate: Audio sample rate in Hz
        channels: Number of audio channels
        format: Audio format
        duration: Audio duration in seconds (calculated if None)
    """
```

### AudioData Properties

- `data`: Raw audio bytes
- `sample_rate`: Audio sample rate in Hz
- `channels`: Number of audio channels
- `format`: Audio format
- `duration`: Audio duration in seconds
- `size_bytes`: Size of audio data in bytes
- `frame_count`: Number of audio frames

## Integration with AudioPlaybackManager

### Centralized Playback

The AudioHandler integrates with the centralized AudioPlaybackManager to provide consistent audio playback across the application:

```python
# AudioHandler provides the core playback functionality
def play_audio(self, audio_data: bytes) -> bool:
    """
    Core audio playback method used by AudioPlaybackManager.
    """

# AudioPlaybackManager orchestrates playback operations
def play_audio_response(self, audio_response: Any, description: str = "audio") -> bool:
    """
    Centralized method that uses AudioHandler for actual playback.
    """
```

### Format Support

The AudioHandler supports multiple audio formats through the AudioPlaybackManager:

- **Raw Audio Bytes**: Direct playback of audio data
- **AudioData Objects**: Structured audio data with metadata
- **WAV Files**: Standard WAV format files
- **Google TTS Responses**: Audio responses from Google Cloud TTS API

## Hardware Integration

### Development Environment

- **PyAudio**: Cross-platform audio I/O library
- **System Default Devices**: Uses system default microphone and speakers
- **Device Selection**: Supports manual device selection for testing
- **Error Simulation**: Simulates hardware errors for testing

### Production Environment (Raspberry Pi)

- **RPi.GPIO**: Hardware button integration (Phase 2)
- **ALSA Audio**: Linux audio system integration
- **Hardware Optimization**: Optimized for Raspberry Pi audio hardware
- **Button Debouncing**: Hardware button debouncing and noise filtering

### Hardware Button Integration (Phase 2)

```python
def setup_hardware_button(self, pin: int = 18) -> bool:
    """
    Setup hardware button for recording control.

    Args:
        pin: GPIO pin number for the button

    Returns:
        True if setup successful, False otherwise
    """

def handle_button_press(self) -> None:
    """
    Handle hardware button press event.
    """

def handle_button_release(self) -> None:
    """
    Handle hardware button release event.
    """
```

## Error Handling

### Audio Recording Errors

- **Device Access**: Microphone not available or in use
- **Permission Errors**: Insufficient permissions for audio access
- **Hardware Failures**: Microphone malfunction or disconnection
- **Format Errors**: Unsupported audio format or parameters

### Audio Playback Errors

- **Device Access**: Speakers not available or in use
- **Format Errors**: Unsupported audio format for playback
- **Hardware Failures**: Speaker malfunction or disconnection
- **Buffer Errors**: Audio buffer overflow or underflow

### Error Recovery Strategies

1. **Automatic Retry**: Retry failed operations with exponential backoff
2. **Device Fallback**: Fall back to alternative audio devices
3. **Format Conversion**: Convert audio to supported format
4. **Resource Cleanup**: Proper cleanup of failed operations
5. **Error Reporting**: Comprehensive error logging and reporting

## Performance Optimization

### Recording Optimization

- **Streaming Processing**: Process audio in real-time chunks
- **Memory Management**: Efficient memory usage for long recordings
- **Buffer Optimization**: Optimized buffer sizes for different sample rates
- **Thread Safety**: Thread-safe recording operations

### Playback Optimization

- **Asynchronous Playback**: Non-blocking audio playback
- **Buffer Management**: Efficient audio buffer management
- **Format Optimization**: Optimized audio format for playback
- **Device Optimization**: Optimized device settings for performance

### Resource Management

- **Connection Pooling**: Reuse audio connections when possible
- **Memory Cleanup**: Automatic cleanup of unused audio resources
- **Device Caching**: Cache device information for faster access
- **Thread Management**: Efficient thread usage for audio operations

## Testing Integration

### Unit Testing

- **Component Isolation**: Test individual audio operations
- **Mock Hardware**: Simulate audio hardware for testing
- **Error Simulation**: Test error handling and recovery
- **Performance Testing**: Test audio processing performance

### Integration Testing

- **End-to-End Testing**: Test complete audio pipeline
- **Device Testing**: Test with real audio hardware
- **Format Testing**: Test various audio formats
- **Error Recovery Testing**: Test error recovery scenarios

### Test Utilities

```python
def create_test_audio(duration: float = 1.0, frequency: float = 440.0) -> bytes:
    """
    Create test audio data for testing.

    Args:
        duration: Audio duration in seconds
        frequency: Audio frequency in Hz

    Returns:
        Test audio data as bytes
    """

def compare_audio(audio1: bytes, audio2: bytes) -> float:
    """
    Compare two audio samples and return similarity score.

    Args:
        audio1: First audio sample
        audio2: Second audio sample

    Returns:
        Similarity score (0.0 to 1.0)
    """
```

## Configuration Examples

### Development Configuration

```python
config = AudioConfig(
    sample_rate=16000,
    channels=1,
    format=pyaudio.paInt16,
    chunk_size=1024,
    recording_timeout=30.0,
    playback_timeout=60.0
)
```

### Production Configuration (Raspberry Pi)

```python
config = AudioConfig(
    sample_rate=16000,
    channels=1,
    format=pyaudio.paInt16,
    chunk_size=2048,
    input_device="USB Microphone",
    output_device="HDMI Audio",
    recording_timeout=60.0,
    playback_timeout=120.0
)
```

## Security Considerations

### Audio Data Security

- **Temporary Storage**: Audio data not persisted to disk
- **Memory Protection**: Secure memory handling for audio data
- **Access Control**: Proper permissions for audio device access
- **Data Encryption**: Encrypted transmission of audio data

### Device Security

- **Device Validation**: Validate audio device capabilities
- **Permission Checks**: Verify audio device permissions
- **Access Logging**: Log audio device access for security
- **Error Handling**: Secure error handling without data leakage

## Future Enhancements

### Advanced Features

- **Noise Reduction**: Real-time noise reduction and filtering
- **Echo Cancellation**: Echo cancellation for better audio quality
- **Voice Activity Detection**: Automatic voice activity detection
- **Audio Compression**: Audio compression for efficient storage

### Multi-Device Support

- **Bluetooth Audio**: Support for Bluetooth audio devices
- **USB Audio**: Enhanced USB audio device support
- **Network Audio**: Network audio streaming capabilities
- **Multi-Channel Audio**: Support for multi-channel audio systems

### Performance Improvements

- **Hardware Acceleration**: GPU acceleration for audio processing
- **Parallel Processing**: Parallel audio processing capabilities
- **Caching**: Audio data caching for improved performance
- **Optimization**: Continuous performance optimization
