"""
Google Cloud API Client Module for Leadership Button Device

Handles Speech-to-Text and Text-to-Speech API interactions with
secure configuration management and robust error handling.
"""

import json
import logging
import os
import time
import signal
from contextlib import contextmanager
from typing import Optional, List, Any
from enum import Enum
from pathlib import Path
import re

# Google Cloud dependencies
try:
    from google.cloud import speech
    from google.cloud import texttospeech
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError

    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning(
        "Google Cloud libraries not available - " "API functionality will be limited"
    )

# Retry and configuration dependencies
try:
    # Tenacity imports would go here if retry logic is implemented
    TENACITY_AVAILABLE = False
except ImportError:
    TENACITY_AVAILABLE = False
    logging.warning("Tenacity not available - retry logic will be limited")

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available - environment loading may be limited")


class APIState(Enum):
    """API client state enumeration"""

    INITIALIZING = "initializing"
    READY = "ready"
    AI_ONLY = "ai_only"  # Only AI provider available, speech/TTS unavailable
    PROCESSING_SPEECH = "processing_speech"
    PROCESSING_TTS = "processing_tts"
    ERROR = "error"
    OFFLINE = "offline"


class APIConfig:
    """Configuration class for Google Cloud API settings"""

    def __init__(self, config_file: str = "config/api_config.json"):
        # Load environment variables first
        if DOTENV_AVAILABLE:
            load_dotenv()

        # Load configuration from JSON file
        self.config_data = self._load_json_config(config_file)
        self.secrets = self._load_secrets_from_env()

        # Load environment-specific overrides
        self._load_environment_overrides()

        # Convenience properties for easy access
        self.api_settings = self.config_data["api_settings"]
        self.google_cloud = self.config_data["google_cloud"]
        self.audio_settings = self.config_data["audio_settings"]
        self.performance = self.config_data["performance"]
        self.features = self.config_data["features"]
        self.development = self.config_data["development"]

        # Validate configuration
        self.validate()

    def _load_json_config(self, config_file: str) -> dict:
        """Load configuration from JSON file"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load configuration file {config_file}: {e}")
            raise

    def _load_secrets_from_env(self) -> dict:
        """Load secrets from environment variables"""
        secrets = {
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        # Validate required secrets
        if not secrets["project_id"]:
            logging.warning("GOOGLE_CLOUD_PROJECT not set in environment")
        if not secrets["credentials_path"]:
            logging.warning("GOOGLE_APPLICATION_CREDENTIALS not set in environment")

        return secrets

    def _load_environment_overrides(self) -> None:
        """Load environment-specific configuration overrides"""
        env = self.secrets.get("environment", "development")
        env_config_file = f"config/api_config.{env}.json"

        try:
            env_config = self._load_json_config(env_config_file)
            self._merge_configs(self.config_data, env_config)
            logging.info(f"Loaded environment-specific config: {env_config_file}")
        except FileNotFoundError:
            logging.info(f"No environment-specific config found: {env_config_file}")
        except Exception as e:
            logging.warning(f"Failed to load environment config {env_config_file}: {e}")

    def _merge_configs(self, base_config: dict, override_config: dict) -> None:
        """Recursively merge configuration dictionaries"""
        for key, value in override_config.items():
            if (
                key in base_config
                and isinstance(base_config[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value

    def validate(self) -> bool:
        """Validate configuration parameters"""
        # Validate API settings
        if self.api_settings["timeout"] <= 0:
            raise ValueError("API timeout must be positive")
        if self.api_settings["max_retries"] <= 0:
            raise ValueError("Retry max attempts must be positive")

        # Validate Google Cloud settings
        if not self.google_cloud["region"]:
            raise ValueError("Google Cloud region must be specified")

        # Validate speech settings
        if "speech_to_text" in self.config_data:
            speech_config = self.config_data["speech_to_text"]
            if "sample_rate" in speech_config and speech_config["sample_rate"] <= 0:
                raise ValueError("Speech sample rate must be positive")

        # Validate TTS settings
        if "text_to_speech" in self.config_data:
            tts_config = self.config_data["text_to_speech"]
            if "speaking_rate" in tts_config and tts_config["speaking_rate"] <= 0:
                raise ValueError("TTS speaking rate must be positive")

        return True

    def get_speech_config(self) -> dict:
        """Get speech-to-text configuration"""
        return self.config_data.get("speech_to_text", {})

    def get_tts_config(self) -> dict:
        """Get text-to-speech configuration"""
        return self.config_data.get("text_to_speech", {})

    def get_api_config(self) -> dict:
        """Get API behavior configuration"""
        return self.api_settings

    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.development.get("verbose_logging", False)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding secrets)"""
        config_copy = self.config_data.copy()
        config_copy["secrets"] = {
            "project_id": "***" if self.secrets["project_id"] else None,
            "credentials_path": "***" if self.secrets["credentials_path"] else None,
            "environment": self.secrets["environment"],
        }
        return config_copy

    @property
    def project_id(self) -> str:
        return self.secrets["project_id"]

    @property
    def credentials_path(self) -> str:
        return self.secrets["credentials_path"]

    @property
    def timeout_seconds(self) -> int:
        return self.api_settings["timeout"]

    @property
    def retry_max_attempts(self) -> int:
        return self.api_settings["max_retries"]


