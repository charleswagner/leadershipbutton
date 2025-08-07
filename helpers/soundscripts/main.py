#!/usr/bin/env python3
"""
Main orchestrator for audio helper scripts.

This script coordinates all components to process audio files from multiple directories,
extract comprehensive metadata, and generate a CSV database for the leadership button application.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any
from datetime import datetime

# Import our modules
from config import ProcessingConfig
from utils import setup_logging, chunk_list, get_timestamp
from audio_analyzer import AudioAnalyzer
from metadata_generator import MetadataGenerator
from csv_manager import CSVManager
from directory_scanner import DirectoryScanner
from url_generator import URLGenerator
from kit_processor import KitProcessor


class AudioProcessor:
    """Main orchestrator for audio processing workflow."""

    def __init__(self, config: ProcessingConfig):
        """Initialize the audio processor."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.analyzer = AudioAnalyzer()
        self.metadata_generator = MetadataGenerator()
        self.csv_manager = CSVManager()
        self.directory_scanner = DirectoryScanner()
        self.url_generator = URLGenerator()
        self.kit_processor = KitProcessor()

        # Processing statistics
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "start_time": None,
            "end_time": None,
        }

    def run(self) -> bool:
        """Run the complete audio processing workflow."""

        self.stats["start_time"] = get_timestamp()
        self.logger.info("🚀 Starting audio processing workflow")

        try:
            # Step 1: Initialize CSV file
            self.logger.info("📊 Initializing CSV file")
            self.csv_manager.initialize_csv(self.config.csv_output_path)

            # Step 2: Get already processed files
            self.logger.info("📋 Checking for already processed files")
            processed_files = self.csv_manager.get_processed_files(
                self.config.csv_output_path
            )
            self.logger.info(f"Found {len(processed_files)} already processed files")

            # Step 3: Scan directories for audio files
            self.logger.info("📂 Scanning directories for audio files")
            all_files = self._scan_directories()
            self.stats["total_files"] = len(all_files)

            # Step 4: Filter out already processed files
            unprocessed_files = self.directory_scanner.filter_processed_files(
                all_files, processed_files
            )
            self.logger.info(f"Found {len(unprocessed_files)} unprocessed files")

            if not unprocessed_files:
                self.logger.info("✅ No new files to process")
                return True

            # Step 5: Process files in batches
            self.logger.info(
                f"🔄 Processing {len(unprocessed_files)} files in batches of {self.config.batch_size}"
            )
            self._process_files_in_batches(unprocessed_files)

            # Step 6: Process kit.txt metadata if available
            if os.path.exists(self.config.kit_file_path):
                self.logger.info("📝 Processing kit.txt metadata")
                self.kit_processor.merge_kit_metadata(
                    self.config.csv_output_path, self.config.kit_file_path
                )

            # Step 7: Generate final statistics
            self.stats["end_time"] = get_timestamp()
            self._log_final_statistics()

            self.logger.info("🎉 Audio processing workflow completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Audio processing workflow failed: {e}")
            return False

    def _scan_directories(self) -> List[str]:
        """Scan all configured directories for audio files."""

        directories = [
            self.config.google_drive_path,
            self.config.mixkit_path,
            self.config.filmcow_path,
        ]

        all_files = []
        for directory in directories:
            if os.path.exists(directory):
                files = self.directory_scanner.scan_directory(directory)
                self.logger.info(f"Found {len(files)} files in {directory}")
                all_files.extend(files)
            else:
                self.logger.warning(f"Directory does not exist: {directory}")

        return all_files

    def _process_files_in_batches(self, files: List[str]) -> None:
        """Process files in batches with error recovery."""

        batches = chunk_list(files, self.config.batch_size)

        for batch_num, batch in enumerate(batches, 1):
            self.logger.info(
                f"📦 Processing batch {batch_num}/{len(batches)} ({len(batch)} files)"
            )

            try:
                self._process_batch(batch)

                # Create backup after each batch
                if (
                    batch_num % (self.config.backup_interval // self.config.batch_size)
                    == 0
                ):
                    self.csv_manager.backup_csv(self.config.csv_output_path)
                    self.logger.info("💾 Created CSV backup")

            except Exception as e:
                self.logger.error(f"❌ Batch {batch_num} failed: {e}")
                # Continue with next batch
                continue

    def _process_batch(self, files: List[str]) -> None:
        """Process a single batch of files."""

        for file_path in files:
            try:
                self._process_single_file(file_path)
                self.stats["processed_files"] += 1

            except Exception as e:
                self.logger.error(f"❌ Failed to process {file_path}: {e}")
                self.stats["failed_files"] += 1
                # Continue with next file
                continue

    def _process_single_file(self, file_path: str) -> None:
        """Process a single audio file."""

        filename = os.path.basename(file_path)
        self.logger.debug(f"🎵 Processing: {filename}")

        # Step 1: Analyze audio file
        analysis = self.analyzer.analyze_audio_file(file_path)

        # Step 2: Get source directory
        source_dir = self._get_source_directory(file_path)

        # Step 3: Generate enhanced metadata
        metadata = self.metadata_generator.enhance_metadata(analysis, source_dir)

        # Step 4: Validate metadata
        if not self.metadata_generator.validate_metadata(metadata):
            self.logger.warning(f"⚠️ Invalid metadata for {filename}")
            self.stats["skipped_files"] += 1
            return

        # Step 5: Append to CSV
        success = self.csv_manager.append_row_to_csv(
            self.config.csv_output_path, metadata
        )
        if not success:
            raise Exception(f"Failed to write metadata to CSV for {filename}")

        self.logger.debug(
            f"✅ Processed: {filename} ({metadata['audio_type']}, confidence: {metadata['confidence']:.2f})"
        )

    def _get_source_directory(self, file_path: str) -> str:
        """Determine source directory from file path."""

        # Extract the directory name that contains the file
        dir_path = os.path.dirname(file_path)

        # Map to our known directory types
        if "mixkit" in dir_path.lower():
            return "mixkit"
        elif "filmcow" in dir_path.lower():
            return "filmcow"
        else:
            return "google"

    def _log_final_statistics(self) -> None:
        """Log final processing statistics."""

        duration = "unknown"
        if self.stats["start_time"] and self.stats["end_time"]:
            try:
                start = datetime.fromisoformat(
                    self.stats["start_time"].replace("Z", "+00:00")
                )
                end = datetime.fromisoformat(
                    self.stats["end_time"].replace("Z", "+00:00")
                )
                duration = str(end - start)
            except Exception:
                pass

        self.logger.info("📊 Final Processing Statistics:")
        self.logger.info(f"   Total files found: {self.stats['total_files']}")
        self.logger.info(f"   Files processed: {self.stats['processed_files']}")
        self.logger.info(f"   Files failed: {self.stats['failed_files']}")
        self.logger.info(f"   Files skipped: {self.stats['skipped_files']}")
        self.logger.info(f"   Processing time: {duration}")

        # Get CSV statistics
        csv_stats = self.csv_manager.get_csv_statistics(self.config.csv_output_path)
        if "error" not in csv_stats:
            self.logger.info(f"   CSV total rows: {csv_stats['total_rows']}")
            self.logger.info(f"   Audio types: {csv_stats['audio_types']}")
            self.logger.info(
                f"   Source directories: {csv_stats['source_directories']}"
            )


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""

    parser = argparse.ArgumentParser(
        description="Audio Helper Scripts - Process audio files and generate metadata CSV"
    )

    parser.add_argument("--config", type=str, help="Path to configuration file (JSON)")

    parser.add_argument("--output", type=str, help="Output CSV file path")

    parser.add_argument(
        "--directories", type=str, help="Comma-separated list of directories to process"
    )

    parser.add_argument("--batch-size", type=int, help="Batch size for processing")

    parser.add_argument(
        "--test-mode", action="store_true", help="Run in test mode with limited files"
    )

    parser.add_argument(
        "--resume", action="store_true", help="Resume processing from where it left off"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser


def main():
    """Main entry point."""

    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Create configuration
    config = ProcessingConfig()

    # Override config with command line arguments
    if args.output:
        config.csv_output_path = args.output
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.test_mode:
        config.test_mode = True
        config.test_sample_size = 5

    # Create and run processor
    processor = AudioProcessor(config)
    success = processor.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
