"""
Complete Voice Workflow Unit Tests

This module tests the entire voice-first interaction workflow:
1. Spacebar press → Recording start
2. Audio recording → Audio data capture
3. Speech-to-Text → Text transcription
4. Gemini AI → Leadership coaching response
5. Text-to-Speech → Audio synthesis
6. Audio playback → Complete cycle

Testing Strategy:
- Unit tests for individual components
- Integration tests for component interactions
- Mock-based tests for reliability
- Real API tests for validation
- Error scenario coverage
- Performance benchmarks
"""

import unittest
import time
import threading
import os
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager
import tempfile
import json

from src.leadership_button.main_loop import MainLoop, ApplicationState
from src.leadership_button.audio_handler import AudioHandler, AudioData
from src.leadership_button.api_client import APIManager, APIState, APIConfig
from src.leadership_button.gemini_provider import GeminiFlashProvider


class TestCompleteVoiceWorkflow(unittest.TestCase):
    """Test the complete voice workflow end-to-end"""

    def setUp(self):
        """Set up test environment with mocked dependencies"""
        self.main_loop = None
        self.mock_audio_data = self._create_mock_audio_data()

    def tearDown(self):
        """Clean up test environment"""
        if self.main_loop:
            self.main_loop.stop()

    def _create_mock_audio_data(self) -> AudioData:
        """Create realistic mock audio data for testing"""
        # 2 seconds of 16-bit audio at 16kHz
        sample_count = 16000 * 2
        mock_bytes = b"\x00\x01" * sample_count
        return AudioData(data=mock_bytes, format="int16", sample_rate=16000, channels=1)

    # =============================================================================
    # 1. COMPONENT UNIT TESTS
    # =============================================================================

    def test_audio_handler_recording_cycle(self):
        """Test audio recording start/stop cycle"""
        with patch("src.leadership_button.audio_handler.pyaudio.PyAudio"):
            audio_handler = AudioHandler()

            # Test recording lifecycle
            audio_handler.start_recording()
            self.assertTrue(audio_handler.is_recording())

            time.sleep(0.1)  # Brief recording

            audio_data = audio_handler.stop_recording()
            self.assertFalse(audio_handler.is_recording())
            self.assertIsInstance(audio_data, AudioData)

    def test_speech_to_text_configuration(self):
        """Test speech-to-text configuration and API setup"""
        with patch("src.leadership_button.api_client.speech.SpeechClient"):
            api_manager = APIManager()

            # Verify configuration loads correctly
            speech_config = api_manager.config.get_speech_config()
            required_fields = [
                "sample_rate_hertz",
                "language_code",
                "model",
                "max_alternatives",
            ]

            for field in required_fields:
                self.assertIn(field, speech_config, f"Missing required field: {field}")

    def test_gemini_ai_integration(self):
        """Test Gemini AI provider initialization and processing"""
        gemini_config = {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 150,
        }

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            provider = GeminiFlashProvider(gemini_config)

            self.assertEqual(provider.name, "Gemini Flash")
            self.assertTrue(provider.is_available())

    def test_tts_voice_compatibility(self):
        """Test that the configured TTS voice is supported by Google Cloud"""
        config = APIConfig()
        tts_config = config.config_data["text_to_speech"]
        voice_name = tts_config["voice_name"]

        # List of known supported Google Cloud TTS voices
        supported_voices = [
            "en-US-Standard-A",
            "en-US-Standard-B",
            "en-US-Standard-C",
            "en-US-Standard-D",
            "en-US-Wavenet-A",
            "en-US-Wavenet-B",
            "en-US-Wavenet-C",
            "en-US-Wavenet-D",
            "en-US-Wavenet-E",
            "en-US-Wavenet-F",
            "en-US-Wavenet-G",
            "en-US-Wavenet-H",
            "en-US-Wavenet-I",
            "en-US-Wavenet-J",
        ]

        self.assertIn(
            voice_name,
            supported_voices,
            f"Voice '{voice_name}' is not in the list of supported Google Cloud TTS voices",
        )

        # Verify it's a high-quality voice
        self.assertTrue(
            voice_name.startswith("en-US-Wavenet")
            or voice_name.startswith("en-US-Standard"),
            "Voice should be a Standard or Wavenet voice for compatibility",
        )

        print(f"✅ Voice compatibility verified: {voice_name}")

    def test_text_to_speech_audio_quality(self):
        """Test text-to-speech audio quality settings"""
        with patch("src.leadership_button.api_client.texttospeech.TextToSpeechClient"):
            config = APIConfig()
            api_manager = APIManager(config)

            # Test TTS config has quality settings
            tts_config = api_manager.config.config_data["text_to_speech"]

            # Verify volume is loud enough (should be > 0 dB)
            self.assertGreater(
                tts_config["volume_gain_db"],
                0,
                "Volume should be boosted for audibility",
            )

            # Verify speaking rate is reasonable (should be > 1.0 for responsiveness)
            self.assertGreater(
                tts_config["speaking_rate"],
                1.0,
                "Speaking rate should be faster than default",
            )

            # Verify using high-quality voice
            self.assertTrue(
                "Wavenet" in tts_config["voice_name"]
                or "Standard" in tts_config["voice_name"],
                "Should use high-quality Wavenet or Standard voice",
            )

            print(
                f"✅ Audio quality settings: {tts_config['speaking_rate']}x speed, +{tts_config['volume_gain_db']}dB"
            )

    def test_text_to_speech_configuration(self):
        """Test text-to-speech configuration"""
        with patch("src.leadership_button.api_client.texttospeech.TextToSpeechClient"):
            api_manager = APIManager()

            # Test TTS config has required fields
            audio_config = api_manager.config.audio_settings
            self.assertIn("output_sample_rate", audio_config)
            self.assertGreater(audio_config["output_sample_rate"], 0)

    # =============================================================================
    # 2. INTEGRATION TESTS - MOCKED APIs
    # =============================================================================

    def test_speech_to_text_integration_mocked(self):
        """Test speech-to-text with mocked Google Cloud API"""
        mock_result = Mock()
        mock_result.results = [Mock()]
        mock_result.results[0].alternatives = [Mock()]
        mock_result.results[0].alternatives[
            0
        ].transcript = "How can I improve team motivation?"
        mock_result.results[0].alternatives[0].confidence = 0.95

        with patch(
            "src.leadership_button.api_client.speech.SpeechClient"
        ) as mock_speech:
            mock_speech.return_value.recognize.return_value = mock_result

            api_manager = APIManager()
            result = api_manager.speech_to_text(self.mock_audio_data)

            self.assertEqual(result, "How can I improve team motivation?")

    def test_ai_processing_integration_mocked(self):
        """Test AI processing with mocked Gemini API"""
        mock_response = "Great question! Focus on active listening and recognition..."

        with patch("google.generativeai.GenerativeModel") as mock_model:
            mock_model.return_value.generate_content.return_value.text = mock_response

            # Test with environment variable
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                gemini_config = {"model": "gemini-1.5-flash", "temperature": 0.7}
                provider = GeminiFlashProvider(gemini_config)

                result = provider.process_text("How can I improve team motivation?", {})
                self.assertEqual(result, mock_response)

    def test_text_to_speech_integration_mocked(self):
        """Test text-to-speech with mocked Google Cloud API"""
        mock_audio_content = b"fake_audio_bytes_for_testing" * 100

        with patch(
            "src.leadership_button.api_client.texttospeech.TextToSpeechClient"
        ) as mock_tts:
            mock_tts.return_value.synthesize_speech.return_value.audio_content = (
                mock_audio_content
            )

            api_manager = APIManager()
            result = api_manager.text_to_speech("Great leadership advice here...")

            self.assertIsNotNone(result)

    # =============================================================================
    # 3. FULL WORKFLOW INTEGRATION TESTS
    # =============================================================================

    @patch("src.leadership_button.audio_handler.AudioHandler.start_recording")
    @patch("src.leadership_button.audio_handler.AudioHandler.stop_recording")
    @patch("src.leadership_button.api_client.APIManager.process_conversation_turn")
    def test_spacebar_workflow_mocked(self, mock_process, mock_stop, mock_start):
        """Test complete spacebar press/release workflow with mocked components"""
        # Setup mocks
        mock_stop.return_value = self.mock_audio_data
        mock_process.return_value = b"mock_response_audio"

        # Create MainLoop and simulate spacebar workflow
        main_loop = MainLoop()
        main_loop.start()

        # Simulate spacebar press
        main_loop._handle_spacebar_press()
        self.assertEqual(main_loop.current_state, ApplicationState.RECORDING)
        mock_start.assert_called_once()

        # Simulate spacebar release
        main_loop._handle_spacebar_release()
        self.assertEqual(main_loop.current_state, ApplicationState.PROCESSING)
        mock_stop.assert_called_once()
        mock_process.assert_called_once()

        main_loop.stop()

    def test_complete_pipeline_mocked(self):
        """Test the complete audio→text→AI→audio pipeline with mocks"""
        # Mock the entire pipeline
        with patch(
            "src.leadership_button.api_client.speech.SpeechClient"
        ) as mock_speech, patch(
            "google.generativeai.GenerativeModel"
        ) as mock_gemini, patch(
            "src.leadership_button.api_client.texttospeech.TextToSpeechClient"
        ) as mock_tts, patch.dict(
            "os.environ", {"GEMINI_API_KEY": "test-key"}
        ):

            # Setup speech-to-text mock
            mock_speech_result = Mock()
            mock_speech_result.results = [Mock()]
            mock_speech_result.results[0].alternatives = [Mock()]
            mock_speech_result.results[0].alternatives[
                0
            ].transcript = "Leadership question"
            mock_speech.return_value.recognize.return_value = mock_speech_result

            # Setup Gemini AI mock
            mock_gemini.return_value.generate_content.return_value.text = (
                "Leadership advice"
            )

            # Setup text-to-speech mock
            mock_tts.return_value.synthesize_speech.return_value.audio_content = (
                b"audio_response"
            )

            # Test complete pipeline
            api_manager = APIManager()
            result = api_manager.process_conversation_turn(self.mock_audio_data)

            self.assertIsNotNone(result)

    # =============================================================================
    # 4. ERROR SCENARIO TESTS
    # =============================================================================

    def test_missing_google_cloud_credentials(self):
        """Test behavior when Google Cloud credentials are missing"""
        with patch.dict("os.environ", {}, clear=True):
            # Remove any existing Google Cloud env vars
            with self.assertRaises(RuntimeError) as context:
                api_manager = APIManager()
                api_manager.speech_to_text(self.mock_audio_data)

            self.assertIn("Speech-to-Text service unavailable", str(context.exception))

    def test_missing_gemini_api_key(self):
        """Test behavior when Gemini API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            gemini_config = {"model": "gemini-1.5-flash"}

            with self.assertRaises((ValueError, RuntimeError)):
                provider = GeminiFlashProvider(gemini_config)
                provider.process_text("test question", {})

    def test_audio_recording_failure(self):
        """Test handling of audio recording failures"""
        with patch(
            "src.leadership_button.audio_handler.pyaudio.PyAudio"
        ) as mock_pyaudio:
            mock_pyaudio.side_effect = Exception("Audio device not available")

            with self.assertRaises(Exception):
                audio_handler = AudioHandler()
                audio_handler.start_recording()

    def test_api_timeout_handling(self):
        """Test API timeout scenarios"""
        with patch(
            "src.leadership_button.api_client.speech.SpeechClient"
        ) as mock_speech:
            mock_speech.return_value.recognize.side_effect = Exception(
                "Request timeout"
            )

            api_manager = APIManager()
            result = api_manager.speech_to_text(self.mock_audio_data)

            # Should handle gracefully and return None
            self.assertIsNone(result)

    # =============================================================================
    # 5. PERFORMANCE TESTS
    # =============================================================================

    def test_response_time_requirements(self):
        """Test that the workflow meets response time requirements"""
        with patch(
            "src.leadership_button.api_client.speech.SpeechClient"
        ) as mock_speech, patch(
            "google.generativeai.GenerativeModel"
        ) as mock_gemini, patch(
            "src.leadership_button.api_client.texttospeech.TextToSpeechClient"
        ) as mock_tts, patch.dict(
            "os.environ", {"GEMINI_API_KEY": "test-key"}
        ):

            # Setup fast mocks
            mock_speech.return_value.recognize.return_value = (
                self._create_mock_speech_result()
            )
            mock_gemini.return_value.generate_content.return_value.text = (
                "Quick response"
            )
            mock_tts.return_value.synthesize_speech.return_value.audio_content = (
                b"audio"
            )

            # Measure performance
            start_time = time.time()

            api_manager = APIManager()
            result = api_manager.process_conversation_turn(self.mock_audio_data)

            end_time = time.time()
            processing_time = end_time - start_time

            # Should complete within reasonable time (mocked, so should be very fast)
            self.assertLess(
                processing_time, 1.0, "Workflow should complete quickly with mocks"
            )

    def test_memory_usage(self):
        """Test memory usage during workflow"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Run workflow multiple times
        for _ in range(5):
            api_manager = APIManager()
            # Simulate workflow without actual API calls

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Should not have excessive memory growth (< 50MB increase)
        self.assertLess(
            memory_increase, 50 * 1024 * 1024, "Memory usage should be reasonable"
        )

    # =============================================================================
    # 6. REAL API INTEGRATION TESTS (Optional - requires credentials)
    # =============================================================================

    @unittest.skipUnless(
        "INTEGRATION_TESTS" in os.environ,
        "Set INTEGRATION_TESTS=1 to run real API tests",
    )
    def test_real_google_cloud_integration(self):
        """Test with real Google Cloud APIs (requires valid credentials)"""
        api_manager = APIManager()

        if api_manager.state == APIState.READY:
            result = api_manager.speech_to_text(self.mock_audio_data)
            # Real API might return None for fake audio, but shouldn't error
            # This test validates that the API setup and config are correct
        else:
            self.skipTest("Google Cloud APIs not available")

    @unittest.skipUnless(
        "INTEGRATION_TESTS" in os.environ,
        "Set INTEGRATION_TESTS=1 to run real API tests",
    )
    def test_real_gemini_integration(self):
        """Test with real Gemini API (requires valid API key)"""
        if "GEMINI_API_KEY" in os.environ:
            gemini_config = {"model": "gemini-1.5-flash", "temperature": 0.7}
            provider = GeminiFlashProvider(gemini_config)

            result = provider.process_text("What is good leadership?", {})
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 10)  # Should get a real response
        else:
            self.skipTest("GEMINI_API_KEY not available")

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _create_mock_speech_result(self):
        """Create a properly structured mock speech recognition result"""
        mock_result = Mock()
        mock_result.results = [Mock()]
        mock_result.results[0].alternatives = [Mock()]
        mock_result.results[0].alternatives[0].transcript = "Test leadership question"
        mock_result.results[0].alternatives[0].confidence = 0.95
        return mock_result


if __name__ == "__main__":
    # Run specific test categories
    import sys
    import os

    if "unit" in sys.argv:
        # Run only unit tests
        suite = unittest.TestLoader().loadTestsFromName(
            "test_audio_handler_recording_cycle"
        )
        unittest.TextTestRunner(verbosity=2).run(suite)
    elif "integration" in sys.argv:
        # Run integration tests
        os.environ["INTEGRATION_TESTS"] = "1"
        unittest.main(verbosity=2)
    else:
        # Run all tests except real API tests
        unittest.main(verbosity=2)
