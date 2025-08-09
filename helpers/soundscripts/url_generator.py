"""
URL generation and validation for Google Cloud Storage.
"""

import os
import logging
from typing import Dict, List
from config import get_url_mapping
from urllib.parse import quote


class URLGenerator:
    """Generate and validate Google Cloud Storage URLs for audio files."""

    def __init__(self):
        """Initialize the URL generator."""
        self.url_mapping = get_url_mapping()
        self.logger = logging.getLogger(__name__)

    def generate_google_cloud_url(
        self, filename: str, source_dir: str, file_path: str = ""
    ) -> str:
        """Generate Google Cloud Storage URL for audio file."""
        # Build relative path after public/sounds/
        rel = filename
        if file_path:
            p = file_path.replace("\\", "/")
            anchor = "/public/sounds/"
            idx = p.lower().find(anchor)
            if idx != -1:
                rel = p[idx + len(anchor) :]
        url_pattern = self.url_mapping.get(
            "cwsounds_prefix", "https://storage.googleapis.com/cwsounds/{relpath}"
        )
        url = url_pattern.format(relpath=quote(rel, safe="/"))

        self.logger.debug(f"Generated URL for {filename}: {url}")
        return url

    def _get_url_pattern_for_directory(self, source_dir: str) -> str:
        """Deprecated: kept for compatibility; now unused."""
        return self.url_mapping.get(
            "cwsounds_prefix", "https://storage.googleapis.com/cwsounds/{relpath}"
        )

    def validate_url(self, url: str) -> bool:
        """Validate URL format and structure."""

        if not url:
            return False

        # Check if URL has required components
        required_components = ["https://", "storage.googleapis.com", "/cwsounds/"]

        for component in required_components:
            if component not in url:
                return False

        # Check if URL ends with a filename
        if not url.split("/")[-1]:
            return False

        return True

    def get_url_mapping(self) -> Dict[str, str]:
        """Get current URL mapping configuration."""
        return self.url_mapping.copy()

    def update_url_mapping(self, new_mapping: Dict[str, str]) -> None:
        """Update URL mapping configuration."""
        self.url_mapping.update(new_mapping)
        self.logger.info(f"Updated URL mapping: {new_mapping}")

    def get_url_statistics(self, urls: List[str]) -> Dict[str, int]:
        """Get statistics about generated URLs."""

        stats = {
            "total_urls": len(urls),
            "valid_urls": 0,
            "invalid_urls": 0,
            "by_pattern": {"google": 0, "mixkit": 0, "filmcow": 0},
        }

        for url in urls:
            if self.validate_url(url):
                stats["valid_urls"] += 1

                # Count by pattern
                if "mixkit" in url:
                    stats["by_pattern"]["mixkit"] += 1
                elif "filmcow" in url:
                    stats["by_pattern"]["filmcow"] += 1
                else:
                    stats["by_pattern"]["google"] += 1
            else:
                stats["invalid_urls"] += 1

        return stats

    def extract_filename_from_url(self, url: str) -> str:
        """Extract filename from Google Cloud Storage URL."""

        if not self.validate_url(url):
            return ""

        # Get the last part of the URL path
        path_parts = url.split("/")
        filename = path_parts[-1]

        return filename

    def get_directory_from_url(self, url: str) -> str:
        """Extract directory type from Google Cloud Storage URL."""

        if not self.validate_url(url):
            return ""

        if "mixkit" in url:
            return "mixkit"
        elif "filmcow" in url:
            return "filmcow"
        else:
            return "google"

    def generate_batch_urls(self, filenames: List[str], source_dir: str) -> List[str]:
        """Generate URLs for a batch of filenames."""

        urls = []
        for filename in filenames:
            url = self.generate_google_cloud_url(filename, source_dir)
            urls.append(url)

        self.logger.info(f"Generated {len(urls)} URLs for {source_dir}")
        return urls

    def validate_batch_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """Validate a batch of URLs and return results."""

        results = {"valid": [], "invalid": []}

        for url in urls:
            if self.validate_url(url):
                results["valid"].append(url)
            else:
                results["invalid"].append(url)

        self.logger.info(
            f"URL validation: {len(results['valid'])} valid, {len(results['invalid'])} invalid"
        )
        return results
