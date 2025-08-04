"""
Tests for Gemini Flash AI Provider

Tests the GeminiFlashProvider implementation following the project's testing
architecture principles with thorough coverage and no business logic in tests.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the provider to test
from src.leadership_button.gemini_provider import GeminiFlashProvider


class TestGeminiFlashProvider:
    """Test suite for GeminiFlashProvider."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        self.mock_config = {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 150,
            "timeout": 30,
        }

        # Mock environment variable
        self.api_key = "test-api-key-12345"

    def test_provider_requires_api_key_in_environment(self):
        """Test that provider enforces .env file security requirement."""
        # Clear any existing API key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GeminiFlashProvider(self.mock_config)

            assert "GEMINI_API_KEY not found in environment variables" in str(
                exc_info.value
            )
            assert ".env file" in str(exc_info.value)

    @patch("src.leadership_button.gemini_provider.genai")
    def test_provider_initialization_success(self, mock_genai):
        """Test successful provider initialization."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            # Mock the GenerativeModel
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)

            assert provider.get_provider_name() == "Gemini Flash"
            assert provider.is_available() is True
            assert provider.model_name == "gemini-1.5-flash"
            assert provider.temperature == 0.7
            assert provider.max_tokens == 150

            # Verify API was configured with the key
            mock_genai.configure.assert_called_once_with(api_key=self.api_key)

    @patch("src.leadership_button.gemini_provider.GEMINI_AVAILABLE", False)
    def test_provider_fails_when_library_unavailable(self):
        """Test provider fails gracefully when Gemini library is not available."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            with pytest.raises(RuntimeError) as exc_info:
                GeminiFlashProvider(self.mock_config)

            assert "Google Generative AI library not installed" in str(exc_info.value)

    @patch("src.leadership_button.gemini_provider.genai")
    def test_provider_handles_model_initialization_failure(self, mock_genai):
        """Test provider handles model initialization failure."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            # Mock model initialization failure
            mock_genai.GenerativeModel.side_effect = Exception("Model init failed")

            with pytest.raises(RuntimeError) as exc_info:
                GeminiFlashProvider(self.mock_config)

            assert "Failed to initialize Gemini model" in str(exc_info.value)

    @patch("src.leadership_button.gemini_provider.genai")
    def test_process_text_success(self, mock_genai):
        """Test successful text processing."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            # Set up mocks
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Mock successful response
            mock_response = Mock()
            mock_response.prompt_feedback.block_reason = None
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[
                0
            ].text = "Great question about leadership!"

            mock_model.generate_content.return_value = mock_response

            provider = GeminiFlashProvider(self.mock_config)
            result = provider.process_text("What is leadership?", {})

            assert result == "Great question about leadership!"
            assert mock_model.generate_content.called

    @patch("src.leadership_button.gemini_provider.genai")
    def test_process_text_handles_empty_input(self, mock_genai):
        """Test handling of empty input text."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)
            result = provider.process_text("", {})

            assert "didn't catch that" in result
            assert "repeat your question" in result

    @patch("src.leadership_button.gemini_provider.genai")
    def test_process_text_handles_safety_block(self, mock_genai):
        """Test handling of safety filter blocks."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Mock blocked response
            mock_response = Mock()
            mock_response.prompt_feedback.block_reason = "SAFETY"

            mock_model.generate_content.return_value = mock_response

            provider = GeminiFlashProvider(self.mock_config)
            result = provider.process_text("inappropriate content", {})

            assert "conversation stays focused on leadership" in result

    @patch("src.leadership_button.gemini_provider.genai")
    def test_process_text_handles_api_failure(self, mock_genai):
        """Test handling of API failures with fallback response."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Mock API failure
            mock_model.generate_content.side_effect = Exception("API Error")

            provider = GeminiFlashProvider(self.mock_config)
            result = provider.process_text("What is leadership?", {})

            assert "trouble connecting to my AI systems" in result
            assert "Great leaders focus on" in result

    @patch("src.leadership_button.gemini_provider.genai")
    def test_process_text_creates_leadership_prompt(self, mock_genai):
        """Test that leadership coaching prompt is created correctly."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Mock successful response
            mock_response = Mock()
            mock_response.prompt_feedback.block_reason = None
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[0].text = "Leadership advice"

            mock_model.generate_content.return_value = mock_response

            provider = GeminiFlashProvider(self.mock_config)
            provider.process_text("How to motivate team?", {"user_name": "Alice"})

            # Check that prompt was created with leadership context
            call_args = mock_model.generate_content.call_args[0][0]
            assert "leadership and emotional intelligence coach" in call_args
            assert "actionable advice" in call_args
            assert "How to motivate team?" in call_args

    @patch("src.leadership_button.gemini_provider.genai")
    def test_configure_updates_settings(self, mock_genai):
        """Test that provider configuration can be updated."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)

            # Update configuration
            new_settings = {"temperature": 0.9, "max_tokens": 200, "timeout": 45}
            provider.configure(new_settings)

            assert provider.temperature == 0.9
            assert provider.max_tokens == 200
            assert provider.timeout == 45

    @patch("src.leadership_button.gemini_provider.genai")
    def test_get_model_info(self, mock_genai):
        """Test that model information is returned correctly."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)
            info = provider.get_model_info()

            assert info["provider"] == "Gemini Flash"
            assert info["model"] == "gemini-1.5-flash"
            assert info["temperature"] == 0.7
            assert info["max_tokens"] == 150
            assert info["timeout"] == 30
            assert info["available"] is True

    @patch("src.leadership_button.gemini_provider.genai")
    def test_response_cleaning_removes_markdown(self, mock_genai):
        """Test that response cleaning removes markdown formatting."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)

            # Test markdown removal
            cleaned = provider._clean_response("**Bold** and *italic* text")
            assert cleaned == "Bold and italic text"

    @patch("src.leadership_button.gemini_provider.genai")
    def test_response_cleaning_truncates_long_responses(self, mock_genai):
        """Test that overly long responses are truncated appropriately."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": self.api_key}):
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model

            provider = GeminiFlashProvider(self.mock_config)

            # Create a very long response
            long_response = "This is a sentence. " * 50  # ~1000 characters
            cleaned = provider._clean_response(long_response)

            # Should be truncated to reasonable length
            assert len(cleaned) < 500
            assert cleaned.endswith(".")  # Should end properly

    def test_aiprover_interface_compliance(self):
        """Test that GeminiFlashProvider implements AIProvider interface correctly."""
        from src.leadership_button.api_client import AIProvider

        # Check that class inherits from AIProvider
        assert issubclass(GeminiFlashProvider, AIProvider)

        # Check required methods exist
        required_methods = [
            "process_text",
            "get_provider_name",
            "is_available",
            "configure",
        ]
        for method in required_methods:
            assert hasattr(GeminiFlashProvider, method)
            assert callable(getattr(GeminiFlashProvider, method))
