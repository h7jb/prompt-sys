"""Provider factory - creates the appropriate AI provider based on configuration."""

from typing import Optional
from ..config import load_config
from .base import AIProvider, ProviderConfig
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider


def create_provider(provider_name: str = "") -> Optional[AIProvider]:
    """Create an AI provider based on configuration.

    Args:
        provider_name: One of 'openai', 'gemini', 'ollama', or '' for auto-detect.

    Returns:
        An initialized AIProvider, or None if no provider is available.

    Examples:
        >>> provider = create_provider("openai")
        >>> if provider and provider.is_available():
        ...     result = provider.improve_prompt("Write code")
    """
    config = load_config()
    name = provider_name or config.get("default_provider", "")

    if name == "openai" or (not name and config.get("openai_api_key")):
        return OpenAIProvider(ProviderConfig(
            api_key=config.get("openai_api_key", ""),
            model=config.get("openai_model", "gpt-4"),
            temperature=0.7,
            max_tokens=2048,
        ))

    if name == "gemini" or (not name and config.get("gemini_api_key")):
        return GeminiProvider(ProviderConfig(
            api_key=config.get("gemini_api_key", ""),
            model=config.get("gemini_model", "gemini-pro"),
            temperature=0.7,
            max_tokens=2048,
        ))

    if name == "ollama" or (not name):
        return OllamaProvider(ProviderConfig(
            model=config.get("ollama_model", "llama2"),
            endpoint=config.get("ollama_endpoint", "http://localhost:11434"),
            temperature=0.7,
            max_tokens=2048,
        ))

    return None


def get_available_providers() -> list:
    """List all configured and available providers.

    Returns:
        List of provider names that are available for use.
    """
    available = []
    for name in ("openai", "gemini", "ollama"):
        provider = create_provider(name)
        if provider and provider.is_available():
            available.append(name)
    return available
