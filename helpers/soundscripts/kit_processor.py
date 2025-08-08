#!/usr/bin/env python3
"""
Kit.txt processor for Mixkit metadata integration.

Implements robust parsing of pipe-delimited kit.txt files, duration
format handling, entry validation, and basic processing statistics.
"""
from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class KitEntry:
    """Represents a single kit.txt entry."""

    filename: str
    title: str
    category: str
    duration: float
    tags: str
    description: str
    raw_line: str
    line_number: int


class KitProcessor:
    """Parses and validates Mixkit kit.txt files.

    Responsibilities:
    - Parse pipe-delimited lines from a kit.txt file
    - Convert duration strings into seconds (float)
    - Validate required fields and basic constraints
    - Collect simple processing statistics
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.logger = logging.getLogger(__name__)
        # Default to INFO if no configuration provided by caller
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)

        self.stats: Dict[str, int] = {
            "total_lines": 0,
            "parsed_entries": 0,
            "valid_entries": 0,
            "invalid_entries": 0,  # structural/format issues
            "parse_errors": 0,
            "validation_errors": 0,
        }

    def parse_kit_file(self, kit_file_path: str) -> List[KitEntry]:
        """Parse a kit.txt file and return a list of validated KitEntry objects.

        Lines starting with '#' or blank lines are ignored.
        Only entries that pass validation are returned.
        """
        if not os.path.exists(kit_file_path):
            self.logger.warning("Kit file not found: %s", kit_file_path)
            return []

        entries: List[KitEntry] = []
        try:
            with open(kit_file_path, "r", encoding="utf-8") as file_handle:
                for line_number, raw_line in enumerate(file_handle, start=1):
                    self.stats["total_lines"] += 1
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    try:
                        entry = self._parse_line(line=line, line_number=line_number)
                        if entry is None:
                            self.stats["invalid_entries"] += 1
                            continue
                        self.stats["parsed_entries"] += 1

                        if self.validate_kit_entry(entry):
                            entries.append(entry)
                            self.stats["valid_entries"] += 1
                        else:
                            self.stats["validation_errors"] += 1
                    except Exception as exc:  # noqa: BLE001 - surface parsing issues to logs
                        self.logger.error(
                            "Error parsing line %d: %s | content='%s'",
                            line_number,
                            exc,
                            line,
                        )
                        self.stats["parse_errors"] += 1
        except OSError as exc:
            self.logger.error("Failed to read kit file '%s': %s", kit_file_path, exc)
            return []

        self.logger.info("Parsed %d valid entries from %s", len(entries), kit_file_path)
        return entries

    def parse_mixkit_catalog(self, kit_file_path: str) -> List[KitEntry]:
        """Parse Mixkit catalog-style kit.txt where entries are blocks like:
        Title\nby Artist\n\nTag1\nTag2\nTag3\nMM:SS\nDownload Free Music

        Returns entries without filenames; filename matching will be performed downstream.
        """
        if not os.path.exists(kit_file_path):
            self.logger.warning("Kit file not found: %s", kit_file_path)
            return []

        def is_duration_line(text: str) -> bool:
            t = text.strip()
            if not t:
                return False
            return (
                t.replace(":", "").isdigit() and (t.count(":") in (1, 2))
            )

        entries: List[KitEntry] = []
        block: List[str] = []

        try:
            with open(kit_file_path, "r", encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if line == "Download Free Music":
                        # finalize current block
                        if block:
                            entry = self._parse_mixkit_block(block)
                            if entry:
                                entries.append(entry)
                            block = []
                        continue

                    if line:
                        block.append(line)

                # flush last block if any
                if block:
                    entry = self._parse_mixkit_block(block)
                    if entry:
                        entries.append(entry)
        except OSError as exc:
            self.logger.error("Failed to read kit file '%s': %s", kit_file_path, exc)
            return []

        self.logger.info("Parsed %d entries from Mixkit catalog format", len(entries))
        return entries

    def _parse_line(self, line: str, line_number: int) -> Optional[KitEntry]:
        """Parse a single line from kit.txt file into a KitEntry or None if invalid."""
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 6:
            self.logger.warning(
                "Invalid format at line %d: expected 6 parts, got %d", line_number, len(parts)
            )
            return None

        filename, title, category, duration_str, tags, description = parts

        duration_seconds = self.parse_duration(duration_str)

        return KitEntry(
            filename=filename,
            title=title,
            category=category,
            duration=duration_seconds,
            tags=tags,
            description=description,
            raw_line=line,
            line_number=line_number,
        )

    def _parse_mixkit_block(self, lines: List[str]) -> Optional[KitEntry]:
        """Parse a single Mixkit block into a KitEntry without filename."""
        if not lines:
            return None

        # Expect first line is title
        title = lines[0].strip()
        # Find artist line starting with 'by '
        artist = ""
        tags: List[str] = []
        duration_str = ""

        idx = 1
        while idx < len(lines):
            line = lines[idx].strip()
            if line.lower().startswith("by "):
                artist = line[3:].strip()
                idx += 1
                break
            idx += 1

        # Collect tags until duration
        while idx < len(lines):
            line = lines[idx].strip()
            if line and (":" in line) and self._looks_like_timecode(line):
                duration_str = line
                idx += 1
                break
            if line and not line.lower().startswith("by "):
                tags.append(line)
            idx += 1

        # Use first tag as category if available
        category = tags[0] if tags else ""
        tags_csv = ",".join(tags)

        # Fallback duration if missing
        duration = 0.0
        if duration_str:
            try:
                duration = self.parse_duration(duration_str)
            except Exception:
                duration = 0.0

        # Build description from artist and tags
        description_parts = []
        if artist:
            description_parts.append(f"Artist: {artist}")
        if tags:
            description_parts.append(f"Tags: {tags_csv}")
        description = " | ".join(description_parts)

        entry = KitEntry(
            filename="",  # unknown at this stage
            title=title,
            category=category,
            duration=duration if duration > 0 else 0.001,  # ensure positive
            tags=tags_csv,
            description=description,
            raw_line="; ".join(lines[:6]),
            line_number=0,
        )
        return entry

    def _looks_like_timecode(self, text: str) -> bool:
        t = text.strip()
        if not t or ":" not in t:
            return False
        parts = t.split(":")
        return all(p.isdigit() for p in parts)

    def parse_duration(self, duration_str: str) -> float:
        """Parse duration into seconds.

        Supported formats:
        - SS or SS.sss (e.g., "2.3", "45")
        - MM:SS (e.g., "3:45")
        - HH:MM:SS (e.g., "1:15:30")
        """
        token = duration_str.strip()
        if ":" not in token:
            # Seconds format (may include decimals)
            value = float(token)
            if value < 0:
                raise ValueError("Duration seconds must be non-negative")
            return value

        parts = token.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            m = int(minutes)
            s = int(seconds)
            if m < 0 or s < 0 or s >= 60:
                raise ValueError(f"Invalid MM:SS format: {token}")
            return float(m * 60 + s)

        if len(parts) == 3:
            hours, minutes, seconds = parts
            h = int(hours)
            m = int(minutes)
            s = int(seconds)
            if h < 0 or m < 0 or m >= 60 or s < 0 or s >= 60:
                raise ValueError(f"Invalid HH:MM:SS format: {token}")
            return float(h * 3600 + m * 60 + s)

        raise ValueError(f"Unsupported duration format: {token}")

    def validate_kit_entry(self, entry: KitEntry) -> bool:
        """Validate KitEntry fields according to basic constraints."""
        max_desc_len: int = int(self.config.get("max_description_length", 1000))

        if not entry.filename or not entry.filename.strip():
            self.logger.warning("Validation error: filename is required")
            return False
        if not entry.title or not entry.title.strip():
            self.logger.warning("Validation error: title is required")
            return False
        if not entry.category or not entry.category.strip():
            self.logger.warning("Validation error: category is required")
            return False
        if entry.duration <= 0:
            self.logger.warning("Validation error: duration must be positive")
            return False
        if len(entry.description) > max_desc_len:
            self.logger.warning("Validation error: description too long (max %d)", max_desc_len)
            return False

        # Basic filename character validation
        invalid_chars = '<>:"/\\|?*'
        if any(char in entry.filename for char in invalid_chars):
            self.logger.warning("Validation error: filename contains invalid characters")
            return False

        # Basic tag normalization check (comma-separated list)
        if entry.tags:
            tag_list = [tag.strip() for tag in entry.tags.split(",") if tag.strip()]
            if len(tag_list) > 0 and any(
                not tag or "," in tag for tag in tag_list
            ):
                self.logger.warning("Validation error: tags must be comma-separated tokens")
                return False

        return True

    def get_kit_statistics(self) -> Dict[str, int]:
        """Return a shallow copy of processing statistics."""
        return dict(self.stats)
