import pytest
import tempfile
import os
from pathlib import Path
from app.audio_processor import AudioProcessor

@pytest.fixture
def audio_processor():
    """Create audio processor instance."""
    return AudioProcessor()

def test_audio_processor_initialization(audio_processor):
    """Test audio processor initialization."""
    assert audio_processor.recognizer is not None
    assert audio_processor.executor is not None

def test_calculate_hash_consistency():
    """Test hash calculation consistency."""
    from app.file_manager import file_manager
    
    data = b"test data"
    hash1 = file_manager.calculate_hash(data)
    hash2 = file_manager.calculate_hash(data)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length

@pytest.mark.asyncio
async def test_process_invalid_audio_file(audio_processor):
    """Test processing invalid audio file."""
    # Create temporary file with invalid data
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(b"invalid audio data")
        temp_path = Path(temp_file.name)
    
    try:
        # This should handle the error gracefully
        with pytest.raises(Exception):
            await audio_processor.process_audio_file(temp_path, "test_hash")
    finally:
        os.unlink(temp_path)

def test_transcribe_empty_audio(audio_processor):
    """Test transcribing empty audio data."""
    result = audio_processor._transcribe_audio_segment(b"")
    assert result is None

def test_detect_speech_segments_invalid_audio(audio_processor):
    """Test speech detection with invalid audio."""
    # This test would need a proper audio segment to work
    # In practice, you'd mock the pydub AudioSegment
    pass