class TranscriptionResult:
    """Container for speech-to-text transcription results"""

    def __init__(self, text: str, confidence: float, alternatives: List[str] = None):
        self.text: str = text
        self.confidence: float = confidence
        self.alternatives: List[str] = alternatives or []
        self.language_code: str = ""
        self.processing_time: float = 0.0

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if transcription has high confidence"""
        return self.confidence >= threshold

    def get_best_alternative(self) -> str:
        """Get the best alternative transcription"""
        return self.alternatives[0] if self.alternatives else self.text


class VoiceConfig:
    """Configuration for text-to-speech voice settings"""

    def __init__(self, name: str = None, language_code: str = None):
        self.name: str = name or "en-US-Wavenet-D"
        self.language_code: str = language_code or "en-US"
        self.ssml_gender: str = "NEUTRAL"
        self.speaking_rate: float = 1.0
        self.pitch: float = 0.0
        self.volume_gain_db: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for API request"""
        return {
            "name": self.name,
            "language_code": self.language_code,
            "ssml_gender": self.ssml_gender,
        }


class Voice:
    """Container for available TTS voice information"""

    def __init__(self, name: str, language_code: str, gender: str):
        self.name: str = name
        self.language_code: str = language_code
        self.ssml_gender: str = gender
        self.natural_sample_rate_hertz: int = 24000

    def __str__(self) -> str:
        return f"{self.name} ({self.language_code}, {self.ssml_gender})"


