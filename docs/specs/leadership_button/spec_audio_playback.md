# Audio Playback Module Specification

## Overview

The AudioPlaybackManager module provides a unified interface for playing audio from various sources including Google TTS API responses, AudioData objects, raw audio bytes, and WAV files. It centralizes all audio playback functionality and handles format conversion automatically.

## Core Architecture

### Purpose

- **Unified Interface**: Single point for all audio playback operations
- **Format Agnostic**: Handles multiple audio formats and sources automatically
- **Error Recovery**: Robust error handling and timeout mechanisms
- **Resource Management**: Proper cleanup and resource management

### Supported Audio Sources

- Google Cloud Text-to-Speech API responses
- AudioData objects from the audio_handler module
- Raw audio bytes
- WAV files (by file path)
- Any object with a `.data` attribute containing audio bytes

## AudioPlaybackManager Class Structure

### Constructor

```python
def __init__(self, audio_config: Optional[AudioConfig] = None):
    """
    Initialize the audio playback manager.

    Args:
        audio_config: Audio configuration. If None, uses default config.
    """
```

### Core Methods

#### Primary Playback Methods

- `play_audio_response(audio_response: Any, description: str = "audio") -> bool`: Play audio from any source without waiting
- `play_audio_and_wait(audio_response: Any, description: str = "audio") -> bool`: Play audio and wait for completion with timeout

#### Audio Data Processing

- `_extract_audio_data(audio_response: Any) -> Optional[bytes]`: Extract raw audio bytes from any response type
- `get_audio_info(audio_response: Any) -> dict`: Get detailed information about audio response

#### Utility Methods

- `save_audio_debug(audio_response: Any, filepath: str) -> bool`: Save audio to file for debugging purposes
- `cleanup()`: Clean up audio handler resources

## Audio Source Handling

### Supported Input Types

#### AudioData Objects

```python
# From audio_handler module
audio_data = AudioData(data=bytes, format="wav", sample_rate=16000, channels=1)
manager.play_audio_response(audio_data, "recorded_audio")
```

#### Raw Bytes

```python
# Direct audio bytes
audio_bytes = b'\x00\x01\x02...'
manager.play_audio_response(audio_bytes, "raw_audio")
```

#### API Response Objects

```python
# Objects with .data attribute
api_response = SomeAPIResponse()  # Has .data attribute with audio bytes
manager.play_audio_response(api_response, "api_response")
```

#### File Paths

```python
# WAV file path
manager.play_audio_response("/path/to/audio.wav", "wav_file")
```

## Playback Behavior

### Non-blocking Playback

```python
# Start playback and return immediately
success = manager.play_audio_response(audio_data, "background_audio")
```

### Blocking Playback with Timeout

```python
# Play and wait for completion (max 5 seconds)
success = manager.play_audio_and_wait(audio_data, "foreground_audio")
```

### Timeout Handling

- **Default Timeout**: 5 seconds for `play_audio_and_wait()`
- **Timeout Action**: Automatically stops playback and logs warning
- **Return Value**: `False` if timeout occurs

## Error Handling

### Error Recovery Strategy

1. **Graceful Degradation**: Continue operation despite individual playback failures
2. **Detailed Logging**: Comprehensive error logging with context
3. **Resource Cleanup**: Automatic cleanup on errors
4. **Return Status**: Boolean return values for all operations

### Error Types Handled

- **Format Extraction Errors**: Unknown or invalid audio formats
- **Playback Initialization Errors**: Audio hardware unavailable
- **Timeout Errors**: Playback takes too long to complete
- **File System Errors**: Invalid file paths or permissions
- **Resource Errors**: Memory or audio device issues

## Audio Information Extraction

### get_audio_info() Return Format

```python
{
    'type': 'AudioData',           # Type of input object
    'size_bytes': 44100,           # Size in bytes
    'sample_rate': 16000,          # Sample rate (if available)
    'channels': 1,                 # Number of channels (if available)
    'format': 'wav',               # Audio format (if available)
    'duration': 2.75               # Duration in seconds (if available)
}
```

## Integration Points

### AudioHandler Integration

- **Direct Usage**: Uses AudioHandler for actual playback operations
- **Configuration**: Shares AudioConfig with AudioHandler
- **State Monitoring**: Monitors playback state through AudioHandler

### MainLoop Integration

- **State Machine**: Integrates with application state management
- **Event Handling**: Called from main loop state handlers
- **Error Propagation**: Reports errors back to main loop

## Convenience Functions

### Module-Level Functions

```python
# Standalone playback functions
play_audio(audio_response, description) -> bool
play_audio_and_wait(audio_response, description) -> bool
get_audio_info(audio_response) -> dict
```

### Automatic Resource Management

- **Auto-Cleanup**: Convenience functions handle resource cleanup automatically
- **Isolated Operations**: Each function call is completely independent
- **Exception Safety**: Resources cleaned up even if exceptions occur

## Performance Considerations

### Optimization Strategies

- **Lazy Initialization**: AudioHandler created only when needed
- **Format Caching**: Efficient audio format detection
- **Memory Management**: Minimal memory footprint for audio data
- **Timeout Prevention**: Prevents hanging on problematic audio

### Resource Usage

- **Memory Efficient**: Streams audio data without large buffers
- **CPU Optimized**: Minimal processing overhead
- **Thread Safe**: Safe for use in multi-threaded environments

## Debugging Support

### Debug Features

- **Audio Saving**: Save any audio response to file for analysis
- **Detailed Logging**: Comprehensive logging at multiple levels
- **Format Inspection**: Detailed audio format information
- **Error Context**: Rich error information with full context

### Debug File Formats

```python
# Save raw audio for debugging
manager.save_audio_debug(audio_response, "debug_output.raw")
```

## Security Considerations

### Data Privacy

- **No Persistent Storage**: Audio data not stored permanently
- **Memory Cleanup**: Audio data cleared from memory after use
- **File Permissions**: Respects file system permissions
- **Error Information**: Sensitive data not exposed in error messages

### Resource Protection

- **Timeout Limits**: Prevents resource exhaustion
- **Error Boundaries**: Contains errors within playback operations
- **Resource Limits**: Respects system audio resource limits

## Future Extensibility

### Plugin Architecture Support

- **Format Plugins**: Extensible for new audio formats
- **Output Plugins**: Support for different output devices
- **Processing Plugins**: Audio effects and processing
- **Monitoring Plugins**: Playback analytics and monitoring

### Enhancement Areas

- **Multi-Device Support**: Multiple audio output devices
- **Advanced Formats**: Support for compressed audio formats
- **Real-time Processing**: Audio effects and real-time processing
- **Network Streaming**: Support for network audio sources
