import assemblyai as aai
import logging

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text."""
        try:
            transcript = self.transcriber.transcribe(audio_bytes)
            return transcript.text
        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return ""
