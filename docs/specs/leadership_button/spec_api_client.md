# API Client Specification

## Overview

The APIManager module provides comprehensive integration with Google Cloud APIs for speech processing and AI interactions. It manages Speech-to-Text (STT), Text-to-Speech (TTS), and Language Model (LLM) operations with secure credential management, error handling, and retry logic. The module supports both real API calls and mocking for testing purposes.

## Core Architecture

### APIManager Class

The primary class that manages all API interactions including STT, TTS, and LLM operations.

### APIConfig Class

Configuration class that defines API credentials, endpoints, and operational parameters.

### APIResponse Class

Data structure that encapsulates API responses with metadata and error information.

## APIManager Class Structure

### Constructor

```python
def __init__(self, config: APIConfig):
    """
    Initialize the API manager with configuration.

    Args:
        config: API configuration containing credentials and settings
    """
```

### Core API Methods

#### Speech-to-Text Operations

```python
def speech_to_text(self, audio_data: bytes) -> Optional[str]:
    """
    Convert audio data to text using Google Cloud Speech-to-Text API.

    Args:
        audio_data: Raw audio bytes to transcribe

    Returns:
        Transcribed text or None if failed
    """

def speech_to_text_with_config(self, audio_data: bytes, config: Dict[str, Any]) -> Optional[str]:
    """
    Convert audio data to text with custom configuration.

    Args:
        audio_data: Raw audio bytes to transcribe
        config: Custom STT configuration parameters

    Returns:
        Transcribed text or None if failed
    """
```

#### Text-to-Speech Operations

```python
def text_to_speech(self, text: str) -> Optional[Any]:
    """
    Convert text to speech using Google Cloud Text-to-Speech API.

    Args:
        text: Text to convert to speech

    Returns:
        Audio response object or None if failed
    """

def text_to_speech_with_config(self, text: str, config: Dict[str, Any]) -> Optional[Any]:
    """
    Convert text to speech with custom configuration.

    Args:
        text: Text to convert to speech
        config: Custom TTS configuration parameters

    Returns:
        Audio response object or None if failed
    """
```

#### Language Model Operations

```python
def process_conversation_turn(self, audio_data: bytes) -> Optional[str]:
    """
    Process a complete conversation turn: STT → LLM → TTS.

    Args:
        audio_data: Raw audio bytes from user input

    Returns:
        Audio response object or None if failed
    """

def process_text_with_llm(self, text: str) -> Optional[str]:
    """
    Process text through the Language Model for AI response.

    Args:
        text: Input text for AI processing

    Returns:
        AI-generated response text or None if failed
    """
```

### LLM Integration and Mocking

#### LLM Provider Interface

```python
def set_llm_provider(self, provider: Any) -> None:
    """
    Set the LLM provider for AI processing.

    Args:
        provider: LLM provider object (real or mock)
    """

def get_llm_provider(self) -> Any:
    """
    Get the current LLM provider.

    Returns:
        Current LLM provider object
    """

def is_llm_mocked(self) -> bool:
    """
    Check if LLM is currently mocked.

    Returns:
        True if LLM is mocked, False if using real provider
    """
```

#### Mock LLM Support

```python
def enable_llm_mocking(self, mock_response: str = "This is a mock AI response.") -> None:
    """
    Enable LLM mocking for testing purposes.

    Args:
        mock_response: Default response for mocked LLM
    """

def disable_llm_mocking(self) -> None:
    """
    Disable LLM mocking and use real LLM provider.
    """

def set_mock_llm_response(self, response: str) -> None:
    """
    Set the response for mocked LLM.

    Args:
        response: Response text for mocked LLM
    """
```

### Configuration and Management

```python
def get_api_status(self) -> Dict[str, Any]:
    """
    Get status of all API services.

    Returns:
        Dictionary with API service status information
    """

def test_api_connection(self) -> bool:
    """
    Test connection to all configured APIs.

    Returns:
        True if all APIs are accessible, False otherwise
    """

def cleanup(self) -> None:
    """
    Clean up API resources and connections.
    """
```

## APIConfig Class Structure

### Constructor

```python
def __init__(self, config_path: str):
    """
    Initialize API configuration from file.

    Args:
        config_path: Path to the API configuration file
    """
```

