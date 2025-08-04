"""
Basic integration tests for Gemini Flash integration.

Simple tests to verify that the core functionality is working without
complex mocking scenarios.
"""

import os
import pytest
from unittest.mock import patch

# Import the classes we need to test
from src.leadership_button.api_client import APIConfig, APIManager
from src.leadership_button.gemini_provider import GeminiFlashProvider


def test_api_config_validation_passes():
    """Test that APIConfig validation passes with correct configuration format."""
    # This test uses the actual config file to ensure it's valid
    with patch.dict(os.environ, {}, clear=True):
        try:
            config = APIConfig("config/api_config.json")
            # If we get here without exception, validation passed
            assert config.timeout_seconds == 30
            assert config.retry_max_attempts == 3
        except Exception as e:
            pytest.fail(f"Configuration validation failed: {e}")


def test_gemini_provider_requires_api_key():
    """Test that GeminiFlashProvider enforces API key requirement."""
    # Clear environment to test security requirement
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            GeminiFlashProvider()

        assert "GEMINI_API_KEY not found" in str(exc_info.value)
        assert ".env file" in str(exc_info.value)


@patch("src.leadership_button.gemini_provider.genai")
def test_gemini_provider_initializes_with_api_key(mock_genai):
    """Test that GeminiFlashProvider initializes correctly with API key."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        # Mock the GenerativeModel
        mock_model = mock_genai.GenerativeModel.return_value

        provider = GeminiFlashProvider()

        assert provider.get_provider_name() == "Gemini Flash"
        assert provider.is_available() is True
        mock_genai.configure.assert_called_once_with(api_key="test-key")


@patch("src.leadership_button.gemini_provider.genai")
def test_gemini_provider_handles_api_failures_gracefully(mock_genai):
    """Test that GeminiFlashProvider handles API failures with fallback."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        # Mock API failure
        mock_model = mock_genai.GenerativeModel.return_value
        mock_model.generate_content.side_effect = Exception("API Error")

        provider = GeminiFlashProvider()
        response = provider.process_text("Test question", {})

        # Should get fallback response, not raise exception
        assert "trouble connecting to my AI systems" in response
        assert isinstance(response, str)
        assert len(response) > 0


@patch("src.leadership_button.api_client.APIConfig._load_json_config")
def test_api_manager_accepts_gemini_provider(mock_load_config):
    """Test that APIManager can accept and use GeminiFlashProvider."""
    # Mock configuration
    mock_config_data = {
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
    mock_load_config.return_value = mock_config_data

    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        with patch("src.leadership_button.gemini_provider.genai") as mock_genai:
            # Mock Gemini components
            mock_model = mock_genai.GenerativeModel.return_value

            # Create APIManager and set Gemini provider
            config = APIConfig("test_config.json")
            api_manager = APIManager(config)

            gemini_provider = GeminiFlashProvider()
            api_manager.set_ai_provider(gemini_provider)

            # Test integration
            status = api_manager.get_api_status()
            assert status["ai_provider"] == "Gemini Flash"


def test_configuration_structure_is_correct():
    """Test that the configuration file has the expected structure."""
    try:
        config = APIConfig("config/api_config.json")

        # Test that all required sections exist
        assert hasattr(config, "api_settings")
        assert hasattr(config, "google_cloud")
        assert hasattr(config, "audio_settings")

        # Test that the new structure is being used
        assert "timeout" in config.api_settings
        assert "max_retries" in config.api_settings

        # Test that properties map correctly
        assert config.timeout_seconds > 0
        assert config.retry_max_attempts > 0

    except Exception as e:
        pytest.fail(f"Configuration structure test failed: {e}")


@patch("src.leadership_button.gemini_provider.genai")
def test_gemini_provider_creates_leadership_prompts(mock_genai):
    """Test that GeminiFlashProvider creates appropriate leadership coaching prompts."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        # Mock successful response
        mock_model = mock_genai.GenerativeModel.return_value
        mock_response = type(
            "MockResponse",
            (),
            {
                "prompt_feedback": type("MockFeedback", (), {"block_reason": None})(),
                "candidates": [
                    type(
                        "MockCandidate",
                        (),
                        {
                            "content": type(
                                "MockContent",
                                (),
                                {
                                    "parts": [
                                        type(
                                            "MockPart",
                                            (),
                                            {"text": "Good leadership advice"},
                                        )()
                                    ]
                                },
                            )()
                        },
                    )()
                ],
            },
        )()
        mock_model.generate_content.return_value = mock_response

        provider = GeminiFlashProvider()
        provider.process_text("What is leadership?", {})

        # Check that prompt was created correctly
        call_args = mock_model.generate_content.call_args[0][0]
        assert "leadership and emotional intelligence coach" in call_args
        assert "What is leadership?" in call_args
        assert "actionable advice" in call_args
