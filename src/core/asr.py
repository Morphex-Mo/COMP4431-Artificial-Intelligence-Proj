"""
Automatic Speech Recognition module
"""

import speech_recognition as sr
import whisper
import io
import tempfile
import os
from typing import Optional
from config.settings import settings

class ASRProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
    
    def transcribe_audio(self, audio_data: bytes, method: str = "whisper") -> Optional[str]:
        """
        Transcribe audio to text using specified method
        
        Args:
            audio_data: Raw audio bytes
            method: "whisper" or "google"
        
        Returns:
            Transcribed text or None if failed
        """
        try:
            if method == "whisper":
                return self._whisper_transcribe(audio_data)
            elif method == "google":
                return self._google_transcribe(audio_data)
        except Exception as e:
            print(f"ASR Error: {e}")
            return None
    
    def _whisper_transcribe(self, audio_data: bytes) -> str:
        """Transcribe using Whisper model"""
        # Whisper needs a file path, not BytesIO
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            try:
                result = self.whisper_model.transcribe(temp_file.name)
                return result["text"]
            finally:
                os.unlink(temp_file.name)
    
    def _google_transcribe(self, audio_data: bytes) -> str:
        """Transcribe using Google Speech Recognition"""
        audio = sr.AudioData(audio_data, 16000, 2)
        return self.recognizer.recognize_google(audio)
