"""Abstract base provider for unified AI model interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class ProviderConfig:
    """Configuration for an AI provider.

    Attributes:
        api_key: API key for authentication.
        model: Model name/identifier.
        endpoint: Custom endpoint URL (for Ollama and compatible APIs).
        temperature: Generation temperature (0.0 - 1.0).
        max_tokens: Maximum tokens in response.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "",
        endpoint: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.temperature = temperature
        self.max_tokens = max_tokens


class AIProvider(ABC):
    """Abstract base class for all AI model providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Send a prompt for AI-powered analysis.

        Args:
            prompt: The prompt text to analyze.

        Returns:
            Dict with analysis results from the AI.

        Raises:
            ConnectionError: If unable to reach the API.
            AuthenticationError: If API key is invalid.
        """
        ...

    @abstractmethod
    def improve_prompt(self, prompt: str, instructions: str = "") -> str:
        """Ask the AI to improve a given prompt.

        Args:
            prompt: The prompt to improve.
            instructions: Optional additional instructions for the improvement.

        Returns:
            Improved prompt text.
        """
        ...

    @abstractmethod
    def generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the AI model.

        Args:
            system_prompt: System-level instructions.
            user_message: The user's message/query.

        Returns:
            The model's response text.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and reachable.

        Returns:
            True if the provider can be used.
        """
        ...

    @staticmethod
    def estimate_cost(text: str, model: str = "") -> float:
        """Estimate the cost of processing the given text.

        Args:
            text: Input text.
            model: Target model name.

        Returns:
            Estimated cost in USD.
        """
        return 0.0


class AuthenticationError(Exception):
    """Raised when API authentication fails."""
    pass
