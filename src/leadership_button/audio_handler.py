"""
Audio Handler Module for Leadership Button Device

Handles audio recording, playback, and hardware integration for both
laptop development and Raspberry Pi production environments.
"""

import logging
import threading
import time
import wave
from typing import Optional, Callable
from enum import Enum

# Core audio dependencies
try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available - audio functionality will be limited")

# Hardware dependencies (Raspberry Pi)
try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.info("RPi.GPIO not available - running in laptop mode")


class DeviceState(Enum):
    """Device state enumeration"""

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    PLAYING = "playing"
    ERROR = "error"


class AudioConfig:
    """Configuration class for audio handling parameters"""

    def __init__(self):
        # Audio parameters
        self.sample_rate: int = 16000
        self.channels: int = 1
        self.chunk_size: int = 1024
        self.format: str = "wav"
        self.device_index: Optional[int] = None

        # Hardware parameters (Raspberry Pi)
        self.button_pin: Optional[int] = None
        self.led_pin: Optional[int] = None

        # Recording parameters
        self.max_recording_duration: int = 30  # seconds

        # PyAudio format mapping
        self.pyaudio_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None

    def validate(self) -> bool:
        """Validate configuration parameters"""
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels <= 0:
            raise ValueError("Channels must be positive")
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if self.max_recording_duration <= 0:
            raise ValueError("Max recording duration must be positive")
        return True


