"""
Kit.txt processor for Mixkit metadata integration.
"""

import os
import logging
import csv
from typing import List, Dict, Any, Optional
from utils import load_json_file, save_json_file, get_timestamp


class KitProcessor:
    """Process Mixkit metadata from kit.txt file."""

    def __init__(self):
        """Initialize the kit processor."""
        self.logger = logging.getLogger(__name__)

    def parse_kit_file(self, kit_path: str) -> List[Dict[str, Any]]:
        """Parse kit.txt file and extract metadata."""

        if not os.path.exists(kit_path):
            self.logger.warning(f"Kit file does not exist: {kit_path}")
            return []

        kit_data = []

        try:
            with open(kit_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    entry = self._parse_kit_line(line, line_num)
                    if entry:
                        kit_data.append(entry)

            self.logger.info(f"Parsed {len(kit_data)} entries from kit.txt")
            return kit_data

        except Exception as e:
            self.logger.error(f"Failed to parse kit file {kit_path}: {e}")
            return []

    def _parse_kit_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single line from kit.txt."""

        try:
            # Expected format: filename|title|category|duration|tags|description
            parts = line.split("|")

            if len(parts) < 4:
                self.logger.warning(f"Invalid kit line {line_num}: insufficient parts")
                return None

            entry = {
                "filename": parts[0].strip(),
                "title": parts[1].strip() if len(parts) > 1 else "",
                "category": parts[2].strip() if len(parts) > 2 else "",
                "duration": (
                    self._parse_duration(parts[3].strip()) if len(parts) > 3 else 0.0
                ),
                "tags": (
                    parts[4].strip().split(",")
                    if len(parts) > 4 and parts[4].strip()
                    else []
                ),
                "description": parts[5].strip() if len(parts) > 5 else "",
                "line_number": line_num,
                "source": "kit.txt",
            }

            # Validate entry
            if self.validate_kit_entry(entry):
                return entry
            else:
                self.logger.warning(
                    f"Invalid kit entry at line {line_num}: {entry['filename']}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to parse kit line {line_num}: {e}")
            return None

    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string to float seconds."""

        try:
            # Handle various duration formats
            duration_str = duration_str.lower().strip()

            if ":" in duration_str:
                # Format: MM:SS or HH:MM:SS
                parts = duration_str.split(":")
                if len(parts) == 2:
                    minutes, seconds = map(float, parts)
                    return minutes * 60 + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = map(float, parts)
                    return hours * 3600 + minutes * 60 + seconds
            else:
                # Try direct float conversion
                return float(duration_str)

        except (ValueError, TypeError):
            return 0.0

    def validate_kit_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate kit entry for completeness and correctness."""

        # Check required fields
        if not entry.get("filename"):
            return False

        # Validate duration
        duration = entry.get("duration", 0)
        if not isinstance(duration, (int, float)) or duration < 0:
            return False

        # Validate tags is a list
        if not isinstance(entry.get("tags", []), list):
            return False

        return True

    def merge_kit_metadata(self, csv_path: str, kit_path: str) -> bool:
        """Merge kit.txt metadata with existing CSV data."""

        if not os.path.exists(csv_path):
            self.logger.error(f"CSV file does not exist: {csv_path}")
            return False

        # Parse kit data
        kit_data = self.parse_kit_file(kit_path)
        if not kit_data:
            self.logger.warning("No kit data to merge")
            return True  # Not an error, just no data

        # Create kit data lookup
        kit_lookup = {entry["filename"]: entry for entry in kit_data}

        # Read existing CSV and merge
        try:
            temp_csv_path = csv_path + ".tmp"

            with open(csv_path, "r", newline="", encoding="utf-8") as infile, open(
                temp_csv_path, "w", newline="", encoding="utf-8"
            ) as outfile:

                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames + [
                    "kit_title",
                    "kit_category",
                    "kit_tags",
                    "kit_description",
                ]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                merged_count = 0
                for row in reader:
                    filename = row.get("filename", "")

                    # Check if we have kit data for this file
                    if filename in kit_lookup:
                        kit_entry = kit_lookup[filename]
                        row["kit_title"] = kit_entry.get("title", "")
                        row["kit_category"] = kit_entry.get("category", "")
                        row["kit_tags"] = "|".join(kit_entry.get("tags", []))
                        row["kit_description"] = kit_entry.get("description", "")
                        merged_count += 1
                    else:
                        row["kit_title"] = ""
                        row["kit_category"] = ""
                        row["kit_tags"] = ""
                        row["kit_description"] = ""

                    writer.writerow(row)

            # Replace original file
            os.replace(temp_csv_path, csv_path)

            self.logger.info(
                f"Successfully merged kit metadata: {merged_count} entries updated"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to merge kit metadata: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
            return False

    def get_kit_statistics(self, kit_path: str) -> Dict[str, Any]:
        """Get statistics about kit.txt file."""

        if not os.path.exists(kit_path):
            return {"error": "File does not exist"}

        kit_data = self.parse_kit_file(kit_path)

        stats = {
            "total_entries": len(kit_data),
            "valid_entries": 0,
            "invalid_entries": 0,
            "categories": {},
            "duration_stats": {
                "min": float("inf"),
                "max": 0.0,
                "total": 0.0,
                "count": 0,
            },
            "files_with_tags": 0,
            "files_with_descriptions": 0,
        }

        for entry in kit_data:
            if self.validate_kit_entry(entry):
                stats["valid_entries"] += 1

                # Category statistics
                category = entry.get("category", "unknown")
                stats["categories"][category] = stats["categories"].get(category, 0) + 1

                # Duration statistics
                duration = entry.get("duration", 0)
                if duration > 0:
                    stats["duration_stats"]["min"] = min(
                        stats["duration_stats"]["min"], duration
                    )
                    stats["duration_stats"]["max"] = max(
                        stats["duration_stats"]["max"], duration
                    )
                    stats["duration_stats"]["total"] += duration
                    stats["duration_stats"]["count"] += 1

                # Tag and description statistics
                if entry.get("tags"):
                    stats["files_with_tags"] += 1
                if entry.get("description"):
                    stats["files_with_descriptions"] += 1
            else:
                stats["invalid_entries"] += 1

        # Calculate average duration
        if stats["duration_stats"]["count"] > 0:
            stats["duration_stats"]["average"] = (
                stats["duration_stats"]["total"] / stats["duration_stats"]["count"]
            )
        else:
            stats["duration_stats"]["average"] = 0.0

        # Handle edge case for min duration
        if stats["duration_stats"]["min"] == float("inf"):
            stats["duration_stats"]["min"] = 0.0

        return stats

    def export_kit_data(
        self, kit_path: str, output_path: str, format: str = "json"
    ) -> bool:
        """Export kit data to different formats."""

        kit_data = self.parse_kit_file(kit_path)
        if not kit_data:
            self.logger.warning("No kit data to export")
            return False

        try:
            if format.lower() == "json":
                return save_json_file(
                    output_path,
                    {
                        "metadata": {
                            "source": kit_path,
                            "export_timestamp": get_timestamp(),
                            "total_entries": len(kit_data),
                        },
                        "entries": kit_data,
                    },
                )
            elif format.lower() == "csv":
                with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                    if kit_data:
                        fieldnames = kit_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(kit_data)
                return True
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to export kit data: {e}")
            return False
