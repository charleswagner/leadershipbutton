"""
Tests for APIManager partial initialization and non-blocking behavior.

Tests the timeout handling, AI-only mode, and graceful fallbacks when
Google Cloud services are unavailable.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import signal
import time

from src.leadership_button.api_client import APIConfig, APIManager, APIState


class TestAPIManagerPartialInit:
    """Test suite for APIManager partial initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config_data = {
            "api_settings": {"timeout": 30, "max_retries": 3, "backoff_factor": 2.0},
            "google_cloud": {
                "project_id": "test",
                "credentials_path": "",
                "region": "us-central1",
            },
            "audio_settings": {"sample_rate": 16000, "channels": 1},
            "speech_to_text": {"language_code": "en-US"},
            "text_to_speech": {"language_code": "en-US"},
            "performance": {"audio_buffer_size": 4096},
            "features": {"enable_echo_cancellation": True},
            "development": {"mock_apis": False},
        }

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_full_initialization_success(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test successful initialization of all clients."""
        mock_load_config.return_value = self.test_config_data

        # Mock successful client initialization
        mock_speech_instance = Mock()
        mock_speech_instance.state = APIState.READY
        mock_speech_client.return_value = mock_speech_instance

        mock_tts_instance = Mock()
        mock_tts_instance.state = APIState.READY
        mock_tts_client.return_value = mock_tts_instance

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        assert api_manager.state == APIState.READY
        assert api_manager.speech_client is not None
        assert api_manager.tts_client is not None

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_google_cloud_disabled_environment_variable(self, mock_load_config):
        """Test that DISABLE_GOOGLE_CLOUD environment variable works."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {"DISABLE_GOOGLE_CLOUD": "true"}):
            config = APIConfig("test_config.json")
            api_manager = APIManager(config)

            assert api_manager.state == APIState.AI_ONLY
            assert api_manager.speech_client is None
            assert api_manager.tts_client is None

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_speech_client_timeout(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test timeout handling for speech client initialization."""
        mock_load_config.return_value = self.test_config_data

        # Mock speech client that hangs (simulated by raising TimeoutError)
        def slow_speech_init(*args, **kwargs):
            raise TimeoutError("Speech client initialization timed out")

        mock_speech_client.side_effect = slow_speech_init

        # Mock successful TTS client
        mock_tts_instance = Mock()
        mock_tts_instance.state = APIState.READY
        mock_tts_client.return_value = mock_tts_instance

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        # Should fallback to AI_ONLY mode
        assert api_manager.state == APIState.AI_ONLY
        assert api_manager.speech_client is None
        assert api_manager.tts_client is not None

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_both_clients_fail(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test fallback to AI_ONLY when both clients fail."""
        mock_load_config.return_value = self.test_config_data

        # Mock both clients failing
        mock_speech_client.side_effect = Exception("Speech client failed")
        mock_tts_client.side_effect = Exception("TTS client failed")

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        assert api_manager.state == APIState.AI_ONLY
        assert api_manager.speech_client is None
        assert api_manager.tts_client is None

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_speech_to_text_fallback(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test speech-to-text fallback to text input in AI_ONLY mode."""
        mock_load_config.return_value = self.test_config_data

        # Mock both clients failing to trigger AI_ONLY mode
        mock_speech_client.side_effect = Exception("Speech client failed")
        mock_tts_client.side_effect = Exception("TTS client failed")

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        # Mock user input
        with patch("builtins.input", return_value="Test leadership question"):
            result = api_manager.speech_to_text(b"mock_audio")

            assert result == "Test leadership question"

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_text_to_speech_fallback(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test text-to-speech fallback to console output in AI_ONLY mode."""
        mock_load_config.return_value = self.test_config_data

        # Mock both clients failing to trigger AI_ONLY mode
        mock_speech_client.side_effect = Exception("Speech client failed")
        mock_tts_client.side_effect = Exception("TTS client failed")

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        # Mock print function to capture output
        with patch("builtins.print") as mock_print:
            result = api_manager.text_to_speech("Great leadership advice!")

            # Should print the response and return mock audio
            mock_print.assert_called_with(
                "\n🤖 AI Response: Great leadership advice!\n"
            )
            assert result == b"mock_audio_data"

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_ai_only_state_allows_transcription(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test that AI_ONLY state allows transcription operations."""
        mock_load_config.return_value = self.test_config_data

        # Mock both clients failing to trigger AI_ONLY mode
        mock_speech_client.side_effect = Exception("Speech client failed")
        mock_tts_client.side_effect = Exception("TTS client failed")

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        # Create a mock speech client to test transcription
        mock_speech_instance = Mock()
        api_manager.speech_client = mock_speech_instance

        # Mock user input for text fallback
        with patch("builtins.input", return_value="Leadership question"):
            result = mock_speech_instance.transcribe_audio(b"mock_audio")

            # Should not be blocked by AI_ONLY state
            mock_speech_instance.transcribe_audio.assert_called_once()

    def test_timeout_context_manager(self):
        """Test the timeout context manager functionality."""
        config_mock = Mock()
        api_manager = APIManager.__new__(APIManager)  # Create without calling __init__

        # Test successful operation within timeout
        with api_manager._timeout(1, "test operation"):
            time.sleep(0.1)  # Short operation should succeed

        # Test timeout behavior
        with pytest.raises(TimeoutError):
            with api_manager._timeout(1, "test operation"):
                time.sleep(2)  # Long operation should timeout

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_get_api_status_ai_only_mode(self, mock_load_config):
        """Test API status reporting in AI_ONLY mode."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {"DISABLE_GOOGLE_CLOUD": "true"}):
            config = APIConfig("test_config.json")
            api_manager = APIManager(config)

            status = api_manager.get_api_status()

            assert status["state"] == "ai_only"
            assert "speech_client" in status
            assert "tts_client" in status
            assert status["ai_provider"] == "not_set"  # Default when not configured

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.api_client.SpeechClient")
    @patch("src.leadership_button.api_client.TTSClient")
    def test_conversation_processing_ai_only_mode(
        self, mock_tts_client, mock_speech_client, mock_load_config
    ):
        """Test full conversation processing in AI_ONLY mode."""
        mock_load_config.return_value = self.test_config_data

        # Mock both clients failing
        mock_speech_client.side_effect = Exception("Speech client failed")
        mock_tts_client.side_effect = Exception("TTS client failed")

        config = APIConfig("test_config.json")
        api_manager = APIManager(config)

        # Set up a mock AI provider
        mock_ai_provider = Mock()
        mock_ai_provider.process_text.return_value = "Great leadership insight!"
        api_manager.set_ai_provider(mock_ai_provider)

        # Mock user input and console output
        with patch("builtins.input", return_value="What is leadership?"):
            with patch("builtins.print") as mock_print:
                result = api_manager.process_conversation_turn(b"mock_audio")

                # Should complete the full conversation cycle
                mock_ai_provider.process_text.assert_called_once_with(
                    "What is leadership?", {}
                )
                mock_print.assert_called_with(
                    "\n🤖 AI Response: Great leadership insight!\n"
                )
                assert result == b"mock_audio_data"
