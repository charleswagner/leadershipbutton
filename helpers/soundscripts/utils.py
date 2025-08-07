"""
Utility functions for audio helper scripts.
"""

import os
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import numpy as np


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("processing.log")],
    )


def get_file_extension(file_path: str) -> str:
    """Get file extension from file path."""
    return os.path.splitext(file_path)[1].lower()


def is_audio_file(file_path: str) -> bool:
    """Check if file is a supported audio format."""
    from config import get_supported_formats

    return get_file_extension(file_path) in get_supported_formats()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def get_source_directory(file_path: str) -> str:
    """Extract source directory name from file path."""
    # Extract the directory name that contains the file
    dir_path = os.path.dirname(file_path)
    return os.path.basename(dir_path)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def list_to_string(lst: List[Any], separator: str = "|") -> str:
    """Convert list to string with separator."""
    if not lst:
        return ""
    return separator.join(str(item) for item in lst)


def string_to_list(s: str, separator: str = "|") -> List[str]:
    """Convert string back to list using separator."""
    if not s:
        return []
    return s.split(separator)


def numpy_to_list(arr: np.ndarray) -> List[float]:
    """Convert numpy array to list of floats."""
    if arr is None:
        return []
    return arr.tolist() if hasattr(arr, "tolist") else list(arr)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of values."""
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "median": 0.0}

    values_array = np.array(values)
    return {
        "mean": float(np.mean(values_array)),
        "std": float(np.std(values_array)),
        "min": float(np.min(values_array)),
        "max": float(np.max(values_array)),
        "median": float(np.median(values_array)),
    }


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def create_backup_filename(original_path: str) -> str:
    """Create backup filename with timestamp."""
    base, ext = os.path.splitext(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_backup_{timestamp}{ext}"


def validate_file_exists(file_path: str) -> bool:
    """Check if file exists and is readable."""
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def validate_directory_exists(dir_path: str) -> bool:
    """Check if directory exists and is accessible."""
    return os.path.isdir(dir_path) and os.access(dir_path, os.R_OK)


def ensure_directory_exists(dir_path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(dir_path, exist_ok=True)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Could not load JSON file {file_path}: {e}")
        return {}


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save data to JSON file safely."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Could not save JSON file {file_path}: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable string."""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    return filename
