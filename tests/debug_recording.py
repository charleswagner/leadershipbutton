#!/usr/bin/env python3
"""
Simple Recording Debug Script

This script tests audio recording functionality in isolation
to help debug the recording issues in the audio loop test.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from leadership_button.audio_handler import AudioHandler, AudioConfig


def test_recording():
    """Test basic recording functionality"""
    print("🎤 Testing Audio Recording")
    print("=" * 40)

    try:
        # Initialize audio handler
        config = AudioConfig()
        audio_handler = AudioHandler(config)
        print("✅ Audio handler initialized")

        # Test recording start
        print("\n🎤 Starting recording...")
        success = audio_handler.start_recording()
        if not success:
            print("❌ Failed to start recording")
            return False

        print("✅ Recording started")

        # Check if recording is active
        if audio_handler.is_recording():
            print("✅ Recording is active")
        else:
            print("❌ Recording is not active")
            return False

        # Record for 5 seconds
        print("🎤 Recording for 5 seconds...")
        print("Please speak into your microphone.")

        start_time = time.time()
        while time.time() - start_time < 5:
            remaining = 5 - int(time.time() - start_time)
            print(f"\rRecording... {remaining} seconds remaining", end="", flush=True)

            # Check if recording is still active
            if not audio_handler.is_recording():
                print(
                    f"\n❌ Recording stopped unexpectedly at {time.time() - start_time:.1f} seconds"
                )
                return False

            time.sleep(0.1)
        print("\n")

        # Stop recording
        print("🎤 Stopping recording...")
        audio_data = audio_handler.stop_recording()

        if audio_data:
            print(f"✅ Recording captured: {audio_data.duration:.2f} seconds")
            print(f"📊 Audio data size: {len(audio_data.data)} bytes")

            # Save to file for debugging
            if audio_data.save_to_file("debug_recording.wav"):
                print("💾 Recording saved to debug_recording.wav")

            return True
        else:
            print("❌ No audio data captured")
            return False

    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        return False


def main():
    """Main function"""
    print("🎤 Audio Recording Debug Tool")
    print("=" * 50)

    success = test_recording()

    if success:
        print("\n🎉 Recording test passed!")
        print("Your microphone is working correctly.")
    else:
        print("\n❌ Recording test failed.")
        print("Please check your microphone settings and permissions.")


if __name__ == "__main__":
    main()
