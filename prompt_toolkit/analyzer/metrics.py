"""Metrics computation for prompt analysis.

Provides token counting, readability scores, complexity analysis,
and other quantitative measurements for prompt text.
"""

import re
import math
from typing import Dict, Any, Optional


class PromptMetrics:
    """Compute and store quantitative metrics for a prompt.

    Attributes:
        word_count: Total number of words.
        char_count: Total number of characters (including spaces).
        char_count_no_spaces: Character count excluding spaces.
        sentence_count: Estimated number of sentences.
        avg_word_length: Average characters per word.
        avg_sentence_length: Average words per sentence.
        token_estimates: Token counts for different model encodings.
        reading_time_seconds: Estimated reading time.
        complexity_score: Text complexity score (0-1).
    """

    def __init__(self, text: str):
        self.text = text
        self.word_count = self._count_words()
        self.char_count = len(text)
        self.char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
        self.sentence_count = self._count_sentences()
        self.avg_word_length = self._avg_word_length()
        self.avg_sentence_length = self._avg_sentence_length()
        self.token_estimates = self._estimate_tokens()
        self.reading_time_seconds = self._reading_time()
        self.complexity_score = self._complexity()

    def _count_words(self) -> int:
        return len(self.text.split())

    def _count_sentences(self) -> int:
        sentences = re.split(r'(?:[.!?؟]+(?:\s|$))|(?:\n{2,})', self.text)
        return max(1, len([s for s in sentences if s.strip()]))

    def _avg_word_length(self) -> float:
        words = self.text.split()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    def _avg_sentence_length(self) -> float:
        return self.word_count / max(self.sentence_count, 1)

    def _estimate_tokens(self) -> Dict[str, int]:
        """Estimate token counts using common heuristics.

        Returns:
            Dict with keys like 'gpt4', 'claude', 'gemini' and estimated token counts.
        """
        text = self.text
        return {
            "gpt4": self._estimate_openai_tokens(text),
            "claude": self._estimate_anthropic_tokens(text),
            "gemini": self._estimate_gemini_tokens(text),
            "average": self._estimate_openai_tokens(text),
        }

    def _estimate_openai_tokens(self, text: str) -> int:
        """Rough OpenAI token estimation (~4 chars per token for English, ~2 for CJK/Arabic)."""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z0-9]', text))
        other_chars = len(text) - arabic_chars - english_chars

        arabic_tokens = arabic_chars / 1.5
        english_tokens = english_chars / 4
        other_tokens = other_chars / 3

        return max(1, int(arabic_tokens + english_tokens + other_tokens))

    def _estimate_anthropic_tokens(self, text: str) -> int:
        """Rough Anthropic token estimation."""
        return max(1, int(len(text) / 3.5))

    def _estimate_gemini_tokens(self, text: str) -> int:
        """Rough Gemini token estimation."""
        return max(1, int(len(text) / 3))

    def _reading_time(self) -> float:
        """Estimate reading time in seconds (avg 200 wpm)."""
        return (self.word_count / 200) * 60

    def _complexity(self) -> float:
        """Calculate complexity score (0-1) based on vocabulary and structure.

        Uses average word length, sentence length, and unique vocabulary ratio.
        """
        words = self.text.split()
        if not words:
            return 0.0

        unique_words = len(set(w.lower() for w in words))
        vocab_richness = min(1.0, unique_words / max(self.word_count, 1) * 2)

        sentence_complexity = min(1.0, self.avg_sentence_length / 30)

        word_complexity = min(1.0, self.avg_word_length / 8)

        score = 0.3 * vocab_richness + 0.4 * sentence_complexity + 0.3 * word_complexity
        return round(min(1.0, score), 2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all metrics to a dictionary."""
        return {
            "word_count": self.word_count,
            "char_count": self.char_count,
            "char_count_no_spaces": self.char_count_no_spaces,
            "sentence_count": self.sentence_count,
            "avg_word_length": round(self.avg_word_length, 1),
            "avg_sentence_length": round(self.avg_sentence_length, 1),
            "token_estimates": self.token_estimates,
            "reading_time_seconds": round(self.reading_time_seconds, 1),
            "reading_time_minutes": round(self.reading_time_seconds / 60, 1),
            "complexity_score": self.complexity_score,
        }


def detect_language(text: str) -> str:
    """Detect primary language of the prompt.

    Args:
        text: The prompt text.

    Returns:
        'ar' for Arabic, 'en' for English, 'mixed' for both, 'unknown' otherwise.
    """
    if not text.strip():
        return "unknown"

    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total = arabic_chars + english_chars

    if total == 0:
        return "unknown"

    arabic_ratio = arabic_chars / total
    if arabic_ratio > 0.8:
        return "ar"
    elif arabic_ratio < 0.2:
        return "en"
    else:
        return "mixed"
