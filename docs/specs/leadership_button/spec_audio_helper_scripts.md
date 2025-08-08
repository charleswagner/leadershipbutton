# Audio Helper Scripts Specification

## Overview

The Audio Helper Scripts system provides automated analysis and metadata extraction for audio files across multiple directories (Google Drive, Mixkit, Filmcow) to generate a comprehensive CSV database for the leadership button application.

## Directory Structure

```
helpers/
└── soundscripts/
    ├── __init__.py
    ├── main.py                    # Main orchestrator
    ├── audio_analyzer.py          # Core audio analysis using Librosa
    ├── metadata_generator.py      # Metadata extraction and processing
    ├── csv_manager.py             # CSV file operations and recovery
    ├── directory_scanner.py       # File system scanning and validation
    ├── url_generator.py           # Google Cloud URL generation
    ├── kit_processor.py           # Mixkit metadata processor
    ├── config.py                  # Configuration and constants
    ├── utils.py                   # Utility functions
    └── tests/
        ├── __init__.py
        ├── test_audio_analyzer.py
        ├── test_metadata_generator.py
        ├── test_csv_manager.py
        ├── test_directory_scanner.py
        ├── test_url_generator.py
        ├── test_kit_processor.py
        └── test_integration.py
```

## Core Components

### 1. Audio Analyzer (`audio_analyzer.py`)

**Purpose**: Extract comprehensive audio metadata using Librosa library.

**Key Functions**:

- `analyze_audio_file(file_path: str) -> AudioAnalysis`
- `extract_basic_metadata(audio_data, sample_rate) -> dict`
- `extract_spectral_features(audio_data, sample_rate) -> dict`
- `extract_temporal_features(audio_data, sample_rate) -> dict`
- `extract_harmonic_features(audio_data, sample_rate) -> dict`
- `detect_beats(audio_data, sample_rate) -> dict`

**Metadata Fields**:

```python
@dataclass
class AudioAnalysis:
    # Basic metadata
    filename: str
    file_path: str
    duration: float
    sample_rate: int
    channels: int
    file_size: int

    # Temporal features
    tempo: float
    beat_count: int
    onset_strength: float
    zero_crossing_rate: float
    rms_energy: float

    # Spectral features
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    spectral_contrast: float
    spectral_flatness: float
    spectral_contrast_mean: float
    spectral_flatness_mean: float

    # Harmonic features
    harmonic_ratio: float
    chroma_features: List[float]
    mfcc_features: List[float]

    # Statistical features
    dynamic_range: float
    loudness: float
    peak_amplitude: float

    # Classification
    audio_type: str  # 'song', 'sound_effect', 'ambiguous'
    confidence: float
```

### 2. Metadata Generator (`metadata_generator.py`)

**Purpose**: Process and enhance audio analysis data.

**Key Functions**:

- `classify_audio_type(analysis: AudioAnalysis) -> Tuple[str, float]`
- `generate_google_cloud_url(filename: str, source_dir: str) -> str`
- `enhance_metadata(analysis: AudioAnalysis, source_dir: str) -> dict`
- `validate_metadata(metadata: dict) -> bool`

**Classification Algorithm**:

```python
def classify_audio_type(analysis: AudioAnalysis) -> Tuple[str, float]:
    """Comprehensive classification using multiple features."""

    song_score = 0
    effect_score = 0

    # Duration analysis (30 points)
    if analysis.duration > 30:
        song_score += 30
    elif analysis.duration < 10:
        effect_score += 30

    # Tempo analysis (25 points)
    if analysis.tempo > 60:
        song_score += 25
    elif analysis.tempo == 0:
        effect_score += 25

    # Beat analysis (20 points)
    if analysis.beat_count > 5:
        song_score += 20
    elif analysis.beat_count <= 1:
        effect_score += 20

    # Harmonic analysis (15 points)
    if analysis.harmonic_ratio > 0.6:
        song_score += 15
    elif analysis.harmonic_ratio < 0.3:
        effect_score += 15

    # Spectral analysis (10 points)
    if analysis.spectral_flatness_mean < 0.1:
        song_score += 10
    elif analysis.spectral_flatness_mean > 0.3:
        effect_score += 10

    # Determine classification
    total_score = song_score + effect_score
    if total_score == 0:
        return 'ambiguous', 0.0

    if song_score > effect_score and song_score >= 50:
        confidence = song_score / total_score
        return 'song', confidence
    elif effect_score > song_score and effect_score >= 50:
        confidence = effect_score / total_score
        return 'sound_effect', confidence
    else:
        return 'ambiguous', 0.5
```

