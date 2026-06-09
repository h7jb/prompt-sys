"""Core analysis engine that orchestrates multi-dimensional evaluation.

Combines all scoring dimensions into a comprehensive prompt quality report.
"""

from typing import List, Dict, Any, Optional
from .dimensions import (
    BaseDimension,
    DimensionResult,
    ClarityDimension,
    RoleDimension,
    TaskDimension,
    ContextDimension,
    ConstraintsDimension,
    ExamplesDimension,
    OutputFormatDimension,
    DetailLevelDimension,
)
from .metrics import PromptMetrics, detect_language


class AnalysisReport:
    """Complete analysis report for a prompt.

    Attributes:
        overall_score: Weighted average score across all dimensions (0-100).
        dimensions: List of individual dimension results.
        metrics: Quantitative metrics for the prompt.
        language: Detected primary language.
        summary: Human-readable summary of the analysis.
        all_suggestions: Aggregated improvement suggestions.
    """

    def __init__(
        self,
        overall_score: float,
        dimensions: List[DimensionResult],
        metrics: PromptMetrics,
        language: str,
    ):
        self.overall_score = overall_score
        self.dimensions = dimensions
        self.metrics = metrics
        self.language = language
        self.summary = self._generate_summary()
        self.all_suggestions = self._collect_suggestions()

    def _generate_summary(self) -> str:
        score = self.overall_score
        if score >= 90:
            return "ممتاز! البرومبت جاهز للاستخدام مع تحسينات بسيطة / Excellent! Ready with minor tweaks."
        elif score >= 75:
            return "جيد جداً - يحتاج بعض التحسينات / Very good - needs some improvements."
        elif score >= 60:
            return "مقبول - يحتاج تحسينات مهمة / Acceptable - needs significant improvements."
        elif score >= 40:
            return "ضعيف - يحتاج إعادة بناء / Weak - needs restructuring."
        else:
            return "غير مناسب - يجب إعادة الكتابة بالكامل / Poor - must be rewritten."

    def _collect_suggestions(self) -> List[str]:
        seen = set()
        suggestions = []
        for dim in self.dimensions:
            for s in dim.suggestions:
                if s not in seen:
                    seen.add(s)
                    suggestions.append(s)
        return suggestions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 1),
            "summary": self.summary,
            "language": self.language,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "metrics": self.metrics.to_dict(),
            "suggestions": self.all_suggestions,
        }


class PromptAnalyzer:
    """Multi-dimensional prompt quality analyzer.

    Orchestrates all scoring dimensions and produces a comprehensive report.

    Args:
        custom_dimensions: Optional list of additional dimensions to include.
    """

    DEFAULT_WEIGHTS = {
        "clarity": 1.0,
        "role": 1.2,
        "task": 1.5,
        "context": 1.0,
        "constraints": 1.3,
        "examples": 0.8,
        "output_format": 1.2,
        "detail_level": 1.0,
    }

    def __init__(self, custom_dimensions: Optional[List[BaseDimension]] = None):
        self._dimensions: List[BaseDimension] = [
            ClarityDimension(weight=self.DEFAULT_WEIGHTS["clarity"]),
            RoleDimension(weight=self.DEFAULT_WEIGHTS["role"]),
            TaskDimension(weight=self.DEFAULT_WEIGHTS["task"]),
            ContextDimension(weight=self.DEFAULT_WEIGHTS["context"]),
            ConstraintsDimension(weight=self.DEFAULT_WEIGHTS["constraints"]),
            ExamplesDimension(weight=self.DEFAULT_WEIGHTS["examples"]),
            OutputFormatDimension(weight=self.DEFAULT_WEIGHTS["output_format"]),
            DetailLevelDimension(weight=self.DEFAULT_WEIGHTS["detail_level"]),
        ]
        if custom_dimensions:
            self._dimensions.extend(custom_dimensions)

    def analyze(self, text: str) -> AnalysisReport:
        """Analyze the given prompt text.

        Args:
            text: The prompt content to analyze.

        Returns:
            Complete AnalysisReport with scores, metrics, and suggestions.
        """
        metrics = PromptMetrics(text)
        language = detect_language(text)

        results: List[DimensionResult] = []
        total_weight = 0.0
        weighted_sum = 0.0

        for dim in self._dimensions:
            result = dim.evaluate(text)
            results.append(result)
            weighted_sum += result.weighted_score
            total_weight += result.weight

        overall_score = (weighted_sum / total_weight * 100) if total_weight > 0 else 0.0
        overall_score = max(0.0, min(100.0, overall_score))

        return AnalysisReport(
            overall_score=overall_score,
            dimensions=results,
            metrics=metrics,
            language=language,
        )

    def analyze_file(self, file_path: str) -> AnalysisReport:
        """Analyze a prompt from a file.

        Args:
            file_path: Path to a text/markdown file.

        Returns:
            AnalysisReport for the file contents.
        """
        from pathlib import Path
        text = Path(file_path).read_text(encoding="utf-8")
        return self.analyze(text)
