#!/usr/bin/env python3
"""
Debug script to test audio playback in isolation
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import time

from leadership_button.api_client import APIManager, APIConfig
from leadership_button.audio_handler import AudioHandler, AudioConfig


def debug_audio_playback():
    """Test audio playback with TTS audio"""
    print("🔍 Debug Audio Playback Test")
    print("=" * 50)

    try:
        # Initialize components
        print("1. Initializing API Manager...")
        api_config = APIConfig("config/api_config.json")
        api_manager = APIManager(api_config)
        if not api_manager.initialize():
            print("❌ Failed to initialize API Manager")
            return False
        print("✅ API Manager initialized")

        print("\n2. Initializing Audio Handler...")
        audio_config = AudioConfig()
        audio_handler = AudioHandler(audio_config)
        print("✅ Audio Handler initialized")

        # Test text
        test_text = "Hello world"
        print(f"\n3. Converting text to speech: '{test_text}'")

        # Get TTS audio
        audio_response = api_manager.text_to_speech(test_text)
        if not audio_response:
            print("❌ No audio response from TTS")
            return False

        print("✅ TTS response received")

        # Check audio response type and format
        if hasattr(audio_response, "data"):
            print("   - Type: AudioData object")
            print(f"   - Data size: {len(audio_response.data)} bytes")
            print(f"   - Sample rate: {audio_response.sample_rate} Hz")
            print(f"   - Channels: {audio_response.channels}")
            print(f"   - Format: {audio_response.format}")
            audio_data = audio_response.data
        else:
            print("   - Type: Raw bytes")
            print(f"   - Data size: {len(audio_response)} bytes")
            audio_data = audio_response

        print("\n4. Playing audio...")
        print(f"   - Audio data type: {type(audio_data)}")
        print(f"   - Audio data length: {len(audio_data)} bytes")

        # Try to play the audio
        success = audio_handler.play_audio(audio_data)
        if not success:
            print("❌ Failed to start audio playback")
            return False

        print("✅ Audio playback started")

        # Wait for playback to complete
        print("   - Waiting for playback to complete...")
        while audio_handler.is_playing():
            time.sleep(0.1)

        print("✅ Audio playback completed")

        # Ask user if they heard it
        response = input("\n🔊 Did you hear the audio? (y/n): ").lower().strip()
        if response == "y":
            print("✅ Audio playback working correctly!")
            return True
        else:
            print("❌ Audio playback not working")

            # Try to save the audio to a file for debugging
            print("\n5. Saving audio to file for debugging...")
            try:
                if hasattr(audio_response, "save_to_file"):
                    audio_response.save_to_file("debug_tts_audio.wav")
                    print("✅ Audio saved to debug_tts_audio.wav")
                else:
                    with open("debug_tts_audio.raw", "wb") as f:
                        f.write(audio_data)
                    print("✅ Raw audio saved to debug_tts_audio.raw")
            except Exception as e:
                print(f"❌ Failed to save audio: {e}")

            return False

    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_audio_playback()
