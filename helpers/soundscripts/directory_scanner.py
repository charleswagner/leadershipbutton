"""
Directory scanning and file validation for audio files.
"""

import os
import logging
from typing import List, Set
from config import get_supported_formats
from utils import is_audio_file, validate_directory_exists


class DirectoryScanner:
    """Scan and validate audio files across directories."""

    def __init__(self):
        """Initialize the directory scanner."""
        self.supported_formats = get_supported_formats()
        self.logger = logging.getLogger(__name__)

    def scan_directory(self, directory_path: str) -> List[str]:
        """Scan directory for audio files recursively."""

        if not validate_directory_exists(directory_path):
            self.logger.warning(
                f"Directory does not exist or is not accessible: {directory_path}"
            )
            return []

        audio_files = []

        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.validate_audio_file(file_path):
                        audio_files.append(file_path)

            self.logger.info(
                f"Found {len(audio_files)} audio files in {directory_path}"
            )
            return audio_files

        except Exception as e:
            self.logger.error(f"Failed to scan directory {directory_path}: {e}")
            return []

    def validate_audio_file(self, file_path: str) -> bool:
        """Validate if file is a supported audio format."""

        # Check if file exists and is readable
        if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
            return False

        # Check file extension
        if not is_audio_file(file_path):
            return False

        # Check file size (skip empty files)
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.logger.debug(f"Skipping empty file: {file_path}")
                return False
        except OSError:
            return False

        return True

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        return self.supported_formats.copy()

    def filter_processed_files(
        self, files: List[str], processed_files: Set[str]
    ) -> List[str]:
        """Filter out already processed files."""

        unprocessed_files = []
        for file_path in files:
            filename = os.path.basename(file_path)
            if filename not in processed_files:
                unprocessed_files.append(file_path)
            else:
                self.logger.debug(f"Skipping already processed file: {filename}")

        self.logger.info(
            f"Filtered {len(files)} files to {len(unprocessed_files)} unprocessed files"
        )
        return unprocessed_files

    def scan_multiple_directories(self, directories: List[str]) -> List[str]:
        """Scan multiple directories for audio files."""

        all_files = []

        for directory in directories:
            if validate_directory_exists(directory):
                files = self.scan_directory(directory)
                all_files.extend(files)
            else:
                self.logger.warning(f"Skipping non-existent directory: {directory}")

        self.logger.info(
            f"Total audio files found across {len(directories)} directories: {len(all_files)}"
        )
        return all_files

    def get_directory_statistics(self, directory_path: str) -> dict:
        """Get statistics about audio files in a directory."""

        if not validate_directory_exists(directory_path):
            return {"error": "Directory does not exist"}

        stats = {
            "total_files": 0,
            "audio_files": 0,
            "format_counts": {},
            "total_size": 0,
            "subdirectories": 0,
        }

        try:
            for root, dirs, files in os.walk(directory_path):
                stats["subdirectories"] += len(dirs)

                for file in files:
                    file_path = os.path.join(root, file)
                    stats["total_files"] += 1

                    if self.validate_audio_file(file_path):
                        stats["audio_files"] += 1

                        # Count by format
                        file_ext = os.path.splitext(file)[1].lower()
                        stats["format_counts"][file_ext] = (
                            stats["format_counts"].get(file_ext, 0) + 1
                        )

                        # Sum file sizes
                        try:
                            file_size = os.path.getsize(file_path)
                            stats["total_size"] += file_size
                        except OSError:
                            pass

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get directory statistics: {e}")
            return {"error": str(e)}

    def find_duplicate_files(self, directory_path: str) -> List[List[str]]:
        """Find duplicate files by filename (case-insensitive)."""

        if not validate_directory_exists(directory_path):
            return []

        filename_groups = {}

        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.validate_audio_file(file_path):
                        # Use lowercase filename as key
                        filename_lower = file.lower()
                        if filename_lower not in filename_groups:
                            filename_groups[filename_lower] = []
                        filename_groups[filename_lower].append(file_path)

            # Return only groups with duplicates
            duplicates = [files for files in filename_groups.values() if len(files) > 1]

            self.logger.info(f"Found {len(duplicates)} groups of duplicate files")
            return duplicates

        except Exception as e:
            self.logger.error(f"Failed to find duplicate files: {e}")
            return []

    def get_files_by_format(self, directory_path: str, format_ext: str) -> List[str]:
        """Get all files of a specific format in directory."""

        if not validate_directory_exists(directory_path):
            return []

        # Normalize format extension
        if not format_ext.startswith("."):
            format_ext = "." + format_ext
        format_ext = format_ext.lower()

        files = []

        try:
            for root, dirs, filenames in os.walk(directory_path):
                for filename in filenames:
                    if filename.lower().endswith(format_ext):
                        file_path = os.path.join(root, filename)
                        if self.validate_audio_file(file_path):
                            files.append(file_path)

            self.logger.info(
                f"Found {len(files)} {format_ext} files in {directory_path}"
            )
            return files

        except Exception as e:
            self.logger.error(f"Failed to get files by format: {e}")
            return []

    def validate_directory_structure(self, directory_path: str) -> dict:
        """Validate directory structure and permissions."""

        validation_result = {
            "exists": False,
            "readable": False,
            "writable": False,
            "audio_files": 0,
            "total_files": 0,
            "errors": [],
        }

        try:
            # Check if directory exists
            if not os.path.exists(directory_path):
                validation_result["errors"].append(
                    f"Directory does not exist: {directory_path}"
                )
                return validation_result

            validation_result["exists"] = True

            # Check permissions
            if os.access(directory_path, os.R_OK):
                validation_result["readable"] = True
            else:
                validation_result["errors"].append(
                    f"Directory not readable: {directory_path}"
                )

            if os.access(directory_path, os.W_OK):
                validation_result["writable"] = True
            else:
                validation_result["errors"].append(
                    f"Directory not writable: {directory_path}"
                )

            # Count files
            for root, dirs, files in os.walk(directory_path):
                validation_result["total_files"] += len(files)

                for file in files:
                    file_path = os.path.join(root, file)
                    if self.validate_audio_file(file_path):
                        validation_result["audio_files"] += 1

            return validation_result

        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result