class SpeechClient:
    """Google Cloud Speech-to-Text API client"""

    def __init__(self, config: APIConfig):
        self.config = config
        self.client = None
        self.state = APIState.INITIALIZING

        if not GOOGLE_CLOUD_AVAILABLE:
            logging.error("Google Cloud Speech library not available")
            self.state = APIState.OFFLINE
            return

        try:
            self.client = speech.SpeechClient()
            self.state = APIState.READY
            logging.info("Speech-to-Text client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Speech-to-Text client: {e}")
            self.state = APIState.ERROR

    def transcribe_audio(self, audio_data) -> Optional[TranscriptionResult]:
        """Convert audio data to text"""
        if self.state not in [APIState.READY, APIState.AI_ONLY]:
            logging.error(f"Cannot transcribe audio in state: {self.state}")
            return None

        # Check if speech client is available
        if not self.client:
            error_msg = "❌ Speech-to-Text service unavailable: Missing Google Cloud credentials\nPlease set up GOOGLE_APPLICATION_CREDENTIALS environment variable\nSee: https://cloud.google.com/docs/authentication/external/set-up-adc"
            logging.error("Speech-to-Text client not initialized")
            raise RuntimeError(error_msg)

        start_time = time.time()

        # Debug: Check audio data
        if hasattr(audio_data, "data"):
            audio_bytes = audio_data.data
        else:
            audio_bytes = audio_data

        logging.info(f"Transcribing audio: {len(audio_bytes)} bytes")

        try:
            self.state = APIState.PROCESSING_SPEECH

            # Prepare audio for API
            audio = self._prepare_audio_for_api(audio_data)

            # Configure recognition
            speech_config = self.config.get_speech_config()
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=speech_config["sample_rate_hertz"],
                language_code=speech_config["language_code"],
                model=speech_config["model"],
                enable_automatic_punctuation=speech_config[
                    "enable_automatic_punctuation"
                ],
                max_alternatives=speech_config["max_alternatives"],
            )

            logging.info(f"Speech config: {speech_config}")

            # Perform recognition
            logging.info("Calling Google Cloud Speech API...")
            response = self.client.recognize(config=config, audio=audio)

            logging.info(
                f"API response received: {len(response.results) if response.results else 0} results"
            )

            # Process results
            if response.results:
                result = response.results[0]
                if result.alternatives:
                    alternative = result.alternatives[0]
                    alternatives = [alt.transcript for alt in result.alternatives[1:]]

                    transcription = TranscriptionResult(
                        text=alternative.transcript,
                        confidence=alternative.confidence,
                        alternatives=alternatives,
                    )
                    transcription.language_code = speech_config["language_code"]
                    transcription.processing_time = time.time() - start_time

                    # 🔍 CLEAR SPEECH-TO-TEXT LOGGING
                    logging.info("=" * 60)
                    logging.info("🎤 SPEECH-TO-TEXT RESULT:")
                    logging.info(f"📝 TRANSCRIBED TEXT: '{transcription.text}'")
                    logging.info(f"📊 CONFIDENCE: {transcription.confidence:.2f}")
                    logging.info(
                        f"⏱️  PROCESSING TIME: {transcription.processing_time:.2f}s"
                    )
                    logging.info("=" * 60)

                    # Also print to console for immediate visibility
                    print("\n" + "=" * 60)
                    print("🎤 SPEECH-TO-TEXT RESULT:")
                    print(f"📝 TRANSCRIBED TEXT: '{transcription.text}'")
                    print(f"📊 CONFIDENCE: {transcription.confidence:.2f}")
                    print(f"⏱️  PROCESSING TIME: {transcription.processing_time:.2f}s")
                    print("=" * 60)

                    logging.info(
                        f"Transcription completed: {len(transcription.text)} chars, "
                        f"confidence: {transcription.confidence:.2f}"
                    )
                    return transcription
                else:
                    logging.warning("No alternatives in transcription result")
            else:
                logging.warning("No transcription results returned")

            return None

        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            self._handle_api_error(e)
            return None
        finally:
            self.state = APIState.READY

    def _prepare_audio_for_api(self, audio_data) -> speech.RecognitionAudio:
        """Prepare audio data for Google Cloud Speech API"""
        try:
            # Convert AudioData to bytes if needed
            if hasattr(audio_data, "data"):
                audio_bytes = audio_data.data
            else:
                audio_bytes = audio_data

            return speech.RecognitionAudio(content=audio_bytes)
        except Exception as e:
            logging.error(f"Failed to prepare audio for API: {e}")
            raise

    def _handle_api_error(self, error: Exception) -> None:
        """Handle API errors and update state"""
        logging.error(f"Speech API error: {error}")
        self.state = APIState.ERROR

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Simple test - list supported languages
            self.client.get_supported_languages()
            return True
        except Exception as e:
            logging.error(f"Speech API connection test failed: {e}")
            return False

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        try:
            response = self.client.get_supported_languages()
            return [lang.language_code for lang in response.languages]
        except Exception as e:
            logging.error(f"Failed to get supported languages: {e}")
            return []


