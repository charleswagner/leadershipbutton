"""
Tests for the main application loop module.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import json
import os

from src.leadership_button.main_loop import (
    MainLoop,
    ApplicationState,
    StateTransitionError,
)


class TestMainLoop(unittest.TestCase):
    """Test cases for the MainLoop class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

        test_config = {
            "audio": {"sample_rate": 16000, "channels": 1},
            "api": {"timeout": 30},
        }

        with open(self.config_file, "w") as f:
            json.dump(test_config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_initialization(self, mock_api_manager, mock_audio_handler):
        """Test MainLoop initialization."""
        # Mock the components
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        # Create MainLoop instance
        main_loop = MainLoop(self.config_file)

        # Verify initialization
        self.assertEqual(main_loop.current_state, ApplicationState.IDLE)
        self.assertFalse(main_loop.running)
        self.assertIsNotNone(main_loop.config)
        self.assertIsNotNone(main_loop.audio_handler)
        self.assertIsNotNone(main_loop.api_client)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_config_loading(self, mock_api_manager, mock_audio_handler):
        """Test configuration loading."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Verify config was loaded correctly
        self.assertIn("audio", main_loop.config)
        self.assertIn("api", main_loop.config)
        self.assertEqual(main_loop.config["audio"]["sample_rate"], 16000)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_default_config_loading(self, mock_api_manager, mock_audio_handler):
        """Test default configuration loading when file doesn't exist."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop("nonexistent_config.json")

        # Verify default config was loaded
        self.assertIn("audio", main_loop.config)
        self.assertIn("api", main_loop.config)
        self.assertIn("logging", main_loop.config)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_valid_state_transitions(self, mock_api_manager, mock_audio_handler):
        """Test valid state transitions."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test valid transitions
        main_loop._transition_state(ApplicationState.RECORDING)
        self.assertEqual(main_loop.current_state, ApplicationState.RECORDING)

        main_loop._transition_state(ApplicationState.PROCESSING)
        self.assertEqual(main_loop.current_state, ApplicationState.PROCESSING)

        main_loop._transition_state(ApplicationState.SPEAKING)
        self.assertEqual(main_loop.current_state, ApplicationState.SPEAKING)

        main_loop._transition_state(ApplicationState.IDLE)
        self.assertEqual(main_loop.current_state, ApplicationState.IDLE)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_invalid_state_transitions(self, mock_api_manager, mock_audio_handler):
        """Test invalid state transitions."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test invalid transition from IDLE to PROCESSING
        with self.assertRaises(StateTransitionError):
            main_loop._transition_state(ApplicationState.PROCESSING)

        # Test invalid transition from IDLE to SPEAKING
        with self.assertRaises(StateTransitionError):
            main_loop._transition_state(ApplicationState.SPEAKING)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_error_state_transition(self, mock_api_manager, mock_audio_handler):
        """Test error state transitions."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test transition to error state from any state
        main_loop._transition_state(ApplicationState.ERROR)
        self.assertEqual(main_loop.current_state, ApplicationState.ERROR)

        # Test transition from error to idle
        main_loop._transition_state(ApplicationState.IDLE)
        self.assertEqual(main_loop.current_state, ApplicationState.IDLE)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_button_press_handling(self, mock_api_manager, mock_audio_handler):
        """Test button press handling."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test button press in IDLE state
        main_loop._handle_button_press()
        self.assertEqual(main_loop.current_state, ApplicationState.RECORDING)

        # Test button press in non-IDLE state (should be ignored)
        main_loop._handle_button_press()
        self.assertEqual(
            main_loop.current_state, ApplicationState.RECORDING
        )  # Should not change

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_recording_complete_handling(self, mock_api_manager, mock_audio_handler):
        """Test recording complete handling."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Set up recording state
        main_loop._transition_state(ApplicationState.RECORDING)

        # Test recording complete
        test_audio_data = b"test_audio_data"
        main_loop._handle_recording_complete(test_audio_data)
        self.assertEqual(main_loop.current_state, ApplicationState.PROCESSING)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_api_response_handling(self, mock_api_manager, mock_audio_handler):
        """Test API response handling."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Set up processing state
        main_loop._transition_state(ApplicationState.PROCESSING)

        # Test API response with audio content
        test_response = {"audio_content": b"test_response_audio"}
        main_loop._handle_api_response(test_response)
        self.assertEqual(main_loop.current_state, ApplicationState.SPEAKING)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_audio_complete_handling(self, mock_api_manager, mock_audio_handler):
        """Test audio complete handling."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Set up speaking state
        main_loop._transition_state(ApplicationState.SPEAKING)

        # Test audio complete
        main_loop._handle_audio_complete()
        self.assertEqual(main_loop.current_state, ApplicationState.IDLE)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_error_handling(self, mock_api_manager, mock_audio_handler):
        """Test error handling."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test error handling
        test_error = Exception("Test error")
        main_loop._handle_error(test_error)

        # Should transition to error state and then back to idle
        self.assertEqual(main_loop.current_state, ApplicationState.IDLE)

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_performance_stats(self, mock_api_manager, mock_audio_handler):
        """Test performance statistics."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Get performance stats
        stats = main_loop.get_performance_stats()

        # Verify stats structure
        self.assertIn("uptime", stats)
        self.assertIn("current_state", stats)
        self.assertIn("response_times", stats)
        self.assertIn("average_response_time", stats)
        self.assertEqual(stats["current_state"], "IDLE")

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_cleanup(self, mock_api_manager, mock_audio_handler):
        """Test cleanup functionality."""
        mock_audio_handler.return_value = Mock()
        mock_api_manager.return_value = Mock()

        main_loop = MainLoop(self.config_file)

        # Test cleanup
        main_loop._cleanup()

        # Verify cleanup methods were called
        main_loop.audio_handler.stop_recording.assert_called_once()
        main_loop.audio_handler.stop_playback.assert_called_once()
        main_loop.api_client.close.assert_called_once()


class TestAudioTestUtils(unittest.TestCase):
    """Test cases for the AudioTestUtils class."""

    def test_generate_test_tone(self):
        """Test test tone generation."""
        from tests.audio_test_utils import AudioTestUtils

        # Test tone generation
        audio_data = AudioTestUtils.generate_test_tone(440, 1.0)

        # Verify audio data
        self.assertIsInstance(audio_data, bytes)
        self.assertGreater(len(audio_data), 0)

        # For 1 second at 16kHz, 16-bit mono: 16000 * 2 = 32000 bytes
        expected_size = 16000 * 2  # sample_rate * bytes_per_sample
        self.assertEqual(len(audio_data), expected_size)

    def test_system_audio_devices(self):
        """Test system audio device detection."""
        from tests.audio_test_utils import AudioTestUtils

        # This test might fail if PyAudio is not available
        try:
            result = AudioTestUtils.test_system_audio_devices()
            # Should return True if PyAudio is available and devices are found
            self.assertIsInstance(result, bool)
        except ImportError:
            # Skip test if PyAudio is not available
            self.skipTest("PyAudio not available")

    @patch("tests.audio_test_utils.AudioHandler")
    def test_audio_playback_mock(self, mock_audio_handler):
        """Test audio playback with mocked audio handler."""
        from tests.audio_test_utils import AudioTestUtils

        # Mock the audio handler
        mock_handler = Mock()
        mock_handler.play_audio.return_value = True
        mock_handler.is_playing.return_value = False
        mock_audio_handler.return_value = mock_handler

        # Test audio playback without user confirmation
        success, message = AudioTestUtils.test_audio_playback(
            require_user_confirmation=False
        )

        self.assertTrue(success)
        self.assertIn("Audio playback completed", message)


if __name__ == "__main__":
    unittest.main()
