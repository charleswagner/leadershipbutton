#!/usr/bin/env python3
"""
Phase 2 Test Runner

This script tests the complete audio helper scripts system integration:
- URL generation and validation
- Kit.txt processing
- Main orchestrator workflow
- Complete end-to-end processing
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_url_generator():
    """Test URL generator functionality."""
    print("🔧 Testing URL Generator...")

    from url_generator import URLGenerator

    generator = URLGenerator()
    assert generator.url_mapping is not None

    # Test URL generation
    url1 = generator.generate_google_cloud_url("test.mp3", "mixkit")
    assert "storage.googleapis.com" in url1
    assert "mixkit" in url1
    assert "test.mp3" in url1

    url2 = generator.generate_google_cloud_url("test.wav", "filmcow")
    assert "filmcow" in url2

    url3 = generator.generate_google_cloud_url("test.ogg", "google")
    assert "google" in url3

    # Test URL validation
    assert generator.validate_url(url1) == True
    assert generator.validate_url("invalid_url") == False
    assert generator.validate_url("") == False

    # Test batch URL generation
    filenames = ["file1.mp3", "file2.wav", "file3.ogg"]
    urls = generator.generate_batch_urls(filenames, "mixkit")
    assert len(urls) == 3
    assert all("mixkit" in url for url in urls)

    # Test URL statistics
    stats = generator.get_url_statistics(urls)
    assert stats["total_urls"] == 3
    assert stats["valid_urls"] == 3

    print("✅ URL Generator tests passed!")


def test_kit_processor():
    """Test kit.txt processor functionality."""
    print("🔧 Testing Kit Processor...")

    from kit_processor import KitProcessor

    processor = KitProcessor()

    # Create test kit.txt content
    test_kit_content = """# Test kit file
