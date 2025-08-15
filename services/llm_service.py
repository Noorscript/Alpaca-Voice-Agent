import logging
from google import genai

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_reply(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """Generate LLM text reply."""
        try:
            resp = self.client.models.generate_content(model=model, contents=prompt)
            return resp.text.strip()
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""
