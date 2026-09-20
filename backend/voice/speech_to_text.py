import io
import os
import base64
import tempfile
import speech_recognition as sr
from typing import Dict, Any, Optional


class SpeechToTextEngine:
    """Processes audio inputs (WAV, base64, or uploaded files) into transcribed text."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust energy threshold dynamically for microphone input
        self.recognizer.dynamic_energy_threshold = True

    def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en-US") -> Dict[str, Any]:
        """Transcribe raw audio bytes using SpeechRecognition."""
        if not audio_bytes or len(audio_bytes) < 10:
            return {
                "success": False,
                "text": "",
                "error": "Audio data is empty or too short."
            }

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                tf.write(audio_bytes)
                temp_path = tf.name

            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=language)

            return {
                "success": True,
                "text": text.strip(),
                "language": language,
                "confidence": 0.95
            }

        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": "Speech was not understood. Please speak clearly into the microphone."
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "text": "",
                "error": f"Speech recognition service request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Failed to process audio: {str(e)}"
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def transcribe_base64(self, base64_str: str, language: str = "en-US") -> Dict[str, Any]:
        """Transcribe base64-encoded audio data."""
        try:
            # Strip data URL header if present (e.g. data:audio/wav;base64,...)
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            raw_bytes = base64.b64decode(base64_str)
            return self.transcribe_audio_bytes(raw_bytes, language=language)
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Invalid base64 audio payload: {str(e)}"
            }


stt_engine = SpeechToTextEngine()
