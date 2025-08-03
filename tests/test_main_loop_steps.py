"""
Tests for individual steps of the MainLoop workflow.

Tests each step of the main loop independently using centralized methods
from the MainLoop class. Follows spec-driven testing principles:
- No business logic in tests (orchestration and verification only)
- No manual input required
- Minimal output (pass/fail only)
- Tests one specific function per method
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


class TestMainLoopSteps(unittest.TestCase):
    """Test individual steps of the MainLoop workflow."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

        test_config = {
            "api_settings": {"timeout_seconds": 30, "retry_max_attempts": 3},
            "google_cloud": {
                "region": "us-central1",
                "speech_to_text": {
                    "sample_rate_hertz": 16000,
                    "language_code": "en-US",
                    "model": "default",
                    "enable_automatic_punctuation": True,
                    "max_alternatives": 1,
                },
                "text_to_speech": {
                    "voice_name": "en-US-Wavenet-D",
                    "language_code": "en-US",
                    "speaking_rate": 1.0,
                    "pitch": 0.0,
                    "volume_gain_db": 0.0,
                },
            },
            "audio_settings": {
                "sample_rate": 16000,
                "channels": 1,
                "output_sample_rate": 16000,
            },
            "performance": {},
            "features": {},
            "development": {"verbose_logging": True},
        }

        with open(self.config_file, "w") as f:
            json.dump(test_config, f)

        # Create MainLoop instance
        self.main_loop = MainLoop(self.config_file)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    # Test 1: Component Initialization
    def test_initialize_components_success(self):
        """Test successful component initialization."""
        # Act
        self.main_loop._initialize_components()

        # Assert
        self.assertIsNotNone(self.main_loop.audio_handler)
        self.assertIsNotNone(self.main_loop.api_client)
        self.assertTrue(self.main_loop.api_client.ai_provider.is_available())

    def test_initialize_components_audio_failure(self):
        """Test component initialization with audio handler failure."""
        with patch("src.leadership_button.main_loop.AudioHandler") as mock_audio:
            mock_audio.side_effect = Exception("Audio initialization failed")

            with self.assertLogs(
                "src.leadership_button.main_loop", level="ERROR"
            ) as log:
                self.main_loop._initialize_components()

            self.assertIn("Failed to initialize audio handler", log.output[-1])

    # Test 2: State Transitions
    def test_transition_state_valid(self):
        """Test valid state transitions."""
        # Act
        self.main_loop._transition_state(ApplicationState.RECORDING)

        # Assert
        self.assertEqual(self.main_loop.get_state(), ApplicationState.RECORDING)

    def test_transition_state_invalid(self):
        """Test invalid state transitions raise errors."""
        # Arrange - start in IDLE state
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

        # Act & Assert - can't go directly from IDLE to SPEAKING
        with self.assertRaises(StateTransitionError):
            self.main_loop._transition_state(ApplicationState.SPEAKING)

    def test_is_valid_transition_logic(self):
        """Test state transition validation logic."""
        # Valid transitions
        self.assertTrue(
            self.main_loop._is_valid_transition(
                ApplicationState.IDLE, ApplicationState.RECORDING
            )
        )
        self.assertTrue(
            self.main_loop._is_valid_transition(
                ApplicationState.RECORDING, ApplicationState.PROCESSING
            )
        )

        # Invalid transitions
        self.assertFalse(
            self.main_loop._is_valid_transition(
                ApplicationState.IDLE, ApplicationState.SPEAKING
            )
        )
        self.assertFalse(
            self.main_loop._is_valid_transition(
                ApplicationState.PROCESSING, ApplicationState.RECORDING
            )
        )

    # Test 3: Recording Start
    @patch("src.leadership_button.main_loop.AudioHandler")
    def test_handle_spacebar_press_success(self, mock_audio_class):
        """Test successful recording start."""
        # Arrange
        mock_audio = Mock()
        mock_audio_class.return_value = mock_audio
        self.main_loop._initialize_components()

        # Act
        self.main_loop._handle_spacebar_press()

        # Assert
        self.assertEqual(self.main_loop.get_state(), ApplicationState.RECORDING)
        mock_audio.start_recording.assert_called_once()

    def test_handle_spacebar_press_wrong_state(self):
        """Test spacebar press ignored in wrong state."""
        # Arrange
        self.main_loop._transition_state(ApplicationState.RECORDING)

        # Act & Assert
        with self.assertLogs(level="WARNING") as log:
            self.main_loop._handle_spacebar_press()

        self.assertIn("Spacebar press ignored", log.output[0])

    def test_handle_spacebar_press_no_audio_handler(self):
        """Test spacebar press when audio handler unavailable."""
        # Arrange
        self.main_loop.audio_handler = None

        # Act & Assert
        with self.assertLogs(level="ERROR") as log:
            self.main_loop._handle_spacebar_press()

        self.assertIn("Cannot start recording", log.output[0])
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

    # Test 4: Recording Stop
    @patch("src.leadership_button.main_loop.AudioHandler")
    def test_handle_spacebar_release_success(self, mock_audio_class):
        """Test successful recording stop."""
        # Arrange
        mock_audio = Mock()
        mock_audio_result = Mock()
        mock_audio_result.data = b"test_audio_data"
        mock_audio.stop_recording.return_value = mock_audio_result
        mock_audio_class.return_value = mock_audio
        self.main_loop._initialize_components()
        self.main_loop._transition_state(ApplicationState.RECORDING)

        # Act
        self.main_loop._handle_spacebar_release()

        # Assert
        mock_audio.stop_recording.assert_called()

    def test_handle_spacebar_release_wrong_state(self):
        """Test spacebar release ignored in wrong state."""
        # Act & Assert
        with self.assertLogs(level="WARNING") as log:
            self.main_loop._handle_spacebar_release()

        self.assertIn("Spacebar release ignored", log.output[0])

    # Test 5: Audio Processing
    @patch("src.leadership_button.main_loop.APIManager")
    def test_handle_recording_complete_success(self, mock_api_class):
        """Test successful audio processing."""
        # Arrange
        mock_api = Mock()
        mock_api.process_conversation_turn.return_value = b"test_response"
        mock_api_class.return_value = mock_api
        self.main_loop._initialize_components()
        self.main_loop._transition_state(ApplicationState.RECORDING)
        self.main_loop._transition_state(ApplicationState.PROCESSING)

        test_audio = b"test_audio_data"

        # Act
        with patch.object(
            self.main_loop, "_handle_api_response"
        ) as mock_handle_response:
            self.main_loop._handle_recording_complete(test_audio)

            # Assert
            self.assertEqual(self.main_loop.get_state(), ApplicationState.PROCESSING)
            mock_api.process_conversation_turn.assert_called_once_with(test_audio)
            mock_handle_response.assert_called_once_with(b"test_response")

    def test_handle_recording_complete_no_audio(self):
        """Test recording complete with no audio data."""
        # Arrange
        self.main_loop._transition_state(ApplicationState.RECORDING)
        self.main_loop._transition_state(ApplicationState.PROCESSING)

        # Act & Assert
        with self.assertLogs("src.leadership_button.main_loop", level="ERROR") as log:
            self.main_loop._handle_recording_complete(None)

        self.assertIn("No audio data received", log.output[0])
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

    def test_handle_recording_complete_wrong_state(self):
        """Test recording complete ignored in wrong state."""
        # Arrange - set up in IDLE state (not PROCESSING)
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

        # Act & Assert
        with self.assertLogs(level="WARNING") as log:
            self.main_loop._handle_recording_complete(b"test_audio")

        self.assertIn("Recording complete ignored", log.output[0])

    # Test 6: API Response Handling
    @patch("src.leadership_button.main_loop.AudioPlaybackManager")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_handle_api_response_success(self, mock_api_class, mock_playback_class):
        """Test successful API response handling."""
        # Arrange
        mock_playback = mock_playback_class.return_value
        mock_playback.play_audio_and_wait.return_value = True

        self.main_loop._initialize_components()
        # The real playback_manager is replaced by the mock here
        self.main_loop.playback_manager = mock_playback

        self.main_loop._transition_state(ApplicationState.RECORDING)
        self.main_loop._transition_state(ApplicationState.PROCESSING)

        test_response = b"test_audio_response"

        # Act
        with patch.object(
            self.main_loop, "_handle_audio_complete"
        ) as mock_audio_complete:
            self.main_loop._handle_api_response(test_response)

            # Assert
            self.assertEqual(self.main_loop.get_state(), ApplicationState.SPEAKING)
            mock_playback.play_audio_and_wait.assert_called_once_with(
                test_response, "api_response.raw"
            )
            mock_audio_complete.assert_called_once()

    def test_handle_api_response_no_response(self):
        """Test API response handling with no response."""
        # Arrange - follow valid transition path: IDLE -> RECORDING -> PROCESSING
        self.main_loop._transition_state(ApplicationState.RECORDING)
        self.main_loop._transition_state(ApplicationState.PROCESSING)

        # Act & Assert
        with self.assertLogs("src.leadership_button.main_loop", level="WARNING") as log:
            self.main_loop._handle_api_response(None)

        self.assertIn("No audio content in API response", log.output[0])
        # No response transitions to IDLE (through _handle_audio_complete)
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

    def test_handle_api_response_wrong_state(self):
        """Test API response ignored in wrong state."""
        # Act & Assert
        with self.assertLogs(level="WARNING") as log:
            self.main_loop._handle_api_response(b"test_response")

        self.assertIn("API response ignored", log.output[0])

    # Test 7: Audio Playback Complete
    def test_handle_audio_complete_success(self):
        """Test successful audio playback completion."""
        # Arrange - follow valid transition path: IDLE -> RECORDING -> PROCESSING -> SPEAKING
        self.main_loop._transition_state(ApplicationState.RECORDING)
        self.main_loop._transition_state(ApplicationState.PROCESSING)
        self.main_loop._transition_state(ApplicationState.SPEAKING)

        # Act
        self.main_loop._handle_audio_complete()

        # Assert
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

    def test_handle_audio_complete_wrong_state(self):
        """Test audio complete ignored in wrong state."""
        # Act & Assert
        with self.assertLogs(level="WARNING") as log:
            self.main_loop._handle_audio_complete()

        self.assertIn("Audio complete ignored", log.output[0])

    # Test 8: Error Handling
    def test_handle_error_transitions_to_error_state(self):
        """Test error handling transitions and recovers to idle state."""
        # Arrange
        test_error = Exception("Test error")

        # Act
        self.main_loop._handle_error(test_error)

        # Assert - error handling recovers back to IDLE state
        self.assertEqual(self.main_loop.get_state(), ApplicationState.IDLE)

    # Test 9: Performance Stats
    def test_get_performance_stats_structure(self):
        """Test performance stats return correct structure."""
        # Act
        stats = self.main_loop.get_performance_stats()

        # Assert
        self.assertIsInstance(stats, dict)
        self.assertIn("uptime", stats)
        self.assertIn("current_state", stats)
        self.assertIn("average_response_time", stats)
        self.assertIn("response_times", stats)

        # Verify data types
        self.assertIsInstance(stats["uptime"], (int, float))
        self.assertIsInstance(stats["current_state"], str)
        self.assertIsInstance(stats["average_response_time"], (int, float))
        self.assertIsInstance(stats["response_times"], list)


if __name__ == "__main__":
    unittest.main()
