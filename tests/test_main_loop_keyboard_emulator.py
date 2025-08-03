"""
Test MainLoop with Keyboard Click Emulator

Tests the complete main loop workflow using a keyboard emulator to simulate
spacebar press/release events. Follows spec-driven testing principles:
- No manual input required
- Tests complete workflow programmatically
- Real verification of state transitions and audio processing
"""

import unittest
from unittest.mock import Mock, patch
import time
import tempfile
import json
import os


from src.leadership_button.main_loop import MainLoop, ApplicationState


class KeyboardEmulator:
    """Emulates keyboard input for testing spacebar press/release events."""

    def __init__(self):
        self.pressed = False
        self.input_events = []
        self.current_event_index = 0
        self.start_time = None

    def add_press_sequence(self, hold_duration: float, delay_before: float = 0):
        """Add a spacebar press/hold/release sequence.

        Args:
            hold_duration: How long to hold the spacebar (seconds)
            delay_before: Delay before pressing spacebar (seconds)
        """
        base_time = len(self.input_events) * 0.1  # Space out events

        # Add delay before press
        if delay_before > 0:
            self.input_events.append(
                {"time": base_time + delay_before, "action": "wait"}
            )
            base_time += delay_before

        # Add press event
        self.input_events.append({"time": base_time, "action": "press"})

        # Add release event
        self.input_events.append(
            {"time": base_time + hold_duration, "action": "release"}
        )

    def start(self):
        """Start the emulator timeline."""
        self.start_time = time.time()
        self.current_event_index = 0
        self.pressed = False

    def check_spacebar_held(self) -> bool:
        """Mock implementation of spacebar checking."""
        if self.start_time is None:
            return False

        current_time = time.time() - self.start_time

        # Process any pending events
        while (
            self.current_event_index < len(self.input_events)
            and self.input_events[self.current_event_index]["time"] <= current_time
        ):

            event = self.input_events[self.current_event_index]
            if event["action"] == "press":
                self.pressed = True
            elif event["action"] == "release":
                self.pressed = False

            self.current_event_index += 1

        return self.pressed

    def is_finished(self) -> bool:
        """Check if all events have been processed."""
        return self.current_event_index >= len(self.input_events)


