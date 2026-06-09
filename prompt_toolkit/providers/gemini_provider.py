"""Google Gemini API provider implementation."""

import json
from typing import Dict, Any, Optional
from .base import AIProvider, ProviderConfig, AuthenticationError


class GeminiProvider(AIProvider):
    """Provider for Google Gemini models."""

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(model="gemini-pro")
        super().__init__(config)
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self._model = genai.GenerativeModel(self.config.model)
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        return self._model

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        if not self.config.api_key:
            raise AuthenticationError("Gemini API key not configured")

        response = self.model.generate_content(
            f"You are a prompt engineering expert. Analyze the given prompt and provide a JSON analysis with: overall_score (0-100), strengths, weaknesses, and improvement_suggestions.\n\nAnalyze this prompt:\n\n{prompt}"
        )
        try:
            return json.loads(response.text)
        except (json.JSONDecodeError, AttributeError):
            return {
                "overall_score": 50,
                "strengths": [],
                "weaknesses": [],
                "improvement_suggestions": [response.text],
            }

    def improve_prompt(self, prompt: str, instructions: str = "") -> str:
        if not self.config.api_key:
            raise AuthenticationError("Gemini API key not configured")

        user_msg = instructions + "\n\n" + prompt if instructions else f"Improve this prompt:\n\n{prompt}"
        response = self.model.generate_content(
            f"You are an expert prompt engineer. Rewrite and improve the given prompt to make it more effective, clear, and comprehensive.\n\n{user_msg}"
        )
        return response.text

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        if not self.config.api_key:
            raise AuthenticationError("Gemini API key not configured")

        response = self.model.generate_content(
            f"{system_prompt}\n\n{user_message}"
        )
        return response.text

    def is_available(self) -> bool:
        if not self.config.api_key:
            return False
        try:
            self.model.generate_content("test")
            return True
        except Exception:
            return False
