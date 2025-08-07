"""
Configuration and constants for audio helper scripts.
"""

import os
from dataclasses import dataclass
from typing import List


@dataclass
class ProcessingConfig:
    """Configuration for audio processing."""

    # Source directories
    google_drive_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds"
    mixkit_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds/mixkit"
    filmcow_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds/filmcow"

    # Output
    csv_output_path: str = "data/soundlibrary.csv"
    kit_file_path: str = (
        "/Users/cwagner/Google Drive/My Drive/public/sounds/mixkit/kit.txt"
    )

    # Processing options
    batch_size: int = 10
    max_retries: int = 3
    backup_interval: int = 50

    # Test mode
    test_mode: bool = False
    test_sample_size: int = 5


# Supported audio formats
SUPPORTED_FORMATS = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]

# URL mapping for Google Cloud Storage
URL_MAPPING = {
    "google": "https://storage.googleapis.com/cwsounds/google/{filename}",
    "mixkit": "https://storage.googleapis.com/cwsounds/mixkit/{filename}",
    "filmcow": "https://storage.googleapis.com/cwsounds/filmcow/{filename}",
}

# CSV headers
CSV_HEADERS = [
    "filename",
    "file_path",
    "duration",
    "sample_rate",
    "channels",
    "file_size",
    "tempo",
    "beat_count",
    "onset_strength",
    "zero_crossing_rate",
    "rms_energy",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "spectral_contrast",
    "spectral_flatness",
    "spectral_contrast_mean",
    "spectral_flatness_mean",
    "harmonic_ratio",
    "chroma_features",
    "mfcc_features",
    "dynamic_range",
    "loudness",
    "peak_amplitude",
    "audio_type",
    "confidence",
    "google_cloud_url",
    "source_directory",
    "processing_timestamp",
]

# Librosa analysis parameters
LIBROSA_CONFIG = {
    "sr": 22050,  # Sample rate for analysis
    "hop_length": 512,
    "n_fft": 2048,
    "n_mfcc": 13,
    "n_chroma": 12,
}

# Classification thresholds
CLASSIFICATION_THRESHOLDS = {
    "duration_song": 30.0,  # Files longer than 30s are likely songs
    "duration_effect": 10.0,  # Files shorter than 10s are likely effects
    "tempo_min": 60.0,  # Minimum tempo to be considered musical
    "beat_count_song": 5,  # Minimum beats for song classification
    "harmonic_ratio_song": 0.6,  # High harmonic content = song
    "harmonic_ratio_effect": 0.3,  # Low harmonic content = effect
    "spectral_flatness_tonal": 0.1,  # Low flatness = tonal (song)
    "spectral_flatness_noisy": 0.3,  # High flatness = noisy (effect)
}


def get_supported_formats() -> List[str]:
    """Get list of supported audio formats."""
    return SUPPORTED_FORMATS.copy()


def get_url_mapping() -> dict:
    """Get URL mapping for Google Cloud Storage."""
    return URL_MAPPING.copy()


def get_csv_headers() -> List[str]:
    """Get CSV headers for output file."""
    return CSV_HEADERS.copy()


def get_librosa_config() -> dict:
    """Get Librosa analysis configuration."""
    return LIBROSA_CONFIG.copy()


def get_classification_thresholds() -> dict:
    """Get classification thresholds."""
    return CLASSIFICATION_THRESHOLDS.copy()
