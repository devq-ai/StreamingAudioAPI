import speech_recognition as sr
from pydub import AudioSegment as PydubAudioSegment
from pydub.silence import detect_nonsilent
import io
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
import asyncio
import concurrent.futures

from .models import AudioSegment
from .config import (
    SAMPLE_RATE, 
    SILENCE_THRESHOLD, 
    SENTENCE_MIN_LENGTH, 
    SENTENCE_MAX_LENGTH,
    SPEECH_RECOGNITION_LANGUAGE
)

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    def _load_audio(self, file_path: Path) -> PydubAudioSegment:
        """Load MP3 audio file."""
        return PydubAudioSegment.from_mp3(file_path)
    
    def _detect_speech_segments(self, audio: PydubAudioSegment) -> List[Tuple[int, int]]:
        """Detect non-silent segments in audio."""
        # Convert to mono and set sample rate
        audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
        
        # Detect non-silent chunks
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=SILENCE_THRESHOLD,
            silence_thresh=audio.dBFS - 16
        )
        
        return nonsilent_ranges
    
    def _transcribe_audio_segment(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio segment to text."""
        try:
            # Create a temporary WAV file for speech recognition
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert MP3 data to WAV for speech recognition
                audio_segment = PydubAudioSegment.from_mp3(io.BytesIO(audio_data))
                audio_segment = audio_segment.set_channels(1).set_frame_rate(SAMPLE_RATE)
                audio_segment.export(temp_file.name, format="wav")
                
                # Transcribe using speech recognition
                with sr.AudioFile(temp_file.name) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(
                        audio, 
                        language=SPEECH_RECOGNITION_LANGUAGE
                    )
                    
                # Clean up temp file
                Path(temp_file.name).unlink()
                return text
                
        except (sr.UnknownValueError, sr.RequestError, Exception):
            return None
    
    def _split_by_sentences(self, audio: PydubAudioSegment, speech_ranges: List[Tuple[int, int]]) -> List[Tuple[PydubAudioSegment, str]]:
        """Split audio into sentence-based segments using speech-to-text."""
        segments = []
        
        for start_ms, end_ms in speech_ranges:
            # Extract audio segment
            segment_audio = audio[start_ms:end_ms]
            
            # Skip very short or very long segments
            duration_seconds = len(segment_audio) / 1000.0
            if duration_seconds < SENTENCE_MIN_LENGTH or duration_seconds > SENTENCE_MAX_LENGTH:
                continue
            
            # Export segment to bytes for transcription
            buffer = io.BytesIO()
            segment_audio.export(buffer, format="mp3")
            audio_data = buffer.getvalue()
            
            # Transcribe segment
            text = self._transcribe_audio_segment(audio_data)
            
            # If transcription successful and contains sentence-ending punctuation
            if text and any(punct in text for punct in ['.', '!', '?']):
                segments.append((segment_audio, text))
            elif text:  # Include segments with text even without punctuation
                segments.append((segment_audio, text))
        
        return segments
    
    async def process_audio_file(self, file_path: Path, file_hash: str) -> List[AudioSegment]:
        """Process audio file and return list of sentence segments."""
        loop = asyncio.get_event_loop()
        
        # Load audio file
        audio = await loop.run_in_executor(self.executor, self._load_audio, file_path)
        
        # Detect speech segments
        speech_ranges = await loop.run_in_executor(
            self.executor, 
            self._detect_speech_segments, 
            audio
        )
        
        # Split into sentence segments
        sentence_segments = await loop.run_in_executor(
            self.executor,
            self._split_by_sentences,
            audio,
            speech_ranges
        )
        
        # Create AudioSegment objects
        segments = []
        timestamp = datetime.now()
        
        for sequence, (segment_audio, text) in enumerate(sentence_segments):
            # Export segment to bytes
            buffer = io.BytesIO()
            segment_audio.export(buffer, format="mp3")
            
            # Calculate segment length
            length_seconds = len(segment_audio) / 1000.0
            
            segment = AudioSegment(
                file_hash=file_hash,
                timestamp=timestamp,
                filename_sequence=sequence,
                length_seconds=length_seconds,
                text_content=text,
                file_path=""  # Will be set after saving
            )
            
            segments.append((segment, buffer.getvalue()))
        
        return segments
    
    async def process_audio_stream(self, audio_data: bytes, file_hash: str, sequence_offset: int = 0) -> List[AudioSegment]:
        """Process streaming audio data."""
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = Path(temp_file.name)
        
        try:
            # Process the temporary file
            segments = await self.process_audio_file(temp_path, file_hash)
            
            # Adjust sequence numbers
            for i, (segment, _) in enumerate(segments):
                segment.filename_sequence += sequence_offset
            
            return segments
        finally:
            # Clean up temporary file
            temp_path.unlink()

# Global audio processor instance
audio_processor = AudioProcessor()
