from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the AI provider.
        """
        pass


class MockAIProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        return f"Mock AI response for prompt: {prompt}"