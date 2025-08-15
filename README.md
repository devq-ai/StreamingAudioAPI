# Audio Segmentation API

A FastAPI-based service that processes audio streams and segments them by sentences using speech-to-text analysis.

## Features

- Real-time audio streaming via WebSocket
- Speech-to-text sentence detection
- MP3 file support
- SQLite metadata storage
- File integrity verification with SHA-256 hashing
- RESTful API endpoints

## Prerequisites

### System Dependencies
- Python 3.9+
- FFmpeg (required for audio processing)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Quick Start

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python -m app.main
```

3. Access the API at `http://localhost:8000`
4. View API docs at `http://localhost:8000/docs`

## API Endpoints

- `POST /upload` - Upload MP3 file for processing
- `GET /segments/{file_hash}` - Get segments metadata
- `GET /segments/{file_hash}/{sequence}` - Download specific segment
- `DELETE /segments/{file_hash}` - Delete all segments for a file
- `WebSocket /stream` - Real-time audio streaming

## Testing

Run tests with:
```bash
pytest
```

## Configuration

Modify settings in `app/config.py`:
- File size limits
- Audio processing parameters
- Database configuration