class AudioData:
    """Container for audio data with metadata"""

    def __init__(self, data: bytes, format: str, sample_rate: int, channels: int):
        self.data: bytes = data
        self.format: str = format
        self.sample_rate: int = sample_rate
        self.channels: int = channels
        self.duration: float = self._calculate_duration()

    def _calculate_duration(self) -> float:
        """Calculate audio duration in seconds"""
        if not self.data:
            return 0.0

        # For 16-bit audio: 2 bytes per sample
        bytes_per_sample = 2
        bytes_per_second = self.sample_rate * self.channels * bytes_per_sample
        return len(self.data) / bytes_per_second

    def save_to_file(self, filepath: str) -> bool:
        """Save audio data to a file"""
        try:
            with wave.open(filepath, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(self.data)
            return True
        except Exception as e:
            logging.error(f"Failed to save audio file: {e}")
            return False

    def get_file_size(self) -> int:
        """Get the size of audio data in bytes"""
        return len(self.data)


class AudioHandler:
    """Main audio handling class for recording, playback, and hardware integration"""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.config.validate()

        # Initialize PyAudio
        self.audio = None
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                logging.error(f"Failed to initialize PyAudio: {e}")
                self.audio = None

        # State management
        self.state = DeviceState.IDLE
        self.state_lock = threading.Lock()

        # Recording state
        self.recording_stream = None
        self.recording_data = []
        self.recording_thread = None
        self.stop_recording_event = threading.Event()

        # Playback state
        self.playback_stream = None
        self.playback_thread = None
        self.stop_playback_event = threading.Event()

        # Hardware state (Raspberry Pi)
        self.button_thread = None
        self.button_callback: Optional[Callable] = None
        self.button_state = False
        self.led_state = False

        # Initialize hardware if available
        if GPIO_AVAILABLE:
            self.setup_hardware()
        else:
            logging.info("Running in laptop mode - hardware features disabled")

    def start_recording(self) -> bool:
        """Start audio recording"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            logging.error("PyAudio not available for recording")
            return False

        with self.state_lock:
            if self.state != DeviceState.IDLE:
                logging.warning(f"Cannot start recording in state: {self.state}")
                return False

            self.state = DeviceState.RECORDING

        try:
            # Reset recording data
            self.recording_data = []
            self.stop_recording_event.clear()

            # Open recording stream
            self.recording_stream = self.audio.open(
                format=self.config.pyaudio_format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.device_index,
                frames_per_buffer=self.config.chunk_size,
            )

            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._record_audio_stream, daemon=True
            )
            self.recording_thread.start()

            logging.info("Audio recording started")
            return True

        except Exception as e:
            logging.error(f"Failed to start recording: {e}")
            with self.state_lock:
                self.state = DeviceState.ERROR
            return False

    def stop_recording(self) -> Optional[AudioData]:
        """Stop audio recording and return captured data"""
        if self.state != DeviceState.RECORDING:
            logging.warning("Not currently recording")
            return None

        # Signal recording thread to stop
        self.stop_recording_event.set()

        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)

        # Close recording stream
        if self.recording_stream:
            try:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
            except Exception as e:
                logging.error(f"Error closing recording stream: {e}")
            finally:
                self.recording_stream = None

        # Process recorded data
        if self.recording_data:
            audio_bytes = b"".join(self.recording_data)
            audio_data = AudioData(
                data=audio_bytes,
                format=self.config.format,
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
            )

            with self.state_lock:
                self.state = DeviceState.IDLE

            logging.info(
                f"Recording stopped - captured {audio_data.duration:.2f} seconds"
            )
            return audio_data
        else:
            with self.state_lock:
                self.state = DeviceState.IDLE
            logging.warning("No audio data captured")
            return None

    def _record_audio_stream(self):
        """Internal method for continuous recording loop"""
        start_time = time.time()
        max_duration = self.config.max_recording_duration

        try:
            while not self.stop_recording_event.is_set():
                # Check for timeout
                if time.time() - start_time > max_duration:
                    logging.warning(f"Recording timeout after {max_duration} seconds")
                    break

                # Read audio chunk
                try:
                    data = self.recording_stream.read(
                        self.config.chunk_size, exception_on_overflow=False
                    )
                    self.recording_data.append(data)
                except Exception as e:
                    logging.error(f"Error reading audio data: {e}")
                    break

        except Exception as e:
            logging.error(f"Error in recording thread: {e}")

        logging.debug("Recording thread finished")

    def play_audio(self, audio_data: bytes) -> bool:
        """Play audio data through speakers"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            logging.error("PyAudio not available for playback")
            return False

        with self.state_lock:
            if self.state == DeviceState.PLAYING:
                logging.warning("Already playing audio")
                return False
            self.state = DeviceState.PLAYING

        try:
            # Stop any current playback
            self.stop_playback_event.set()
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)

            # Start new playback
            self.stop_playback_event.clear()
            self.playback_thread = threading.Thread(
                target=self._play_audio_stream, args=(audio_data,), daemon=True
            )
            self.playback_thread.start()

            return True

        except Exception as e:
            logging.error(f"Failed to start audio playback: {e}")
            with self.state_lock:
                self.state = DeviceState.ERROR
            return False

    def _play_audio_stream(self, audio_data: bytes):
        """Internal method for audio playback"""
        playback_stream = None

        try:
            # Open playback stream
            playback_stream = self.audio.open(
                format=self.config.pyaudio_format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                output=True,
                frames_per_buffer=self.config.chunk_size,
            )

            # Play audio in chunks
            chunk_size = self.config.chunk_size * 2  # 2 bytes per sample
            for i in range(0, len(audio_data), chunk_size):
                if self.stop_playback_event.is_set():
                    break

                chunk = audio_data[i:i + chunk_size]
                playback_stream.write(chunk)

            logging.info("Audio playback completed")

        except Exception as e:
            logging.error(f"Error during audio playback: {e}")

        finally:
            # Clean up playback stream
            if playback_stream:
                try:
                    playback_stream.stop_stream()
                    playback_stream.close()
                except Exception as e:
                    logging.error(f"Error closing playback stream: {e}")

            # Reset state
            with self.state_lock:
                if self.state == DeviceState.PLAYING:
                    self.state = DeviceState.IDLE

    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.state == DeviceState.RECORDING

    def is_playing(self) -> bool:
        """Check if currently playing audio"""
        return self.state == DeviceState.PLAYING

    def setup_hardware(self) -> bool:
        """Initialize hardware components (Raspberry Pi only)"""
        if not GPIO_AVAILABLE:
            logging.info("GPIO not available - skipping hardware setup")
            return False

        try:
            # Initialize GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Setup button pin
            if self.config.button_pin:
                GPIO.setup(self.config.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    self.config.button_pin,
                    GPIO.BOTH,
                    callback=self._button_callback,
                    bouncetime=50,
                )

            # Setup LED pin
            if self.config.led_pin:
                GPIO.setup(self.config.led_pin, GPIO.OUT)
                GPIO.output(self.config.led_pin, GPIO.LOW)

            logging.info("Hardware setup completed")
            return True

        except Exception as e:
            logging.error(f"Hardware setup failed: {e}")
            return False

    def monitor_button(self) -> None:
        """Start monitoring hardware button (Raspberry Pi only)"""
        if not GPIO_AVAILABLE:
            logging.info("Button monitoring not available in laptop mode")
            return

        # Button monitoring is handled by GPIO event detection
        # This method exists for API compatibility
        logging.info("Button monitoring active via GPIO events")

    def _button_callback(self, channel):
        """GPIO callback for button state changes"""
        try:
            button_pressed = GPIO.input(channel) == GPIO.LOW

            if button_pressed != self.button_state:
                self.button_state = button_pressed

                if button_pressed:
                    logging.debug("Button pressed")
                    if self.button_callback:
                        self.button_callback("button_press")
                    self.start_recording()
                else:
                    logging.debug("Button released")
                    if self.button_callback:
                        self.button_callback("button_release")
                    self.stop_recording()

        except Exception as e:
            logging.error(f"Error in button callback: {e}")

    def set_led_state(self, state: bool) -> None:
        """Control status LED (Raspberry Pi only)"""
        if not GPIO_AVAILABLE or not self.config.led_pin:
            return

        try:
            GPIO.output(self.config.led_pin, GPIO.HIGH if state else GPIO.LOW)
            self.led_state = state
            logging.debug(f"LED state set to: {state}")
        except Exception as e:
            logging.error(f"Failed to set LED state: {e}")

    def set_button_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function for button events"""
        self.button_callback = callback

    def get_state(self) -> DeviceState:
        """Get current device state"""
        return self.state

    def cleanup(self) -> None:
        """Clean up resources and stop all operations"""
        logging.info("Cleaning up audio handler...")

        # Stop recording
        if self.is_recording():
            self.stop_recording()

        # Stop playback
        self.stop_playback_event.set()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=2.0)

        # Clean up PyAudio
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                logging.error(f"Error terminating PyAudio: {e}")

        # Clean up GPIO
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                logging.info("GPIO cleanup completed")
            except Exception as e:
                logging.error(f"GPIO cleanup error: {e}")

        logging.info("Audio handler cleanup completed")


# Laptop simulation utilities
def simulate_button_press(handler: AudioHandler) -> None:
    """Simulate button press for laptop testing"""
    if handler.button_callback:
        handler.button_callback("button_press")
    handler.start_recording()


def simulate_button_release(handler: AudioHandler) -> None:
    """Simulate button release for laptop testing"""
    if handler.button_callback:
        handler.button_callback("button_release")
    handler.stop_recording()
