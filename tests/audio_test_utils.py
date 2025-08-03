#!/usr/bin/env python3
"""
Audio Testing Utilities

Reusable audio testing functions for both unit tests and integration tests.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import time
import math
from typing import Optional, Tuple

from leadership_button.audio_handler import AudioHandler, AudioConfig


class AudioTestUtils:
    """Utility class for audio testing functions"""

    @staticmethod
    def test_system_audio_devices() -> bool:
        """Test system audio capabilities and list devices"""
        print("🔧 System Audio Diagnostics")
        print("=" * 40)

        try:
            import pyaudio

            audio = pyaudio.PyAudio()

            # List available output devices
            print("Available output devices:")
            output_devices = []
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info["maxOutputChannels"] > 0:
                    print(f"  Device {i}: {device_info['name']}")
                    output_devices.append(i)

            if not output_devices:
                print("❌ No output devices found")
                audio.terminate()
                return False

            # Get default output device
            try:
                default_output = audio.get_default_output_device_info()
                print(f"\nDefault output device: {default_output['name']}")
            except Exception as e:
                print(f"⚠️  Could not get default output device: {e}")

            audio.terminate()
            print("✅ System audio devices detected")
            return True

        except Exception as e:
            print(f"❌ System audio test failed: {e}")
            return False

    @staticmethod
    def generate_test_tone(
        frequency: int = 440, duration: float = 1.0, sample_rate: int = 16000
    ) -> bytes:
        """Generate a test tone (sine wave) for audio testing"""
        samples = int(sample_rate * duration)
        audio_data = bytearray()

        for i in range(samples):
            # Generate sine wave
            value = int(
                32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate)
            )
            # Convert to 16-bit little-endian
            audio_data.extend(value.to_bytes(2, byteorder="little", signed=True))

        return bytes(audio_data)

    @staticmethod
    def test_audio_playback(
        audio_data: Optional[bytes] = None,
        frequency: int = 440,
        duration: float = 1.0,
        require_user_confirmation: bool = True,
    ) -> Tuple[bool, str]:
        """
        Test basic audio playback functionality

        Args:
            audio_data: Pre-generated audio data (if None, generates test tone)
            frequency: Frequency of test tone in Hz (if generating)
            duration: Duration of test tone in seconds (if generating)
            require_user_confirmation: Whether to ask user for confirmation

        Returns:
            Tuple of (success: bool, message: str)
        """
        print("🔊 Testing Audio Playback")
        print("=" * 40)

        try:
            # Initialize audio handler
            config = AudioConfig()
            audio_handler = AudioHandler(config)
            print("✅ Audio handler initialized")

            # Generate or use provided audio data
            if audio_data is None:
                audio_data = AudioTestUtils.generate_test_tone(frequency, duration)
                print(f"✅ Generated test tone: {frequency}Hz for {duration} seconds")
            else:
                print(f"✅ Using provided audio data: {len(audio_data)} bytes")

            print(f"📊 Audio data size: {len(audio_data)} bytes")

            # Test playback
            print("\n🔊 Playing test tone...")
            if frequency == 440:
                print("You should hear a beep sound (A4 note) for 1 second.")
            else:
                print(f"You should hear a {frequency}Hz tone for {duration} seconds.")

            success = audio_handler.play_audio(audio_data)

            if success:
                print("✅ Audio playback started")

                # Wait for playback to complete
                while audio_handler.is_playing():
                    time.sleep(0.1)

                print("✅ Audio playback completed")

                if require_user_confirmation:
                    # Ask user for confirmation
                    response = (
                        input("\nDid you hear the test tone? (y/n): ").strip().lower()
                    )
                    if response in ["y", "yes"]:
                        return True, "Audio playback is working correctly!"
                    else:
                        return False, "User did not hear the test tone"
                else:
                    return True, "Audio playback completed without user confirmation"
            else:
                return False, "Failed to start audio playback"

        except Exception as e:
            return False, f"Audio playback test failed: {e}"

    @staticmethod
    def run_comprehensive_audio_test() -> bool:
        """Run a comprehensive audio test including system check and playback"""
        print("🎵 Comprehensive Audio Test")
        print("=" * 50)

        # Step 1: Test system audio devices
        system_ok = AudioTestUtils.test_system_audio_devices()

        if not system_ok:
            print("\n❌ System audio test failed.")
            print("Please check your audio device configuration.")
            return False

        # Step 2: Test actual playback
        playback_ok, message = AudioTestUtils.test_audio_playback()

        if playback_ok:
            print(f"\n🎉 {message}")
            return True
        else:
            print(f"\n❌ {message}")
            print("Please check your speaker settings and volume.")
            return False

    @staticmethod
    def test_audio_recording(duration: float = 3.0) -> Tuple[bool, Optional[bytes]]:
        """
        Test audio recording functionality

        Args:
            duration: Recording duration in seconds

        Returns:
            Tuple of (success: bool, audio_data: Optional[bytes])
        """
        print("🎤 Testing Audio Recording")
        print("=" * 40)

        try:
            # Initialize audio handler
            config = AudioConfig()
            audio_handler = AudioHandler(config)
            print("✅ Audio handler initialized")

            # Start recording
            success = audio_handler.start_recording()
            if not success:
                return False, None

            print(f"🎤 Recording for {duration} seconds...")
            print("Please speak into your microphone.")

            # Record for specified duration
            start_time = time.time()
            while time.time() - start_time < duration:
                remaining = duration - (time.time() - start_time)
                print(
                    f"\rRecording... {remaining:.1f} seconds remaining",
                    end="",
                    flush=True,
                )
                time.sleep(0.1)
            print("\n")

            # Stop recording
            audio_data = audio_handler.stop_recording()
            if audio_data:
                print(f"✅ Recording captured: {audio_data.duration:.2f} seconds")
                print(f"📊 Audio data size: {len(audio_data.data)} bytes")
                return True, audio_data.data
            else:
                print("❌ No audio data captured")
                return False, None

        except Exception as e:
            print(f"❌ Audio recording test failed: {e}")
            return False, None


def main():
    """Main function for standalone audio testing"""
    print("🎵 Audio Testing Utilities - Standalone Test")
    print("=" * 60)

    success = AudioTestUtils.run_comprehensive_audio_test()

    if success:
        print("\n🎉 All audio tests passed!")
        print("Your audio system is ready for integration testing.")
    else:
        print("\n❌ Audio tests failed.")
        print("Please resolve audio issues before running integration tests.")

    return success


if __name__ == "__main__":
    main()
