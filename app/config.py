import os
from pathlib import Path

# Database configuration
DATABASE_URL = "sqlite:///./audio_segments.db"

# File storage configuration
SEGMENTS_DIR = Path("./segments")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_FORMATS = [".mp3"]

# Audio processing configuration
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming
SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 500  # ms

# Speech recognition configuration
SPEECH_RECOGNITION_LANGUAGE = "en-US"
SENTENCE_MIN_LENGTH = 1.0  # seconds
SENTENCE_MAX_LENGTH = 30.0  # seconds

# Create directories
SEGMENTS_DIR.mkdir(exist_ok=True)
