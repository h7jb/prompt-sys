"""CLI entry point for prompt analysis with enhanced output."""

import sys
import io
import argparse
from pathlib import Path
from ..analyzer.engine import PromptAnalyzer
from ..improver.suggestions import SuggestionEngine

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, UnicodeDecodeError):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def print_report(report):
    """Print a formatted analysis report to the terminal."""
    score = report.overall_score
    grade = "EXCELLENT" if score >= 90 else "GOOD" if score >= 70 else "WEAK" if score >= 40 else "POOR"

    print()
    print("=" * 60)
    print("  PROMPT ANALYSIS REPORT")
    print("=" * 60)
    print(f"  Overall Score: {score:.1f}/100 - {grade}")
    print(f"  Language: {report.language}")
    print(f"  Summary: {report.summary}")
    print("=" * 60)
    print()
    print("  DIMENSION SCORES:")
    for dim in report.dimensions:
        bar_len = int(dim.score * 20)
        bar = "#" * bar_len + "." * (20 - bar_len)
        name = dim.name.replace(" / ", " - ")
        print(f"  {name:<35s} {dim.score*100:>5.1f}% |{bar}|")

    m = report.metrics
    print()
    print("  METRICS:")
    print(f"  Words: {m.word_count} | Characters: {m.char_count} | Sentences: {m.sentence_count}")
    print(f"  Avg word length: {m.avg_word_length:.1f} | Avg sentence: {m.avg_sentence_length:.1f} words")
    print(f"  Reading time: {m.reading_time_seconds:.0f}s ({m.reading_time_seconds/60:.1f} min)")
    print(f"  Complexity: {m.complexity_score:.0%}")
    print(f"  Estimated tokens (GPT-4): {m.token_estimates.get('gpt4', 0)}")
    print()

    if report.all_suggestions:
        print("  IMPROVEMENT SUGGESTIONS:")
        for i, s in enumerate(report.all_suggestions, 1):
            print(f"  {i}. {s}")
        print()

    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a prompt file and score it across multiple dimensions."
    )
    parser.add_argument("file", help="Path to the prompt file (.txt, .md)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    analyzer = PromptAnalyzer()
    sys.stdout.reconfigure(encoding="utf-8")
    report = analyzer.analyze_file(str(file_path))

    if args.json:
        import json
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
