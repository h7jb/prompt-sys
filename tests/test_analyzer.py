"""Unit tests for the Prompt Analyzer engine and dimensions."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prompt_toolkit.analyzer.engine import PromptAnalyzer
from prompt_toolkit.analyzer.dimensions import (
    RoleDimension,
    TaskDimension,
    ContextDimension,
    ConstraintsDimension,
    ExamplesDimension,
    OutputFormatDimension,
    DetailLevelDimension,
    ClarityDimension,
)
from prompt_toolkit.analyzer.metrics import PromptMetrics, detect_language


class TestMetrics(unittest.TestCase):
    """Test quantitative metrics computation."""

    def test_word_count(self):
        m = PromptMetrics("Hello world")
        self.assertEqual(m.word_count, 2)

    def test_word_count_arabic(self):
        m = PromptMetrics("مرحبا بالعالم")
        self.assertEqual(m.word_count, 2)

    def test_char_count(self):
        m = PromptMetrics("Hello")
        self.assertEqual(m.char_count, 5)

    def test_sentence_count(self):
        m = PromptMetrics("First sentence. Second sentence. Third!")
        self.assertEqual(m.sentence_count, 3)

    def test_reading_time(self):
        m = PromptMetrics("word " * 200)
        self.assertAlmostEqual(m.reading_time_seconds, 60, delta=5)

    def test_token_estimate_gpt4(self):
        m = PromptMetrics("Hello world, this is a test.")
        self.assertGreater(m.token_estimates["gpt4"], 0)

    def test_complexity_score(self):
        m = PromptMetrics("This is a simple test with basic words only.")
        self.assertGreaterEqual(m.complexity_score, 0)
        self.assertLessEqual(m.complexity_score, 1)

    def test_complexity_empty(self):
        m = PromptMetrics("")
        self.assertEqual(m.complexity_score, 0.0)

    def test_empty_metrics(self):
        m = PromptMetrics("")
        self.assertEqual(m.word_count, 0)
        self.assertEqual(m.char_count, 0)


class TestLanguageDetection(unittest.TestCase):
    """Test language detection."""

    def test_detect_arabic(self):
        text = "مرحبا بكم في هذا البرنامج التعليمي"
        self.assertEqual(detect_language(text), "ar")

    def test_detect_english(self):
        text = "Welcome to this educational program"
        self.assertEqual(detect_language(text), "en")

    def test_detect_mixed(self):
        text = "مرحبا world هذا test"
        self.assertEqual(detect_language(text), "mixed")

    def test_detect_unknown(self):
        text = "12345 !!!"
        self.assertEqual(detect_language(text), "unknown")

    def test_empty(self):
        self.assertEqual(detect_language(""), "unknown")


class TestDimensions(unittest.TestCase):
    """Test individual scoring dimensions."""

    def test_role_dimension_found_ar(self):
        dim = RoleDimension()
        result = dim.evaluate("أنت خبير في تحليل البيانات")
        self.assertGreater(result.score, 0.5)

    def test_role_dimension_found_en(self):
        dim = RoleDimension()
        result = dim.evaluate("You are an expert data analyst")
        self.assertGreater(result.score, 0.5)

    def test_role_dimension_missing(self):
        dim = RoleDimension()
        result = dim.evaluate("Do this task for me")
        self.assertAlmostEqual(result.score, 0.0)

    def test_task_dimension_found(self):
        dim = TaskDimension()
        result = dim.evaluate("Your task is to analyze the data")
        self.assertGreater(result.score, 0.5)

    def test_task_with_steps(self):
        dim = TaskDimension()
        text = """Your tasks:
1. Analyze the data
2. Create a report
3. Present findings"""
        result = dim.evaluate(text)
        self.assertGreater(result.score, 0.8)

    def test_task_dimension_missing(self):
        dim = TaskDimension()
        result = dim.evaluate("Just something random here")
        self.assertAlmostEqual(result.score, 0.0)

    def test_context_dimension_found(self):
        dim = ContextDimension()
        result = dim.evaluate("Because the project is late, we need context about the current situation")
        self.assertGreater(result.score, 0.5)

    def test_context_dimension_missing(self):
        dim = ContextDimension()
        result = dim.evaluate("Do this now")
        self.assertAlmostEqual(result.score, 0.0)

    def test_constraints_dimension_found(self):
        dim = ConstraintsDimension()
        text = "Avoid jargon. Must be formal. Do not exceed 500 words. Use professional tone."
        result = dim.evaluate(text)
        self.assertGreater(result.score, 0.5)

    def test_constraints_dimension_missing(self):
        dim = ConstraintsDimension()
        result = dim.evaluate("Write something")
        self.assertAlmostEqual(result.score, 0.0)

    def test_examples_dimension_found(self):
        dim = ExamplesDimension()
        result = dim.evaluate("For example, here is a sample. Here is another example.")
        self.assertGreater(result.score, 0.5)

    def test_examples_dimension_missing(self):
        dim = ExamplesDimension()
        result = dim.evaluate("Complete this task without any reference or guidance material")
        self.assertAlmostEqual(result.score, 0.0)

    def test_output_format_dimension_found(self):
        dim = OutputFormatDimension()
        result = dim.evaluate("Output format: Present as a table with 3 columns")
        self.assertGreater(result.score, 0.5)

    def test_output_format_missing(self):
        dim = OutputFormatDimension()
        result = dim.evaluate("Just tell me the answer")
        self.assertAlmostEqual(result.score, 0.0)

    def test_detail_level_very_short(self):
        dim = DetailLevelDimension()
        result = dim.evaluate("Hi")
        self.assertAlmostEqual(result.score, 0.0)

    def test_detail_level_good(self):
        dim = DetailLevelDimension()
        text = "This is a moderately detailed prompt with enough information. " * 10
        result = dim.evaluate(text)
        self.assertGreaterEqual(result.score, 0.5)

    def test_detail_level_comprehensive(self):
        dim = DetailLevelDimension()
        text = "Word " * 250
        result = dim.evaluate(text)
        self.assertGreaterEqual(result.score, 0.7)

    def test_clarity_vague(self):
        dim = ClarityDimension()
        result = dim.evaluate("Do some stuff and make a thing for me")
        self.assertLess(result.score, 0.5)

    def test_clarity_specific(self):
        dim = ClarityDimension()
        result = dim.evaluate("Create a specific report with exact metrics and precise data points")
        self.assertGreater(result.score, 0.5)


class TestPromptAnalyzer(unittest.TestCase):
    """Test the full PromptAnalyzer orchestration."""

    def setUp(self):
        self.analyzer = PromptAnalyzer()

    def test_analyze_empty(self):
        report = self.analyzer.analyze("")
        self.assertIsNotNone(report)
        self.assertLess(report.overall_score, 20)

    def test_analyze_weak_prompt(self):
        prompt = "Write code for me"
        report = self.analyzer.analyze(prompt)
        self.assertIsNotNone(report)
        self.assertLess(report.overall_score, 50)
        self.assertGreater(len(report.all_suggestions), 0)

    def test_analyze_good_prompt(self):
        prompt = """# Role
