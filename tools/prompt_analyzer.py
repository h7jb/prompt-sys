"""Legacy wrapper - uses new Prompt Toolkit analyzer with CLI interface.

Provides backward-compatible CLI for prompt analysis with enhanced output.
"""

import sys
import io
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, UnicodeDecodeError):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prompt_toolkit.analyzer.engine import PromptAnalyzer


def analyze_prompt(file_path):
    """Analyze a prompt file (legacy-compatible interface).

    Args:
        file_path: Path to a text or markdown file containing a prompt.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    analyzer = PromptAnalyzer()
    report = analyzer.analyze(content)

    print()
    print("=" * 50)
    print("PROMPT ANALYSIS REPORT")
    print("=" * 50)

    score = report.overall_score
    if score >= 90:
        grade = "EXCELLENT!"
    elif score >= 70:
        grade = "GOOD (Needs some tweaks)"
    elif score >= 40:
        grade = "WEAK (Needs major improvements)"
    else:
        grade = "POOR (Must be rewritten)"

    print(f"[Score: {score:.1f}/100] - {grade}")
    print(f"[Language: {report.language}]")

    print()
    print("Dimension Scores:")
    for dim in report.dimensions:
        bar = "#" * int(dim.score * 20) + "." * (20 - int(dim.score * 20))
        name = dim.name.replace(" / ", " - ")
        print(f"  {name:<35s} {dim.score*100:>5.0f}% |{bar}|")

    m = report.metrics
    print()
    print("Metrics:")
    print(f"  Words: {m.word_count} | Chars: {m.char_count} | Tokens (GPT-4): {m.token_estimates.get('gpt4', 0)}")
    print(f"  Reading Time: {m.reading_time_seconds:.0f}s ({m.reading_time_seconds/60:.1f} min)")

    if report.all_suggestions:
        print()
        print(f"Suggestions ({len(report.all_suggestions)}):")
        for s in report.all_suggestions:
            print(f"  * {s}")
    else:
        print()
        print("Your prompt is perfect! No suggestions needed.")

    print("=" * 50)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a prompt file and score it out of 100.")
    parser.add_argument("file", help="Path to the markdown or text file containing the prompt")
    args = parser.parse_args()
    analyze_prompt(args.file)
