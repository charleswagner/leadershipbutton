"""
Integration tests for Gemini Flash AI Provider

Tests the complete integration workflow from MainLoop through APIManager
to GeminiFlashProvider, ensuring the end-to-end functionality works correctly.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import components to test
from src.leadership_button.main_loop import MainLoop
from src.leadership_button.api_client import APIConfig, APIManager
from src.leadership_button.gemini_provider import GeminiFlashProvider


class TestGeminiIntegration:
    """Integration test suite for Gemini Flash integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_api_key = "test-gemini-key-12345"
        self.test_config_data = {
            "api_settings": {"timeout": 30, "max_retries": 3, "backoff_factor": 2.0},
            "google_cloud": {
                "project_id": "test-project",
                "credentials_path": "/path/to/test/creds.json",
                "region": "us-central1",
            },
            "gemini": {
                "model": "gemini-1.5-flash",
                "temperature": 0.7,
                "max_tokens": 150,
                "timeout": 30,
            },
            "audio_settings": {
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 1024,
                "format": "int16",
            },
            "speech_to_text": {
                "language_code": "en-US",
                "model": "latest_long",
                "use_enhanced": True,
                "enable_automatic_punctuation": True,
            },
            "text_to_speech": {
                "language_code": "en-US",
                "voice_name": "en-US-Standard-A",
                "audio_encoding": "LINEAR16",
            },
            "performance": {
                "audio_buffer_size": 4096,
                "processing_timeout": 30,
                "connection_timeout": 10,
            },
            "features": {
                "enable_echo_cancellation": True,
                "enable_noise_suppression": True,
                "enable_automatic_gain_control": True,
            },
            "development": {
                "mock_apis": False,
                "log_level": "INFO",
                "enable_debug_audio": False,
            },
        }

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_api_config_loads_with_correct_format(self, mock_load_config):
        """Test that APIConfig loads with the correct configuration format."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {}, clear=True):
            config = APIConfig("test_config.json")

            # Test that new format properties work
            assert config.api_settings["timeout"] == 30
            assert config.api_settings["max_retries"] == 3
            assert config.timeout_seconds == 30  # Property should map correctly
            assert config.retry_max_attempts == 3  # Property should map correctly

            # Test validation passes
            assert config.validate() is None  # Should not raise exception

    @patch("src.leadership_button.gemini_provider.genai")
    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_gemini_provider_integrates_with_api_manager(
        self, mock_load_config, mock_genai
    ):
        """Test that GeminiFlashProvider integrates correctly with APIManager."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {"GEMINI_API_KEY": self.test_api_key}):
            # Mock Gemini components
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Create APIManager with GeminiFlashProvider
            config = APIConfig("test_config.json")
            api_manager = APIManager(config)

            # Set up Gemini provider
            gemini_provider = GeminiFlashProvider()
            api_manager.set_ai_provider(gemini_provider)

            # Test integration
            status = api_manager.get_api_status()
            assert status["ai_provider"] == "Gemini Flash"
            assert api_manager.ai_provider is not None
            assert api_manager.ai_provider.get_provider_name() == "Gemini Flash"

    @patch("src.leadership_button.gemini_provider.genai")
    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.main_loop.MainLoop._initialize_audio_handler")
    def test_main_loop_uses_gemini_when_available(
        self, mock_audio_init, mock_load_config, mock_genai
    ):
        """Test that MainLoop uses Gemini provider when GEMINI_API_KEY is available."""
        mock_load_config.return_value = self.test_config_data
        mock_audio_init.return_value = None  # Skip audio initialization

        with patch.dict(os.environ, {"GEMINI_API_KEY": self.test_api_key}):
            # Mock Gemini components
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Initialize MainLoop
            main_loop = MainLoop()

            # Verify Gemini provider is set up
            assert main_loop.api_client is not None
            assert main_loop.api_client.ai_provider is not None
            assert (
                main_loop.api_client.ai_provider.get_provider_name() == "Gemini Flash"
            )

    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    @patch("src.leadership_button.main_loop.MainLoop._initialize_audio_handler")
    def test_main_loop_falls_back_to_mock_when_gemini_unavailable(
        self, mock_audio_init, mock_load_config
    ):
        """Test that MainLoop falls back to mock provider when Gemini is unavailable."""
        mock_load_config.return_value = self.test_config_data
        mock_audio_init.return_value = None

        # No GEMINI_API_KEY set
        with patch.dict(os.environ, {}, clear=True):
            main_loop = MainLoop()

            # Verify mock provider is used as fallback
            assert main_loop.api_client is not None
            assert main_loop.api_client.ai_provider is not None
            assert "Mock" in main_loop.api_client.ai_provider.get_provider_name()

    @patch("src.leadership_button.gemini_provider.genai")
    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_end_to_end_text_processing(self, mock_load_config, mock_genai):
        """Test end-to-end text processing through the complete stack."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {"GEMINI_API_KEY": self.test_api_key}):
            # Mock successful Gemini response
            mock_model = Mock()
            mock_response = Mock()
            mock_response.prompt_feedback.block_reason = None
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[
                0
            ].text = "Effective leadership requires clear communication and empathy."

            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            # Create the complete stack
            config = APIConfig("test_config.json")
            api_manager = APIManager(config)
            gemini_provider = GeminiFlashProvider()
            api_manager.set_ai_provider(gemini_provider)

            # Test text processing
            response = api_manager.ai_provider.process_text(
                "What makes a good leader?", {}
            )

            assert (
                response
                == "Effective leadership requires clear communication and empathy."
            )
            assert mock_model.generate_content.called

            # Verify leadership coaching prompt was created
            call_args = mock_model.generate_content.call_args[0][0]
            assert "leadership and emotional intelligence coach" in call_args
            assert "What makes a good leader?" in call_args

    @patch("src.leadership_button.gemini_provider.genai")
    @patch("src.leadership_button.api_client.APIConfig._load_json_config")
    def test_error_handling_and_fallback_responses(self, mock_load_config, mock_genai):
        """Test error handling and fallback responses throughout the stack."""
        mock_load_config.return_value = self.test_config_data

        with patch.dict(os.environ, {"GEMINI_API_KEY": self.test_api_key}):
            # Mock API failure
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception(
                "API temporarily unavailable"
            )
            mock_genai.GenerativeModel.return_value = mock_model

            # Create provider and test error handling
            provider = GeminiFlashProvider()
            response = provider.process_text("Test question", {})

            # Should get fallback response
            assert "trouble connecting to my AI systems" in response
            assert "Great leaders focus on" in response

    def test_configuration_validation_catches_errors(self):
        """Test that configuration validation catches common errors."""

        # Test invalid timeout
        invalid_config = self.test_config_data.copy()
        invalid_config["api_settings"]["timeout"] = -1

        with patch(
            "src.leadership_button.api_client.APIConfig._load_json_config"
        ) as mock_load:
            mock_load.return_value = invalid_config

            with pytest.raises(ValueError, match="API timeout must be positive"):
                APIConfig("test_config.json")

        # Test invalid max_retries
        invalid_config = self.test_config_data.copy()
        invalid_config["api_settings"]["max_retries"] = 0

        with patch(
            "src.leadership_button.api_client.APIConfig._load_json_config"
        ) as mock_load:
            mock_load.return_value = invalid_config

            with pytest.raises(ValueError, match="Retry max attempts must be positive"):
                APIConfig("test_config.json")

    @patch("src.leadership_button.gemini_provider.genai")
    def test_provider_enforces_env_security_requirement(self, mock_genai):
        """Test that provider enforces the .env file security requirement."""

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GeminiFlashProvider()

            assert "GEMINI_API_KEY not found in environment variables" in str(
                exc_info.value
            )
            assert ".env file" in str(exc_info.value)

    @patch("src.leadership_button.gemini_provider.genai")
    def test_provider_configuration_from_config_file(self, mock_genai):
        """Test that provider can be configured from configuration data."""

        with patch.dict(os.environ, {"GEMINI_API_KEY": self.test_api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Test with custom configuration
            custom_config = {
                "model": "gemini-1.5-flash",
                "temperature": 0.9,
                "max_tokens": 200,
                "timeout": 45,
            }

            provider = GeminiFlashProvider(custom_config)

            assert provider.model_name == "gemini-1.5-flash"
            assert provider.temperature == 0.9
            assert provider.max_tokens == 200
            assert provider.timeout == 45
