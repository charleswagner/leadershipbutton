"""
Centralized Audio Playback Module

This module provides a unified interface for playing audio from various sources:
- Google TTS API responses
- AudioData objects
- Raw audio bytes
- WAV files

It handles all the format conversion and playback logic in one place.
"""

import logging
import time
from typing import Optional, Any
import threading
from pathlib import Path

from .audio_handler import AudioHandler, AudioConfig, AudioData, audio_config_manager

logger = logging.getLogger(__name__)


class AudioPlaybackManager:
    """
    Centralized audio playback manager that handles all audio sources and formats.
    Uses centralized audio configuration for consistency.
    """

    def __init__(
        self,
        audio_config: Optional[AudioConfig] = None,
        api_config_data: Optional[Any] = None,
    ):
        """
        Initialize the audio playback manager.

        Args:
            audio_config: Audio configuration. If None, uses centralized config.
            api_config_data: API configuration data to update centralized config.
        """
        # Update centralized config if API config provided
        if api_config_data:
            audio_config_manager.update_config(api_config_data)

        # Use provided config or create from centralized manager
        self.audio_config = audio_config or AudioConfig()
        self.audio_handler = AudioHandler(self.audio_config)
        self.logger = logging.getLogger(__name__)

        playback_config = audio_config_manager.get_playback_config()
        self.logger.info(
            f"🔧 AudioPlaybackManager: Using centralized playback config ({playback_config['sample_rate']} Hz)"
        )

    def play_audio_response(
        self, audio_response: Any, description: str = "audio"
    ) -> bool:
        """
        Play audio from any response type (TTS API, AudioData, raw bytes, etc.)

        Args:
            audio_response: Audio data from any source
            description: Description of the audio for logging

        Returns:
            True if playback started successfully, False otherwise
        """
        try:
            # For AudioData objects, pass directly to preserve sample rate info
            if isinstance(audio_response, AudioData):
                success = self.audio_handler.play_audio(audio_response)
                audio_size = len(audio_response.data)
                self.logger.info(
                    f"🔊 PLAYING AudioData: {audio_response.sample_rate} Hz, {audio_size} bytes"
                )
            else:
                # Extract audio data for other response types
                audio_data = self._extract_audio_data(audio_response)
                if not audio_data:
                    self.logger.error(
                        f"Failed to extract audio data from {description}"
                    )
                    return False
                success = self.audio_handler.play_audio(audio_data)
                audio_size = len(audio_data)
                self.logger.info(f"🔊 PLAYING raw bytes: {audio_size} bytes")

            if success:
                self.logger.info(
                    f"✅ Audio playback started for {description}: "
                    f"{audio_size} bytes"
                )
                return True
            else:
                self.logger.error(
                    f"❌ Failed to start audio playback for {description}"
                )
                return False

        except Exception as e:
            self.logger.error(f"❌ Audio playback failed for {description}: {e}")
            return False

    def play_audio_and_wait(
        self,
        audio_response: Any,
        description: str = "audio",
        stop_event: Optional[threading.Event] = None,
    ) -> bool:
        """
        Play audio and wait for completion.

        Args:
            audio_response: Audio data from any source
            description: Description of the audio for logging

        Returns:
            True if playback completed successfully, False otherwise
        """
        try:
            # Start playback
            if not self.play_audio_response(audio_response, description):
                return False

            # Wait for completion with no forced timeout; rely on stop_event or natural completion
            self.logger.info(f"⏱️  Waiting for {description} playback to complete...")
            sleep_interval = 0.1

            while self.audio_handler.is_playing():
                # If a stop event is provided and set, interrupt playback
                if stop_event is not None and stop_event.is_set():
                    try:
                        self.audio_handler.stop_playback()
                    except Exception:
                        pass
                    break
                time.sleep(sleep_interval)

            self.logger.info(f"✅ {description} playback completed")
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Audio playback and wait failed for {description}: {e}"
            )
            return False

    def _extract_audio_data(self, audio_response: Any) -> Optional[bytes]:
        """
        Extract raw audio bytes from any response type.

        Args:
            audio_response: Audio data from any source

        Returns:
            Raw audio bytes, or None if extraction failed
        """
        try:
            # Case 1: AudioData object (from our audio_handler module)
            if isinstance(audio_response, AudioData):
                self.logger.debug(
                    f"Extracting from AudioData object: {len(audio_response.data)} bytes"
                )
                return audio_response.data

            # Case 2: Has .data attribute (AudioData-like object)
            elif hasattr(audio_response, "data") and hasattr(
                audio_response.data, "__len__"
            ):
                self.logger.debug(
                    f"Extracting from object with .data attribute: {len(audio_response.data)} bytes"
                )
                return audio_response.data

            # Case 3: Raw bytes
            elif isinstance(audio_response, bytes):
                self.logger.debug(
                    f"Extracting from raw bytes: {len(audio_response)} bytes"
                )
                return audio_response

            # Case 4: String (file path)
            elif isinstance(audio_response, str):
                file_path = Path(audio_response)
                if file_path.exists():
                    self.logger.debug(f"Reading audio from file: {file_path}")
                    with open(file_path, "rb") as f:
                        return f.read()
                else:
                    self.logger.error(f"Audio file not found: {file_path}")
                    return None

            # Case 5: None or empty
            elif audio_response is None:
                self.logger.error("Audio response is None")
                return None

            # Case 6: Unknown type
            else:
                self.logger.error(
                    f"Unknown audio response type: {type(audio_response)}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to extract audio data: {e}")
            return None

    def get_audio_info(self, audio_response: Any) -> dict:
        """
        Get information about the audio response.

        Args:
            audio_response: Audio data from any source

        Returns:
            Dictionary with audio information
        """
        info = {
            "type": type(audio_response).__name__,
            "size_bytes": None,
            "sample_rate": None,
            "channels": None,
            "format": None,
        }

        try:
            # Extract audio data
            audio_data = self._extract_audio_data(audio_response)
            if audio_data:
                info["size_bytes"] = len(audio_data)

            # Get additional info for AudioData objects
            if isinstance(audio_response, AudioData):
                info["sample_rate"] = audio_response.sample_rate
                info["channels"] = audio_response.channels
                info["format"] = audio_response.format
                info["duration"] = audio_response.duration

            # Get additional info for objects with .data attribute
            elif hasattr(audio_response, "data"):
                if hasattr(audio_response, "sample_rate"):
                    info["sample_rate"] = audio_response.sample_rate
                if hasattr(audio_response, "channels"):
                    info["channels"] = audio_response.channels
                if hasattr(audio_response, "format"):
                    info["format"] = audio_response.format

        except Exception as e:
            self.logger.error(f"Failed to get audio info: {e}")

        return info

    def save_audio_debug(self, audio_response: Any, filepath: str) -> bool:
        """
        Save audio response to a file for debugging.

        Args:
            audio_response: Audio data from any source
            filepath: Path to save the audio file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            audio_data = self._extract_audio_data(audio_response)
            if not audio_data:
                return False

            # Save as raw audio
            with open(filepath, "wb") as f:
                f.write(audio_data)

            self.logger.info(
                f"💾 Debug audio saved: {filepath} ({len(audio_data)} bytes)"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to save debug audio: {e}")
            return False

    def cleanup(self):
        """Clean up audio handler resources."""
        if self.audio_handler:
            self.audio_handler.cleanup()

    def stop_playback(self) -> None:
        """Immediately stop any active playback."""
        try:
            if self.audio_handler:
                self.audio_handler.stop_playback()
        except Exception:
            pass


# Convenience functions for easy use
def play_audio(audio_response: Any, description: str = "audio") -> bool:
    """
    Convenience function to play audio from any source.

    Args:
        audio_response: Audio data from any source
        description: Description of the audio for logging

    Returns:
        True if playback started successfully, False otherwise
    """
    manager = AudioPlaybackManager()
    try:
        return manager.play_audio_response(audio_response, description)
    finally:
        manager.cleanup()


def play_audio_and_wait(
    audio_response: Any,
    description: str = "audio",
    stop_event: Optional[threading.Event] = None,
) -> bool:
    """
    Convenience function to play audio and wait for completion.

    Args:
        audio_response: Audio data from any source
        description: Description of the audio for logging

    Returns:
        True if playback completed successfully, False otherwise
    """
    manager = AudioPlaybackManager()
    try:
        return manager.play_audio_and_wait(audio_response, description, stop_event)
    finally:
        manager.cleanup()


def get_audio_info(audio_response: Any) -> dict:
    """
    Convenience function to get audio information.

    Args:
        audio_response: Audio data from any source

    Returns:
        Dictionary with audio information
    """
    manager = AudioPlaybackManager()
    try:
        return manager.get_audio_info(audio_response)
    finally:
        manager.cleanup()
