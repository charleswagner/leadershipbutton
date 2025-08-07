"""
Unit tests for audio analyzer module.
"""

import unittest
import tempfile
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from audio_analyzer import AudioAnalyzer, AudioAnalysis


class TestAudioAnalyzer(unittest.TestCase):
    """Test cases for AudioAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AudioAnalyzer()

        # Create mock audio data
        self.mock_audio_data = np.random.rand(22050)  # 1 second at 22050 Hz
        self.mock_sample_rate = 22050

        # Create mock analysis result
        self.mock_analysis = AudioAnalysis(
            filename="test_audio.wav",
            file_path="/path/to/test_audio.wav",
            duration=1.0,
            sample_rate=22050,
            channels=1,
            file_size=44100,
            tempo=120.0,
            beat_count=4,
            onset_strength=0.5,
            zero_crossing_rate=0.1,
            rms_energy=0.3,
            spectral_centroid=2000.0,
            spectral_bandwidth=1000.0,
            spectral_rolloff=4000.0,
            spectral_contrast=0.2,
            spectral_flatness=0.1,
            spectral_contrast_mean=0.2,
            spectral_flatness_mean=0.1,
            harmonic_ratio=0.7,
            chroma_features=[0.1] * 12,
            mfcc_features=[0.1] * 13,
            dynamic_range=0.8,
            loudness=0.3,
            peak_amplitude=0.9,
            audio_type="",
            confidence=0.0,
        )

    def test_analyzer_initialization(self):
        """Test AudioAnalyzer initialization."""
        # Verify analyzer is created with config
        self.assertIsNotNone(self.analyzer.config)
        self.assertIsNotNone(self.analyzer.logger)
        self.assertIn("sr", self.analyzer.config)
        self.assertIn("hop_length", self.analyzer.config)

    @patch("librosa.load")
    def test_analyze_audio_file_success(self, mock_load):
        """Test successful audio file analysis."""
        # Mock librosa.load to return test data
        mock_load.return_value = (self.mock_audio_data, self.mock_sample_rate)

        # Mock all the feature extraction methods
        with patch.object(
            self.analyzer, "_extract_basic_metadata"
        ) as mock_basic, patch.object(
            self.analyzer, "_extract_temporal_features"
        ) as mock_temporal, patch.object(
            self.analyzer, "_extract_spectral_features"
        ) as mock_spectral, patch.object(
            self.analyzer, "_extract_harmonic_features"
        ) as mock_harmonic, patch.object(
            self.analyzer, "_extract_statistical_features"
        ) as mock_statistical:

            # Set up mock return values
            mock_basic.return_value = {
                "filename": "test.wav",
                "file_path": "/path/test.wav",
                "duration": 1.0,
                "sample_rate": 22050,
                "channels": 1,
                "file_size": 44100,
            }
            mock_temporal.return_value = {
                "tempo": 120.0,
                "beat_count": 4,
                "onset_strength": 0.5,
                "zero_crossing_rate": 0.1,
                "rms_energy": 0.3,
            }
            mock_spectral.return_value = {
                "spectral_centroid": 2000.0,
                "spectral_bandwidth": 1000.0,
                "spectral_rolloff": 4000.0,
                "spectral_contrast": 0.2,
                "spectral_flatness": 0.1,
                "spectral_contrast_mean": 0.2,
                "spectral_flatness_mean": 0.1,
            }
            mock_harmonic.return_value = {
                "harmonic_ratio": 0.7,
                "chroma_features": [0.1] * 12,
                "mfcc_features": [0.1] * 13,
            }
            mock_statistical.return_value = {
                "dynamic_range": 0.8,
                "loudness": 0.3,
                "peak_amplitude": 0.9,
            }

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(b"fake audio data")
                temp_file_path = temp_file.name

            try:
                # Test analysis
                result = self.analyzer.analyze_audio_file(temp_file_path)

                # Verify result is AudioAnalysis object
                self.assertIsInstance(result, AudioAnalysis)
                self.assertEqual(result.filename, "test.wav")
                self.assertEqual(result.duration, 1.0)
                self.assertEqual(result.tempo, 120.0)

                # Verify all methods were called
                mock_basic.assert_called_once()
                mock_temporal.assert_called_once()
                mock_spectral.assert_called_once()
                mock_harmonic.assert_called_once()
                mock_statistical.assert_called_once()

            finally:
                # Clean up
                os.unlink(temp_file_path)

    def test_analyze_audio_file_not_found(self):
        """Test audio file analysis with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.analyzer.analyze_audio_file("/nonexistent/file.wav")

    @patch("librosa.load")
    def test_analyze_audio_file_load_error(self, mock_load):
        """Test audio file analysis with load error."""
        # Mock librosa.load to raise exception
        mock_load.side_effect = Exception("Load error")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(RuntimeError):
                self.analyzer.analyze_audio_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_extract_basic_metadata(self):
        """Test basic metadata extraction."""
        result = self.analyzer._extract_basic_metadata(
            "/path/to/test.wav", self.mock_audio_data, self.mock_sample_rate
        )

        # Verify basic metadata
        self.assertEqual(result["filename"], "test.wav")
        self.assertEqual(result["sample_rate"], 22050)
        self.assertEqual(result["channels"], 1)
        self.assertIn("duration", result)
        self.assertIn("file_size", result)

    @patch("librosa.beat.beat_track")
    @patch("librosa.onset.onset_strength")
    @patch("librosa.feature.zero_crossing_rate")
    @patch("librosa.feature.rms")
    def test_extract_temporal_features_success(
        self, mock_rms, mock_zcr, mock_onset, mock_beat
    ):
        """Test successful temporal feature extraction."""
        # Mock return values
        mock_beat.return_value = (120.0, np.array([0, 0.5, 1.0, 1.5]))
        mock_onset.return_value = np.array([0.5, 0.6, 0.4, 0.7])
        mock_zcr.return_value = np.array([[0.1, 0.2, 0.1, 0.3]])
        mock_rms.return_value = np.array([[0.3, 0.4, 0.2, 0.5]])

        result = self.analyzer._extract_temporal_features(
            self.mock_audio_data, self.mock_sample_rate
        )

        # Verify temporal features
        self.assertEqual(result["tempo"], 120.0)
        self.assertEqual(result["beat_count"], 4)
        self.assertIn("onset_strength", result)
        self.assertIn("zero_crossing_rate", result)
        self.assertIn("rms_energy", result)

    @patch("librosa.beat.beat_track")
    def test_extract_temporal_features_error(self, mock_beat):
        """Test temporal feature extraction with error."""
        # Mock to raise exception
        mock_beat.side_effect = Exception("Beat detection error")

        result = self.analyzer._extract_temporal_features(
            self.mock_audio_data, self.mock_sample_rate
        )

        # Verify default values are returned
        self.assertEqual(result["tempo"], 0.0)
        self.assertEqual(result["beat_count"], 0)
        self.assertEqual(result["onset_strength"], 0.0)
        self.assertEqual(result["zero_crossing_rate"], 0.0)
        self.assertEqual(result["rms_energy"], 0.0)

    def test_get_analysis_summary(self):
        """Test analysis summary generation."""
        summary = self.analyzer.get_analysis_summary(self.mock_analysis)

        # Verify summary contains key fields
        expected_fields = [
            "filename",
            "duration",
            "tempo",
            "beat_count",
            "harmonic_ratio",
            "spectral_flatness",
            "file_size",
        ]
        for field in expected_fields:
            self.assertIn(field, summary)

        # Verify values match
        self.assertEqual(summary["filename"], "test_audio.wav")
        self.assertEqual(summary["duration"], 1.0)
        self.assertEqual(summary["tempo"], 120.0)


