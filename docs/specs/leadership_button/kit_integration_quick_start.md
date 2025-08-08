# Phase 3: Kit.txt Integration - Quick Start Guide

## Immediate Next Steps (Week 1)

This guide provides the specific steps to begin implementing Phase 3: Kit.txt Integration, starting with Week 1 tasks.

## Prerequisites

- ✅ Phase 2 audio helper scripts system is complete and tested
- ✅ Existing CSV structure and processing pipeline is working
- ✅ Test data available for validation

## Day 1-2: Basic Parser Structure

### Step 1: Create KitProcessor Module

**File**: `helpers/soundscripts/kit_processor.py`

```python
#!/usr/bin/env python3
"""
Kit.txt processor for Mixkit metadata integration.
"""
import os
import logging
import csv
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from utils import load_json_file, save_json_file, get_timestamp

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
    """Processes kit.txt files and integrates metadata with CSV data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'total_entries': 0,
            'valid_entries': 0,
            'invalid_entries': 0,
            'parse_errors': 0,
            'validation_errors': 0
        }
    
    def parse_kit_file(self, kit_file_path: str) -> List[KitEntry]:
        """Parse a kit.txt file and return list of KitEntry objects."""
        if not os.path.exists(kit_file_path):
            self.logger.warning(f"Kit file not found: {kit_file_path}")
            return []
        
        entries = []
        with open(kit_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    entry = self._parse_line(line, line_num)
                    if entry:
                        entries.append(entry)
                        self.stats['valid_entries'] += 1
                    else:
                        self.stats['invalid_entries'] += 1
                except Exception as e:
                    self.logger.error(f"Error parsing line {line_num}: {e}")
                    self.stats['parse_errors'] += 1
        
        self.stats['total_entries'] = len(entries)
        self.logger.info(f"Parsed {len(entries)} valid entries from {kit_file_path}")
        return entries
    
    def _parse_line(self, line: str, line_number: int) -> Optional[KitEntry]:
        """Parse a single line from kit.txt file."""
        parts = line.split('|')
        if len(parts) != 6:
            self.logger.warning(f"Invalid format at line {line_number}: expected 6 parts, got {len(parts)}")
            return None
        
        filename, title, category, duration_str, tags, description = parts
        
        # Parse duration
        try:
            duration = self.parse_duration(duration_str)
        except ValueError as e:
            self.logger.warning(f"Invalid duration at line {line_number}: {duration_str} - {e}")
            return None
        
        return KitEntry(
            filename=filename.strip(),
            title=title.strip(),
            category=category.strip(),
            duration=duration,
            tags=tags.strip(),
            description=description.strip(),
            raw_line=line,
            line_number=line_number
        )
    
    def parse_duration(self, duration_str: str) -> float:
        """Parse duration string into seconds."""
        duration_str = duration_str.strip()
        
        # Handle seconds format (e.g., "2.3")
        if ':' not in duration_str:
            return float(duration_str)
        
        # Handle MM:SS format (e.g., "3:45")
        parts = duration_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        
        # Handle HH:MM:SS format (e.g., "1:15:30")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        
        raise ValueError(f"Unsupported duration format: {duration_str}")
    
    def validate_kit_entry(self, entry: KitEntry) -> bool:
        """Validate a KitEntry object."""
        errors = []
        
        # Required field validation
        if not entry.filename:
            errors.append("Filename is required")
        
        if not entry.title:
            errors.append("Title is required")
        
        if not entry.category:
            errors.append("Category is required")
        
        # Duration validation
        if entry.duration <= 0:
            errors.append("Duration must be positive")
        
        # Description length validation
        if len(entry.description) > 1000:
            errors.append("Description too long (max 1000 characters)")
        
        if errors:
            self.logger.warning(f"Validation errors for entry {entry.filename}: {errors}")
            self.stats['validation_errors'] += 1
            return False
        
        return True
    
    def get_kit_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
```

### Step 2: Update Configuration

**File**: `helpers/soundscripts/config.py`

Add to existing configuration:

```python
# Kit.txt Integration Configuration
KIT_FILE_PATHS = {
    'mixkit': 'data/mixkit/kit.txt',
    'filmcow': 'data/filmcow/kit.txt',
    'google': 'data/google/kit.txt'
}

KIT_PROCESSING_CONFIG = {
    'enable_kit_integration': True,
    'prefer_kit_data': ['title', 'category', 'tags', 'description'],
    'preserve_existing': ['duration', 'file_size', 'analysis_data'],
    'matching_confidence_threshold': 0.8,
    'max_description_length': 1000
}
```

### Step 3: Create Test Data

**File**: `helpers/soundscripts/data/test_kit.txt`

```txt
beautiful_song.mp3|Beautiful Song|Music|3:45|happy,upbeat|A beautiful uplifting song
door_slam.wav|Door Slam|Sound Effect|2.3|impact,door|A door slamming sound
wind_ambient.ogg|Wind|Ambient|15:30|nature,wind|Gentle wind sounds
```

## Day 3-4: Format Parsing

### Step 4: Create Basic Test Script

