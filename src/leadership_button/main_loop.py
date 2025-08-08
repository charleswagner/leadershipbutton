"""
Main Application Loop for Leadership & EQ Coach

This module implements the central orchestrator that manages the application
lifecycle, coordinates between audio handling and API client modules, and provides
a robust state machine for handling user interactions.
"""

import json
import logging
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pynput import keyboard

# Assuming these modules exist and are structured as per the specs
# These will be placeholder imports if the actual files don't exist yet
from .api_client import APIManager, APIConfig
from .audio_handler import AudioHandler
from .audio_playback import AudioPlaybackManager


class ApplicationState(Enum):
    """Application states for the state machine."""

    IDLE = "IDLE"
    RECORDING = "RECORDING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


class StateTransitionError(Exception):
    """Custom exception for invalid state transitions."""

    pass


class MainLoop:
    """
    Central orchestrator for the Leadership Button application.
    Manages state, coordinates components, and handles the main event loop.
    """

    def __init__(self, config_path: Optional[str] = "config/api_config.json"):
        """
        Initialize the main application loop.

        Args:
            config_path: Path to the API configuration file.
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.state_lock = threading.Lock()
        self.current_state = ApplicationState.IDLE

        # New: Event for spacebar state, more thread-safe
        self.spacebar_pressed_event = threading.Event()
        self.keyboard_listener: Optional[keyboard.Listener] = None

        self.audio_handler: Optional[AudioHandler] = None
        self.api_client: Optional[APIManager] = None
        self.playback_manager: Optional[AudioPlaybackManager] = None

        self.start_time = 0.0
        self.response_times: List[float] = []

        # Initialize all components
        self._initialize_components()

        self.logger.info("MainLoop initialization complete")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Provide a default configuration."""
        return {"audio": {"sample_rate": 16000, "channels": 1}, "api": {"timeout": 30}}

    def _initialize_components(self) -> None:
        """Initialize all required components."""
        try:
            # Initialize API client with centralized audio config
            config = APIConfig()
            self.api_client = APIManager(config)
            self.logger.info("API client initialized")

            # Initialize audio handler for microphone recording
            from .audio_handler import AudioHandler

            self.audio_handler = AudioHandler(config.config_data)
            self.logger.info("Audio handler initialized for microphone recording")

            # Initialize audio playback manager with centralized config
            self.playback_manager = AudioPlaybackManager(
                api_config_data=config.config_data
            )
            self.logger.info(
                "Audio playback manager initialized with centralized config"
            )

            # Set up AI provider (Gemini Flash with mock fallback)
            self._setup_ai_provider()

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            # Store the error for debugging
            self._last_error = str(e)

    def _setup_ai_provider(self) -> None:
        """Set up the AI provider for leadership coaching."""
        try:
            # Try to set up Gemini Flash provider
            from .gemini_provider import GeminiFlashProvider

            gemini_config = {
                "model": "gemini-1.5-flash",
                "temperature": 0.7,
                "max_tokens": 150,
                "timeout": 30,
            }

            gemini_provider = GeminiFlashProvider(gemini_config)

            if self.api_client:
                self.api_client.set_ai_provider(gemini_provider)
                self.logger.info("Gemini Flash AI provider set up successfully")

        except (ImportError, ValueError, RuntimeError) as e:
            # Fallback to mock provider if Gemini setup fails
            self.logger.warning(f"Failed to set up Gemini Flash provider: {e}")
            self.logger.info("Falling back to Mock AI provider")
            self._setup_mock_ai_provider()

    def _setup_mock_ai_provider(self) -> None:
        """Set up a mock AI provider as fallback."""

        # Import centralized prompts
        from .prompts_config import PromptsConfig

        # This setup is for development/testing as per spec
        class MockAIProvider:
            def process_text(self, text: str, context: dict) -> str:
                return PromptsConfig.get_mock_response(text)

            def get_provider_name(self) -> str:
                return PromptsConfig.get_mock_provider_name()

            def is_available(self) -> bool:
                return True

            def configure(self, settings: dict) -> None:
                pass

        if self.api_client:
            self.api_client.set_ai_provider(MockAIProvider())
            self.logger.info("Mock AI provider set up as fallback")

    def start(self) -> None:
        """Start the main application loop."""
        with self.state_lock:
            if self.running:
                self.logger.warning("MainLoop is already running")
                return
            self.running = True
            self.current_state = ApplicationState.IDLE
            self.start_time = time.time()

        self.logger.info("MainLoop started")

        self._initialize_components()

        # Set up and start the keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.keyboard_listener.start()

        print("🎤 HOLD THE SPACEBAR TO RECORD")
        print("Press Ctrl+C to exit.")

        # The listener runs in a separate thread, so we can wait for it to stop.
        # The main thread will block here until self.keyboard_listener.stop()
        # is called.
        self.keyboard_listener.join()

    def stop(self) -> None:
        """Stop the application and cleanup resources."""
        self.logger.info("Stopping MainLoop...")
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        with self.state_lock:
            if not self.running:
                return
            self.running = False

        self._cleanup()
        self.logger.info("MainLoop stopped")

    def _cleanup(self) -> None:
        """Cleanup resources and stop background threads."""
        try:
            if self.audio_handler:
                self.audio_handler.stop_recording()
            if self.api_client:
                self.api_client.cleanup()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def on_press(self, key):
        """Callback for key press events."""
        if key == keyboard.Key.space:
            # Check if the event is already set to avoid re-triggering
            if not self.spacebar_pressed_event.is_set():
                self.spacebar_pressed_event.set()
                if self.current_state == ApplicationState.IDLE:
                    self._handle_spacebar_press()
                elif self.current_state == ApplicationState.SPEAKING:
                    # Interrupt playback and start a new recording immediately
                    try:
                        if (
                            self.playback_manager
                            and self.playback_manager.audio_handler
                        ):
                            self.playback_manager.audio_handler.stop_playback()
                            self.logger.info("⏹️ Playback interrupted by user")
                    except Exception as exc:
                        self.logger.warning(f"Failed to stop playback: {exc}")
                    # Transition to recording
                    self._transition_state(ApplicationState.IDLE)
                    self._handle_spacebar_press()

    def on_release(self, key):
        """Callback for key release events."""
        if key == keyboard.Key.space:
            # Check if the event was set to avoid false releases
            if self.spacebar_pressed_event.is_set():
                self.spacebar_pressed_event.clear()
                if self.current_state == ApplicationState.RECORDING:
                    self._handle_spacebar_release()

    def _handle_spacebar_press(self) -> None:
        """Handle spacebar press event."""
        if self.current_state != ApplicationState.IDLE:
            self.logger.warning(f"Spacebar press ignored in state {self.current_state}")
            return

        if not self.audio_handler:
            self.logger.error("Cannot start recording - audio handler not available")
            self._handle_error(Exception("Audio handler not available"))
            return

        try:
            self._transition_state(ApplicationState.RECORDING)
            self.audio_handler.start_recording()
            self.logger.info("Recording started")
        except Exception as e:
            self._handle_error(e)

    def _handle_spacebar_release(self) -> None:
        """Handle spacebar release event."""
        if self.current_state != ApplicationState.RECORDING:
            self.logger.warning(
                f"Spacebar release ignored in state {self.current_state}"
            )
            return

        if not self.audio_handler:
            self.logger.error("Cannot stop recording - audio handler not available")
            self._handle_error(Exception("Audio handler not available"))
            return

        try:
            self._transition_state(ApplicationState.PROCESSING)
            # The test will mock _handle_recording_complete, so this call is fine.
            # The error is in the subsequent calls.
            audio_data = self.audio_handler.stop_recording()
            if audio_data and audio_data.data:
                self.logger.info("Recording stopped successfully")
                self._handle_recording_complete(audio_data.data)
            else:
                self.logger.error("No audio data from recording, returning to idle.")
                self._transition_state(ApplicationState.IDLE)
        except Exception as e:
            self._handle_error(e)

    def _handle_recording_complete(self, audio_data: bytes) -> None:
        """Process completed recording."""
        if self.current_state != ApplicationState.PROCESSING:
            self.logger.warning(
                f"Recording complete ignored in state {self.current_state}"
            )
            return

        if not audio_data:
            self.logger.error("No audio data received")
            self._handle_error(Exception("No audio data received"))
            return

        if not self.api_client:
            self.logger.error("API client not available")
            self._handle_error(Exception("API client not available"))
            return

        try:
            self.logger.info("Sending audio to API for processing...")
            response = self.api_client.process_conversation_turn(audio_data)
            self._handle_api_response(response)
        except Exception as e:
            self.logger.error(f"Failed to process audio: {e}")
            self._handle_error(e)

    def _handle_api_response(self, response: Any) -> None:
        """Handle API response and initiate playback."""
        if self.current_state != ApplicationState.PROCESSING:
            self.logger.warning(f"API response ignored in state {self.current_state}")
            return

        if not response:
            self.logger.warning("No audio content in API response, returning to idle.")
            self._transition_state(ApplicationState.IDLE)
            return

        if not self.playback_manager:
            self.logger.error("Playback manager not available")
            self._handle_error(Exception("Playback manager not available"))
            return

        try:
            self._transition_state(ApplicationState.SPEAKING)
            # Pass the full response object to preserve AudioData sample rate info
            # DO NOT extract .data - that loses the sample rate information!
            self.playback_manager.play_audio_and_wait(response, "api_response")
            self._handle_audio_complete()
        except Exception as e:
            self._handle_error(e)

    def _handle_audio_complete(self) -> None:
        """Handle audio playback completion."""
        if self.current_state != ApplicationState.SPEAKING:
            self.logger.warning(f"Audio complete ignored in state {self.current_state}")
            return

        self._transition_state(ApplicationState.IDLE)
        self.logger.info("Playback complete, returning to idle.")

    def _handle_error(self, error: Exception) -> None:
        """Handle errors and recover to IDLE state."""
        self.logger.error(f"Error occurred: {error}")
        self.logger.error(f"Error details: {type(error).__name__}: {str(error)}")

        if self.current_state != ApplicationState.ERROR:
            self._transition_state(ApplicationState.ERROR)

        # Attempt to recover to IDLE
        time.sleep(1)
        self._transition_state(ApplicationState.IDLE)

    def _transition_state(self, new_state: ApplicationState) -> None:
        """Internal state transition method."""
        with self.state_lock:
            old_state = self.current_state
            if (
                not self._is_valid_transition(old_state, new_state)
                and new_state != ApplicationState.ERROR
            ):
                error_msg = f"Invalid state transition: {old_state} -> {new_state}"
                self.logger.error(error_msg)
                # In a real scenario, we might not want to raise if we can recover
                # For now, we log it and allow the transition to ERROR state
                if new_state != ApplicationState.IDLE:  # Allow recovery to IDLE
                    raise StateTransitionError(error_msg)

            self.current_state = new_state
            self.logger.info(f"State transitioned from {old_state} to {new_state}")

    def _is_valid_transition(
        self, from_state: ApplicationState, to_state: ApplicationState
    ) -> bool:
        """Defines valid state transitions."""
        valid_transitions = {
            ApplicationState.IDLE: [ApplicationState.RECORDING, ApplicationState.ERROR],
            ApplicationState.RECORDING: [
                ApplicationState.PROCESSING,
                ApplicationState.ERROR,
            ],
            ApplicationState.PROCESSING: [
                ApplicationState.SPEAKING,
                ApplicationState.IDLE,
                ApplicationState.ERROR,
            ],
            ApplicationState.SPEAKING: [ApplicationState.IDLE, ApplicationState.ERROR],
            ApplicationState.ERROR: [ApplicationState.IDLE],
        }
        return to_state in valid_transitions.get(from_state, [])

    def get_state(self) -> ApplicationState:
        """Get current application state."""
        with self.state_lock:
            return self.current_state

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        uptime = time.time() - self.start_time if self.start_time > 0 else 0
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0
        )

        return {
            "uptime": uptime,
            "current_state": self.get_state().value,
            "average_response_time": avg_response_time,
            "response_times": self.response_times,
        }