You are an expert Python developer.

# Task
Create a REST API with the following endpoints.

# Context
We are building a microservice for user management.

# Constraints
- Use FastAPI
- Keep it under 500 lines
- Include error handling

# Output Format
Provide the code with explanations.
"""
        report = self.analyzer.analyze(prompt)
        self.assertIsNotNone(report)
        self.assertGreater(report.overall_score, 60)
        self.assertEqual(len(report.dimensions), 8)

    def test_analyze_arabic(self):
        prompt = "اكتب لي خطة تسويق"
        report = self.analyzer.analyze(prompt)
        self.assertEqual(report.language, "ar")
        self.assertIsNotNone(report)

    def test_report_structure(self):
        prompt = "You are an expert. Your task is to analyze."
        report = self.analyzer.analyze(prompt)
        d = report.to_dict()
        self.assertIn("overall_score", d)
        self.assertIn("dimensions", d)
        self.assertIn("metrics", d)
        self.assertIn("suggestions", d)
        self.assertEqual(len(d["dimensions"]), 8)

    def test_analyze_file(self):
        prompt = "You are a test expert."
        import tempfile
        import os
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        try:
            f.write(prompt)
            f.close()
            report = self.analyzer.analyze_file(f.name)
            self.assertIsNotNone(report)
        finally:
            os.unlink(f.name)

    def test_dimension_weights(self):
        prompt = "Hello"
        report = self.analyzer.analyze(prompt)
        for dim in report.dimensions:
            self.assertGreaterEqual(dim.weight, 0)
            self.assertGreaterEqual(dim.score, 0)
            self.assertLessEqual(dim.score, 1)


class TestSuggestions(unittest.TestCase):
    """Test the suggestion engine."""

    def setUp(self):
        self.analyzer = PromptAnalyzer()
        from prompt_toolkit.improver.suggestions import SuggestionEngine
        self.suggester = SuggestionEngine()

    def test_generate_suggestions(self):
        prompt = "Do stuff"
        report = self.analyzer.analyze(prompt)
        plan = self.suggester.generate_plan(report, prompt)
        self.assertGreater(len(plan.suggestions), 0)
        self.assertIsNotNone(plan.original_prompt)

    def test_suggestion_priorities(self):
        prompt = ""
        report = self.analyzer.analyze(prompt)
        plan = self.suggester.generate_plan(report, prompt)
        for s in plan.suggestions:
            self.assertIn(s.priority, ("high", "medium", "low"))

    def test_improvement_plan_structure(self):
        prompt = "Do some coding task"
        report = self.analyzer.analyze(prompt)
        plan = self.suggester.generate_plan(report, prompt)
        d = plan.to_dict()
        self.assertIn("original_prompt", d)
        self.assertIn("suggestions", d)
        self.assertIn("critical_count", d)


class TestRewriter(unittest.TestCase):
    """Test the prompt rewriter."""

    def setUp(self):
        from prompt_toolkit.improver.rewriter import PromptRewriter
        self.rewriter = PromptRewriter()

    def test_rewrite_short_prompt(self):
        result = self.rewriter.rewrite_template("Write code")
        self.assertGreater(len(result), 20)
        self.assertIn("Role", result)
        self.assertIn("Task", result)
        self.assertIn("Constraints", result)

    def test_rewrite_arabic(self):
        result = self.rewriter.rewrite_template("اكتب لي مقالة")
        self.assertIn("الدور", result)
        self.assertIn("المهمة", result)
        self.assertGreater(len(result), 20)

    def test_rewrite_enhanced(self):
        original = "You are an expert. Do the task."
        result = self.rewriter.rewrite_enhanced(original)
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
        self.assertGreater(len(result), len(original))

    def test_expand_very_short(self):
        result = self.rewriter.rewrite_template("Hello")
        self.assertTrue("Enhanced" in result or "المحسن" in result)


if __name__ == "__main__":
    unittest.main()
