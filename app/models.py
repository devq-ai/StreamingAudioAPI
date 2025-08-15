from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AudioSegment(BaseModel):
    id: Optional[int] = None
    file_hash: str
    timestamp: datetime
    filename_sequence: int
    length_seconds: float
    text_content: Optional[str] = None
    file_path: str

class UploadResponse(BaseModel):
    message: str
    file_hash: str
    segments_count: int
    processing_time: float

class SegmentInfo(BaseModel):
    segment_id: int
    filename_sequence: int
    length_seconds: float
    text_content: Optional[str]
    file_path: str

class StreamStatus(BaseModel):
    status: str
    segments_processed: int
    current_file_hash: Optional[str] = None
