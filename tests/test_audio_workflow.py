#!/usr/bin/env python3
"""
Audio Workflow Test Script

This script allows testing the complete audio workflow on a laptop:
1. Simulate button presses
2. Record audio
3. Process through API
4. Play back response
"""

import sys
import time


from leadership_button.main_loop import MainLoop, ApplicationState


class AudioWorkflowTester:
    """Test the complete audio workflow"""

    def __init__(self):
        self.main_loop = None
        self.running = False

    def setup(self):
        """Initialize the main loop for testing"""
        print("🎯 Setting up Audio Workflow Tester...")

        try:
            self.main_loop = MainLoop()
            print("✅ MainLoop initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MainLoop: {e}")
            return False

    def simulate_button_press(self):
        """Simulate a button press to start recording"""
        if not self.main_loop:
            print("❌ MainLoop not initialized")
            return False

        print("\n🔘 Simulating button press...")

        # Check if we're in IDLE state
        if self.main_loop.current_state != ApplicationState.IDLE:
            print(
                f"⚠️  Cannot start recording - current state: {self.main_loop.current_state.value}"
            )
            return False

        # Trigger button press
        self.main_loop._handle_button_press()

        if self.main_loop.current_state == ApplicationState.RECORDING:
            print("✅ Recording started successfully")
            return True
        else:
            print(
                f"❌ Failed to start recording - state: {self.main_loop.current_state.value}"
            )
            return False

    def simulate_recording_complete(self, audio_data=None):
        """Simulate recording completion with optional audio data"""
        if not self.main_loop:
            print("❌ MainLoop not initialized")
            return False

        if self.main_loop.current_state != ApplicationState.RECORDING:
            print(
                f"⚠️  Not currently recording - state: {self.main_loop.current_state.value}"
            )
            return False

        print("\n🎤 Simulating recording completion...")

        # Use provided audio data or create dummy data
        if audio_data is None:
            # Create dummy audio data (1 second of silence)
            sample_rate = 16000
            channels = 1
            duration = 1.0  # 1 second
            samples = int(sample_rate * duration * channels)
            audio_data = b"\x00" * (samples * 2)  # 16-bit audio = 2 bytes per sample

        # Trigger recording complete
        self.main_loop._handle_recording_complete(audio_data)

        if self.main_loop.current_state == ApplicationState.PROCESSING:
            print("✅ Processing started successfully")
            return True
        else:
            print(
                f"❌ Failed to start processing - state: {self.main_loop.current_state.value}"
            )
            return False

    def simulate_api_response(
        self,
        response_text="Hello! I'm your leadership coach. How can I help you today?",
    ):
        """Simulate API response with text-to-speech"""
        if not self.main_loop:
            print("❌ MainLoop not initialized")
            return False

        if self.main_loop.current_state != ApplicationState.PROCESSING:
            print(
                f"⚠️  Not currently processing - state: {self.main_loop.current_state.value}"
            )
            return False

        print("\n🤖 Simulating API response...")

        # Create mock API response
        mock_response = {
            "text": response_text,
            "audio_content": b"mock_audio_data",  # This would be real TTS audio
            "confidence": 0.95,
        }

        # Trigger API response
        self.main_loop._handle_api_response(mock_response)

        if self.main_loop.current_state == ApplicationState.SPEAKING:
            print("✅ Audio playback started successfully")
            return True
        else:
            print(
                f"❌ Failed to start audio playback - state: {self.main_loop.current_state.value}"
            )
            return False

    def simulate_audio_complete(self):
        """Simulate audio playback completion"""
        if not self.main_loop:
            print("❌ MainLoop not initialized")
            return False

        if self.main_loop.current_state != ApplicationState.SPEAKING:
            print(
                f"⚠️  Not currently playing audio - state: {self.main_loop.current_state.value}"
            )
            return False

        print("\n🔊 Simulating audio playback completion...")

        # Trigger audio complete
        self.main_loop._handle_audio_complete()

        if self.main_loop.current_state == ApplicationState.IDLE:
            print("✅ Returned to idle state successfully")
            return True
        else:
            print(
                f"❌ Failed to return to idle - state: {self.main_loop.current_state.value}"
            )
            return False

    def run_full_workflow_test(self):
        """Run a complete workflow test"""
        print("\n" + "=" * 50)
        print("🎯 RUNNING FULL AUDIO WORKFLOW TEST")
        print("=" * 50)

        if not self.setup():
            return False

        # Step 1: Simulate button press
        if not self.simulate_button_press():
            return False

        time.sleep(1)  # Simulate recording time

        # Step 2: Simulate recording complete
        if not self.simulate_recording_complete():
            return False

        time.sleep(2)  # Simulate processing time

        # Step 3: Simulate API response
        if not self.simulate_api_response():
            return False

        time.sleep(1)  # Simulate audio playback time

        # Step 4: Simulate audio complete
        if not self.simulate_audio_complete():
            return False

        print("\n" + "=" * 50)
        print("✅ FULL WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        return True

    def interactive_test(self):
        """Interactive test mode"""
        print("\n🎮 INTERACTIVE TEST MODE")
        print("Commands: 'press', 'record', 'api', 'play', 'status', 'quit'")

        if not self.setup():
            return

        self.running = True

        while self.running:
            try:
                command = input("\n> ").strip().lower()

                if command == "quit":
                    self.running = False
                    print("👋 Goodbye!")

                elif command == "status":
                    if self.main_loop:
                        print(f"Current State: {self.main_loop.current_state.value}")
                    else:
                        print("MainLoop not initialized")

                elif command == "press":
                    self.simulate_button_press()

                elif command == "record":
                    self.simulate_recording_complete()

                elif command == "api":
                    self.simulate_api_response()

                elif command == "play":
                    self.simulate_audio_complete()

                elif command == "help":
                    print("Commands:")
                    print("  press  - Simulate button press")
                    print("  record - Simulate recording complete")
                    print("  api    - Simulate API response")
                    print("  play   - Simulate audio playback complete")
                    print("  status - Show current state")
                    print("  quit   - Exit")

                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main test function"""
    print("🎯 Leadership & EQ Coach - Audio Workflow Tester")
    print("=" * 50)

    tester = AudioWorkflowTester()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            # Run full workflow test
            success = tester.run_full_workflow_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--interactive":
            # Run interactive test
            tester.interactive_test()
        else:
            print("Usage: python3 test_audio_workflow.py [--full|--interactive]")
            sys.exit(1)
    else:
        # Default to full test
        success = tester.run_full_workflow_test()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