test_song.mp3|Beautiful Song|Music|3:45|happy,upbeat|A beautiful uplifting song
test_effect.wav|Door Slam|Sound Effect|2.3|impact,door|A door slamming sound
test_ambient.ogg|Wind|Ambient|15:30|nature,wind|Gentle wind sounds
"""

    # Create temporary kit file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as temp_file:
        temp_file.write(test_kit_content)
        kit_path = temp_file.name

    try:
        # Test parsing
        kit_data = processor.parse_kit_file(kit_path)
        assert len(kit_data) == 3

        # Test entry validation
        for entry in kit_data:
            assert processor.validate_kit_entry(entry) == True
            assert "filename" in entry
            assert "title" in entry
            assert "category" in entry
            assert "duration" in entry

        # Test duration parsing
        song_entry = next(e for e in kit_data if e["filename"] == "test_song.mp3")
        assert song_entry["duration"] == 225.0  # 3:45 = 225 seconds

        effect_entry = next(e for e in kit_data if e["filename"] == "test_effect.wav")
        assert effect_entry["duration"] == 2.3

        # Test statistics
        stats = processor.get_kit_statistics(kit_path)
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 3
        assert "Music" in stats["categories"]
        assert "Sound Effect" in stats["categories"]

        print("✅ Kit Processor tests passed!")

    finally:
        # Clean up
        if os.path.exists(kit_path):
            os.unlink(kit_path)


def test_main_orchestrator():
    """Test main orchestrator functionality."""
    print("🔧 Testing Main Orchestrator...")

    from main import AudioProcessor
    from config import ProcessingConfig

    # Create test configuration
    config = ProcessingConfig()
    config.test_mode = True
    config.test_sample_size = 2
    config.batch_size = 1

    # Create temporary output path
    csv_path = tempfile.mktemp(suffix=".csv")
    config.csv_output_path = csv_path

    try:
        # Test processor initialization
        processor = AudioProcessor(config)
        assert processor.config == config
        assert processor.analyzer is not None
        assert processor.metadata_generator is not None
        assert processor.csv_manager is not None
        assert processor.directory_scanner is not None
        assert processor.url_generator is not None
        assert processor.kit_processor is not None

        # Test statistics initialization
        assert processor.stats["total_files"] == 0
        assert processor.stats["processed_files"] == 0
        assert processor.stats["failed_files"] == 0

        print("✅ Main Orchestrator tests passed!")

    finally:
        # Clean up
        if os.path.exists(csv_path):
            os.unlink(csv_path)


def test_integration():
    """Test integration between components."""
    print("🔧 Testing Integration...")

    from audio_analyzer import AudioAnalyzer, AudioAnalysis
    from metadata_generator import MetadataGenerator
    from csv_manager import CSVManager
    from url_generator import URLGenerator

    # Create components
    analyzer = AudioAnalyzer()
    metadata_gen = MetadataGenerator()
    csv_manager = CSVManager()
    url_gen = URLGenerator()

    # Create test analysis
    analysis = AudioAnalysis(
        filename="test_integration.wav",
        file_path="/path/test_integration.wav",
        duration=35.0,
        sample_rate=22050,
        channels=1,
        file_size=44100,
        tempo=120.0,
        beat_count=10,
        onset_strength=0.5,
        zero_crossing_rate=0.1,
        rms_energy=0.3,
        spectral_centroid=2000.0,
        spectral_bandwidth=1000.0,
        spectral_rolloff=4000.0,
        spectral_contrast=0.2,
        spectral_flatness=0.05,
        spectral_contrast_mean=0.2,
        spectral_flatness_mean=0.05,
        harmonic_ratio=0.8,
        chroma_features=[0.1] * 12,
        mfcc_features=[0.1] * 13,
        dynamic_range=0.8,
        loudness=0.3,
        peak_amplitude=0.9,
        audio_type="",
        confidence=0.0,
    )

    # Test metadata generation
    metadata = metadata_gen.enhance_metadata(analysis, "mixkit")
    assert metadata["filename"] == "test_integration.wav"
    assert metadata["audio_type"] in ["song", "sound_effect", "ambiguous"]
    assert metadata["confidence"] > 0

    # Test URL generation
    url = url_gen.generate_google_cloud_url(metadata["filename"], "mixkit")
    assert "storage.googleapis.com" in url
    assert "mixkit" in url

    # Test CSV operations
    csv_path = tempfile.mktemp(suffix=".csv")
    try:
        csv_manager.initialize_csv(csv_path)
        success = csv_manager.append_row_to_csv(csv_path, metadata)
        assert success == True

        # Verify file was written
        processed_files = csv_manager.get_processed_files(csv_path)
        assert "test_integration.wav" in processed_files

        # Test statistics
        stats = csv_manager.get_csv_statistics(csv_path)
        assert stats["total_rows"] == 1
        assert metadata["audio_type"] in stats["audio_types"]

    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)

    print("✅ Integration tests passed!")


def test_command_line_interface():
    """Test command line interface."""
    print("🔧 Testing Command Line Interface...")

    from main import create_parser

    parser = create_parser()

    # Test help
    help_output = parser.format_help()
    assert "Audio Helper Scripts" in help_output
    assert "--test-mode" in help_output
    assert "--verbose" in help_output

    # Test argument parsing
    args = parser.parse_args(["--test-mode", "--verbose", "--batch-size", "5"])
    assert args.test_mode == True
    assert args.verbose == True
    assert args.batch_size == 5

    print("✅ Command Line Interface tests passed!")


def main():
    """Run all Phase 2 tests."""
    print("🚀 Starting Phase 2 Tests...")
    print("=" * 50)

    try:
        test_url_generator()
        test_kit_processor()
        test_main_orchestrator()
        test_integration()
        test_command_line_interface()

        print("=" * 50)
        print("🎉 All Phase 2 tests passed!")
        print("✅ Complete system integration is working correctly")
        print("✅ Ready for Phase 3: Kit.txt Integration")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
