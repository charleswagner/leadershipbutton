#!/usr/bin/env python3
"""
Standalone Audio Analyzer Runner

This script allows you to run the audio analyzer on individual audio files
to see the comprehensive metadata extraction in action.
"""

import sys
import os
import argparse
from pprint import pprint

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from audio_analyzer import AudioAnalyzer
from utils import setup_logging


def analyze_single_file(file_path: str, verbose: bool = False) -> None:
    """Analyze a single audio file and display results."""

    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return

    # Set up logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    print(f"🎵 Analyzing audio file: {os.path.basename(file_path)}")
    print("=" * 60)

    try:
        # Create analyzer and analyze file
        analyzer = AudioAnalyzer()
        analysis = analyzer.analyze_audio_file(file_path)

        # Display basic info
        print("📊 Basic Information:")
        print(f"   Filename: {analysis.filename}")
        print(f"   Duration: {analysis.duration:.2f} seconds")
        print(f"   Sample Rate: {analysis.sample_rate} Hz")
        print(f"   Channels: {analysis.channels}")
        print(f"   File Size: {analysis.file_size} bytes")
        print()

        # Display temporal features
        print("⏱️ Temporal Features:")
        print(f"   Tempo: {analysis.tempo:.2f} BPM")
        print(f"   Beat Count: {analysis.beat_count}")
        print(f"   Onset Strength: {analysis.onset_strength:.4f}")
        print(f"   Zero Crossing Rate: {analysis.zero_crossing_rate:.4f}")
        print(f"   RMS Energy: {analysis.rms_energy:.4f}")
        print()

        # Display spectral features
        print("🌈 Spectral Features:")
        print(f"   Spectral Centroid: {analysis.spectral_centroid:.2f} Hz")
        print(f"   Spectral Bandwidth: {analysis.spectral_bandwidth:.2f} Hz")
        print(f"   Spectral Rolloff: {analysis.spectral_rolloff:.2f} Hz")
        print(f"   Spectral Contrast: {analysis.spectral_contrast:.4f}")
        print(f"   Spectral Flatness: {analysis.spectral_flatness:.4f}")
        print(f"   Spectral Contrast Mean: {analysis.spectral_contrast_mean:.4f}")
        print(f"   Spectral Flatness Mean: {analysis.spectral_flatness_mean:.4f}")
        print()

        # Display harmonic features
        print("🎼 Harmonic Features:")
        print(f"   Harmonic Ratio: {analysis.harmonic_ratio:.4f}")
        print(f"   Chroma Features: {len(analysis.chroma_features)} dimensions")
        print(f"   MFCC Features: {len(analysis.mfcc_features)} dimensions")
        print()

        # Display statistical features
        print("📈 Statistical Features:")
        print(f"   Dynamic Range: {analysis.dynamic_range:.4f}")
        print(f"   Loudness: {analysis.loudness:.4f}")
        print(f"   Peak Amplitude: {analysis.peak_amplitude:.4f}")
        print()

        # Display classification if available
        if analysis.audio_type:
            print("🏷️ Classification:")
            print(f"   Audio Type: {analysis.audio_type}")
            print(f"   Confidence: {analysis.confidence:.4f}")
            print()

        # Display detailed features in verbose mode
        if verbose:
            print("🔍 Detailed Features:")
            print(
                f"   Chroma Features: {[f'{x:.3f}' for x in analysis.chroma_features[:5]]}... (12 total)"
            )
            print(
                f"   MFCC Features: {[f'{x:.3f}' for x in analysis.mfcc_features[:5]]}... (13 total)"
            )
            print()

        print("✅ Analysis completed successfully!")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()


def find_sample_audio_files() -> list:
    """Find sample audio files in common locations."""

    possible_locations = [
        "/Users/cwagner/Google Drive/My Drive/public/sounds",
        "/Users/cwagner/Google Drive/My Drive/public/sounds/mixkit",
        "/Users/cwagner/Google Drive/My Drive/public/sounds/filmcow",
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Music"),
        ".",
    ]

    audio_extensions = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]
    found_files = []

    for location in possible_locations:
        if os.path.exists(location):
            try:
                for file in os.listdir(location):
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        found_files.append(os.path.join(location, file))
                        if len(found_files) >= 5:  # Limit to first 5 files
                            break
            except PermissionError:
                continue

        if len(found_files) >= 5:
            break

    return found_files


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Standalone Audio Analyzer - Test audio analysis on individual files"
    )

    parser.add_argument("file_path", nargs="?", help="Path to audio file to analyze")

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed features",
    )

    parser.add_argument(
        "--find-samples", action="store_true", help="Find and list sample audio files"
    )

    args = parser.parse_args()

    if args.find_samples:
        print("🔍 Looking for sample audio files...")
        sample_files = find_sample_audio_files()

        if sample_files:
            print(f"📁 Found {len(sample_files)} sample audio files:")
            for i, file_path in enumerate(sample_files, 1):
                print(f"   {i}. {file_path}")
            print()
            print("💡 To analyze a file, run:")
            print(f'   python3 run_audio_analyzer.py "{sample_files[0]}"')
        else:
            print("❌ No sample audio files found in common locations")
        return

    if not args.file_path:
        print("❌ Please provide a file path to analyze")
        print("💡 Usage examples:")
        print("   python3 run_audio_analyzer.py /path/to/audio/file.mp3")
        print("   python3 run_audio_analyzer.py --find-samples")
        print("   python3 run_audio_analyzer.py --help")
        return

    # Analyze the specified file
    analyze_single_file(args.file_path, args.verbose)


if __name__ == "__main__":
    main()
