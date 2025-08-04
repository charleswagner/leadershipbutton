#!/usr/bin/env python3
"""
Main Executable Script for Leadership & EQ Coach

This script serves as the entry point for the Leadership & EQ Coach application.
It provides command line interface, signal handling, and different operation modes
for development, production, and testing environments.
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

from leadership_button.main_loop import MainLoop

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


class ApplicationManager:
    """Manages the main application lifecycle and command line interface."""

    def __init__(self):
        self.main_loop: Optional[MainLoop] = None
        self.logger = logging.getLogger(__name__)
        self.running = False

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received signal {signal_name}, initiating graceful shutdown")
        self.stop()

    def setup_logging(self, mode: str = "development") -> None:
        """Configure application logging based on mode."""
        # Check environment variable for verbose logging
        verbose_logging = os.getenv("VERBOSE_LOGGING", "").lower() == "true"

        # Try to read verbose logging from config file
        try:
            if mode == "development":
                dev_config_file = "config/api_config.development.json"
                if Path(dev_config_file).exists():
                    with open(dev_config_file, "r") as f:
                        dev_config = json.load(f)
                        verbose_logging = dev_config.get("development", {}).get(
                            "verbose_logging", verbose_logging
                        )
        except Exception:
            pass  # Fall back to environment variable or default

        if mode == "development":
            log_level = logging.DEBUG
            if verbose_logging:
                log_format = (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(funcName)s:%(lineno)d - %(message)s"
                )
            else:
                log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:  # production
            log_level = logging.INFO
            log_format = "%(asctime)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("logs/application.log"),
            ],
        )

        # Set verbose logging for our application modules if enabled
        if verbose_logging:
            logging.getLogger("leadership_button").setLevel(logging.DEBUG)
            self.logger.info("Verbose logging enabled")

        # Suppress verbose library logs in production
        if mode == "production":
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("google").setLevel(logging.WARNING)

    def run_tests(self) -> bool:
        """Run application tests and return success status."""
        self.logger.info("Running application tests...")

        try:
            # Import and run tests
            import unittest
            from tests.test_main_loop import TestMainLoop

            # Create test suite
            test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMainLoop)

            # Run tests
            test_runner = unittest.TextTestRunner(verbosity=2)
            result = test_runner.run(test_suite)

            if result.wasSuccessful():
                self.logger.info("✓ All tests passed")
                return True
            else:
                self.logger.error(f"✗ {len(result.failures)} tests failed")
                return False

        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return False

    def show_status(self) -> None:
        """Display application status and health information."""
        if not self.main_loop:
            print("Application not running")
            return

        stats = self.main_loop.get_performance_stats()
        current_state = self.main_loop.current_state.value

        print("\n=== Leadership & EQ Coach Status ===")
        print(f"Status: {'Running' if self.running else 'Stopped'}")
        print(f"Current State: {current_state}")
        print(f"Uptime: {stats['uptime']:.1f} seconds")
        print(f"Average Response Time: {stats['average_response_time']:.2f} seconds")
        print(f"Total Interactions: {len(stats['response_times'])}")

        # Component status
        print("\n=== Component Status ===")
        print(
            f"Audio Handler: {'✓ Ready' if self.main_loop.audio_handler else '✗ Not Available'}"
        )
        print(
            f"API Client: {'✓ Ready' if self.main_loop.api_client else '✗ Not Available'}"
        )

        # Configuration status
        print("\n=== Configuration ===")
        print(f"Config Loaded: {'✓ Yes' if self.main_loop.config else '✗ No'}")

        print("\n" + "=" * 35)

    def record_audio_to_file(self, filename: str) -> None:
        """Record audio to a file for testing purposes."""
        print(f"🎤 Recording audio to {filename}")
        print("Press Ctrl+C to stop recording")

        try:
            # Initialize main loop for recording
            self.main_loop = MainLoop()

            # Set up logging
            self.setup_logging("development")

            # Create logs directory if it doesn't exist
            Path("logs").mkdir(exist_ok=True)

            # Start recording
            if self.main_loop.audio_handler:
                success = self.main_loop.audio_handler.start_recording()
                if not success:
                    print("❌ Failed to start recording")
                    return

                print("✅ Recording started. Speak into your microphone...")

                # Record until interrupted
                try:
                    while True:
                        time.sleep(0.1)
                        if not self.main_loop.audio_handler.is_recording():
                            break
                except KeyboardInterrupt:
                    print("\n⏹️  Stopping recording...")

                # Stop recording and get audio data
                audio_data = self.main_loop.audio_handler.stop_recording()
                if audio_data:
                    # Save to file
                    if audio_data.save_to_file(filename):
                        print(f"✅ Audio saved to {filename}")
                        print(f"📊 Duration: {audio_data.duration:.2f} seconds")
                        print(f"📊 File size: {audio_data.get_file_size()} bytes")
                    else:
                        print("❌ Failed to save audio file")
                else:
                    print("❌ No audio data captured")
            else:
                print("❌ Audio handler not available")

        except KeyboardInterrupt:
            print("\n⚠️  Recording interrupted by user")
        except Exception as e:
            print(f"❌ Recording failed: {e}")
        finally:
            if self.main_loop:
                self.main_loop.stop()

    def start(
        self, mode: str = "development", config_path: Optional[str] = None
    ) -> None:
        """Start the main application."""
        self.logger.info(f"Starting Leadership & EQ Coach in {mode} mode")

        try:
            # Set up logging
            self.setup_logging(mode)

            # Create logs directory if it doesn't exist
            Path("logs").mkdir(exist_ok=True)

            # Initialize main loop
            self.main_loop = MainLoop(config_path)
            self.running = True

            # Display startup information
            print("\n🎯 Leadership & EQ Coach v1.0")
            print(f"Mode: {mode.capitalize()}")
            print("Press Ctrl+C to stop\n")

            # Start the main loop (this initializes components)
            self.main_loop.start()

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            sys.exit(1)
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the application gracefully."""
        if not self.running:
            return

        self.logger.info("Stopping application...")
        self.running = False

        if self.main_loop:
            self.main_loop.stop()

        self.logger.info("Application stopped")
        sys.exit(0)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Leadership & EQ Coach - AI-powered leadership assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/main.py --mode development    # Start in development mode
  python3 src/main.py --mode production     # Start in production mode
  python3 src/main.py --test                # Run tests
  python3 src/main.py --status              # Show application status
  python3 src/main.py --record test.wav     # Record audio to file
        """,
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["development", "production"],
        default="development",
        help="Application mode (default: development)",
    )

    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")

    parser.add_argument(
        "--test", "-t", action="store_true", help="Run application tests"
    )

    parser.add_argument(
        "--status", "-s", action="store_true", help="Show application status"
    )

    parser.add_argument(
        "--record",
        "-r",
        type=str,
        metavar="FILENAME",
        help="Record audio to file (e.g., --record test_audio.wav)",
    )

    parser.add_argument(
        "--version", "-v", action="version", version="Leadership & EQ Coach v1.0"
    )

    return parser


def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()

    app_manager = ApplicationManager()

    try:
        if args.test:
            # Run tests
            success = app_manager.run_tests()
            sys.exit(0 if success else 1)

        elif args.status:
            # Show status (requires running application)
            app_manager.show_status()
            sys.exit(0)

        elif args.record:
            # Record audio to file
            app_manager.record_audio_to_file(args.record)
            sys.exit(0)

        else:
            # Start application
            config_path = args.config if args.config else "config/api_config.json"
            app_manager.start(mode=args.mode, config_path=config_path)

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