class TTSClient:
    """Google Cloud Text-to-Speech API client"""

    def __init__(self, config: APIConfig):
        self.config = config
        self.client = None
        self.state = APIState.INITIALIZING

        if not GOOGLE_CLOUD_AVAILABLE:
            logging.error("Google Cloud TTS library not available")
            self.state = APIState.OFFLINE
            return

        try:
            self.client = texttospeech.TextToSpeechClient()
            self.state = APIState.READY
            logging.info("Text-to-Speech client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Text-to-Speech client: {e}")
            self.state = APIState.ERROR

    def synthesize_text(
        self, text: str, voice_config: Optional[VoiceConfig] = None
    ) -> Optional[Any]:
        """Convert text to audio"""
        if self.state != APIState.READY:
            logging.error(f"Cannot synthesize text in state: {self.state}")
            return None

        try:
            self.state = APIState.PROCESSING_TTS

            # Use default voice config if not provided
            if voice_config is None:
                tts_config = self.config.get_tts_config()
                voice_config = VoiceConfig(
                    name=tts_config["voice_name"],
                    language_code=tts_config["language_code"],
                )
                voice_config.speaking_rate = tts_config["speaking_rate"]
                voice_config.pitch = tts_config["pitch"]
                voice_config.volume_gain_db = tts_config["volume_gain_db"]

            # Prepare synthesis request
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # 🔍 COMPLETE TTS CONFIGURATION LOGGING
            logging.info("=" * 60)
            logging.info("🔊 TEXT-TO-SPEECH COMPLETE CONFIGURATION:")
            logging.info("=" * 60)

            # Voice Configuration
            logging.info("🎤 VOICE CONFIGURATION:")
            logging.info(f"  📛 Voice Name: {voice_config.name}")
            logging.info(f"  🌍 Language: {voice_config.language_code}")
            logging.info(f"  ⚡ Speaking Rate: {voice_config.speaking_rate}x")
            logging.info(f"  🎵 Pitch: {voice_config.pitch} semitones")
            logging.info(f"  🔊 Volume Gain: +{voice_config.volume_gain_db} dB")

            # Audio Configuration
            audio_settings = self.config.audio_settings
            logging.info("🔧 AUDIO CONFIGURATION:")
            logging.info(
                f"  📊 Output Sample Rate: {audio_settings['output_sample_rate']} Hz"
            )
            logging.info(f"  🎙️  Input Sample Rate: {audio_settings['sample_rate']} Hz")
            logging.info(f"  📻 Channels: {audio_settings['channels']}")
            logging.info(f"  📦 Format: {audio_settings['format']}")
            logging.info(f"  🔢 Chunk Size: {audio_settings['chunk_size']} bytes")
            logging.info(f"  🎛️  Encoding: LINEAR16 (WAV)")

            # Text Configuration
            logging.info("📝 TEXT CONFIGURATION:")
            logging.info(f"  📄 Input Length: {len(text)} characters")
            logging.info(
                f"  📝 Text Preview: '{text[:100]}{'...' if len(text) > 100 else ''}'"
            )
            logging.info(
                f"  🔤 Text Type: {'Named Voice' if voice_config.name else 'Generic Voice'}"
            )

            # API Configuration
            tts_config_full = self.config.get_tts_config()
            logging.info("⚙️  API CONFIGURATION:")
            logging.info(
                f"  🎯 Voice Selection: {voice_config.name or 'Auto-select by gender'}"
            )
            logging.info(
                f"  🎛️  Audio Encoding: {tts_config_full.get('audio_encoding', 'LINEAR16')}"
            )
            logging.info(f"  🔄 Client State: {self.state}")

            logging.info("=" * 60)

            # Also print to console for immediate visibility
            print("\n" + "=" * 60)
            print("🔊 TEXT-TO-SPEECH COMPLETE CONFIGURATION:")
            print("=" * 60)

            # Voice Configuration
            print("🎤 VOICE CONFIGURATION:")
            print(f"  📛 Voice Name: {voice_config.name}")
            print(f"  🌍 Language: {voice_config.language_code}")
            print(f"  ⚡ Speaking Rate: {voice_config.speaking_rate}x")
            print(f"  🎵 Pitch: {voice_config.pitch} semitones")
            print(f"  🔊 Volume Gain: +{voice_config.volume_gain_db} dB")

            # Audio Configuration
            print("🔧 AUDIO CONFIGURATION:")
            print(f"  📊 Output Sample Rate: {audio_settings['output_sample_rate']} Hz")
            print(f"  🎙️  Input Sample Rate: {audio_settings['sample_rate']} Hz")
            print(f"  📻 Channels: {audio_settings['channels']}")
            print(f"  📦 Format: {audio_settings['format']}")
            print(f"  🔢 Chunk Size: {audio_settings['chunk_size']} bytes")
            print(f"  🎛️  Encoding: LINEAR16 (WAV)")

            # Text Configuration
            print("📝 TEXT CONFIGURATION:")
            print(f"  📄 Input Length: {len(text)} characters")
            print(
                f"  📝 Text Preview: '{text[:100]}{'...' if len(text) > 100 else ''}'"
            )
            print(
                f"  🔤 Text Type: {'Named Voice' if voice_config.name else 'Generic Voice'}"
            )

            # API Configuration
            print("⚙️  API CONFIGURATION:")
            print(
                f"  🎯 Voice Selection: {voice_config.name or 'Auto-select by gender'}"
            )
            print(
                f"  🎛️  Audio Encoding: {tts_config_full.get('audio_encoding', 'LINEAR16')}"
            )
            print(f"  🔄 Client State: {self.state}")

            print("=" * 60)

            # Determine appropriate gender based on voice name (only for generic selection)
            if voice_config.name:
                # Named voice - gender is handled by the API automatically
                ssml_gender = None  # Not used for named voices
            else:
                # Generic voice selection - determine gender from language/preferences
                ssml_gender = texttospeech.SsmlVoiceGender.FEMALE  # Default preference

            # Create voice selection params
            # When using a specific voice name, don't include gender (API conflict)
            if voice_config.name:
                # Specific named voice - gender is already known by the API
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_config.language_code,
                    name=voice_config.name,
                )
            else:
                # Generic voice selection - use gender to help select
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_config.language_code,
                    ssml_gender=ssml_gender,
                )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.config.audio_settings["output_sample_rate"],
                speaking_rate=voice_config.speaking_rate,
                pitch=voice_config.pitch,
                volume_gain_db=voice_config.volume_gain_db,
            )

            # Perform synthesis
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Convert to AudioData
            audio_data = self._convert_api_audio_to_audiodata(response.audio_content)

            logging.info(
                f"TTS synthesis completed: {len(text)} chars -> {len(audio_data.data)} bytes"
            )
            return audio_data

        except Exception as e:
            logging.error(f"TTS synthesis failed: {e}")
            self._handle_api_error(e)
            return None
        finally:
            self.state = APIState.READY

    def _convert_api_audio_to_audiodata(self, api_response: bytes):
        """Convert API audio response to AudioData object"""
        try:
            from .audio_handler import AudioData

            return AudioData(
                data=api_response,
                format="wav",
                sample_rate=self.config.audio_settings["output_sample_rate"],
                channels=self.config.audio_settings["channels"],
            )
        except ImportError:
            # Fallback if audio_handler not available
            logging.warning("AudioData class not available, returning raw bytes")
            return api_response

    def _handle_api_error(self, error: Exception) -> None:
        """Handle API errors and update state"""
        logging.error(f"TTS API error: {error}")
        self.state = APIState.ERROR

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Simple test - list available voices
            self.client.list_voices()
            return True
        except Exception as e:
            logging.error(f"TTS API connection test failed: {e}")
            return False

    def get_available_voices(self, language_code: str = None) -> List[Voice]:
        """Get list of available voices"""
        try:
            request = texttospeech.ListVoicesRequest()
            if language_code:
                request.language_code = language_code

            response = self.client.list_voices(request=request)

            voices = []
            for voice in response.voices:
                voices.append(
                    Voice(
                        name=voice.name,
                        language_code=(
                            voice.language_codes[0] if voice.language_codes else ""
                        ),
                        gender=voice.ssml_gender.name,
                    )
                )

            return voices
        except Exception as e:
            logging.error(f"Failed to get available voices: {e}")
            return []