class TestAudioAnalysis(unittest.TestCase):
    """Test cases for AudioAnalysis dataclass."""

    def test_audio_analysis_creation(self):
        """Test AudioAnalysis object creation."""
        analysis = AudioAnalysis(
            filename="test.wav",
            file_path="/path/test.wav",
            duration=1.0,
            sample_rate=22050,
            channels=1,
            file_size=44100,
            tempo=120.0,
            beat_count=4,
            onset_strength=0.5,
            zero_crossing_rate=0.1,
            rms_energy=0.3,
            spectral_centroid=2000.0,
            spectral_bandwidth=1000.0,
            spectral_rolloff=4000.0,
            spectral_contrast=0.2,
            spectral_flatness=0.1,
            spectral_contrast_mean=0.2,
            spectral_flatness_mean=0.1,
            harmonic_ratio=0.7,
            chroma_features=[0.1] * 12,
            mfcc_features=[0.1] * 13,
            dynamic_range=0.8,
            loudness=0.3,
            peak_amplitude=0.9,
            audio_type="",
            confidence=0.0,
        )

        # Verify all fields are set correctly
        self.assertEqual(analysis.filename, "test.wav")
        self.assertEqual(analysis.duration, 1.0)
        self.assertEqual(analysis.tempo, 120.0)
        self.assertEqual(len(analysis.chroma_features), 12)
        self.assertEqual(len(analysis.mfcc_features), 13)


if __name__ == "__main__":
    unittest.main()