### 3. CSV Manager (`csv_manager.py`)

**Purpose**: Handle CSV file operations with error recovery.

**Key Functions**:

- `create_csv_file(output_path: str, headers: List[str]) -> None`
- `append_row_to_csv(output_path: str, row_data: dict) -> None`
- `get_processed_files(csv_path: str) -> Set[str]`
- `resume_processing(csv_path: str, source_dirs: List[str]) -> List[str]`
- `backup_csv(csv_path: str) -> str`

**CSV Structure**:

```csv
filename,file_path,duration,sample_rate,channels,file_size,tempo,beat_count,onset_strength,zero_crossing_rate,rms_energy,spectral_centroid,spectral_bandwidth,spectral_rolloff,spectral_contrast,spectral_flatness,spectral_contrast_mean,spectral_flatness_mean,harmonic_ratio,chroma_features,mfcc_features,dynamic_range,loudness,peak_amplitude,audio_type,confidence,google_cloud_url,source_directory,processing_timestamp
```

### 4. Directory Scanner (`directory_scanner.py`)

**Purpose**: Scan and validate audio files across multiple directories.

**Key Functions**:

- `scan_directory(directory_path: str) -> List[str]`
- `validate_audio_file(file_path: str) -> bool`
- `get_supported_formats() -> List[str]`
- `filter_processed_files(files: List[str], processed_files: Set[str]) -> List[str]`

**Supported Formats**:

- `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.aac`

### 5. URL Generator (`url_generator.py`)

**Purpose**: Generate Google Cloud Storage URLs for audio files.

**Key Functions**:

- `generate_google_cloud_url(filename: str, source_dir: str) -> str`
- `validate_url(url: str) -> bool`
- `get_url_mapping() -> dict`

**URL Patterns**:

```python
URL_MAPPING = {
    'google': 'https://storage.googleapis.com/cwsounds/google/{filename}',
    'mixkit': 'https://storage.googleapis.com/cwsounds/mixkit/{filename}',
    'filmcow': 'https://storage.googleapis.com/cwsounds/filmcow/{filename}'
}
```

### 6. Kit Processor (`kit_processor.py`)

**Purpose**: Process Mixkit metadata from kit.txt file.

**Key Functions**:

- `parse_kit_file(kit_path: str) -> List[dict]`
- `merge_kit_metadata(csv_data: List[dict], kit_data: List[dict]) -> List[dict]`
- `validate_kit_entry(entry: dict) -> bool`

**Kit.txt Format**:

```
filename|title|category|duration|tags|description
```

## Main Orchestrator (`main.py`)

### Configuration

```python
@dataclass
class ProcessingConfig:
    # Source directories
    google_drive_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds"
    mixkit_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds/mixkit"
    filmcow_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds/filmcow"

    # Output
    csv_output_path: str = "data/soundlibrary.csv"
    kit_file_path: str = "/Users/cwagner/Google Drive/My Drive/public/sounds/mixkit/kit.txt"

    # Processing options
    batch_size: int = 10
    max_retries: int = 3
    backup_interval: int = 50

    # Test mode
    test_mode: bool = False
    test_sample_size: int = 5
```

### Main Processing Flow

