"""
Metadata generator for processing and enhancing audio analysis data.
"""

import os
import logging
from typing import Dict, Any, Tuple, List
from audio_analyzer import AudioAnalysis
from config import get_classification_thresholds, get_url_mapping
from utils import get_source_directory, list_to_string, get_timestamp


class MetadataGenerator:
    """Process and enhance audio analysis data."""

    def __init__(self):
        """Initialize the metadata generator."""
        self.thresholds = get_classification_thresholds()
        self.url_mapping = get_url_mapping()
        self.logger = logging.getLogger(__name__)

    def enhance_metadata(
        self, analysis: AudioAnalysis, source_dir: str
    ) -> Dict[str, Any]:
        """Enhance audio analysis with classification and additional metadata."""

        # Classify audio type
        audio_type, confidence = self.classify_audio_type(analysis)

        # Generate Google Cloud URL
        google_cloud_url = self.generate_google_cloud_url(analysis.filename, source_dir)

        # Convert lists to strings for CSV storage
        chroma_features_str = list_to_string(analysis.chroma_features)
        mfcc_features_str = list_to_string(analysis.mfcc_features)

        # Create enhanced metadata dictionary
        metadata = {
            "filename": analysis.filename,
            "file_path": analysis.file_path,
            "duration": analysis.duration,
            "sample_rate": analysis.sample_rate,
            "channels": analysis.channels,
            "file_size": analysis.file_size,
            "tempo": analysis.tempo,
            "beat_count": analysis.beat_count,
            "onset_strength": analysis.onset_strength,
            "zero_crossing_rate": analysis.zero_crossing_rate,
            "rms_energy": analysis.rms_energy,
            "spectral_centroid": analysis.spectral_centroid,
            "spectral_bandwidth": analysis.spectral_bandwidth,
            "spectral_rolloff": analysis.spectral_rolloff,
            "spectral_contrast": analysis.spectral_contrast,
            "spectral_flatness": analysis.spectral_flatness,
            "spectral_contrast_mean": analysis.spectral_contrast_mean,
            "spectral_flatness_mean": analysis.spectral_flatness_mean,
            "harmonic_ratio": analysis.harmonic_ratio,
            "chroma_features": chroma_features_str,
            "mfcc_features": mfcc_features_str,
            "dynamic_range": analysis.dynamic_range,
            "loudness": analysis.loudness,
            "peak_amplitude": analysis.peak_amplitude,
            "audio_type": audio_type,
            "confidence": confidence,
            "google_cloud_url": google_cloud_url,
            "source_directory": source_dir,
            "processing_timestamp": get_timestamp(),
        }

        self.logger.info(
            f"Enhanced metadata for {analysis.filename}: {audio_type} (confidence: {confidence:.2f})"
        )
        return metadata

    def classify_audio_type(self, analysis: AudioAnalysis) -> Tuple[str, float]:
        """Classify audio as song, sound effect, or ambiguous using comprehensive analysis."""

        song_score = 0
        effect_score = 0

        # Duration analysis (30 points)
        if analysis.duration > self.thresholds["duration_song"]:
            song_score += 30
        elif analysis.duration < self.thresholds["duration_effect"]:
            effect_score += 30

        # Tempo analysis (25 points)
        if analysis.tempo > self.thresholds["tempo_min"]:
            song_score += 25
        elif analysis.tempo == 0:
            effect_score += 25

        # Beat analysis (20 points)
        if analysis.beat_count > self.thresholds["beat_count_song"]:
            song_score += 20
        elif analysis.beat_count <= 1:
            effect_score += 20

        # Harmonic analysis (15 points)
        if analysis.harmonic_ratio > self.thresholds["harmonic_ratio_song"]:
            song_score += 15
        elif analysis.harmonic_ratio < self.thresholds["harmonic_ratio_effect"]:
            effect_score += 15

        # Spectral analysis (10 points)
        if analysis.spectral_flatness_mean < self.thresholds["spectral_flatness_tonal"]:
            song_score += 10
        elif (
            analysis.spectral_flatness_mean > self.thresholds["spectral_flatness_noisy"]
        ):
            effect_score += 10

        # Determine classification
        total_score = song_score + effect_score
        if total_score == 0:
            return "ambiguous", 0.0

        if song_score > effect_score and song_score >= 50:
            confidence = song_score / total_score
            return "song", confidence
        elif effect_score > song_score and effect_score >= 50:
            confidence = effect_score / total_score
            return "sound_effect", confidence
        else:
            return "ambiguous", 0.5

    def generate_google_cloud_url(self, filename: str, source_dir: str) -> str:
        """Generate Google Cloud Storage URL for audio file."""

        # Map source directory to URL pattern
        if "mixkit" in source_dir.lower():
            url_pattern = self.url_mapping["mixkit"]
        elif "filmcow" in source_dir.lower():
            url_pattern = self.url_mapping["filmcow"]
        else:
            url_pattern = self.url_mapping["google"]

        # Generate URL
        url = url_pattern.format(filename=filename)

        self.logger.debug(f"Generated URL for {filename}: {url}")
        return url

    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata for completeness and correctness."""

        required_fields = [
            "filename",
            "file_path",
            "duration",
            "sample_rate",
            "channels",
            "file_size",
            "audio_type",
            "confidence",
            "google_cloud_url",
            "source_directory",
            "processing_timestamp",
        ]

        # Check required fields
        for field in required_fields:
            if field not in metadata or metadata[field] is None:
                self.logger.error(f"Missing required field: {field}")
                return False

        # Validate numeric fields
        numeric_fields = [
            "duration",
            "sample_rate",
            "channels",
            "file_size",
            "tempo",
            "beat_count",
            "confidence",
        ]

        for field in numeric_fields:
            if field in metadata:
                try:
                    float(metadata[field])
                except (ValueError, TypeError):
                    self.logger.error(
                        f"Invalid numeric value for {field}: {metadata[field]}"
                    )
                    return False

        # Validate audio type
        valid_types = ["song", "sound_effect", "ambiguous"]
        if metadata.get("audio_type") not in valid_types:
            self.logger.error(f"Invalid audio type: {metadata.get('audio_type')}")
            return False

        # Validate confidence range
        confidence = metadata.get("confidence", 0)
        if not (0 <= confidence <= 1):
            self.logger.error(f"Invalid confidence value: {confidence}")
            return False

        return True

    def get_classification_details(self, analysis: AudioAnalysis) -> Dict[str, Any]:
        """Get detailed classification information for debugging."""

        audio_type, confidence = self.classify_audio_type(analysis)

        details = {
            "audio_type": audio_type,
            "confidence": confidence,
            "classification_factors": {
                "duration": {
                    "value": analysis.duration,
                    "threshold_song": self.thresholds["duration_song"],
                    "threshold_effect": self.thresholds["duration_effect"],
                    "score": (
                        "song"
                        if analysis.duration > self.thresholds["duration_song"]
                        else (
                            "effect"
                            if analysis.duration < self.thresholds["duration_effect"]
                            else "neutral"
                        )
                    ),
                },
                "tempo": {
                    "value": analysis.tempo,
                    "threshold_min": self.thresholds["tempo_min"],
                    "score": (
                        "song"
                        if analysis.tempo > self.thresholds["tempo_min"]
                        else "effect" if analysis.tempo == 0 else "neutral"
                    ),
                },
                "beat_count": {
                    "value": analysis.beat_count,
                    "threshold_song": self.thresholds["beat_count_song"],
                    "score": (
                        "song"
                        if analysis.beat_count > self.thresholds["beat_count_song"]
                        else "effect" if analysis.beat_count <= 1 else "neutral"
                    ),
                },
                "harmonic_ratio": {
                    "value": analysis.harmonic_ratio,
                    "threshold_song": self.thresholds["harmonic_ratio_song"],
                    "threshold_effect": self.thresholds["harmonic_ratio_effect"],
                    "score": (
                        "song"
                        if analysis.harmonic_ratio
                        > self.thresholds["harmonic_ratio_song"]
                        else (
                            "effect"
                            if analysis.harmonic_ratio
                            < self.thresholds["harmonic_ratio_effect"]
                            else "neutral"
                        )
                    ),
                },
                "spectral_flatness": {
                    "value": analysis.spectral_flatness_mean,
                    "threshold_tonal": self.thresholds["spectral_flatness_tonal"],
                    "threshold_noisy": self.thresholds["spectral_flatness_noisy"],
                    "score": (
                        "song"
                        if analysis.spectral_flatness_mean
                        < self.thresholds["spectral_flatness_tonal"]
                        else (
                            "effect"
                            if analysis.spectral_flatness_mean
                            > self.thresholds["spectral_flatness_noisy"]
                            else "neutral"
                        )
                    ),
                },
            },
        }

        return details

    def get_metadata_summary(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of metadata for logging."""

        return {
            "filename": metadata.get("filename", ""),
            "duration": metadata.get("duration", 0),
            "audio_type": metadata.get("audio_type", ""),
            "confidence": metadata.get("confidence", 0),
            "source_directory": metadata.get("source_directory", ""),
            "file_size": metadata.get("file_size", 0),
            "tempo": metadata.get("tempo", 0),
            "beat_count": metadata.get("beat_count", 0),
        }
