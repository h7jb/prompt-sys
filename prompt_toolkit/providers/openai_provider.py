"""OpenAI API provider implementation."""

import json
from typing import Dict, Any, Optional
from .base import AIProvider, ProviderConfig, AuthenticationError


class OpenAIProvider(AIProvider):
    """Provider for OpenAI models (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(model="gpt-4")
        super().__init__(config)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        if not self.config.api_key:
            raise AuthenticationError("OpenAI API key not configured")

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt engineering expert. Analyze the given prompt and provide a JSON analysis with: overall_score (0-100), strengths, weaknesses, and improvement_suggestions."
                },
                {"role": "user", "content": f"Analyze this prompt:\n\n{prompt}"}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        try:
            return json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            return {
                "overall_score": 50,
                "strengths": ["Could not parse AI response"],
                "weaknesses": [],
                "improvement_suggestions": [response.choices[0].message.content],
            }

    def improve_prompt(self, prompt: str, instructions: str = "") -> str:
        if not self.config.api_key:
            raise AuthenticationError("OpenAI API key not configured")

        system_msg = "You are an expert prompt engineer. Rewrite and improve the given prompt to make it more effective, clear, and comprehensive."
        user_msg = instructions + "\n\nOriginal prompt:\n" + prompt if instructions else f"Improve this prompt:\n\n{prompt}"

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        if not self.config.api_key:
            raise AuthenticationError("OpenAI API key not configured")

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content

    def is_available(self) -> bool:
        if not self.config.api_key:
            return False
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
