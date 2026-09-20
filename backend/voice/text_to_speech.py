import io
import os
import re
import base64
import tempfile
from typing import Dict, Any, Optional
from gtts import gTTS


class TextToSpeechEngine:
    """Synthesizes text into spoken audio files or base64 audio data for browser playback."""

    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang

    def clean_text_for_speech(self, text: str) -> str:
        """Strip markdown syntax, code blocks, and symbols that sound strange when spoken."""
        # Remove code blocks ```...```
        clean = re.sub(r"```[\s\S]*?```", " [Code snippet provided on screen] ", text)
        # Remove inline code backticks `...`
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        # Remove markdown headers, bullets, bolding
        clean = re.sub(r"(?:^|\s)[#*~>]+\s*", " ", clean)
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean)
        clean = re.sub(r"\*([^*]+)\*", r"\1", clean)
        # Remove URLs
        clean = re.sub(r"https?://\S+", "link provided", clean)
        # Collapse multiple whitespaces
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean or "I have processed your request."


    def synthesize_to_bytes(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Convert text into MP3 audio bytes using gTTS."""
        spoken_text = self.clean_text_for_speech(text)
        lang = language or self.default_lang

        try:
            tts = gTTS(text=spoken_text, lang=lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

            return {
                "success": True,
                "spoken_text": spoken_text,
                "audio_base64": f"data:audio/mpeg;base64,{b64_audio}",
                "mime_type": "audio/mpeg",
                "size_bytes": len(audio_bytes)
            }
        except Exception as e:
            return {
                "success": False,
                "spoken_text": spoken_text,
                "error": f"TTS synthesis failed: {str(e)}",
                "audio_base64": None
            }

    def synthesize_to_file(self, text: str, output_path: str, language: Optional[str] = None) -> bool:
        """Save synthesized audio directly to a file."""
        spoken_text = self.clean_text_for_speech(text)
        lang = language or self.default_lang
        try:
            tts = gTTS(text=spoken_text, lang=lang, slow=False)
            tts.save(output_path)
            return True
        except Exception:
            return False


tts_engine = TextToSpeechEngine()
