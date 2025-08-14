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
