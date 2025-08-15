import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import db_manager
import tempfile
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
async def setup_db():
    """Setup test database."""
    # Use temporary database for testing
    test_db_path = tempfile.mktemp(suffix=".db")
    db_manager.db_path = test_db_path
    
    await db_manager.init_db()
    
    yield
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)

@pytest.fixture
def sample_mp3_data():
    """Create minimal MP3 data for testing."""
    # This is a minimal MP3 header - in real tests you'd use actual MP3 data
    return b'\xff\xfb\x90\x00' + b'\x00' * 1000

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_invalid_format(client):
    """Test upload with invalid file format."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"not an mp3", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_file_too_large(client):
    """Test upload with oversized file."""
    large_data = b'\xff\xfb\x90\x00' + b'\x00' * (101 * 1024 * 1024)  # 101MB
    response = client.post(
        "/upload",
        files={"file": ("large.mp3", large_data, "audio/mpeg")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_valid_file(client, setup_db, sample_mp3_data):
    """Test successful file upload."""
    # Mock the audio processor to avoid FFmpeg dependency
    with patch('app.main.audio_processor.process_audio_file') as mock_process:
        from app.models import AudioSegment
        from datetime import datetime
        import hashlib
        
        # Calculate actual hash of sample data
        file_hash = hashlib.sha256(sample_mp3_data).hexdigest()
        
        # Create mock AudioSegment object
        mock_segment = AudioSegment(
            file_hash=file_hash,
            timestamp=datetime.now(),
            filename_sequence=1,
            length_seconds=5.0,
            text_content='Test transcription',
            file_path=''
        )
        
        # Mock successful processing - returns list of (AudioSegment, audio_bytes) tuples
        mock_process.return_value = [(mock_segment, b'mock_audio_data')]
        
        response = client.post(
            "/upload",
            files={"file": ("test.mp3", sample_mp3_data, "audio/mpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_hash"] == file_hash
        assert data["message"] == "File processed successfully"
        assert data["segments_count"] == 1
        assert "processing_time" in data

def test_get_segments_not_found(client):
    """Test getting segments for non-existent hash."""
    response = client.get("/segments/nonexistent_hash")
    assert response.status_code == 404
    assert "No segments found" in response.json()["detail"]

def test_websocket_connection():
    """Test WebSocket connection."""
    with TestClient(app) as client:
        with client.websocket_connect("/stream") as websocket:
            # Connection should be established
            assert websocket is not None