### Configuration Properties

- `project_id`: Google Cloud project ID
- `credentials_path`: Path to service account credentials
- `stt_config`: Speech-to-Text API configuration
- `tts_config`: Text-to-Speech API configuration
- `llm_config`: Language Model configuration
- `retry_config`: Retry logic configuration
- `timeout_config`: Timeout settings for API calls

### Configuration Examples

```python
# Development Configuration
config = APIConfig("config/api_config.development.json")

# Production Configuration
config = APIConfig("config/api_config.production.json")

# Test Configuration with Mocking
config = APIConfig("config/api_config.test.json")
```

## APIResponse Class Structure

### Constructor

```python
def __init__(self,
             success: bool,
             data: Any = None,
             error: Optional[str] = None,
             metadata: Optional[Dict[str, Any]] = None):
    """
    Initialize API response object.

    Args:
        success: Whether the API call was successful
        data: Response data from the API
        error: Error message if failed
        metadata: Additional metadata about the response
    """
```

### Response Properties

- `success`: Boolean indicating success/failure
- `data`: Response data from the API
- `error`: Error message if the call failed
- `metadata`: Additional response metadata
- `timestamp`: Timestamp of the API call
- `duration`: Duration of the API call

## Integration with MainLoop

### Centralized Method Support

The APIManager provides methods that are called by the MainLoop's centralized test methods:

```python
# MainLoop calls these methods for testing
def test_speech_to_text(self, audio_data: bytes) -> Optional[str]:
    """
    MainLoop centralized method that calls APIManager.speech_to_text()
    """

def test_text_to_speech(self, text: str) -> Optional[Any]:
    """
    MainLoop centralized method that calls APIManager.text_to_speech()
    """
```

### State Management Integration

- **Processing State**: APIManager operations trigger MainLoop state transitions
- **Error Handling**: API errors are propagated to MainLoop for error recovery
- **Response Handling**: API responses trigger audio playback in MainLoop

## Error Handling

### API Error Categories

- **Authentication Errors**: Invalid credentials, expired tokens
- **Network Errors**: Connection timeouts, network failures
- **Rate Limiting**: API quota exceeded, rate limit violations
- **Service Errors**: API service unavailable, internal errors
- **Data Errors**: Invalid audio format, unsupported text

### Error Recovery Strategies

1. **Automatic Retry**: Retry failed operations with exponential backoff
2. **Credential Refresh**: Automatically refresh expired credentials
3. **Fallback Responses**: Provide fallback responses for critical failures
4. **Graceful Degradation**: Continue operation with reduced functionality
5. **Error Reporting**: Comprehensive error logging and reporting

### Retry Logic

```python
def _retry_with_backoff(self, operation: Callable, max_retries: int = 3) -> Any:
    """
    Execute operation with exponential backoff retry logic.

    Args:
        operation: Function to execute
        max_retries: Maximum number of retry attempts

    Returns:
        Operation result or raises exception after max retries
    """
```

## Security Considerations

### Credential Management

- **Secure Storage**: Credentials stored in encrypted configuration files
- **Environment Variables**: Support for environment variable credentials
- **Credential Rotation**: Automatic credential refresh and rotation
- **Access Control**: Proper file permissions for credential files

### Data Security

- **Encrypted Transmission**: All API communications use HTTPS/TLS
- **Temporary Storage**: Audio data not persisted beyond processing
- **Access Logging**: Log API access for security monitoring
- **Data Validation**: Validate all input data before API transmission

### Privacy Protection

- **No Data Persistence**: Audio and text data not stored permanently
- **Minimal Logging**: Sensitive data excluded from logs
- **User Consent**: Clear user consent for data processing
- **Data Minimization**: Only necessary data transmitted to APIs

## Performance Optimization

### Connection Management

- **Connection Pooling**: Reuse API connections when possible
- **Keep-Alive**: Maintain persistent connections for better performance
- **Connection Limits**: Manage connection limits to prevent resource exhaustion
- **Timeout Optimization**: Optimize timeout values for different operations

### Caching Strategies

