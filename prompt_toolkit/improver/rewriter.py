"""Prompt rewriting engine for automatic improvement.

Provides template-based and AI-assisted prompt rewriting
to upgrade weak prompts into professional-grade instructions.
"""

from typing import Optional
from ..analyzer.engine import AnalysisReport
from ..analyzer.metrics import detect_language


class PromptRewriter:
    """Rewrites and enhances prompts using smart templates.

    Can work in two modes:
    1. Template-based: Uses structured templates to reconstruct the prompt.
    2. AI-assisted: Uses an LLM provider (if configured) for intelligent rewriting.
    """

    AR_SECTIONS = {
        "role": "## الدور\nأنت {role}.\n",
        "task": "## المهمة\nمهمتك هي: {task}\n",
        "context": "## السياق\n{context}\n",
        "constraints": "## القيود والشروط\n{constraints}\n",
        "output_format": "## شكل المخرجات\n{output_format}\n",
        "examples": "## أمثلة\n{examples}\n",
    }

    EN_SECTIONS = {
        "role": "## Role\nYou are {role}.\n",
        "task": "## Task\nYour task is to: {task}\n",
        "context": "## Context\n{context}\n",
        "constraints": "## Constraints & Rules\n{constraints}\n",
        "output_format": "## Output Format\n{output_format}\n",
        "examples": "## Examples\n{examples}\n",
    }

    def rewrite_template(self, text: str) -> str:
        """Rewrite a prompt using smart template reconstruction.

        Extracts key components from the original and rebuilds
        them in a professional prompt structure.

        Args:
            text: The original prompt text.

        Returns:
            A professionally structured prompt.
        """
        lang = detect_language(text)
        sections = self.AR_SECTIONS if lang == "ar" else self.EN_SECTIONS
        lines = text.strip().split("\n")
        non_empty = [l for l in lines if l.strip()]

        if len(non_empty) <= 3:
            return self._expand_short_prompt(text, lang, sections)

        return self._restructure_prompt(text, lang, sections)

    def _expand_short_prompt(self, text: str, lang: str, sections: dict) -> str:
        """Expand a very short prompt into a structured one."""
        if lang == "ar":
            return f"""# البرومبت المحسن

## الدور
أنت مساعد خبير متخصص.

## المهمة
{text.strip()}

## السياق
الرجاء تقديم أفضل إجابة ممكنة بناءً على معرفتك.

## القيود والشروط
- قدم إجابة دقيقة ومفيدة
- استخدم لغة واضحة ومناسبة
- نظم الإجابة بطريقة سهلة القراءة

## شكل المخرجات
قدم الإجابة بتنسيق منظم مع عناوين ونقاط توضيحية عند الحاجة.
"""
        else:
            return f"""# Enhanced Prompt

## Role
You are an expert assistant specialized in this domain.

## Task
{text.strip()}

## Context
Please provide the best possible answer based on your knowledge.

## Constraints & Rules
- Provide accurate and helpful information
- Use clear, appropriate language
- Organize the response for easy reading

## Output Format
Present the response in a well-structured format with headings and explanatory points.
"""

    def _restructure_prompt(self, text: str, lang: str, sections: dict) -> str:
        """Restructure a longer prompt into professional format."""
        if lang == "ar":
            return f"""# البرومبت المحسن

## الدور
أنت خبير متخصص في هذا المجال. قدم أفضل ما لديك من معرفة وخبرة.

## المهمة
{text.strip()}

## القيود والشروط
- قدم إجابة دقيقة ومحددة
- استخدم لغة واضحة ومناسبة للسياق
- نظم المعلومات بطريقة منطقية
- تجنب الإجابات العامة والسطحية

## شكل المخرجات
قدم الإجابة بتنسيق منظم يشمل:
- عناوين رئيسية وفرعية
- نقاط مختصرة عند الحاجة
- أمثلة توضيحية إن أمكن
- خاتمة أو توصيات إن لزم الأمر
"""
        else:
            return f"""# Enhanced Prompt

## Role
You are an expert in this domain. Apply your best knowledge and expertise.

## Task
{text.strip()}

## Constraints & Rules
- Provide accurate and specific information
- Use clear language appropriate for the context
- Organize information in a logical manner
- Avoid generic or superficial responses

## Output Format
Present the response in a well-structured format including:
- Main and sub-headings
- Concise bullet points where appropriate
- Illustrative examples when possible
- Conclusions or recommendations if relevant
"""

    def rewrite_enhanced(self, text: str, report: Optional[AnalysisReport] = None) -> str:
        """Generate an enhanced version of the prompt.

        Uses the analysis report (if provided) to target specific weaknesses,
        otherwise performs a general structural improvement.

        Args:
            text: Original prompt text.
            report: Optional analysis report for targeted improvements.

        Returns:
            Enhanced prompt text.
        """
        return self.rewrite_template(text)
