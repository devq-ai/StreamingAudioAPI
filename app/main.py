from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, WebSocketDisconnect
from fastapi.responses import FileResponse
import asyncio
import time
from datetime import datetime
from typing import List
import json

from .models import UploadResponse, SegmentInfo, StreamStatus, AudioSegment
from .database import db_manager
from .file_manager import file_manager
from .audio_processor import audio_processor
from .config import MAX_FILE_SIZE, SUPPORTED_FORMATS

app = FastAPI(
    title="Audio Segmentation API",
    description="Real-time audio streaming API with sentence-based segmentation",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await db_manager.init_db()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/upload", response_model=UploadResponse)
async def upload_audio_file(file: UploadFile = File(...)):
    """Upload and process audio file."""
    start_time = time.time()
    
    # Validate file format
    if not any(file.filename.lower().endswith(fmt) for fmt in SUPPORTED_FORMATS):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported: {SUPPORTED_FORMATS}"
        )
    
    # Read file data
    file_data = await file.read()
    
    # Validate file size
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
        )
    
    # Calculate file hash
    file_hash = file_manager.calculate_hash(file_data)
    
    # Save temporary file for processing
    temp_path = await file_manager.save_temp_file(file_data)
    
    try:
        # Process audio file
        segments_data = await audio_processor.process_audio_file(temp_path, file_hash)
        
        # Save segments and store in database
        segments_count = 0
        for segment, audio_data in segments_data:
            # Save segment file
            segment_path = await file_manager.save_segment(
                file_hash, 
                segment.filename_sequence, 
                audio_data
            )
            
            # Update segment with file path
            segment.file_path = str(segment_path)
            
            # Store in database
            await db_manager.insert_segment(segment)
            segments_count += 1
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            message="File processed successfully",
            file_hash=file_hash,
            segments_count=segments_count,
            processing_time=processing_time
        )
    
    finally:
        # Clean up temporary file
        temp_path.unlink()

@app.get("/segments/{file_hash}", response_model=List[SegmentInfo])
async def get_segments(file_hash: str):
    """Get all segments for a file hash."""
    segments = await db_manager.get_segments_by_hash(file_hash)
    
    if not segments:
        raise HTTPException(status_code=404, detail="No segments found for this file hash")
    
    return [
        SegmentInfo(
            segment_id=segment.id,
            filename_sequence=segment.filename_sequence,
            length_seconds=segment.length_seconds,
            text_content=segment.text_content,
            file_path=segment.file_path
        )
        for segment in segments
    ]

@app.get("/segments/{file_hash}/{sequence}")
async def download_segment(file_hash: str, sequence: int):
    """Download a specific audio segment."""
    segments = await db_manager.get_segments_by_hash(file_hash)
    
    # Find segment with matching sequence
    target_segment = None
    for segment in segments:
        if segment.filename_sequence == sequence:
            target_segment = segment
            break
    
    if not target_segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Verify file exists and integrity
    segment_path = target_segment.file_path
    if not file_manager.verify_file_integrity(segment_path, file_hash):
        raise HTTPException(status_code=500, detail="File integrity check failed")
    
    return FileResponse(
        segment_path,
        media_type="audio/mpeg",
        filename=f"segment_{sequence:04d}.mp3"
    )

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming."""
    await websocket.accept()
    
    current_hash = None
    sequence_counter = 0
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Calculate hash for this chunk
            chunk_hash = file_manager.calculate_hash(data)
            
            # If this is a new stream, reset counter
            if current_hash != chunk_hash:
                current_hash = chunk_hash
                sequence_counter = 0
            
            try:
                # Process audio chunk
                segments_data = await audio_processor.process_audio_stream(
                    data, 
                    current_hash, 
                    sequence_counter
                )
                
                # Save segments and store in database
                for segment, audio_data in segments_data:
                    # Save segment file
                    segment_path = await file_manager.save_segment(
                        current_hash,
                        segment.filename_sequence,
                        audio_data
                    )
                    
                    # Update segment with file path
                    segment.file_path = str(segment_path)
                    
                    # Store in database
                    await db_manager.insert_segment(segment)
                    sequence_counter += 1
                
                # Send status update
                status = StreamStatus(
                    status="processed",
                    segments_processed=len(segments_data),
                    current_file_hash=current_hash
                )
                await websocket.send_text(status.json())
                
            except Exception as e:
                # Send error status
                error_status = StreamStatus(
                    status=f"error: {str(e)}",
                    segments_processed=0,
                    current_file_hash=current_hash
                )
                await websocket.send_text(error_status.json())
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for hash: {current_hash}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()

@app.delete("/segments/{file_hash}")
async def delete_segments(file_hash: str):
    """Delete all segments for a file hash."""
    deleted_count = await db_manager.delete_segments_by_hash(file_hash)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No segments found for this file hash")
    
    return {"message": f"Deleted {deleted_count} segments", "file_hash": file_hash}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
