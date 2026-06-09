"""Ollama API provider implementation for local LLMs."""

import json
from typing import Dict, Any, Optional
from .base import AIProvider, ProviderConfig, AuthenticationError


class OllamaProvider(AIProvider):
    """Provider for locally-hosted Ollama models."""

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(
                model="llama2",
                endpoint="http://localhost:11434",
            )
        super().__init__(config)

    def _request(self, payload: dict) -> dict:
        """Send a request to the Ollama API."""
        import urllib.request
        import urllib.error

        url = f"{self.config.endpoint.rstrip('/')}/api/generate"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"Ollama API error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach Ollama at {self.config.endpoint}: {e.reason}")

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        response = self._request({
            "model": self.config.model,
            "prompt": f"You are a prompt engineering expert. Analyze the given prompt and provide a JSON analysis with: overall_score (0-100), strengths, weaknesses, and improvement_suggestions.\n\nAnalyze this prompt:\n\n{prompt}",
            "stream": False,
        })
        try:
            return json.loads(response.get("response", "{}"))
        except (json.JSONDecodeError, AttributeError):
            return {
                "overall_score": 50,
                "strengths": [],
                "weaknesses": [],
                "improvement_suggestions": [response.get("response", "")],
            }

    def improve_prompt(self, prompt: str, instructions: str = "") -> str:
        user_msg = instructions + "\n\n" + prompt if instructions else f"Improve this prompt:\n\n{prompt}"
        response = self._request({
            "model": self.config.model,
            "prompt": f"You are an expert prompt engineer. Rewrite and improve the given prompt.\n\n{user_msg}",
            "stream": False,
        })
        return response.get("response", "")

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        response = self._request({
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{user_message}",
            "stream": False,
        })
        return response.get("response", "")

    def is_available(self) -> bool:
        try:
            self._request({"model": self.config.model, "prompt": "test", "stream": False})
            return True
        except Exception:
            return False
