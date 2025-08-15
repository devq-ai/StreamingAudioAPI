import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Optional
from .models import AudioSegment
from .config import DATABASE_URL

class DatabaseManager:
    def __init__(self, db_path: str = "audio_segments.db"):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize the database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audio_segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    filename_sequence INTEGER NOT NULL,
                    length_seconds REAL NOT NULL,
                    text_content TEXT,
                    file_path TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_hash 
                ON audio_segments(file_hash)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON audio_segments(timestamp)
            """)
            
            await db.commit()
    
    async def insert_segment(self, segment: AudioSegment) -> int:
        """Insert a new audio segment and return its ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO audio_segments 
                (file_hash, timestamp, filename_sequence, length_seconds, text_content, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                segment.file_hash,
                segment.timestamp,
                segment.filename_sequence,
                segment.length_seconds,
                segment.text_content,
                segment.file_path
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_segments_by_hash(self, file_hash: str) -> List[AudioSegment]:
        """Get all segments for a specific file hash."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM audio_segments 
                WHERE file_hash = ? 
                ORDER BY filename_sequence
            """, (file_hash,))
            
            rows = await cursor.fetchall()
            return [
                AudioSegment(
                    id=row["id"],
                    file_hash=row["file_hash"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    filename_sequence=row["filename_sequence"],
                    length_seconds=row["length_seconds"],
                    text_content=row["text_content"],
                    file_path=row["file_path"]
                )
                for row in rows
            ]
    
    async def get_segment_by_id(self, segment_id: int) -> Optional[AudioSegment]:
        """Get a specific segment by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM audio_segments WHERE id = ?
            """, (segment_id,))
            
            row = await cursor.fetchone()
            if row:
                return AudioSegment(
                    id=row["id"],
                    file_hash=row["file_hash"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    filename_sequence=row["filename_sequence"],
                    length_seconds=row["length_seconds"],
                    text_content=row["text_content"],
                    file_path=row["file_path"]
                )
            return None
    
    async def delete_segments_by_hash(self, file_hash: str) -> int:
        """Delete all segments for a specific file hash."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM audio_segments WHERE file_hash = ?
            """, (file_hash,))
            await db.commit()
            return cursor.rowcount

# Global database manager instance
db_manager = DatabaseManager()