class TestMainLoopKeyboardEmulator(unittest.TestCase):
    """Test MainLoop with keyboard emulation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

        test_config = {
            "audio": {"sample_rate": 16000, "channels": 1},
            "api": {"timeout": 30},
        }

        with open(self.config_file, "w") as f:
            json.dump(test_config, f)

        # Create keyboard emulator
        self.keyboard = KeyboardEmulator()

        # Create MainLoop instance
        self.main_loop = MainLoop(self.config_file)

        # Track state changes for verification
        self.state_history = []

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _track_state_changes(self, new_state):
        """Track state changes for verification."""
        self.state_history.append({"state": new_state, "time": time.time()})

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_single_recording_cycle_with_emulator(
        self, mock_api_class, mock_audio_class
    ):
        """Test a complete recording cycle using keyboard emulator."""
        # Arrange - Set up mocks
        mock_audio = Mock()
        mock_audio_result = Mock()
        mock_audio_result.data = b"test_audio_data_12345"
        mock_audio.start_recording.return_value = True
        mock_audio.stop_recording.return_value = mock_audio_result
        mock_audio.is_recording.return_value = True
        mock_audio_class.return_value = mock_audio

        mock_api = Mock()
        mock_api.process_conversation_turn.return_value = b"mock_response_audio"
        mock_api_class.return_value = mock_api

        # Set up keyboard sequence: wait 0.2s, press for 1.5s, release
        self.keyboard.add_press_sequence(hold_duration=1.5, delay_before=0.2)

        # Track state changes by patching _transition_state
        original_transition = self.main_loop._transition_state

        def track_transition(new_state):
            self._track_state_changes(new_state)
            return original_transition(new_state)

        # Mock the keyboard input method
        self.main_loop._check_spacebar_held = self.keyboard.check_spacebar_held

        # Act - Run the main loop in a separate thread with emulated input
        self.main_loop._transition_state = track_transition

        # Initialize components
        self.main_loop._initialize_components()

        # Start keyboard emulator
        self.keyboard.start()

        # Simulate main loop execution with timeout
        start_time = time.time()
        timeout = 5.0  # 5 second timeout

        while time.time() - start_time < timeout:
            if self.keyboard.is_finished() and len(self.state_history) >= 3:
                break

            # Simulate one iteration of the main loop
            spacebar_held = self.main_loop._check_spacebar_held()

            # State change detection (from main loop logic)
            if spacebar_held and not self.main_loop.spacebar_pressed:
                # Spacebar just pressed down
                self.main_loop.spacebar_pressed = True
                self.main_loop._handle_spacebar_press()

            elif not spacebar_held and self.main_loop.spacebar_pressed:
                # Spacebar just released
                self.main_loop.spacebar_pressed = False
                self.main_loop._handle_spacebar_release()

            time.sleep(0.05)  # Small delay to simulate main loop timing

        # Assert - Verify the complete workflow executed
        self.assertGreaterEqual(
            len(self.state_history), 3, "Should have at least 3 state transitions"
        )

        # Verify state transition sequence: RECORDING -> PROCESSING -> SPEAKING
        state_names = [s["state"].value for s in self.state_history]

        self.assertIn("RECORDING", state_names, "Should transition to RECORDING state")
        self.assertIn(
            "PROCESSING", state_names, "Should transition to PROCESSING state"
        )
        self.assertIn("SPEAKING", state_names, "Should transition to SPEAKING state")

        # Verify method calls occurred
        mock_audio.start_recording.assert_called()
        mock_audio.stop_recording.assert_called()
        mock_api.process_conversation_turn.assert_called_with(b"test_audio_data_12345")

        # Verify final state is IDLE (after audio completion)
        final_state = self.main_loop.get_state()
        self.assertEqual(
            final_state, ApplicationState.IDLE, "Should return to IDLE state"
        )

    @patch("src.leadership_button.main_loop.AudioHandler")
    @patch("src.leadership_button.main_loop.APIManager")
    def test_keyboard_emulator_integration(self, mock_api_class, mock_audio_class):
        """Test that keyboard emulator integrates correctly with main loop components."""
        # Arrange - Set up mocks
        mock_audio = Mock()
        mock_audio_result = Mock()
        mock_audio_result.data = b"integration_test_data"
        mock_audio.start_recording.return_value = True
        mock_audio.stop_recording.return_value = mock_audio_result
        mock_audio_class.return_value = mock_audio

        mock_api = Mock()
        mock_api.process_conversation_turn.return_value = b"integration_response"
        mock_api_class.return_value = mock_api

        # Test a quick press/release sequence
        self.keyboard.add_press_sequence(hold_duration=0.3, delay_before=0.1)

        # Mock the keyboard input method
        self.main_loop._check_spacebar_held = self.keyboard.check_spacebar_held

        # Act - Test integration
        self.main_loop._initialize_components()
        self.keyboard.start()

        # Simulate workflow
        press_detected = False
        release_detected = False
        start_time = time.time()

        while time.time() - start_time < 3.0:  # 3 second timeout
            spacebar_held = self.main_loop._check_spacebar_held()

            if spacebar_held and not press_detected:
                press_detected = True
                self.main_loop.spacebar_pressed = True
                self.main_loop._handle_spacebar_press()

            elif not spacebar_held and press_detected and not release_detected:
                release_detected = True
                self.main_loop.spacebar_pressed = False
                self.main_loop._handle_spacebar_release()
                break

            time.sleep(0.02)

        # Assert - Verify integration works
        self.assertTrue(press_detected, "Should detect emulated spacebar press")
        self.assertTrue(release_detected, "Should detect emulated spacebar release")
        mock_audio.start_recording.assert_called_once()
        mock_audio.stop_recording.assert_called_once()
        mock_api.process_conversation_turn.assert_called_once_with(
            b"integration_test_data"
        )

    @patch("src.leadership_button.main_loop.AudioHandler")
    def test_spacebar_timing_with_emulator(self, mock_audio_class):
        """Test spacebar press/release timing detection."""
        # Arrange
        mock_audio = Mock()
        mock_audio.start_recording.return_value = True
        mock_audio_class.return_value = mock_audio

        # Test different hold durations
        test_durations = [0.1, 0.5, 1.0, 2.0]  # Various hold times

        for duration in test_durations:
            with self.subTest(duration=duration):
                # Reset emulator
                self.keyboard = KeyboardEmulator()
                self.keyboard.add_press_sequence(hold_duration=duration)
                self.main_loop._check_spacebar_held = self.keyboard.check_spacebar_held

                # Act - Simulate timing
                self.keyboard.start()
                press_detected = False
                release_detected = False

                start_time = time.time()
                while time.time() - start_time < duration + 1.0:
                    spacebar_held = self.main_loop._check_spacebar_held()

                    if spacebar_held and not press_detected:
                        press_detected = True
                    elif not spacebar_held and press_detected and not release_detected:
                        release_detected = True
                        break

                    time.sleep(0.02)

                # Assert
                self.assertTrue(
                    press_detected, f"Should detect press for {duration}s hold"
                )
                self.assertTrue(
                    release_detected, f"Should detect release for {duration}s hold"
                )

    def test_keyboard_emulator_functionality(self):
        """Test the keyboard emulator itself works correctly."""
        # Arrange
        self.keyboard.add_press_sequence(hold_duration=1.0, delay_before=0.5)

        # Act & Assert - Test emulator behavior
        self.assertFalse(
            self.keyboard.check_spacebar_held(), "Should start not pressed"
        )

        self.keyboard.start()

        # Before delay
        self.assertFalse(
            self.keyboard.check_spacebar_held(), "Should not be pressed during delay"
        )

        # Simulate time passing to reach press event
        time.sleep(0.6)  # Past the 0.5s delay
        self.assertTrue(
            self.keyboard.check_spacebar_held(), "Should be pressed after delay"
        )

        # Simulate time passing to reach release event
        time.sleep(1.1)  # Past the 1.0s hold duration
        self.assertFalse(
            self.keyboard.check_spacebar_held(), "Should be released after hold"
        )

        self.assertTrue(
            self.keyboard.is_finished(), "Should be finished after all events"
        )


if __name__ == "__main__":
    # Run with verbose output to see test progress
    unittest.main(verbosity=2)
