"""
CSV file operations and management with error recovery.
"""

import os
import csv
import logging
import shutil
from typing import List, Dict, Any, Set
from config import get_csv_headers
from utils import ensure_directory_exists, create_backup_filename, get_timestamp


class CSVManager:
    """Manage CSV file operations with error recovery."""

    def __init__(self):
        """Initialize the CSV manager."""
        self.headers = get_csv_headers()
        self.logger = logging.getLogger(__name__)

    def initialize_csv(self, output_path: str) -> None:
        """Initialize CSV file with headers if it doesn't exist."""

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_directory_exists(output_dir)

        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(output_path):
            self.logger.info(f"Creating new CSV file: {output_path}")
            self._write_headers(output_path)
        else:
            self.logger.info(f"CSV file already exists: {output_path}")

    def _write_headers(self, output_path: str) -> None:
        """Write headers to CSV file."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writeheader()
            self.logger.debug(f"Headers written to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to write headers to {output_path}: {e}")
            raise

    def append_row_to_csv(self, output_path: str, row_data: Dict[str, Any]) -> bool:
        """Append a single row to CSV file."""

        try:
            # Ensure all required fields are present
            complete_row = self._prepare_row_data(row_data)

            # Append row to CSV
            with open(output_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writerow(complete_row)

            self.logger.debug(
                f"Row appended to {output_path}: {row_data.get('filename', 'unknown')}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to append row to {output_path}: {e}")
            return False

    def _prepare_row_data(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare row data ensuring all headers are present."""

        # Create complete row with all headers
        complete_row = {}
        for header in self.headers:
            complete_row[header] = row_data.get(header, "")

        return complete_row

    def get_processed_files(self, csv_path: str) -> Set[str]:
        """Get set of already processed filenames from CSV."""

        processed_files = set()

        if not os.path.exists(csv_path):
            self.logger.info(f"CSV file does not exist: {csv_path}")
            return processed_files

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    filename = row.get("filename", "")
                    if filename:
                        processed_files.add(filename)

            self.logger.info(f"Found {len(processed_files)} already processed files")
            return processed_files

        except Exception as e:
            self.logger.error(f"Failed to read processed files from {csv_path}: {e}")
            return set()

    def backup_csv(self, csv_path: str) -> str:
        """Create a backup of the CSV file."""

        if not os.path.exists(csv_path):
            self.logger.warning(f"Cannot backup non-existent file: {csv_path}")
            return ""

        try:
            backup_path = create_backup_filename(csv_path)
            shutil.copy2(csv_path, backup_path)
            self.logger.info(f"CSV backup created: {backup_path}")
            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to create CSV backup: {e}")
            return ""

    def resume_processing(self, csv_path: str, source_dirs: List[str]) -> List[str]:
        """Get list of unprocessed files for resume functionality."""

        from directory_scanner import DirectoryScanner

        # Get already processed files
        processed_files = self.get_processed_files(csv_path)

        # Get all files from source directories
        scanner = DirectoryScanner()
        all_files = []

        for directory in source_dirs:
            if os.path.exists(directory):
                files = scanner.scan_directory(directory)
                all_files.extend(files)
            else:
                self.logger.warning(f"Source directory does not exist: {directory}")

        # Filter out already processed files
        unprocessed_files = []
        for file_path in all_files:
            filename = os.path.basename(file_path)
            if filename not in processed_files:
                unprocessed_files.append(file_path)

        self.logger.info(
            f"Found {len(unprocessed_files)} unprocessed files out of {len(all_files)} total"
        )
        return unprocessed_files

    def validate_csv_structure(self, csv_path: str) -> bool:
        """Validate that CSV file has correct structure."""

        if not os.path.exists(csv_path):
            self.logger.error(f"CSV file does not exist: {csv_path}")
            return False

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Check if all required headers are present
                actual_headers = set(reader.fieldnames or [])
                required_headers = set(self.headers)

                missing_headers = required_headers - actual_headers
                if missing_headers:
                    self.logger.error(f"Missing headers in CSV: {missing_headers}")
                    return False

                # Count rows
                row_count = sum(1 for row in reader)
                self.logger.info(
                    f"CSV validation passed: {row_count} rows, {len(actual_headers)} headers"
                )
                return True

        except Exception as e:
            self.logger.error(f"CSV validation failed: {e}")
            return False

    def get_csv_statistics(self, csv_path: str) -> Dict[str, Any]:
        """Get statistics about the CSV file."""

        if not os.path.exists(csv_path):
            return {"error": "File does not exist"}

        try:
            stats = {
                "total_rows": 0,
                "audio_types": {},
                "source_directories": {},
                "file_size_total": 0,
                "duration_total": 0.0,
                "processing_timestamps": [],
            }

            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    stats["total_rows"] += 1

                    # Count audio types
                    audio_type = row.get("audio_type", "unknown")
                    stats["audio_types"][audio_type] = (
                        stats["audio_types"].get(audio_type, 0) + 1
                    )

                    # Count source directories
                    source_dir = row.get("source_directory", "unknown")
                    stats["source_directories"][source_dir] = (
                        stats["source_directories"].get(source_dir, 0) + 1
                    )

                    # Sum file sizes
                    file_size = int(row.get("file_size", 0))
                    stats["file_size_total"] += file_size

                    # Sum durations
                    duration = float(row.get("duration", 0))
                    stats["duration_total"] += duration

                    # Collect timestamps
                    timestamp = row.get("processing_timestamp", "")
                    if timestamp:
                        stats["processing_timestamps"].append(timestamp)

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get CSV statistics: {e}")
            return {"error": str(e)}

    def export_filtered_csv(
        self, input_path: str, output_path: str, filters: Dict[str, Any]
    ) -> bool:
        """Export filtered CSV based on criteria."""

        if not os.path.exists(input_path):
            self.logger.error(f"Input CSV does not exist: {input_path}")
            return False

        try:
            with open(input_path, "r", newline="", encoding="utf-8") as infile:
                reader = csv.DictReader(infile)

                with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=self.headers)
                    writer.writeheader()

                    for row in reader:
                        if self._row_matches_filters(row, filters):
                            writer.writerow(row)

            self.logger.info(f"Filtered CSV exported to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export filtered CSV: {e}")
            return False

    def _row_matches_filters(
        self, row: Dict[str, Any], filters: Dict[str, Any]
    ) -> bool:
        """Check if row matches filter criteria."""

        for field, value in filters.items():
            if field not in row:
                continue

            row_value = row[field]

            # Handle different filter types
            if isinstance(value, dict):
                # Range filter: {'min': 10, 'max': 100}
                if "min" in value and float(row_value) < value["min"]:
                    return False
                if "max" in value and float(row_value) > value["max"]:
                    return False
            elif isinstance(value, list):
                # List filter: ['song', 'sound_effect']
                if row_value not in value:
                    return False
            else:
                # Exact match filter
                if str(row_value) != str(value):
                    return False

        return True
