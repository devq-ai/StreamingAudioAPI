import hashlib
import aiofiles
from pathlib import Path
from typing import BinaryIO
from .config import SEGMENTS_DIR

class FileManager:
    def __init__(self, base_dir: Path = SEGMENTS_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)
    
    def calculate_hash(self, data: bytes) -> str:
        """Calculate SHA-256 hash of file data."""
        return hashlib.sha256(data).hexdigest()
    
    async def calculate_hash_from_file(self, file_path: Path) -> str:
        """Calculate SHA-256 hash from file."""
        hash_obj = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def get_segment_dir(self, file_hash: str) -> Path:
        """Get directory path for storing segments of a file."""
        segment_dir = self.base_dir / file_hash[:2] / file_hash[2:4] / file_hash
        segment_dir.mkdir(parents=True, exist_ok=True)
        return segment_dir
    
    async def save_segment(self, file_hash: str, sequence: int, data: bytes) -> Path:
        """Save audio segment to file."""
        segment_dir = self.get_segment_dir(file_hash)
        filename = f"segment_{sequence:04d}.mp3"
        file_path = segment_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(data)
        
        return file_path
    
    async def save_temp_file(self, data: bytes, suffix: str = ".mp3") -> Path:
        """Save temporary file for processing."""
        temp_dir = self.base_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        file_hash = self.calculate_hash(data)
        temp_path = temp_dir / f"{file_hash}{suffix}"
        
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(data)
        
        return temp_path
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str) -> bool:
        """Verify file integrity using hash comparison."""
        try:
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            return actual_hash == expected_hash
        except Exception:
            return False
    
    async def cleanup_temp_files(self):
        """Clean up temporary files."""
        temp_dir = self.base_dir / "temp"
        if temp_dir.exists():
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()

# Global file manager instance
file_manager = FileManager()
