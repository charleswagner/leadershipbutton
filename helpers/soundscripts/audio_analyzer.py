"""
Audio analysis using Librosa library for comprehensive metadata extraction.
"""

import os
import logging
import numpy as np
from typing import List
from dataclasses import dataclass

try:
    import librosa
    import librosa.display

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


@dataclass
class AudioAnalysis:
    """Data class to hold comprehensive audio analysis results."""

    # Basic file information
    filename: str
    file_path: str
    duration: float
    sample_rate: int
    channels: int
    file_size: int

    # Temporal features
    tempo: float
    beat_count: int
    onset_strength: float
    zero_crossing_rate: float
    rms_energy: float

    # Spectral features
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    spectral_contrast: float
    spectral_flatness: float
    spectral_contrast_mean: float
    spectral_flatness_mean: float

    # Harmonic features
    harmonic_ratio: float
    chroma_features: List[float]
    mfcc_features: List[float]

    # Statistical features
    dynamic_range: float
    loudness: float
    peak_amplitude: float

    # Classification (to be filled by metadata generator)
    audio_type: str = ""
    confidence: float = 0.0


class AudioAnalyzer:
    """Comprehensive audio analysis using Librosa."""

    def __init__(self):
        """Initialize the audio analyzer."""
        self.logger = logging.getLogger(__name__)

        if not LIBROSA_AVAILABLE:
            raise ImportError(
                "Librosa library is required but not installed. "
                "Please install with: pip install librosa"
            )

    def analyze_audio_file(self, file_path: str) -> AudioAnalysis:
        """Analyze an audio file and extract comprehensive metadata."""

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        self.logger.debug(f"Analyzing audio file: {file_path}")

        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None, mono=False)

            # Handle stereo files
            if y.ndim > 1:
                channels = y.shape[0]
                y_mono = librosa.to_mono(y)
            else:
                channels = 1
                y_mono = y

            # Get basic file information
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            duration = len(y_mono) / sr

            # Extract temporal features
            tempo, beat_count, onset_strength = self._extract_temporal_features(
                y_mono, sr
            )
            zero_crossing_rate = self._calculate_zero_crossing_rate(y_mono)
            rms_energy = self._calculate_rms_energy(y_mono)

            # Extract spectral features
            spectral_features = self._extract_spectral_features(y_mono, sr)

            # Extract harmonic features
            harmonic_features = self._extract_harmonic_features(y_mono, sr)

            # Extract statistical features
            statistical_features = self._extract_statistical_features(y_mono)

            # Create analysis object
            analysis = AudioAnalysis(
                filename=filename,
                file_path=file_path,
                duration=duration,
                sample_rate=sr,
                channels=channels,
                file_size=file_size,
                tempo=tempo,
                beat_count=beat_count,
                onset_strength=onset_strength,
                zero_crossing_rate=zero_crossing_rate,
                rms_energy=rms_energy,
                **spectral_features,
                **harmonic_features,
                **statistical_features,
            )

            self.logger.debug(f"Analysis completed for {filename}")
            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze audio file {file_path}: {e}")
            raise

    def _extract_temporal_features(self, y: np.ndarray, sr: int) -> tuple:
        """Extract temporal features: tempo, beat count, onset strength."""

        try:
            # Extract tempo and beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_count = len(beats)

            # Calculate onset strength
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_strength = (
                np.mean(librosa.onset.onset_strength(y=y, sr=sr))
                if len(onset_frames) > 0
                else 0.0
            )

            return float(tempo), beat_count, float(onset_strength)

        except Exception as e:
            self.logger.warning(f"Failed to extract temporal features: {e}")
            return 0.0, 0, 0.0

    def _calculate_zero_crossing_rate(self, y: np.ndarray) -> float:
        """Calculate zero crossing rate."""

        try:
            zcr = librosa.feature.zero_crossing_rate(y)
            return float(np.mean(zcr))
        except Exception as e:
            self.logger.warning(f"Failed to calculate zero crossing rate: {e}")
            return 0.0

    def _calculate_rms_energy(self, y: np.ndarray) -> float:
        """Calculate RMS energy."""

        try:
            rms = librosa.feature.rms(y=y)
            return float(np.mean(rms))
        except Exception as e:
            self.logger.warning(f"Failed to calculate RMS energy: {e}")
            return 0.0

    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> dict:
        """Extract spectral features."""

        features = {
            "spectral_centroid": 0.0,
            "spectral_bandwidth": 0.0,
            "spectral_rolloff": 0.0,
            "spectral_contrast": 0.0,
            "spectral_flatness": 0.0,
            "spectral_contrast_mean": 0.0,
            "spectral_flatness_mean": 0.0,
        }

        try:
            # Spectral centroid
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            features["spectral_centroid"] = float(np.mean(centroid))

            # Spectral bandwidth
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            features["spectral_bandwidth"] = float(np.mean(bandwidth))

            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features["spectral_rolloff"] = float(np.mean(rolloff))

            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features["spectral_contrast"] = float(np.mean(contrast))
            features["spectral_contrast_mean"] = float(np.mean(contrast))

            # Spectral flatness
            flatness = librosa.feature.spectral_flatness(y=y)
            features["spectral_flatness"] = float(np.mean(flatness))
            features["spectral_flatness_mean"] = float(np.mean(flatness))

        except Exception as e:
            self.logger.warning(f"Failed to extract spectral features: {e}")

        return features

    def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> dict:
        """Extract harmonic features."""

        features = {
            "harmonic_ratio": 0.0,
            "chroma_features": [0.0] * 12,
            "mfcc_features": [0.0] * 13,
        }

        try:
            # Harmonic-percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_energy = np.sum(y_harmonic**2)
            total_energy = np.sum(y**2)
            features["harmonic_ratio"] = (
                float(harmonic_energy / total_energy) if total_energy > 0 else 0.0
            )

            # Chroma features (12-dimensional)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features["chroma_features"] = [float(x) for x in np.mean(chroma, axis=1)]

            # MFCC features (13-dimensional)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features["mfcc_features"] = [float(x) for x in np.mean(mfcc, axis=1)]

        except Exception as e:
            self.logger.warning(f"Failed to extract harmonic features: {e}")

        return features

    def _extract_statistical_features(self, y: np.ndarray) -> dict:
        """Extract statistical features."""

        features = {"dynamic_range": 0.0, "loudness": 0.0, "peak_amplitude": 0.0}

        try:
            # Dynamic range (difference between max and min amplitude)
            features["dynamic_range"] = float(np.max(y) - np.min(y))

            # Loudness (RMS value)
            features["loudness"] = float(np.sqrt(np.mean(y**2)))

            # Peak amplitude
            features["peak_amplitude"] = float(np.max(np.abs(y)))

        except Exception as e:
            self.logger.warning(f"Failed to extract statistical features: {e}")

        return features

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        return [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]

    def validate_audio_file(self, file_path: str) -> bool:
        """Validate if file is a supported audio format."""

        if not os.path.exists(file_path):
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.get_supported_formats()

    def get_file_info(self, file_path: str) -> dict:
        """Get basic file information without full analysis."""

        if not os.path.exists(file_path):
            return {}

        try:
            # Get duration without loading full audio
            duration = librosa.get_duration(path=file_path)

            return {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "duration": duration,
                "is_valid": self.validate_audio_file(file_path),
            }

        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "duration": 0.0,
                "is_valid": False,
            }