```python
def main():
    """Main processing orchestrator with error recovery."""

    config = load_config()

    # Initialize CSV file
    csv_manager.initialize_csv(config.csv_output_path)

    # Get already processed files
    processed_files = csv_manager.get_processed_files(config.csv_output_path)

    # Scan directories for unprocessed files
    all_files = []
    for directory in [config.google_drive_path, config.mixkit_path, config.filmcow_path]:
        files = directory_scanner.scan_directory(directory)
        unprocessed = directory_scanner.filter_processed_files(files, processed_files)
        all_files.extend(unprocessed)

    # Process files in batches
    for batch in chunk_files(all_files, config.batch_size):
        try:
            process_batch(batch, config)
            csv_manager.backup_csv(config.csv_output_path)
        except Exception as e:
            logging.error(f"Batch processing failed: {e}")
            continue

    # Process kit.txt metadata
    if os.path.exists(config.kit_file_path):
        kit_processor.merge_kit_metadata(config.csv_output_path, config.kit_file_path)

    logging.info("Processing complete!")

def process_batch(files: List[str], config: ProcessingConfig):
    """Process a batch of audio files."""

    for file_path in files:
        try:
            # Analyze audio file
            analysis = audio_analyzer.analyze_audio_file(file_path)

            # Generate metadata
            metadata = metadata_generator.enhance_metadata(analysis, get_source_directory(file_path))

            # Append to CSV
            csv_manager.append_row_to_csv(config.csv_output_path, metadata)

            logging.info(f"Processed: {os.path.basename(file_path)}")

        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
            continue
```

## Testing Strategy

### Test Structure

All tests are located in `helpers/soundscripts/tests/` to maintain separation from main application tests.

### Test Conventions

1. **No Business Logic**: Tests only contain orchestration and verification logic
2. **Independent Functions**: Each function can be tested independently
3. **Mock External Dependencies**: Use mocks for file I/O and external APIs
4. **Small Test Data**: Use minimal audio files for testing

### Test Categories

#### Unit Tests

- `test_audio_analyzer.py`: Test individual analysis functions
- `test_metadata_generator.py`: Test classification and metadata enhancement
- `test_csv_manager.py`: Test CSV operations and recovery
- `test_directory_scanner.py`: Test file scanning and validation
- `test_url_generator.py`: Test URL generation and validation
- `test_kit_processor.py`: Test kit.txt parsing and merging

#### Integration Tests

- `test_integration.py`: Test complete workflow with small sample

### Test Data

```python
TEST_AUDIO_FILES = {
    'song': 'tests/data/test_song.mp3',      # 30-second lullaby
    'effect': 'tests/data/test_effect.wav',  # 2-second door closing
    'ambiguous': 'tests/data/test_wind.ogg'  # 15-second wind
}
```

## Error Recovery and Resilience

### Checkpoint System

- CSV backup every 50 processed files
- Track processed files to enable resume functionality
- Detailed error logging with file paths and error types

### Resume Functionality

```python
def resume_processing(csv_path: str, source_dirs: List[str]) -> List[str]:
    """Resume processing from where it left off."""

    processed_files = csv_manager.get_processed_files(csv_path)
    all_files = []

    for directory in source_dirs:
        files = directory_scanner.scan_directory(directory)
        unprocessed = directory_scanner.filter_processed_files(files, processed_files)
        all_files.extend(unprocessed)

    return all_files
```

### Error Handling

- Graceful handling of corrupted audio files
- Retry logic for transient failures
- Detailed error reporting for debugging
- Continue processing on individual file failures

## Implementation Phases

### Phase 1: Core Infrastructure

1. Set up directory structure
2. Implement basic audio analysis with Librosa
3. Create CSV manager with recovery
4. Write unit tests for core functions

### Phase 2: Directory Integration

1. Implement directory scanner
2. Add URL generation
3. Test with small sample from each directory
4. Validate CSV output format

### Phase 3: Full Processing

1. Process complete directories
2. Implement error recovery
3. Add comprehensive logging
4. Performance optimization

## Success Criteria

1. **Comprehensive Metadata**: All available Librosa features extracted
2. **Accurate Classification**: >90% accuracy for song/sound effect classification
3. **Error Recovery**: Can resume processing after failures
4. **Performance**: Process 1000+ files efficiently
5. **Data Integrity**: CSV contains all required fields and valid data
6. **Test Coverage**: >90% test coverage for all functions
7. **Modularity**: Each function can be tested independently
8. **Documentation**: Clear usage instructions and examples

## Usage Examples

### Basic Processing

```bash
cd helpers/soundscripts
python main.py
```

### Test Mode

```bash
python main.py --test-mode --test-sample-size 10
```

### Resume Processing

```bash
python main.py --resume
```

### Process Specific Directory

```bash
python main.py --directories mixkit,filmcow
```

This specification provides a comprehensive framework for building robust, testable, and maintainable audio helper scripts that meet all the user's requirements.
