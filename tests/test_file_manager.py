import pytest
import tempfile
import os
from pathlib import Path
from app.file_manager import FileManager

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

@pytest.fixture
def file_manager(temp_dir):
    """Create file manager with temporary directory."""
    return FileManager(temp_dir)

def test_calculate_hash(file_manager):
    """Test hash calculation."""
    data = b"test data for hashing"
    hash_result = file_manager.calculate_hash(data)
    
    assert isinstance(hash_result, str)
    assert len(hash_result) == 64  # SHA-256 hex string
    
    # Same data should produce same hash
    hash_result2 = file_manager.calculate_hash(data)
    assert hash_result == hash_result2

@pytest.mark.asyncio
async def test_calculate_hash_from_file(file_manager, temp_dir):
    """Test hash calculation from file."""
    test_data = b"file content for hashing"
    test_file = temp_dir / "test.txt"
    
    # Write test file
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    # Calculate hash
    file_hash = await file_manager.calculate_hash_from_file(test_file)
    direct_hash = file_manager.calculate_hash(test_data)
    
    assert file_hash == direct_hash

def test_get_segment_dir(file_manager):
    """Test segment directory creation."""
    test_hash = "abcdef1234567890" * 4  # 64 character hash
    
    segment_dir = file_manager.get_segment_dir(test_hash)
    
    assert segment_dir.exists()
    assert segment_dir.name == test_hash
    assert segment_dir.parent.name == test_hash[2:4]
    assert segment_dir.parent.parent.name == test_hash[:2]

@pytest.mark.asyncio
async def test_save_segment(file_manager):
    """Test saving audio segment."""
    test_hash = "a" * 64
    sequence = 1
    test_data = b"fake audio data"
    
    file_path = await file_manager.save_segment(test_hash, sequence, test_data)
    
    assert file_path.exists()
    assert file_path.name == "segment_0001.mp3"
    
    # Verify content
    with open(file_path, 'rb') as f:
        assert f.read() == test_data

@pytest.mark.asyncio
async def test_save_temp_file(file_manager):
    """Test saving temporary file."""
    test_data = b"temporary file data"
    
    temp_path = await file_manager.save_temp_file(test_data)
    
    assert temp_path.exists()
    assert temp_path.suffix == ".mp3"
    
    # Verify content
    with open(temp_path, 'rb') as f:
        assert f.read() == test_data

def test_verify_file_integrity(file_manager, temp_dir):
    """Test file integrity verification."""
    test_data = b"integrity test data"
    test_file = temp_dir / "integrity_test.txt"
    
    # Write test file
    with open(test_file, 'wb') as f:
        f.write(test_data)
    
    # Calculate expected hash
    expected_hash = file_manager.calculate_hash(test_data)
    
    # Verify integrity
    assert file_manager.verify_file_integrity(test_file, expected_hash)
    
    # Test with wrong hash
    wrong_hash = "0" * 64
    assert not file_manager.verify_file_integrity(test_file, wrong_hash)
    
    # Test with non-existent file
    fake_file = temp_dir / "nonexistent.txt"
    assert not file_manager.verify_file_integrity(fake_file, expected_hash)

@pytest.mark.asyncio
async def test_cleanup_temp_files(file_manager):
    """Test cleanup of temporary files."""
    # Create some temp files
    temp_data1 = b"temp file 1"
    temp_data2 = b"temp file 2"
    
    temp_path1 = await file_manager.save_temp_file(temp_data1)
    temp_path2 = await file_manager.save_temp_file(temp_data2)
    
    assert temp_path1.exists()
    assert temp_path2.exists()
    
    # Cleanup
    await file_manager.cleanup_temp_files()
    
    # Files should be gone
    assert not temp_path1.exists()
    assert not temp_path2.exists()
