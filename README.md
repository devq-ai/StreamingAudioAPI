# StreamingAudioAPI
Simple audio file API for integrity

## Intial Idea

Create a Python API service for audio stream processing with sentence segmentation.
I'll stick with what I know:
+ FastAPI - REST API framework
+ PyTest - Testing framework
+ SQLite - Metadata storage (file_hash, timestamp, filename_sequence, length)
+ Hashing - hashlib (SHA-256) for reasonable file integrity (can always migrate to more sophisticated if needed)
+ Some audio libraries (TBD)

## Plan

A quick [Google search recommends](https://www.google.com/search?q=python+mp3+library+voice-to-text+sentence+recognition&oq=python+mp3+library+voice-to-text+sentence+&gs_lcrp=EgZjaHJvbWUqBwgBECEYoAEyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRigATIHCAUQIRigATIHCAYQIRiPAjIHCAcQIRiPAtIBCTcxNDAxajBqN6gCALACAA&sourceid=chrome&ie=UTF-8) the following libraries to hande the speech to text analysis:
```
To perform voice-to-text sentence recognition from an MP3 file in Python, you typically need to combine an audio processing library with a speech recognition library.
1. Audio Processing (MP3 to WAV conversion):
Speech recognition libraries often work best with WAV format. You can use a library like pydub to handle the conversion of MP3 files to WAV.
    from pydub import AudioSegment

    # Load the MP3 file
    audio = AudioSegment.from_mp3("your_audio.mp3")

    # Export as WAV
    audio.export("your_audio.wav", format="wav")
2. Speech Recognition:
The SpeechRecognition library is a popular choice for Python, providing an interface to various speech recognition APIs (e.g., Google Web Speech API, Google Cloud Speech-to-Text, Sphinx, Wit.ai, IBM Watson, Houndify).
    import speech_recognition as sr

    # Initialize the recognizer
    r = sr.Recognizer()

    # Load the WAV file (after converting from MP3)
    with sr.AudioFile("your_audio.wav") as source:
        audio_data = r.record(source)  # Read the entire audio file

    # Perform speech recognition using Google Web Speech API (free, online)
    try:
        text = r.recognize_google(audio_data)
        print("Transcription:", text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
```

At a minimum we need the following:
```
fastapi // Start with FastAPI
uvicorn // Minimal low-level server/application interface for async frameworks
pydub // "Pydub lets you do stuff to audio in a way that isn't stupid."
speech-recognition // Library for performing speech recognition, with support for several engines and APIs, online and offline.
python-multipart // SQLite schema: segments(id, file_hash, timestamp, filename_sequence, length_seconds)
websockets // WebSocket endpoint for real-time audio streaming
pytest // Unit testing
pytest-asyncio // Keep it simple for development
```

## Execution

Here are the Main Components:
```
audio_processor.py - Speech-to-text and segmentation logic
database.py - SQLite operations
file_manager.py - File storage and hashing
main.py - FastAPI app with WebSocket endpoint
tests/ - PyTest test suite
```
PROMPT: `Proceed with implementing these components, start with the core structure and expand based on the implied requirements.`

---
I'll create the complete API service structure. Here are the main components:

## Project Structure
```
audio_segmentation_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── audio_processor.py
│   ├── file_manager.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_audio_processor.py
│   └── test_file_manager.py
├── segments/
├── requirements.txt
└── README.md
```

`Now I'll create the core files:`

`Now I'll create the test files:`

## Project Summary

Created a complete audio segmentation API with the following components:

**Core Features:**
- **Real-time streaming** via WebSocket endpoint
- **Speech-to-text sentence detection** using Google Speech Recognition
- **MP3 file processing** with pydub
- **SQLite metadata storage** (file_hash, timestamp, filename_sequence, length_seconds)
- **SHA-256 hashing** for file integrity verification
- **RESTful API** with FastAPI

**Key Endpoints:**
- `POST /upload` - Upload MP3 files
- `WebSocket /stream` - Real-time audio streaming
- `GET /segments/{file_hash}` - Retrieve segment metadata
- `GET /segments/{file_hash}/{sequence}` - Download specific segments
- `DELETE /segments/{file_hash}` - Remove segments

**Technical Architecture:**
- Modular design with separate components for database, file management, and audio processing
- Async/await throughout for performance
- Comprehensive error handling
- File integrity verification
- Organized storage by hash prefix

**Testing:**
- PyTest suite covering API endpoints, audio processing, and file management
- Fixtures for database setup and temporary files
- Edge case testing for invalid inputs

**Usage:**
```bash
pip install -r requirements.txt
python -m app.main  # Starts server on localhost:8000
pytest  # Run tests
```

The service processes audio streams, detects sentence boundaries using speech-to-text, and saves each sentence as a separate MP3 file with metadata tracking in SQLite.
---

### Tests are failing.
- Adding `httpx`.
- Starting `venv` with Python 3.12 since I'm still running Python 3.9 for this virtrual environment.
- Installing FFmpeg libary.  
- The code expects a list of tuples (segment_audio, text) but the mock is returning a list of dictionaries.
- The file hash is calculated from the actual file data, not from the mock. I'll fix this by using the actual hash of the sample data.
- UploadResponse doesn't have a "status" field. I'll fix this.

```
  Test Results:

  ✅ All 18 tests are now passing (100% success rate)
  - API endpoint tests: 6/6 ✅
  - Audio processor tests: 5/5 ✅
  - File manager tests: 7/7 ✅

  The warnings about FFmpeg/ffprobe are expected since it's not installed, but the tests pass because we're
  mocking the audio processing functionality where needed.
```












