"""Configuration management for Prompt Toolkit.

Handles API keys, model preferences, and user settings
with support for environment variables and config files.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


DEFAULT_CONFIG = {
    "openai_api_key": "",
    "openai_model": "gpt-4",
    "gemini_api_key": "",
    "gemini_model": "gemini-pro",
    "ollama_endpoint": "http://localhost:11434",
    "ollama_model": "llama2",
    "default_provider": "none",
    "language": "auto",
    "token_limit_warning": 4000,
    "theme": "default",
    "library_path": "",
}


def get_config_path() -> Path:
    """Return the path to the configuration file."""
    return Path.home() / ".prompt_toolkit" / "config.json"


def get_library_path() -> Path:
    """Return the path to the prompt library storage file."""
    return Path.home() / ".prompt_toolkit" / "library.json"


def ensure_config_dir() -> None:
    """Create configuration directory if it does not exist."""
    get_config_path().parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from file, merging with defaults.

    Returns:
        Dict with all configuration values.
    """
    config = dict(DEFAULT_CONFIG)
    config_path = get_config_path()
    if config_path.exists():
        try:
            user_config = json.loads(config_path.read_text(encoding="utf-8"))
            config.update(user_config)
        except (json.JSONDecodeError, OSError):
            pass

    config["openai_api_key"] = config["openai_api_key"] or os.getenv("OPENAI_API_KEY", "")
    config["gemini_api_key"] = config["gemini_api_key"] or os.getenv("GEMINI_API_KEY", "")

    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file.

    Args:
        config: Configuration dictionary to persist.
    """
    ensure_config_dir()
    safe_config = {k: v for k, v in config.items() if k in DEFAULT_CONFIG}
    get_config_path().write_text(
        json.dumps(safe_config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