class AIProvider:
    """Interface for AI text processing providers"""

    def process_text(self, text: str, context: dict) -> str:
        """Process text and return AI response"""
        raise NotImplementedError("AIProvider must be implemented by subclass")

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "base_provider"

    def is_available(self) -> bool:
        """Check if provider is available"""
        return False

    def configure(self, settings: dict) -> None:
        """Configure provider settings"""
        pass


class APIManager:
    """Manages API connections and conversation flow"""

    def __init__(self, config: APIConfig):
        self.config = config
        self.speech_client: Optional[SpeechClient] = None
        self.tts_client: Optional[TTSClient] = None
        self.ai_provider: Optional[Any] = None
        self.state = APIState.INITIALIZING

        # Initialize centralized audio configuration with API config data
        from .audio_handler import audio_config_manager

        audio_config_manager.update_config(config.config_data)
        logging.info("🔧 APIManager: Initialized centralized audio configuration")

        # Initialize API clients in background
        self._initialize_background()

    def _initialize_background(self) -> None:
        """Initialize Speech and TTS clients with non-blocking timeouts"""
        speech_available = False
        tts_available = False

        # Check if Google Cloud should be disabled entirely
        if os.getenv("DISABLE_GOOGLE_CLOUD", "false").lower() == "true":
            logging.info("Google Cloud services disabled by environment variable")
            self.speech_client = None
            self.tts_client = None
            self.state = APIState.AI_ONLY
            logging.info("API Manager initialized in AI-only mode")
            return

        # Try to initialize Speech client with timeout
        try:
            with self._timeout(5, "Speech-to-Text client initialization"):
                self.speech_client = SpeechClient(self.config)
                speech_available = self.speech_client.state == APIState.READY
        except (TimeoutError, Exception) as e:
            logging.warning(f"Speech client initialization failed/timed out: {e}")
            self.speech_client = None

        # Try to initialize TTS client with timeout
        try:
            with self._timeout(5, "Text-to-Speech client initialization"):
                self.tts_client = TTSClient(self.config)
                tts_available = self.tts_client.state == APIState.READY
        except (TimeoutError, Exception) as e:
            logging.warning(f"TTS client initialization failed/timed out: {e}")
            self.tts_client = None

        # Determine final state based on what's available
        if speech_available and tts_available:
            self.state = APIState.READY
            logging.info("API Manager fully initialized (Speech + TTS + AI)")
        elif speech_available or tts_available:
            self.state = APIState.AI_ONLY  # Partial functionality
            available_services = []
            if speech_available:
                available_services.append("Speech")
            if tts_available:
                available_services.append("TTS")
            logging.info(
                f"API Manager partially initialized ({'+'.join(available_services)} + AI)"
            )
        else:
            self.state = APIState.AI_ONLY  # AI-only mode
            logging.info(
                "API Manager initialized in AI-only mode (Speech/TTS unavailable)"
            )

    @contextmanager
    def _timeout(self, seconds: int, operation_name: str):
        """Context manager for timeout operations"""

        def timeout_handler(signum, frame):
            raise TimeoutError(f"{operation_name} timed out after {seconds} seconds")

        # Set up the timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            # Clean up
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def initialize(self) -> bool:
        """Initialize the API manager"""
        return self.state == APIState.READY

    def speech_to_text(self, audio_data) -> Optional[str]:
        """Convert audio to text"""
        if not self.speech_client:
            error_msg = "❌ Speech-to-Text service unavailable: Missing Google Cloud credentials\nPlease set up GOOGLE_APPLICATION_CREDENTIALS environment variable\nSee: https://cloud.google.com/docs/authentication/external/set-up-adc"
            logging.error("Speech client not initialized")
            raise RuntimeError(error_msg)

        result = self.speech_client.transcribe_audio(audio_data)
        return result.text if result else None

    def text_to_speech(self, text: str) -> Optional[Any]:
        """Convert text to audio"""
        if not self.tts_client:
            error_msg = "❌ Text-to-Speech service unavailable: Missing Google Cloud credentials\nPlease set up GOOGLE_APPLICATION_CREDENTIALS environment variable\nSee: https://cloud.google.com/docs/authentication/external/set-up-adc"
            logging.error("TTS client not initialized")
            raise RuntimeError(error_msg)

        # Sanitize text for TTS API (remove newlines and normalize whitespace)
        sanitized_text = text.replace("\n", " ").replace("\r", " ")
        sanitized_text = re.sub(r"\s+", " ", sanitized_text).strip()

        if sanitized_text != text:
            logging.debug(
                f"🧹 TTS TEXT SANITIZED: '{text[:50]}...' → '{sanitized_text[:50]}...'"
            )

        return self.tts_client.synthesize_text(sanitized_text)

    def process_conversation_turn(self, audio_data) -> Optional[Any]:
        """Process a complete conversation turn: audio -> text -> AI -> audio"""
        if not self.ai_provider:
            logging.error("AI provider not set")
            print("\n❌ AI PROVIDER NOT SET")

            # Create fallback response with user's requested message
            from .prompts_config import PromptsConfig

            fallback_audio = self.text_to_speech(
                PromptsConfig.get_fallback_response("api_unavailable")
            )
            if fallback_audio:
                logging.info("✅ Created fallback response audio (AI provider not set)")
                print("✅ Created fallback response audio (AI provider not set)")
                return fallback_audio
            else:
                logging.error(
                    "❌ Failed to create fallback response audio (AI provider not set)"
                )
                print(
                    "❌ Failed to create fallback response audio (AI provider not set)"
                )
                return None

        logging.info("🔄 STARTING CONVERSATION PIPELINE")
        logging.info("=" * 60)

        # Step 1: Speech to text
        logging.info("STEP 1: 🎤 Speech-to-Text")
        text = self.speech_to_text(audio_data)
        if not text:
            logging.error("❌ PIPELINE FAILED: Failed to transcribe audio")
            return None

        # Step 2: AI processing
        logging.info("STEP 2: 🤖 AI Processing")
        logging.info(f"🎯 STARTING PROMPT-BASED AI PROCESSING")
        logging.info(f"🔤 USER INPUT TO AI: '{text}'")
        logging.info(f"📏 INPUT LENGTH: {len(text)} characters")
        sanitized_text = None  # Initialize for scope
        try:
            # This will trigger comprehensive prompt logging in GeminiFlashProvider
            response_text = self.ai_provider.process_text(text, {})
            logging.info("🤖 AI RESPONSE RECEIVED:")
            logging.info(f"📝 AI RESPONSE TEXT: '{response_text}'")
            logging.info(f"📏 RESPONSE LENGTH: {len(response_text)} characters")

            # Also print to console for immediate visibility
            print("\n🤖 AI RESPONSE RECEIVED:")
            print(f"📝 AI RESPONSE TEXT: '{response_text}'")
            print(f"📏 RESPONSE LENGTH: {len(response_text)} characters")

            # Sanitize AI response text for TTS (remove newlines and extra whitespace)
            sanitized_text = response_text.replace("\n", " ").replace("\r", " ")
            # Clean up multiple spaces
            sanitized_text = re.sub(r"\s+", " ", sanitized_text).strip()

            # Check if sanitization resulted in empty text
            if not sanitized_text:
                logging.warning("Sanitized text is empty, using fallback response")
                print("⚠️ Sanitized text is empty, using fallback response")
                from .prompts_config import PromptsConfig

                sanitized_text = PromptsConfig.get_fallback_response("empty_response")

            logging.info("🧹 TEXT SANITIZATION:")
            logging.info(f"📝 ORIGINAL: '{response_text[:100]}...'")
            logging.info(f"🧼 SANITIZED: '{sanitized_text[:100]}...'")
            print("🧹 TEXT SANITIZED FOR TTS:")
            print(f"📝 ORIGINAL: '{response_text[:100]}...'")
            print(f"🧼 SANITIZED: '{sanitized_text[:100]}...'")

            # Check final sanitized text length before proceeding
            if not sanitized_text or len(sanitized_text.strip()) == 0:
                logging.error("Final sanitized text is empty after all processing")
                print("❌ Final sanitized text is empty after all processing")
                from .prompts_config import PromptsConfig

                sanitized_text = PromptsConfig.get_fallback_response("empty_response")

        except Exception as e:
            logging.error(f"❌ PIPELINE FAILED: AI processing failed: {e}")
            print(f"\n❌ AI PROCESSING FAILED: {e}")

            # Create fallback response with user's requested message
            from .prompts_config import PromptsConfig

            fallback_audio = self.text_to_speech(
                PromptsConfig.get_fallback_response("api_unavailable")
            )
            if fallback_audio:
                logging.info("✅ Created fallback response audio")
                print("✅ Created fallback response audio")
                return fallback_audio
            else:
                logging.error("❌ Failed to create fallback response audio")
                print("❌ Failed to create fallback response audio")
                return None

        # Step 3: Text to speech
        logging.info("STEP 3: 🔊 Text-to-Speech")
        if not sanitized_text:
            logging.warning(
                "❌ No sanitized text available, using final fallback for TTS"
            )
            print("⚠️ No sanitized text available, using final fallback for TTS")
            from .prompts_config import PromptsConfig

            sanitized_text = PromptsConfig.get_fallback_response("empty_response")

        logging.info(f"🗣️  CONVERTING TO SPEECH: '{sanitized_text[:50]}...'")
        response_audio = self.text_to_speech(sanitized_text)
        if not response_audio:
            logging.error("❌ PIPELINE FAILED: Failed to synthesize response audio")
            return None

        logging.info("✅ CONVERSATION PIPELINE COMPLETED SUCCESSFULLY")
        logging.info("=" * 60)
        return response_audio

    def get_api_status(self) -> dict:
        """Get status of all API components"""
        return {
            "state": self.state.value,
            "speech_client": (
                self.speech_client.state.value
                if self.speech_client
                else "not_initialized"
            ),
            "tts_client": (
                self.tts_client.state.value if self.tts_client else "not_initialized"
            ),
            "ai_provider": (
                self.ai_provider.get_provider_name() if self.ai_provider else "not_set"
            ),
            "project_id": self.config.project_id,
            "environment": self.config.secrets["environment"],
        }

    def set_ai_provider(self, provider: AIProvider) -> None:
        """Set the AI provider for text processing"""
        self.ai_provider = provider
        logging.info(f"AI provider set to: {provider.get_provider_name()}")

    def cleanup(self) -> None:
        """Clean up API resources"""
        logging.info("Cleaning up API Manager...")

        # Clean up clients
        if self.speech_client:
            self.speech_client.state = APIState.OFFLINE
        if self.tts_client:
            self.tts_client.state = APIState.OFFLINE

        self.state = APIState.OFFLINE
        logging.info("API Manager cleanup completed")


# Utility functions for easy testing
def test_google_cloud_connection() -> bool:
    """Test Google Cloud connection and credentials"""
    try:
        credentials, project = default()
        logging.info(f"Google Cloud authentication successful for project: {project}")
        return True
    except DefaultCredentialsError:
        logging.error("Google Cloud credentials not found")
        return False
    except Exception as e:
        logging.error(f"Google Cloud authentication failed: {e}")
        return False


def create_api_manager(
    config_file: str = "config/api_config.json",
) -> Optional[APIManager]:
    """Create and initialize an API manager"""
    try:
        config = APIConfig(config_file)
        manager = APIManager(config)

        if manager.initialize():
            logging.info("API Manager created and initialized successfully")
            return manager
        else:
            logging.error("Failed to initialize API Manager")
            return None

    except Exception as e:
        logging.error(f"Failed to create API Manager: {e}")
        return None
