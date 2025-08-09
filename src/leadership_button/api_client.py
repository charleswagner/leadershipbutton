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
import html
import xml.etree.ElementTree as ET

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
        """Convert plain text to audio (non-SSML)."""
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

            # Prepare synthesis request (plain text)
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
                f"  🔤 Text Type: {'Named Voice' if voice_config.name else 'Generic Voice'}"
            )

            # API Configuration
            tts_config_full = self.config.get_tts_config()
            logging.info("⚙️  API CONFIGURATION:")
            logging.info(
                f"  🎯 Voice Selection: {voice_config.name or 'Auto-select by gender'}"
            )
            logging.info(
                f"  🎛️  Audio Encoding: {tts_config_full.get('audio_encoding', 'MP3')}"
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
            print(f"  🎛️  Encoding: MP3")

            # Text Configuration
            print("📝 TEXT CONFIGURATION:")
            print(f"  📄 Input Length: {len(text)} characters")
            print(
                f"  🔤 Text Type: {'Named Voice' if voice_config.name else 'Generic Voice'}"
            )

            # API Configuration
            print("⚙️  API CONFIGURATION:")
            print(
                f"  🎯 Voice Selection: {voice_config.name or 'Auto-select by gender'}"
            )
            print(
                f"  🎛️  Audio Encoding: {tts_config_full.get('audio_encoding', 'MP3')}"
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

            print("--- FINAL TEXT SENT TO GOOGLE ---")
            print(text)
            print("--------------444444-------------------")

            # Perform synthesis
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            print("After response ---------------------------------")

            # Convert to AudioData
            audio_data = self._convert_api_audio_to_audiodata(response.audio_content)

            # Persist generated audio for later review
            try:
                from pathlib import Path as _P
                from datetime import datetime as _DT
                import os as _os
                base = _P(_os.environ.get("LB_LOG_DIR", "logs")) / "audio" / "generated"
                base.mkdir(parents=True, exist_ok=True)
                ts = _DT.now().strftime("%Y%m%d-%H%M%S%f")
                out_path = base / f"tts_text_{ts}.wav"
                try:
                    # If AudioData available, save via helper
                    audio_data.save_to_file(str(out_path))
                except Exception:
                    with open(out_path, "wb") as f:
                        f.write(response.audio_content)
                logging.info("💾 Saved generated TTS (text) to %s", out_path)
            except Exception as _exc:
                logging.warning("Failed to save generated TTS (text): %s", _exc)

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

    def synthesize_ssml(
        self, ssml: str, voice_config: Optional[VoiceConfig] = None
    ) -> Optional[Any]:
        """Convert SSML to audio.

        Expects a valid SSML document enclosed in <speak>...</speak>.
        """
        if self.state != APIState.READY:
            logging.error(f"Cannot synthesize SSML in state: {self.state}")
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

            # Validate SSML (parse and require <speak> root)
            try:
                # Strip <s> tags prior to XML validation to avoid malformed sentence nesting
                ssml = re.sub(r"</?s\\b[^>]*>", "", ssml)
                root = ET.fromstring(ssml)
                if root.tag.lower() != "speak":
                    raise ValueError("SSML must have <speak> as the root element")
            except Exception as exc:
                logging.error("Invalid SSML provided: %s", exc)
                raise

            # Prepare synthesis request (SSML)

            print("--- FINAL TEXT SENT TO GOOGLE ---")
            print(ssml)
            print("--------------666-------------------")
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

            # Log SSML preview and mode
            logging.info("📝 SSML INPUT (preview full): %s", ssml)
            print("📝 SSML INPUT (preview full):", ssml)

            # Voice selection (same as in synthesize_text)
            if voice_config.name:
                ssml_gender = None
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_config.language_code,
                    name=voice_config.name,
                )
            else:
                ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
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

            # Log FULL SSML for debugging
            logging.info("SSML FINAL — BEGIN")
            for i, line in enumerate(ssml.split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("SSML FINAL — END")
            print("\nSSML FINAL — BEGIN")
            for i, line in enumerate(ssml.split("\n"), 1):
                print(f"{i:3d}: {line}")
            print("SSML FINAL — END")

            # Validate that the outgoing request is JSON-serializable (debug check)
            try:
                req_probe = {
                    "input": {"ssml": ssml},
                    "voice": {
                        "languageCode": voice.language_code,
                        **(
                            {"name": voice.name} if getattr(voice, "name", None) else {}
                        ),
                    },
                    "audioConfig": {
                        "audioEncoding": texttospeech.AudioEncoding.LINEAR16.name,
                        "speakingRate": audio_config.speaking_rate,
                        "pitch": (
                            audio_config.pitch_hz
                            if hasattr(audio_config, "pitch_hz")
                            else voice_config.pitch
                        ),
                        "sampleRateHertz": self.config.audio_settings[
                            "output_sample_rate"
                        ],
                        "volumeGainDb": voice_config.volume_gain_db,
                    },
                }
                _ = json.dumps(req_probe)  # ensure serializable
            except Exception as exc:
                logging.error("TTS request JSON validation failed: %s", exc)
                raise

            # Debug SSML already printed above; avoid duplicate noisy logs

            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            audio_data = self._convert_api_audio_to_audiodata(response.audio_content)

            # Persist generated SSML audio for later review
            try:
                from pathlib import Path as _P
                from datetime import datetime as _DT
                import os as _os
                base = _P(_os.environ.get("LB_LOG_DIR", "logs")) / "audio" / "generated"
                base.mkdir(parents=True, exist_ok=True)
                ts = _DT.now().strftime("%Y%m%d-%H%M%S%f")
                out_path = base / f"tts_ssml_{ts}.wav"
                try:
                    audio_data.save_to_file(str(out_path))
                except Exception:
                    with open(out_path, "wb") as f:
                        f.write(response.audio_content)
                logging.info("💾 Saved generated TTS (ssml) to %s", out_path)
            except Exception as _exc:
                logging.warning("Failed to save generated TTS (ssml): %s", _exc)
            logging.info(
                f"TTS SSML synthesis completed: {len(ssml)} chars -> {len(audio_data.data)} bytes"
            )
            return audio_data
        except Exception as e:
            logging.error(f"TTS SSML synthesis failed: {e}")
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
        """Convert text (plain) to audio."""
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

    def text_to_speech_ssml(self, ssml: str) -> Optional[Any]:
        """Convert SSML to audio, with minimal validation/sanitization."""
        if not self.tts_client:
            error_msg = "❌ Text-to-Speech service unavailable: Missing Google Cloud credentials\nPlease set up GOOGLE_APPLICATION_CREDENTIALS environment variable\nSee: https://cloud.google.com/docs/authentication/external/set-up-adc"
            logging.error("TTS client not initialized")
            raise RuntimeError(error_msg)

        # Light cleanup of SSML whitespace
        cleaned = re.sub(r"\s+", " ", ssml).strip()

        # Normalize <audio> tags that contain inner text
        cleaned = self._normalize_audio_tag_inner_text(cleaned)

        # Normalize/resolve audio src values (also strips leading '@' and trims)
        try:
            cleaned = self._rewrite_ssml_audio_srcs(cleaned)
        except Exception:
            pass

        # Whitelist enforcement removed per user request

        # Music clip auto-enforcement removed per user request

        # Cap overly long breaks to 2s to reduce total output length
        cleaned = self._cap_long_breaks(cleaned, max_seconds=2.0)

        # Normalize/remove <s> sentence tags which frequently cause malformed SSML from LLMs
        try:
            cleaned = re.sub(r"</?s\\b[^>]*>", "", cleaned)
        except Exception:
            pass

        # Log the exact SSML that will be sent to Google TTS — immediately before the API call
        try:
            logging.info("SSML FINAL — BEGIN")
            for i, line in enumerate((cleaned or "").split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("SSML FINAL — END")
            print("\nSSML FINAL — BEGIN")
            for i, line in enumerate((cleaned or "").split("\n"), 1):
                print(f"{i:3d}: {line}")
            print("SSML FINAL — END")
        except Exception:
            # Ensure logging never blocks the API call
            pass

        # Final call with cleaned SSML
        return self.tts_client.synthesize_ssml(cleaned)

    def _rewrite_ssml_audio_srcs(self, ssml: str) -> str:
        """Replace <audio src="..."/> tokens with Google Cloud Storage URLs.

        - Accepts tokens like `feeling_paper`, `feeling_paper.ogg`, or human titles
        - Matches against the sound library CSV by filename stem, kit_title, or tags
        - Uses CSV `google_cloud_url` if present, otherwise derives from `source_directory`
        - Logs each mapping with original token and resolved URL
        """
        import csv as _csv
        from pathlib import Path as _P

        def _norm(s: str) -> str:
            s = (s or "").strip().lower()
            s = re.sub(r"\.[a-z0-9]+$", "", s)  # drop extension
            s = s.replace("-", "_").replace(" ", "_")
            s = re.sub(r"[^a-z0-9_]+", "_", s)
            s = re.sub(r"_+", "_", s).strip("_")
            return s

        # Build index once per APIManager instance
        if not hasattr(self, "_sound_url_index"):
            csv_path = _P("helpers/soundscripts/data/soundlibrary.csv")
            index: dict[str, dict] = {}
            if csv_path.exists():
                try:
                    with csv_path.open("r", encoding="utf-8") as f:
                        r = _csv.DictReader(f)
                        for row in r:
                            filename = (row.get("filename") or "").strip()
                            gcs = (row.get("google_cloud_url") or "").strip()
                            src_dir = (
                                (row.get("source_directory") or "").strip().lower()
                            )
                            # Derive from file_path if no URL provided, following cw{ext}/{rel_path_after_public_sounds}
                            if not gcs and filename:
                                from urllib.parse import quote

                                file_path = (row.get("file_path") or "").strip()
                                rel_path = ""
                                if file_path:
                                    # Normalize separators
                                    p = file_path.replace("\\", "/")
                                    anchor = "/public/sounds/"
                                    idx = p.lower().find(anchor)
                                    if idx != -1:
                                        rel_path = p[idx + len(anchor) :]
                                if not rel_path:
                                    # Fallback to filename only
                                    rel_path = filename
                                safe_rel = quote(rel_path, safe="/")
                                gcs = f"https://storage.googleapis.com/cwsounds/{safe_rel}"
                            keys: set[str] = set()
                            if filename:
                                keys.add(_norm(filename))
                            title = (row.get("kit_title") or "").strip()
                            if title:
                                keys.add(_norm(title))
                            tags = (row.get("kit_tags") or "").strip()
                            if tags:
                                for t in tags.split(","):
                                    t = t.strip()
                                    if t:
                                        keys.add(_norm(t))
                            for k in keys:
                                if k and k not in index:
                                    index[k] = {
                                        "url": gcs,
                                        "filename": filename,
                                        "source_directory": src_dir,
                                    }
                    logging.info("📚 Built sound URL index with %d keys", len(index))
                except Exception as exc:
                    logging.warning("Failed to read sound library CSV: %s", exc)
                    index = {}
            else:
                logging.warning("Sound library CSV not found at %s", csv_path)
                index = {}
            self._sound_url_index = index

        # Regex supports src in single or double quotes, and self-close or paired closing
        audio_pat = re.compile(
            r"<\s*audio[^>]*?src=(?:\"([^\"]+)\"|'([^']+)')[^>]*?(/?>|></\s*audio\s*>)",
            re.IGNORECASE,
        )

        def _resolve(token: str) -> tuple[Optional[str], Optional[str]]:
            # Normalize token: trim whitespace and remove any leading '@'
            tok = token.strip()
            if tok.startswith("@"):
                tok = tok.lstrip("@").strip()
            if tok.startswith("http://") or tok.startswith("https://"):
                return tok, "url"
            key = _norm(tok)
            # exact key
            if key in self._sound_url_index:
                return self._sound_url_index[key]["url"], key
            # if token has extension, try stem
            stem = _norm(re.sub(r"\.[a-z0-9]+$", "", tok))
            if stem in self._sound_url_index:
                return self._sound_url_index[stem]["url"], stem
            # partial contains
            for k, meta in self._sound_url_index.items():
                if key and (key in k or k in key or stem in k or k in stem):
                    return meta["url"], k
            # Fallback: attempt to derive from filename directly against CSV rows
            try:
                import csv as _csv
                from urllib.parse import quote as _quote

                csv_path = _P("helpers/soundscripts/data/soundlibrary.csv")
                if csv_path.exists():
                    with csv_path.open("r", encoding="utf-8") as _f:
                        r = _csv.DictReader(_f)
                        tok_lower = tok.lower()
                        for row in r:
                            fn = (row.get("filename") or "").lower()
                            if fn and (fn == tok_lower or stem in _norm(fn)):
                                fp = (row.get("file_path", "") or "").replace("\\", "/")
                                anchor = "/public/sounds/"
                                rel = row.get("filename", "")
                                i = fp.lower().find(anchor)
                                if i != -1:
                                    rel = fp[i + len(anchor) :]
                                return (
                                    f"https://storage.googleapis.com/cwsounds/{_quote(rel, safe='/')}",
                                    fn,
                                )
            except Exception:
                pass
            return None, None

        def _repl(m: re.Match) -> str:
            whole = m.group(0)
            src = m.group(1) or m.group(2) or ""
            resolved, matched_key = _resolve(src)
            if resolved:
                logging.info(
                    "🔗 <audio> src mapped: token='%s' key='%s' -> '%s'",
                    src,
                    matched_key,
                    resolved,
                )
                return whole.replace(src, resolved)
            logging.warning("⚠️ No mapping found for <audio> src token '%s'", src)
            return whole

        # Log all tokens discovered
        for m in audio_pat.finditer(ssml):
            raw_src = m.group(1) or m.group(2)
            logging.info("👂 Found <audio> tag src='%s'", raw_src)

        return audio_pat.sub(_repl, ssml)

    def _normalize_audio_tag_inner_text(self, ssml: str) -> str:
        """Move any inner text out of <audio>...</audio> so TTS won't treat it as audio content.

        Example: <audio src="...">Some text</audio> -> <audio src="..."></audio> Some text
        """
        # Capture audio tags with inner text (non-tag text)
        patt = re.compile(
            r"(<\s*audio\b[^>]*>)([^<][\s\S]*?)(</\s*audio\s*>)", re.IGNORECASE
        )

        def _repl(m: re.Match) -> str:
            open_tag, inner, close_tag = (
                m.group(1),
                (m.group(2) or "").strip(),
                m.group(3),
            )
            if inner:
                logging.info("✂️ Moved inner text out of <audio>: '%s'", inner[:120])
                return f"{open_tag}{close_tag} {inner}"
            return m.group(0)

        return patt.sub(_repl, ssml)

    def _strip_unsupported_ssml_for_google(self, ssml: str) -> str:
        """Remove/replace SSML tags not supported by Google TTS.

        - Google TTS does not support <audio src="..."/>, so we replace each with
          a short <break/> and log what was removed. The audio should be played by
          the playback pipeline, not TTS.
        """
        # Remove <audio> tags, leave a brief pause
        audio_pat = re.compile(
            r"<\s*audio[^>]*?src=(?:\"([^\"]+)\"|'([^']+)')[^>]*?(/?>|></\s*audio\s*>)",
            re.IGNORECASE,
        )

        removed: list[str] = []

        def _repl(m: re.Match) -> str:
            src = m.group(1) or m.group(2) or ""
            removed.append(src)
            return '<break time="300ms"/>'

        out = audio_pat.sub(_repl, ssml)
        if removed:
            logging.info(
                "🧱 Stripped %d <audio> tags not supported by Google TTS", len(removed)
            )
            for src in removed:
                logging.info("   - audio src removed: %s", src)
        return out

    def _load_kid_audio_whitelist(self) -> set:
        from pathlib import Path as _P
        import csv as _csv

        top = _P("tmp/top100_kid_story_audio.csv")
        wl: set = set()
        if top.exists():
            try:
                with top.open("r", encoding="utf-8") as f:
                    r = _csv.DictReader(f)
                    for row in r:
                        rel = (row.get("relpath") or "").strip()
                        if rel:
                            wl.add(rel)
            except Exception as exc:
                logging.warning("Failed loading whitelist: %s", exc)
        return wl

    def _enforce_audio_whitelist(self, ssml: str) -> str:
        """Remove <audio> tags whose relpath is not in the top-100 whitelist."""
        wl = getattr(self, "_kid_audio_wl", None)
        if wl is None:
            wl = self._load_kid_audio_whitelist()
            self._kid_audio_wl = wl
        if not wl:
            return ssml
        pat = re.compile(
            r"<\s*audio[^>]*?src=(?:\"([^\"]+)\"|'([^']+)')[^>]*?(/?>|></\s*audio\s*>)",
            re.IGNORECASE,
        )

        def _rel_from_url(u: str) -> str:
            u = u or ""
            key = "cwsounds/"
            i = u.find(key)
            return u[i + len(key) :] if i != -1 else u

        removed = 0

        def _repl(m: re.Match) -> str:
            src = m.group(1) or m.group(2) or ""
            rel = _rel_from_url(src)
            if rel in wl:
                return m.group(0)
            nonlocal removed
            removed += 1
            return ""

        out = pat.sub(_repl, ssml)
        if removed:
            logging.info("🧹 Removed %d non-whitelisted <audio> tags", removed)
        return out

    def _enforce_music_clip_25s(self, ssml: str) -> str:
        """Ensure all Mixkit music audio tags are clipped to 25 seconds with a fade out.

        Adds clipEnd="25s" and fadeOutDur="2s" if not already present.
        """
        pat = re.compile(
            r"(<\s*audio\b)([^>]*?)src=(?:\"([^\"]+)\"|'([^']+)')([^>]*?)(/?>)",
            re.IGNORECASE,
        )

        def _needs_clip(attrs: str) -> bool:
            al = attrs.lower()
            return "clipend=" not in al

        def _needs_fade(attrs: str) -> bool:
            al = attrs.lower()
            return "fadeoutdur=" not in al

        def _is_mixkit_url(u: str) -> bool:
            return "cwsounds/mixkit/" in u

        def _repl(m: re.Match) -> str:
            start, pre, src1, src2, post, end = m.groups()
            src = src1 or src2 or ""
            if _is_mixkit_url(src) and (
                _needs_clip(pre + post) or _needs_fade(pre + post)
            ):
                attrs = pre + post
                if _needs_clip(attrs):
                    attrs += ' clipEnd="25s"'
                if _needs_fade(attrs):
                    attrs += ' fadeOutDur="2s"'
                return f'{start}{pre}src="{src}"{attrs}{end}'
            return m.group(0)

        out = pat.sub(_repl, ssml)
        return out

    def _cap_long_breaks(self, ssml: str, max_seconds: float = 2.0) -> str:
        pat = re.compile(
            r"<\s*break\s+time=\"([0-9]+\.?[0-9]*)(ms|s)\"\s*/>", re.IGNORECASE
        )

        def _repl(m: re.Match) -> str:
            val, unit = m.groups()
            try:
                num = float(val)
            except Exception:
                return m.group(0)
            seconds = num / 1000.0 if unit.lower() == "ms" else num
            if seconds <= max_seconds:
                return m.group(0)
            # cap
            return f'<break time="{max_seconds}s"/>'

        return pat.sub(_repl, ssml)

    @staticmethod
    def _clean_llm_response_to_ssml_or_text(raw: str) -> tuple[str, bool]:
        """Extract a valid SSML document from LLM text if present; otherwise return plain text.

        Returns (output, is_ssml).
        - Strips code fences and any pre/post text around <speak> ... </speak>
        - Normalizes smart quotes and illegal XML chars
        - Replaces unsupported <audio .../> tags with <break/>
        - Fixes a common typo like </"prosody>
        """
        if not raw:
            return "", False

        text = raw.strip()
        # Remove code fences like ```xml ... ``` or ```
        text = re.sub(r"```[a-zA-Z]*\n?", "", text)
        text = text.replace("```", "").strip()

        # Normalize smart quotes/dashes
        trans = {
            ord("“"): '"',
            ord("”"): '"',
            ord("‘"): "'",
            ord("’"): "'",
            ord("—"): "-",
            ord("–"): "-",
        }
        text = text.translate(trans)

        # Fix obvious closing tag typo
        text = text.replace('</"prosody>', "</prosody>")

        # Extract <speak> ... </speak>
        lower = text.lower()
        start = lower.find("<speak")
        end = lower.rfind("</speak>")
        if start != -1 and end != -1:
            # Move end to include closing tag
            end += len("</speak>")
            ssml = text[start:end]
            # Remove zero-width and control chars that break XML
            ssml = re.sub(r"[\u200B\uFEFF\x00-\x08\x0B\x0C\x0E-\x1F]", "", ssml)
            # Escape stray ampersands not part of entities
            ssml = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", ssml)
            return ssml.strip(), True

        # No SSML found; return cleaned plain text
        plain = re.sub(r"\s+", " ", text).strip()
        return plain, False

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

            # Try to extract SSML block; fall back to plain text
            cleaned, is_ssml = self._clean_llm_response_to_ssml_or_text(response_text)
            if is_ssml:
                logging.info("🧩 Detected SSML response from AI (using SSML mode)")
                sanitized_text = cleaned  # reuse variable name for downstream logging
            else:
                sanitized_text = cleaned

            # Check if sanitization resulted in empty text
            if not sanitized_text or len(sanitized_text.strip()) == 0:
                logging.warning("Sanitized text is empty, using fallback response")
                print("⚠️ Sanitized text is empty, using fallback response")
                from .prompts_config import PromptsConfig

                sanitized_text = PromptsConfig.get_fallback_response("empty_response")

            logging.info("🧹 TEXT/SSML SANITIZATION:")
            logging.info("📝 ORIGINAL (full) — BEGIN")
            for i, line in enumerate((response_text or "").split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("📝 ORIGINAL (full) — END")
            logging.info("🧼 SANITIZED (full) — BEGIN")
            for i, line in enumerate((sanitized_text or "").split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info(" SANITIZED (full) — END")
            print("🧹 TEXT SANITIZED FOR TTS (full):")
            print("📝 ORIGINAL — BEGIN")
            print(response_text)
            print("📝 ORIGINAL — END")
            print("🧼 SANITIZED — BEGIN")
            print(sanitized_text)
            print("🧼 SANITIZED — END")

            # Warn if speak tag present but not properly closed
            if (
                "<speak" in sanitized_text.lower()
                and "</speak>" not in sanitized_text.lower()
            ):
                logging.warning(
                    "SSML appears to start with <speak> but lacks a closing </speak> tag. Falling back to PLAINTEXT."
                )

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
        # Route to SSML or plain text API appropriately
        if sanitized_text.strip().lower().startswith(
            "<speak"
        ) and sanitized_text.strip().lower().endswith("</speak>"):
            # Before sending, rewrite any <audio src="token"/> references to GCS URLs
            try:
                ssml_with_urls = self._rewrite_ssml_audio_srcs(sanitized_text)
            except Exception as _exc:
                logging.warning("SSML audio URL rewrite failed: %s", _exc)
                ssml_with_urls = sanitized_text
            # Send SSML with <audio> tags directly; Google TTS supports SSML <audio>
            response_audio = self.text_to_speech_ssml(ssml_with_urls)
        else:
            logging.info("🔀 TTS MODE: PLAINTEXT")
            print("🔀 TTS MODE: PLAINTEXT")
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
