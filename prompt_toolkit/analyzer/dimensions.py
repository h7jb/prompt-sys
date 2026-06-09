"""Scoring dimensions for prompt quality evaluation.

Each dimension evaluates a specific aspect of prompt quality
and produces a normalized score (0.0 to 1.0) plus supporting evidence.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import re


class DimensionResult:
    """Result of evaluating a single quality dimension.

    Attributes:
        name: Human-readable dimension name.
        score: Normalized score from 0.0 to 1.0.
        weight: Relative importance weight for this dimension.
        details: List of specific findings (positive or negative).
        suggestions: List of improvement suggestions.
    """

    def __init__(
        self,
        name: str,
        score: float,
        weight: float = 1.0,
        details: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.name = name
        self.score = max(0.0, min(1.0, score))
        self.weight = weight
        self.details = details or []
        self.suggestions = suggestions or []

    @property
    def weighted_score(self) -> float:
        """Return the weight-adjusted score."""
        return self.score * self.weight

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 2),
            "details": self.details,
            "suggestions": self.suggestions,
        }


class BaseDimension(ABC):
    """Abstract base for a single scoring dimension."""

    def __init__(self, weight: float = 1.0):
        self.weight = weight

    @abstractmethod
    def evaluate(self, text: str) -> DimensionResult:
        """Evaluate the given prompt text against this dimension.

        Args:
            text: The prompt content to evaluate.

        Returns:
            A DimensionResult with score and findings.
        """
        ...


class ClarityDimension(BaseDimension):
    """Evaluates overall clarity and specificity of the prompt."""

    AR_PATTERNS = {
        "vague": [
            r"\b(شيء|أشياء|عمل|اعمل|سوي|سو|حاجة|حاجات|كذا)\b",
            r"\b(بعض|شوي|قليل|كثير|كثييير)\b",
        ],
        "specific": [
            r"\b(بالضبط|محدد|دقيق|تفصيل|خطوة|مرحلة)\b",
            r"\b(أرقام|نسب|مؤشرات|مقاييس|معايير)\b",
        ],
    }

    EN_PATTERNS = {
        "vague": [
            r"\b(thing|stuff|something|do|make|create|good|nice|great)\b",
            r"\b(some|a few|many|a lot|little|bit)\b",
        ],
        "specific": [
            r"\b(specific|exact|precise|detailed|step|phase)\b",
            r"\b(numbers|percentages|metrics|criteria|standards)\b",
        ],
    }

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        score = 0.5

        vague_count = 0
        specific_count = 0

        for pattern in self.AR_PATTERNS["vague"]:
            vague_count += len(re.findall(pattern, text_lower))
        for pattern in self.EN_PATTERNS["vague"]:
            vague_count += len(re.findall(pattern, text_lower))
        for pattern in self.AR_PATTERNS["specific"]:
            specific_count += len(re.findall(pattern, text_lower))
        for pattern in self.EN_PATTERNS["specific"]:
            specific_count += len(re.findall(pattern, text_lower))

        if specific_count > vague_count:
            score = 0.8 + min(0.2, specific_count * 0.02)
            details.append("Uses specific, precise language")
        elif vague_count > 3:
            score = max(0.2, 0.5 - vague_count * 0.05)
            details.append("Contains vague or ambiguous terms")
            suggestions.append("Replace vague words with specific, measurable terms")
        else:
            score = 0.5
            details.append("Moderate clarity; could be more specific")

        if specific_count > 0:
            details.append(f"Found {specific_count} precise terms")

        return DimensionResult(
            name="وضوح التعليمات / Clarity",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class RoleDimension(BaseDimension):
    """Evaluates whether a clear role/persona is defined."""

    AR_ROLE_PATTERNS = [
        r"(أنت\s+(خبير|مختص|محترف|مساعد|استشاري|مطور|مصمم|كاتب|محلل))",
        r"(دورك\s+(هو|يكون|أن)\s+)",
        r"(بصفتك\s+(خبير|مختص|محترف|مساعد))",
        r"(اعمل\s+كـ?\s*)",
        r"(تتصرف\s+بصفة\s+)",
    ]

    EN_ROLE_PATTERNS = [
        r"(you\s+are\s+(an?\s+)?(expert|specialist|professional|assistant|consultant|developer|designer|writer|analyst))",
        r"(act\s+as\s+(an?\s+)?)",
        r"(your\s+role\s+(is|will\s+be)\s+)",
        r"(role\s*:\s*)",
        r"(persona\s*:\s*)",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        score = 0.0

        for pattern in self.AR_ROLE_PATTERNS + self.EN_ROLE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                score = 1.0
                details.append(f"Role defined: '{match.group(0).strip()}'")
                break

        if score == 0.0:
            suggestions.append("Add a clear role definition (e.g., 'You are an expert in ...')")
            details.append("No role or persona defined")

        return DimensionResult(
            name="تحديد الدور / Role",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class TaskDimension(BaseDimension):
    """Evaluates whether the task/objective is clearly stated."""

    AR_TASK_PATTERNS = [
        r"(مهمتك|المطلوب|أريد|هدف|الهدف|المطلوب\s+منك)",
        r"(يجب\s+أن\s+تقوم|مطلوب\s+منك|اطلب\s+منك)",
        r"(أحتاج|أرغب|أريد\s+منك)",
    ]

    EN_TASK_PATTERNS = [
        r"(task|objective|goal|mission|purpose)",
        r"(your\s+(task|job|mission|goal|objective)\s+(is|will\s+be))",
        r"(i\s+(want|need|require|would\s+like))",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        has_task = False
        has_subtasks = False
        score = 0.0

        for pattern in self.AR_TASK_PATTERNS + self.EN_TASK_PATTERNS:
            if re.search(pattern, text_lower):
                has_task = True
                details.append("Task/objective clearly stated")
                score = 0.6
                break

        numbered_steps = len(re.findall(r"^\d+[\.\)]", text, re.MULTILINE))
        bullet_steps = len(re.findall(r"^[-*+]\s+", text, re.MULTILINE))

        if numbered_steps >= 3 or bullet_steps >= 3:
            has_subtasks = True
            details.append(f"Task broken into {numbered_steps + bullet_steps} specific steps")
            score = 1.0
        elif numbered_steps >= 1 or bullet_steps >= 1:
            has_subtasks = True
            details.append("Includes some structured sub-tasks")
            score = 0.8

        if not has_task:
            suggestions.append("Clearly state the main task or objective")
            details.append("No clear task or objective found")

        return DimensionResult(
            name="وضوح المهمة / Task",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class ContextDimension(BaseDimension):
    """Evaluates whether sufficient context/background is provided."""

    AR_CONTEXT_PATTERNS = [
        r"(سياق|خلفية|بسبب|لأن|من\s+أجل|لكي|لكيلا)",
        r"(الوضع\s+الحالي|المشكلة|الفرصة|التحدي)",
        r"(المشروع|الفكرة|المنتج|الخدمة|المجال)",
    ]

    EN_CONTEXT_PATTERNS = [
        r"(context|background|because|since|as\s+part\s+of)",
        r"(current\s+(situation|state)|problem|opportunity|challenge)",
        r"(project|idea|product|service|domain|field)",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        score = 0.0
        context_clues = 0

        for pattern in self.AR_CONTEXT_PATTERNS + self.EN_CONTEXT_PATTERNS:
            context_clues += len(re.findall(pattern, text_lower))

        word_count = len(text.split())

        if context_clues >= 4:
            score = 1.0
            details.append("Rich contextual background provided")
        elif context_clues >= 2:
            score = 0.6
            details.append("Some context provided; could be expanded")
        elif context_clues >= 1:
            score = 0.3
            details.append("Minimal context; add background information")
            suggestions.append("Add more context about why this task matters")
        else:
            details.append("No background or context found")
            suggestions.append("Add context: explain the situation, problem, or goal")

        if word_count > 100 and score < 0.6:
            suggestions.append("Use the available length to add more relevant context")

        return DimensionResult(
            name="السياق والمعلومات / Context",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class ConstraintsDimension(BaseDimension):
    """Evaluates whether constraints, rules and boundaries are defined."""

    AR_CONSTRAINTS = [
        r"(قيود|شروط|تجنب|يمنع|ممنوع|لا\s+تقم|لا\s+تستخدم)",
        r"(يجب|يلزم|ضروري|لازم|إلزامي)",
        r"(النبرة|اللغة|الطول|التنسيق|الصيغة)",
    ]

    EN_CONSTRAINTS = [
        r"(constraints?|rules?|limitations?|boundaries|restrictions?)",
        r"(avoid|do\s+not|must\s+not|never|prohibited|banned)",
        r"(must|required|mandatory|necessary)",
        r"(tone|style|format|length|language|voice)",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        constraint_count = 0
        categories_found = set()

        combined = self.AR_CONSTRAINTS + self.EN_CONSTRAINTS
        for pattern in combined:
            matches = re.findall(pattern, text_lower)
            constraint_count += len(matches)
            if matches:
                categories_found.add("general")

        if re.search(r"(avoid|do\s+not|must\s+not|تجنب|يمنع|ممنوع|لا\s+تقم)", text_lower):
            categories_found.add("avoidance")
        if re.search(r"(must|required|يجب|يلزم|ضروري)", text_lower):
            categories_found.add("requirements")
        if re.search(r"(tone|style|format|length|النبرة|اللغة|الطول|التنسيق)", text_lower):
            categories_found.add("format")

        if constraint_count >= 5 and len(categories_found) >= 2:
            score = 1.0
            details.append(f"Comprehensive constraints ({constraint_count} rules in {len(categories_found)} categories)")
        elif constraint_count >= 3:
            score = 0.7
            details.append(f"Some constraints found ({constraint_count} rules)")
        elif constraint_count >= 1:
            score = 0.4
            details.append("Minimal constraints; add more specific rules")
            suggestions.append("Add more specific constraints (tone, length, format, what to avoid)")
        else:
            score = 0.0
            details.append("No constraints or rules defined")
            suggestions.append("Add constraints: tone, length, format, and things to avoid")

        return DimensionResult(
            name="القيود والتعليمات / Constraints",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class ExamplesDimension(BaseDimension):
    """Evaluates whether examples or demonstrations are provided."""

    AR_EXAMPLE_PATTERNS = [
        r"(مثال|أمثلة|على\s+سبيل\s+المثال|توضيح|نموذج)",
        r"(مثل\s+|مثلاً|على\s+س belie\s+المثال|طريقة)",
        r"(نمط|قالب|sample|template)",
    ]

    EN_EXAMPLE_PATTERNS = [
        r"\b(example|sample)\b",
        r"(for\s+example|e\.g\.|for\s+instance)",
        r"(demonstrat|illustrat|showcase)",
        r"\b(template|pattern)\b",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        example_count = 0

        for pattern in self.AR_EXAMPLE_PATTERNS + self.EN_EXAMPLE_PATTERNS:
            example_count += len(re.findall(pattern, text_lower))

        if example_count >= 3:
            score = 1.0
            details.append(f"Multiple examples provided ({example_count})")
        elif example_count >= 1:
            score = 0.6
            details.append(f"Contains at least one example ({example_count} found)")
        else:
            score = 0.0
            details.append("No examples found")
            suggestions.append("Add examples to clarify expected output")

        return DimensionResult(
            name="الأمثلة والتوضيح / Examples",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class OutputFormatDimension(BaseDimension):
    """Evaluates whether output format is clearly specified."""

    AR_FORMAT_PATTERNS = [
        r"(تنسيق|شكل|صيغة|هيكل|تنظيم)\s+(المخرج|الناتج|النتيجة|الإجابة)",
        r"(جدول|قائمة|عناوين|نقاط|فقرات|markdown|json|csv|xml)",
        r"(أخرج|اكتب|قدم|أنشئ)\s+(النتيجة|الإجابة|المخرج)",
    ]

    EN_FORMAT_PATTERNS = [
        r"(format|structure|layout|template)\s+(of\s+)?(the\s+)?(output|response|result|answer)",
        r"(output\s+(format|structure|should\s+be|must\s+be))",
        r"(table|list|bullets?|headings?|paragraphs?|markdown|json|csv|xml)",
        r"(present|write|return|provide|format)\s+(as|in|using)",
    ]

    def evaluate(self, text: str) -> DimensionResult:
        text_lower = text.lower()
        details: List[str] = []
        suggestions: List[str] = []
        format_clues = 0
        format_type = ""

        for pattern in self.AR_FORMAT_PATTERNS:
            if re.search(pattern, text_lower):
                format_clues += 1

        for pattern in self.EN_FORMAT_PATTERNS:
            if re.search(pattern, text_lower):
                format_clues += 1

        format_types = {
            "table": r"(جدول|table|columns?|rows?)",
            "list": r"(قائمة|list|bullets?|نقاط)",
            "json": r"(json|json\s+object|json\s+array)",
            "markdown": r"(markdown|md|ماركداون)",
            "code": r"(code|كود|script|سكريبت)",
            "report": r"(report|تقرير|analysis|تحليل)",
        }

        for fmt_name, pattern in format_types.items():
            if re.search(pattern, text_lower):
                format_type = fmt_name
                break

        if format_clues >= 3:
            score = 1.0
            details.append(f"Output format clearly specified ({format_type or 'structured'})")
        elif format_clues >= 1:
            score = 0.5
            details.append("Output format mentioned but could be more specific")
            suggestions.append("Specify exact output format (table, JSON, markdown, etc.)")
        else:
            score = 0.0
            details.append("No output format specified")
            suggestions.append("Add a clear output format specification")

        return DimensionResult(
            name="تنسيق المخرجات / Output Format",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )


class DetailLevelDimension(BaseDimension):
    """Evaluates the level of detail and depth in the prompt."""

    def evaluate(self, text: str) -> DimensionResult:
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?؟\n]{2,}', text)) + 1
        avg_words_per_sentence = word_count / max(sentence_count, 1)

        details: List[str] = []
        suggestions: List[str] = []

        if word_count < 20:
            score = 0.0
            details.append("Very short prompt (under 20 words)")
            suggestions.append("Expand your prompt with more details and context")
        elif word_count < 50:
            score = 0.3
            details.append(f"Short prompt ({word_count} words)")
            suggestions.append("Add more specific details to improve quality")
        elif word_count < 100:
            score = 0.5
            details.append(f"Moderate length ({word_count} words)")
        elif word_count < 300:
            score = 0.7
            details.append(f"Good detail level ({word_count} words)")
        elif word_count < 800:
            score = 0.9
            details.append(f"Comprehensive prompt ({word_count} words)")
        else:
            score = 0.8
            details.append(f"Very long prompt ({word_count} words) - consider keeping it focused")

        if avg_words_per_sentence < 8:
            details.append("Sentences may be too short or fragmented")
        elif avg_words_per_sentence > 30:
            details.append("Sentences may be too long and complex")
        else:
            details.append("Sentence length is well-balanced")

        return DimensionResult(
            name="مستوى التفاصيل / Detail Level",
            score=score,
            weight=self.weight,
            details=details,
            suggestions=suggestions,
        )
