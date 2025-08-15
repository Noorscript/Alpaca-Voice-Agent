import base64
import logging
import requests

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.murf.ai/v1/speech/generate"

    def generate_audio(self, text: str, voice_id: str) -> str:
        """Generate audio URL from text."""
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }
        payload = {"text": text, "voice_id": voice_id}

        resp = requests.post(self.api_url, json=payload, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Murf API failed: {resp.text}")

        audio_url = resp.json().get("audioFile")
        if not audio_url:
            raise Exception("No audioFile returned from Murf")
        return audio_url

    def fallback_audio_base64(self, fallback_text: str) -> str | None:
        """Fallback to default Murf voice and return base64 audio."""
        try:
            audio_url = self.generate_audio(fallback_text, "en-US-natalie")
            audio_file_resp = requests.get(audio_url)
            return base64.b64encode(audio_file_resp.content).decode("utf-8")
        except Exception as e:
            logger.error(f"Murf fallback failed: {e}")
            return None