**File**: `helpers/soundscripts/test_kit_parser.py`

```python
#!/usr/bin/env python3
"""
Test script for kit.txt parser functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kit_processor import KitProcessor
from config import KIT_PROCESSING_CONFIG

def test_basic_parsing():
    """Test basic kit.txt parsing functionality."""
    processor = KitProcessor(KIT_PROCESSING_CONFIG)
    
    # Test with sample kit file
    test_file = 'data/test_kit.txt'
    entries = processor.parse_kit_file(test_file)
    
    print(f"Parsed {len(entries)} entries:")
    for entry in entries:
        print(f"  {entry.filename}: {entry.title} ({entry.category}) - {entry.duration}s")
    
    # Print statistics
    stats = processor.get_kit_statistics()
    print(f"\nStatistics: {stats}")

if __name__ == "__main__":
    test_basic_parsing()
```

## Day 5-7: Duration Parsing & Validation

### Step 5: Enhanced Duration Parsing

Add to `KitProcessor` class:

```python
def parse_duration(self, duration_str: str) -> float:
    """Parse duration string into seconds with comprehensive format support."""
    duration_str = duration_str.strip()
    
    # Handle seconds format (e.g., "2.3", "45")
    if ':' not in duration_str:
        try:
            return float(duration_str)
        except ValueError:
            raise ValueError(f"Invalid seconds format: {duration_str}")
    
    # Handle MM:SS format (e.g., "3:45", "1:30")
    parts = duration_str.split(':')
    if len(parts) == 2:
        try:
            minutes, seconds = map(int, parts)
            if minutes < 0 or seconds < 0 or seconds >= 60:
                raise ValueError(f"Invalid MM:SS format: {duration_str}")
            return minutes * 60 + seconds
        except ValueError:
            raise ValueError(f"Invalid MM:SS format: {duration_str}")
    
    # Handle HH:MM:SS format (e.g., "1:15:30", "2:45:12")
    if len(parts) == 3:
        try:
            hours, minutes, seconds = map(int, parts)
            if hours < 0 or minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60:
                raise ValueError(f"Invalid HH:MM:SS format: {duration_str}")
            return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            raise ValueError(f"Invalid HH:MM:SS format: {duration_str}")
    
    raise ValueError(f"Unsupported duration format: {duration_str}")
```

### Step 6: Comprehensive Validation

Add to `KitProcessor` class:

```python
def validate_kit_entry(self, entry: KitEntry) -> bool:
    """Comprehensive validation of a KitEntry object."""
    errors = []
    
    # Required field validation
    if not entry.filename or not entry.filename.strip():
        errors.append("Filename is required and cannot be empty")
    
    if not entry.title or not entry.title.strip():
        errors.append("Title is required and cannot be empty")
    
    if not entry.category or not entry.category.strip():
        errors.append("Category is required and cannot be empty")
    
    # Duration validation
    if entry.duration <= 0:
        errors.append("Duration must be positive")
    elif entry.duration > 86400:  # 24 hours
        errors.append("Duration too long (max 24 hours)")
    
    # Tags validation
    if entry.tags:
        # Check for valid tag format (comma-separated)
        tag_list = [tag.strip() for tag in entry.tags.split(',') if tag.strip()]
        if len(tag_list) > 20:
            errors.append("Too many tags (max 20)")
    
    # Description validation
    if len(entry.description) > self.config.get('max_description_length', 1000):
        errors.append(f"Description too long (max {self.config.get('max_description_length', 1000)} characters)")
    
    # Filename validation
    if entry.filename:
        invalid_chars = '<>:"/\\|?*'
        if any(char in entry.filename for char in invalid_chars):
            errors.append("Filename contains invalid characters")
    
    if errors:
        self.logger.warning(f"Validation errors for entry {entry.filename}: {errors}")
        self.stats['validation_errors'] += 1
        return False
    
    return True
```

## Testing Your Implementation

### Run Basic Tests

```bash
cd helpers/soundscripts
python3 test_kit_parser.py
```

### Expected Output

```
Parsed 3 entries:
  beautiful_song.mp3: Beautiful Song (Music) - 225.0s
  door_slam.wav: Door Slam (Sound Effect) - 2.3s
  wind_ambient.ogg: Wind (Ambient) - 930.0s

Statistics: {'total_entries': 3, 'valid_entries': 3, 'invalid_entries': 0, 'parse_errors': 0, 'validation_errors': 0}
```

## Next Steps

After completing Week 1:

1. **Test thoroughly** with various kit.txt formats
2. **Validate error handling** with malformed data
3. **Document any issues** or edge cases discovered
4. **Prepare for Week 2** CSV integration tasks

## Success Criteria for Week 1

- ✅ KitProcessor class created and functional
- ✅ Basic kit.txt parsing working
- ✅ Duration parsing supports all formats
- ✅ Comprehensive validation implemented
- ✅ Error handling and logging working
- ✅ Basic tests passing

This quick start guide provides the foundation for implementing Phase 3: Kit.txt Integration. The modular approach allows for iterative development and testing throughout the process. 