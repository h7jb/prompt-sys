"""Smart suggestion engine for prompt improvements.

Analyzes prompt weaknesses and generates targeted,
actionable improvement suggestions with alternative phrasings.
"""

import re
from typing import List, Dict, Optional, Tuple
from ..analyzer.engine import AnalysisReport
from ..analyzer.metrics import detect_language


class Suggestion:
    """A single improvement suggestion with context.

    Attributes:
        category: The dimension/section this suggestion relates to.
        issue: Description of the identified problem.
        recommendation: What the user should do.
        example: Optional before/after example.
        priority: 'high', 'medium', or 'low'.
    """

    def __init__(
        self,
        category: str,
        issue: str,
        recommendation: str,
        example: Optional[str] = None,
        priority: str = "medium",
    ):
        self.category = category
        self.issue = issue
        self.recommendation = recommendation
        self.example = example
        self.priority = priority

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "issue": self.issue,
            "recommendation": self.recommendation,
            "example": self.example,
            "priority": self.priority,
        }


class ImprovementPlan:
    """Complete improvement plan with prioritized suggestions.

    Attributes:
        original_prompt: The original prompt text.
        suggestions: List of improvement suggestions.
        critical_count: Number of high-priority issues.
        rewritten_prompt: Optional rewritten version of the prompt.
    """

    def __init__(
        self,
        original_prompt: str,
        suggestions: List[Suggestion],
        rewritten_prompt: Optional[str] = None,
    ):
        self.original_prompt = original_prompt
        self.suggestions = suggestions
        self.critical_count = sum(1 for s in suggestions if s.priority == "high")
        self.rewritten_prompt = rewritten_prompt

    def to_dict(self) -> dict:
        return {
            "original_prompt": self.original_prompt,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "critical_count": self.critical_count,
            "rewritten_prompt": self.rewritten_prompt,
        }


class SuggestionEngine:
    """Generates targeted improvement suggestions based on analysis."""

    AR_TEMPLATES = {
        "role": {
            "missing": "أضف دوراً واضحاً للمساعد. مثال: 'أنت خبير في {field} متخصص في {specialty}'",
            "weak": "حدد الدور بدقة أكبر. بدلاً من 'خبير'، قل 'خبير {field} لديه {years} سنوات خبرة'",
        },
        "task": {
            "missing": "حدد المهمة الرئيسية بوضوح. ابدأ بـ 'أريد منك أن تقوم بـ ...' أو 'مهمتك هي ...'",
            "vague": "قسّم المهمة إلى خطوات محددة وقابلة للتنفيذ. استخدم أرقاماً أو نقاطاً.",
        },
        "context": {
            "missing": "أضف معلومات السياق: لماذا تحتاج هذا؟ ما الخلفية؟ ما المشكلة التي تحلها؟",
            "weak": "وسّع السياق. اشرح الوضع الحالي، التحديات، والنتيجة المتوقعة.",
        },
        "constraints": {
            "missing": "حدد القيود: اللغة، النبرة، الطول، التنسيق، والأشياء الممنوعة.",
            "weak": "أضف قيوداً أكثر تحديداً. مثلاً: 'لا يتجاوز 500 كلمة'، 'بأسلوب رسمي'",
        },
        "examples": {
            "missing": "أضف مثالاً واحداً على الأقل لتوضيح النتيجة المتوقعة.",
            "weak": "قدّم أمثلة أكثر تنوعاً تغطي حالات مختلفة.",
        },
        "output_format": {
            "missing": "حدد بوضوح كيف تريد أن تكون النتيجة: جدول، قائمة، تقرير، كود...",
            "weak": "كن أكثر تحديداً في تنسيق المخرج. مثلاً: 'على شكل جدول فيه 3 أعمدة'",
        },
    }

    EN_TEMPLATES = {
        "role": {
            "missing": "Add a clear role for the AI. Example: 'You are an expert {field} specializing in {specialty}'",
            "weak": "Be more specific about the role. Instead of 'expert', say 'Senior {field} with {years} years of experience'",
        },
        "task": {
            "missing": "State the main task clearly. Start with 'Your task is to...' or 'I need you to...'",
            "vague": "Break the task into specific, actionable steps using numbers or bullet points.",
        },
        "context": {
            "missing": "Add context: Why do you need this? What is the background? What problem are you solving?",
            "weak": "Expand the context. Explain the current situation, challenges, and expected outcome.",
        },
        "constraints": {
            "missing": "Specify constraints: language, tone, length, format, and prohibited elements.",
            "weak": "Add more specific constraints. For example: 'Keep under 500 words', 'Use formal tone'",
        },
        "examples": {
            "missing": "Add at least one example to illustrate the expected output.",
            "weak": "Provide more diverse examples covering different cases.",
        },
        "output_format": {
            "missing": "Clearly specify the output format: table, list, report, code...",
            "weak": "Be more specific about formatting. For example: 'A 3-column table with headers'",
        },
    }

    def generate(self, report: AnalysisReport) -> List[Suggestion]:
        """Generate improvement suggestions from an analysis report.

        Args:
            report: AnalysisReport from the PromptAnalyzer.

        Returns:
            List of Suggestion objects ordered by priority.
        """
        lang = report.language if report.language in ("ar", "en") else "en"
        templates = self.AR_TEMPLATES if lang == "ar" else self.EN_TEMPLATES
        suggestions: List[Suggestion] = []

        dim_map = {
            "تحديد الدور / Role": "role",
            "وضوح المهمة / Task": "task",
            "السياق والمعلومات / Context": "context",
            "القيود والتعليمات / Constraints": "constraints",
            "الأمثلة والتوضيح / Examples": "examples",
            "تنسيق المخرجات / Output Format": "output_format",
        }

        for dim in report.dimensions:
            key = dim_map.get(dim.name)
            if key is None:
                continue

            if dim.score < 0.3:
                if key in templates and "missing" in templates[key]:
                    issue = dim.details[0] if dim.details else f"{dim.name}: needs improvement"
                    suggestions.append(Suggestion(
                        category=dim.name,
                        issue=issue,
                        recommendation=templates[key]["missing"],
                        priority="high",
                    ))
            elif dim.score < 0.7:
                if key in templates and "weak" in templates[key]:
                    issue = dim.details[0] if dim.details else f"{dim.name}: could be stronger"
                    suggestions.append(Suggestion(
                        category=dim.name,
                        issue=issue,
                        recommendation=templates[key]["weak"],
                        priority="medium",
                    ))

        suggestions.sort(key=lambda s: {"high": 0, "medium": 1, "low": 2}[s.priority])
        return suggestions

    def generate_plan(self, report: AnalysisReport, text: str) -> ImprovementPlan:
        """Generate a complete improvement plan.

        Args:
            report: Analysis from PromptAnalyzer.
            text: Original prompt text.

        Returns:
            ImprovementPlan with suggestions (and optionally a rewritten prompt).
        """
        suggestions = self.generate(report)
        return ImprovementPlan(
            original_prompt=text,
            suggestions=suggestions,
        )
