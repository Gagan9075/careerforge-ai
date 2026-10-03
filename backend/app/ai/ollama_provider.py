import requests

from app.ai.provider import AIProvider
from app.core.config import settings


class OllamaProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{settings.ollama_url}/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]