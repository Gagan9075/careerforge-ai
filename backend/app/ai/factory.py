from app.ai.ollama_provider import OllamaProvider
from app.ai.provider import AIProvider, MockAIProvider


def get_ai_provider() -> AIProvider:
    from app.core.config import settings

    provider = settings.ai_provider.lower()

    if provider == "mock":
        return MockAIProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported AI provider: {settings.ai_provider}"
    )