# Conversation Manager Specification

## Overview

The ConversationManager module provides persistent conversation storage, user management, and comprehensive logging for the Leadership Button. It enables multi-user support with personalized greetings, conversation continuity, and full conversation history tracking.

## Core Architecture

### Purpose

- **Persistent Conversations**: Store and retrieve conversation history using Firestore
- **User Management**: Support multiple users with personalized experiences
- **Conversation Continuity**: Maintain context across 10-minute conversation windows
- **Comprehensive Logging**: Track all user interactions and system activities
- **Real-Time Monitoring**: Provide live log tailing and analytics

### Key Features

- Firestore integration for conversation persistence
- 10-minute conversation window logic
- Multi-user support with data isolation
- Personalized greetings ("Hello [Name]")
- Follow-up question generation
- Full conversation history logging
- Real-time log tailing capability

## ConversationManager Class Structure

### Constructor

```python
def __init__(self, firestore_config: Dict[str, Any], logging_config: Dict[str, Any]):
    """
    Initialize the conversation manager.

    Args:
        firestore_config: Firestore configuration settings
        logging_config: Logging configuration settings
    """
```

### Core Methods

#### User Management

- `create_user(user_name: str, user_id: str = None) -> str`: Create new user profile
- `get_user(user_id: str) -> Optional[Dict[str, Any]]`: Retrieve user profile
- `update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool`: Update user settings
- `list_users() -> List[Dict[str, Any]]`: List all registered users

#### Conversation Management

- `start_conversation(user_id: str) -> str`: Start new conversation session
- `get_active_conversation(user_id: str) -> Optional[str]`: Get current active conversation
- `add_message(conversation_id: str, user_message: str, ai_response: str) -> bool`: Add message to conversation
- `get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]`: Get full conversation history
- `is_conversation_active(conversation_id: str) -> bool`: Check if conversation is within 10-minute window
- `close_conversation(conversation_id: str) -> bool`: Close conversation session

#### Context Management

- `get_conversation_context(conversation_id: str) -> str`: Get conversation context for AI
- `update_conversation_context(conversation_id: str, context: str) -> bool`: Update conversation context
- `get_user_conversation_summary(user_id: str) -> str`: Get user's conversation summary

#### Logging and Analytics

- `log_user_activity(user_id: str, activity: str, details: Dict[str, Any]) -> None`: Log user activity
- `log_conversation_event(conversation_id: str, event_type: str, data: Dict[str, Any]) -> None`: Log conversation events
- `get_user_analytics(user_id: str) -> Dict[str, Any]`: Get user analytics
- `get_system_analytics() -> Dict[str, Any]`: Get system-wide analytics
- `tail_logs(filter_criteria: Dict[str, Any] = None) -> Generator[str, None, None]`: Real-time log tailing

## Data Models

### User Profile

```python
{
    "user_id": "unique_user_identifier",
    "name": "User Name",
    "created_at": "2024-08-03T01:30:00Z",
    "last_active": "2024-08-03T01:30:00Z",
    "preferences": {
        "voice_settings": {...},
        "coaching_style": "directive|supportive|mixed",
        "notification_settings": {...}
    },
    "conversation_count": 42,
    "total_session_time": 3600
}
```

### Conversation Session

```python
{
    "conversation_id": "unique_conversation_identifier",
    "user_id": "user_identifier",
    "started_at": "2024-08-03T01:30:00Z",
    "last_activity": "2024-08-03T01:35:00Z",
    "status": "active|closed",
    "message_count": 6,
    "context_summary": "Leadership challenge discussion about team conflict"
}
```

### Conversation Message

```python
{
    "message_id": "unique_message_identifier",
    "conversation_id": "conversation_identifier",
    "timestamp": "2024-08-03T01:32:00Z",
    "sender": "user|ai",
    "content": "Message content",
    "message_type": "question|response|follow_up",
    "metadata": {
        "audio_duration": 3.5,
        "confidence_score": 0.95,
        "leadership_topic": "conflict_resolution"
    }
}
```

## Firestore Integration

### Database Structure

```
/users/{user_id}
    - profile data
    - preferences
    - analytics

/conversations/{conversation_id}
    - session data
    - messages subcollection
    - context information

/logs/{log_id}
    - activity logs
    - system events
    - performance metrics
```

### Security Rules

- Users can only access their own data
- Conversation data is isolated by user
- System logs are read-only for users
- Admin access for system management

## Conversation Window Logic

### 10-Minute Window Implementation

```python
def is_conversation_active(self, conversation_id: str) -> bool:
    """
    Check if conversation is within 10-minute activity window.

    Args:
        conversation_id: Conversation identifier

    Returns:
        True if conversation is active, False otherwise
    """
    # Get conversation last activity time
    # Compare with current time
    # Return True if within 10 minutes
```

### Context Preservation

- Maintain conversation context across messages
- Include previous messages in AI prompt
- Preserve leadership topic and coaching style
- Track conversation flow and progression

## User Personalization

