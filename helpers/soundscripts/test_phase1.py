#!/usr/bin/env python3
"""
Phase 1 Test Runner

This script tests the core infrastructure of the audio helper scripts:
- Configuration loading
- Utility functions
- Audio analyzer (with mocks)
- Metadata generator
- CSV manager
- Directory scanner
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_configuration():
    """Test configuration module."""
    print("🔧 Testing Configuration...")

    from config import (
        ProcessingConfig,
        get_supported_formats,
        get_url_mapping,
        get_csv_headers,
        get_librosa_config,
        get_classification_thresholds,
    )

    # Test ProcessingConfig
    config = ProcessingConfig()
    assert config.batch_size == 10
    assert config.max_retries == 3
    assert "Google Drive" in config.google_drive_path

    # Test getter functions
    formats = get_supported_formats()
    assert ".mp3" in formats
    assert ".wav" in formats

    urls = get_url_mapping()
    assert "google" in urls
    assert "mixkit" in urls

    headers = get_csv_headers()
    assert "filename" in headers
    assert "audio_type" in headers

    librosa_config = get_librosa_config()
    assert "sr" in librosa_config
    assert librosa_config["sr"] == 22050

    thresholds = get_classification_thresholds()
    assert "duration_song" in thresholds
    assert "tempo_min" in thresholds

    print("✅ Configuration tests passed!")


def test_utils():
    """Test utility functions."""
    print("🔧 Testing Utils...")

    from utils import (
        get_file_extension,
        is_audio_file,
        safe_float,
        safe_int,
        list_to_string,
        string_to_list,
        numpy_to_list,
        get_timestamp,
    )

    # Test file utilities
    assert get_file_extension("/path/to/file.mp3") == ".mp3"
    assert is_audio_file("/path/to/file.mp3") == True
    assert is_audio_file("/path/to/file.txt") == False

    # Test safe conversions
    assert safe_float("123.45") == 123.45
    assert safe_float("invalid", 0.0) == 0.0
    assert safe_int("123") == 123
    assert safe_int("invalid", 0) == 0

    # Test list utilities
    test_list = [1, 2, 3]
    assert list_to_string(test_list) == "1|2|3"
    assert string_to_list("1|2|3") == ["1", "2", "3"]

    # Test numpy utilities
    test_array = np.array([1.0, 2.0, 3.0])
    result = numpy_to_list(test_array)
    assert len(result) == 3
    assert result[0] == 1.0

    # Test timestamp
    timestamp = get_timestamp()
    assert len(timestamp) > 0
    assert "T" in timestamp  # ISO format

    print("✅ Utils tests passed!")


def test_audio_analyzer():
    """Test audio analyzer with mocks."""
    print("🔧 Testing Audio Analyzer...")

    from audio_analyzer import AudioAnalyzer, AudioAnalysis

    # Test analyzer initialization
    analyzer = AudioAnalyzer()
    assert analyzer.config is not None
    assert analyzer.logger is not None

    # Test AudioAnalysis creation
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

    assert analysis.filename == "test.wav"
    assert analysis.duration == 1.0
    assert len(analysis.chroma_features) == 12
    assert len(analysis.mfcc_features) == 13

    # Test summary generation
    summary = analyzer.get_analysis_summary(analysis)
    assert "filename" in summary
    assert "duration" in summary
    assert "tempo" in summary

    print("✅ Audio Analyzer tests passed!")


def test_metadata_generator():
    """Test metadata generator."""
    print("🔧 Testing Metadata Generator...")

    from metadata_generator import MetadataGenerator
    from audio_analyzer import AudioAnalysis

    generator = MetadataGenerator()
    assert generator.thresholds is not None
    assert generator.url_mapping is not None

    # Create test analysis
    analysis = AudioAnalysis(
        filename="test.wav",
        file_path="/path/test.wav",
        duration=35.0,  # Long enough to be classified as song
        sample_rate=22050,
        channels=1,
        file_size=44100,
        tempo=120.0,  # Has tempo
        beat_count=10,  # Multiple beats
        onset_strength=0.5,
        zero_crossing_rate=0.1,
        rms_energy=0.3,
        spectral_centroid=2000.0,
        spectral_bandwidth=1000.0,
        spectral_rolloff=4000.0,
        spectral_contrast=0.2,
        spectral_flatness=0.05,  # Low flatness = tonal
        spectral_contrast_mean=0.2,
        spectral_flatness_mean=0.05,
        harmonic_ratio=0.8,  # High harmonic content
        chroma_features=[0.1] * 12,
        mfcc_features=[0.1] * 13,
        dynamic_range=0.8,
        loudness=0.3,
        peak_amplitude=0.9,
        audio_type="",
        confidence=0.0,
    )

    # Test classification
    audio_type, confidence = generator.classify_audio_type(analysis)
    assert audio_type in ["song", "sound_effect", "ambiguous"]
    assert 0 <= confidence <= 1

    # Test URL generation
    url = generator.generate_google_cloud_url("test.wav", "mixkit")
    assert "storage.googleapis.com" in url
    assert "mixkit" in url

    # Test metadata enhancement
    metadata = generator.enhance_metadata(analysis, "mixkit")
    assert metadata["filename"] == "test.wav"
    assert metadata["audio_type"] == audio_type
    assert metadata["confidence"] == confidence
    assert "storage.googleapis.com" in metadata["google_cloud_url"]

    # Test validation
    assert generator.validate_metadata(metadata) == True

    print("✅ Metadata Generator tests passed!")


def test_csv_manager():
    """Test CSV manager."""
    print("🔧 Testing CSV Manager...")

    from csv_manager import CSVManager

    manager = CSVManager()
    assert manager.headers is not None
    assert len(manager.headers) > 0

    # Test CSV creation and operations
    csv_path = tempfile.mktemp(suffix=".csv")

    try:
        # Test initialization
        manager.initialize_csv(csv_path)
        assert os.path.exists(csv_path)

        # Test row appending
        test_row = {
            "filename": "test.wav",
            "file_path": "/path/test.wav",
            "duration": 1.0,
            "sample_rate": 22050,
            "channels": 1,
            "file_size": 44100,
            "tempo": 120.0,
            "beat_count": 4,
            "onset_strength": 0.5,
            "zero_crossing_rate": 0.1,
            "rms_energy": 0.3,
            "spectral_centroid": 2000.0,
            "spectral_bandwidth": 1000.0,
            "spectral_rolloff": 4000.0,
            "spectral_contrast": 0.2,
            "spectral_flatness": 0.1,
            "spectral_contrast_mean": 0.2,
            "spectral_flatness_mean": 0.1,
            "harmonic_ratio": 0.7,
            "chroma_features": "0.1|0.1|0.1",
            "mfcc_features": "0.1|0.1|0.1",
            "dynamic_range": 0.8,
            "loudness": 0.3,
            "peak_amplitude": 0.9,
            "audio_type": "song",
            "confidence": 0.8,
            "google_cloud_url": "https://example.com/test.wav",
            "source_directory": "mixkit",
            "processing_timestamp": "2024-01-01T00:00:00",
        }

        success = manager.append_row_to_csv(csv_path, test_row)
        assert success == True

        # Test processed files retrieval
        processed_files = manager.get_processed_files(csv_path)
        assert "test.wav" in processed_files

        # Test backup
        backup_path = manager.backup_csv(csv_path)
        assert os.path.exists(backup_path)

        # Test validation
        assert manager.validate_csv_structure(csv_path) == True

        # Test statistics
        stats = manager.get_csv_statistics(csv_path)
        assert stats["total_rows"] == 1
        assert stats["audio_types"]["song"] == 1

        # Clean up backup
        if os.path.exists(backup_path):
            os.unlink(backup_path)

    finally:
        # Clean up
        if os.path.exists(csv_path):
            os.unlink(csv_path)

    print("✅ CSV Manager tests passed!")


def test_directory_scanner():
    """Test directory scanner."""
    print("🔧 Testing Directory Scanner...")

    from directory_scanner import DirectoryScanner

    scanner = DirectoryScanner()
    assert scanner.supported_formats is not None
    assert ".mp3" in scanner.supported_formats

    # Test file validation
    assert (
        scanner.validate_audio_file("/path/to/file.mp3") == False
    )  # Non-existent file

    # Test format validation
    assert scanner.get_supported_formats() == scanner.supported_formats

    # Test filtering
    files = ["/path/file1.mp3", "/path/file2.wav", "/path/file3.txt"]
    processed_files = {"file1.mp3"}
    unprocessed = scanner.filter_processed_files(files, processed_files)
    assert (
        len(unprocessed) == 2
    )  # file2.wav and file3.txt (though txt will be filtered out)

    print("✅ Directory Scanner tests passed!")


def main():
    """Run all Phase 1 tests."""
    print("🚀 Starting Phase 1 Tests...")
    print("=" * 50)

    try:
        test_configuration()
        test_utils()
        test_audio_analyzer()
        test_metadata_generator()
        test_csv_manager()
        test_directory_scanner()

        print("=" * 50)
        print("🎉 All Phase 1 tests passed!")
        print("✅ Core infrastructure is working correctly")
        print("✅ Ready to proceed to Phase 2")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