- **Response Caching**: Cache API responses where appropriate
- **Credential Caching**: Cache authentication tokens
- **Configuration Caching**: Cache API configuration for faster access
- **Error Caching**: Cache error responses to avoid repeated failures

### Batch Processing

- **Audio Batching**: Process multiple audio chunks efficiently
- **Text Batching**: Batch text processing operations
- **Request Optimization**: Optimize API request formats and sizes

## Testing Integration

### Unit Testing

- **Component Isolation**: Test individual API operations
- **Mock APIs**: Mock external API calls for testing
- **Error Simulation**: Test error handling and recovery
- **Performance Testing**: Test API call performance and timing

### Integration Testing

- **End-to-End Testing**: Test complete API pipeline
- **Real API Testing**: Test with real Google Cloud APIs
- **Mock LLM Testing**: Test with mocked LLM for audio pipeline validation
- **Error Recovery Testing**: Test error recovery scenarios

### Test Utilities

```python
def create_mock_audio_data(duration: float = 1.0) -> bytes:
    """
    Create mock audio data for testing.

    Args:
        duration: Audio duration in seconds

    Returns:
        Mock audio data as bytes
    """

def create_mock_api_response(success: bool, data: Any = None) -> APIResponse:
    """
    Create mock API response for testing.

    Args:
        success: Whether the mock call was successful
        data: Mock response data

    Returns:
        Mock APIResponse object
    """
```

## Configuration Examples

### Development Configuration

```json
{
  "project_id": "leadership-button-dev",
  "credentials_path": "config/service-account-dev.json",
  "stt_config": {
    "language_code": "en-US",
    "sample_rate_hertz": 16000,
    "encoding": "LINEAR16"
  },
  "tts_config": {
    "language_code": "en-US",
    "voice_name": "en-US-Standard-A",
    "audio_encoding": "LINEAR16"
  },
  "llm_config": {
    "model": "gpt-3.5-turbo",
    "max_tokens": 150,
    "temperature": 0.7
  },
  "retry_config": {
    "max_retries": 3,
    "backoff_factor": 2.0
  }
}
```

### Production Configuration

```json
{
  "project_id": "leadership-button-prod",
  "credentials_path": "config/service-account-prod.json",
  "stt_config": {
    "language_code": "en-US",
    "sample_rate_hertz": 16000,
    "encoding": "LINEAR16",
    "enable_automatic_punctuation": true
  },
  "tts_config": {
    "language_code": "en-US",
    "voice_name": "en-US-Standard-A",
    "audio_encoding": "LINEAR16",
    "speaking_rate": 1.0
  },
  "llm_config": {
    "model": "gpt-4",
    "max_tokens": 200,
    "temperature": 0.8
  },
  "retry_config": {
    "max_retries": 5,
    "backoff_factor": 1.5
  }
}
```

### Test Configuration with Mocking

```json
{
  "project_id": "leadership-button-test",
  "credentials_path": "config/service-account-test.json",
  "stt_config": {
    "language_code": "en-US",
    "sample_rate_hertz": 16000,
    "encoding": "LINEAR16"
  },
  "tts_config": {
    "language_code": "en-US",
    "voice_name": "en-US-Standard-A",
    "audio_encoding": "LINEAR16"
  },
  "llm_config": {
    "model": "mock",
    "mock_response": "This is a test response from the mocked LLM."
  },
  "retry_config": {
    "max_retries": 1,
    "backoff_factor": 1.0
  }
}
```

## Future Enhancements

### Advanced Features

- **Multi-language Support**: Support for multiple languages and accents
- **Voice Recognition**: Speaker identification and personalization
- **Advanced AI**: Enhanced conversation capabilities and context awareness
- **Analytics**: API usage tracking and performance optimization

### Integration Improvements

- **Alternative APIs**: Support for alternative speech and AI APIs
- **Offline Processing**: Local processing when APIs are unavailable
- **Real-time Streaming**: Real-time audio streaming for better performance
- **Custom Models**: Support for custom speech and AI models

### Performance Improvements

- **Parallel Processing**: Parallel API calls for better performance
- **Predictive Caching**: Predictive caching based on usage patterns
- **Load Balancing**: Load balancing across multiple API endpoints
- **Optimization**: Continuous performance optimization and tuning