### Personalized Greetings

```python
def get_personalized_greeting(self, user_id: str) -> str:
    """
    Generate personalized greeting for user.

    Args:
        user_id: User identifier

    Returns:
        Personalized greeting string
    """
    # Get user name from profile
    # Generate appropriate greeting
    # Include conversation context if recent
    return f"Hello {user_name}, how can I help with your leadership today?"
```

### User Preferences

- Voice settings and preferences
- Coaching style preferences
- Notification settings
- Conversation history preferences

## Follow-Up Question Generation

### AI Integration

```python
def generate_follow_up_questions(self, conversation_context: str) -> List[str]:
    """
    Generate contextual follow-up questions based on conversation.

    Args:
        conversation_context: Current conversation context

    Returns:
        List of follow-up questions
    """
    # Analyze conversation context
    # Identify leadership topics
    # Generate relevant follow-up questions
    # Return questions for AI to include in response
```

### Question Types

- **Clarification Questions**: "Can you tell me more about..."
- **Action Questions**: "What steps have you considered..."
- **Reflection Questions**: "How do you feel about..."
- **Next Steps**: "What would you like to focus on next..."

## Comprehensive Logging

### Log Categories

- **User Activity**: Login, logout, conversation starts
- **Conversation Events**: Messages, responses, follow-ups
- **System Events**: Errors, performance, API calls
- **Analytics**: Usage patterns, engagement metrics

### Log Format

```python
{
    "timestamp": "2024-08-03T01:30:00Z",
    "level": "INFO|WARNING|ERROR",
    "category": "user_activity|conversation|system",
    "user_id": "user_identifier",
    "conversation_id": "conversation_identifier",
    "event": "conversation_started",
    "details": {...},
    "performance_metrics": {...}
}
```

### Real-Time Log Tailing

```python
def tail_logs(self, filter_criteria: Dict[str, Any] = None) -> Generator[str, None, None]:
    """
    Provide real-time log tailing with filtering.

    Args:
        filter_criteria: Optional filter criteria

    Yields:
        Log entries as they occur
    """
    # Set up Firestore real-time listener
    # Apply filter criteria
    # Yield log entries in real-time
```

## Integration Points

### MainLoop Integration

- **Conversation Management**: Start/continue conversations
- **Context Provision**: Provide conversation context to AI
- **User Identification**: Identify current user
- **Logging Integration**: Log all user interactions

### APIManager Integration

- **Context Enhancement**: Include conversation history in AI prompts
- **Follow-Up Generation**: Generate contextual follow-up questions
- **Response Logging**: Log all AI responses and interactions

### AudioHandler Integration

- **User Greetings**: Play personalized greetings
- **Conversation Feedback**: Audio cues for conversation state
- **Activity Logging**: Log audio interactions and quality

## Performance Considerations

### Optimization Strategies

- **Caching**: Cache frequently accessed user data
- **Batch Operations**: Batch Firestore operations for efficiency
- **Indexing**: Optimize Firestore indexes for query performance
- **Connection Pooling**: Efficient Firestore connection management

### Scalability

- **Multi-User Support**: Efficient handling of multiple concurrent users
- **Data Partitioning**: Partition data by user for isolation
- **Load Balancing**: Distribute load across multiple instances
- **Resource Management**: Efficient memory and CPU usage

## Security and Privacy

### Data Protection

- **User Isolation**: Complete data isolation between users
- **Encryption**: Encrypt sensitive data in transit and at rest
- **Access Control**: Role-based access control for data
- **Audit Logging**: Comprehensive audit trail for all operations

### Privacy Compliance

- **Data Retention**: Configurable data retention policies
- **User Consent**: User consent management for data usage
- **Data Export**: User data export capabilities
- **Data Deletion**: Complete user data deletion on request

## Testing Strategy

### Unit Testing

- **User Management**: Test user creation, retrieval, and updates
- **Conversation Logic**: Test conversation window and context management
- **Logging Functions**: Test logging and analytics functions
- **Data Models**: Test data model validation and serialization

### Integration Testing

- **Firestore Integration**: Test database operations and queries
- **AI Integration**: Test conversation context provision
- **Multi-User Scenarios**: Test user isolation and data separation
- **Performance Testing**: Test system performance under load

### End-to-End Testing

- **Complete User Journey**: Test full user interaction flow
- **Conversation Continuity**: Test conversation persistence and context
- **Logging Verification**: Verify comprehensive logging functionality
- **Multi-User Isolation**: Test complete user data isolation

## Future Enhancements

### Advanced Features

- **Conversation Analytics**: Advanced conversation analysis and insights
- **User Behavior Modeling**: Machine learning for user behavior prediction
- **Automated Insights**: AI-generated insights from conversation patterns
- **Integration APIs**: APIs for third-party integrations

### Platform Expansion

- **Mobile Support**: Mobile app integration
- **Web Dashboard**: Web-based conversation management
- **Team Features**: Team conversation and collaboration
- **Enterprise Integration**: Enterprise system integrations
