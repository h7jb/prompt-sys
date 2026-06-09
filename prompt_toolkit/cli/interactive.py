"""Interactive CLI prompt builder with smart questioning."""

import sys
from pathlib import Path
from ..analyzer.engine import PromptAnalyzer
from ..improver.suggestions import SuggestionEngine
from ..improver.rewriter import PromptRewriter


def print_header():
    print("=" * 60)
    print("  INTERACTIVE PROMPT ENGINEER v2")
    print("  Professional Prompt Builder & Analyzer")
    print("=" * 60)
    print()


def build_prompt_interactive() -> str:
    """Guide the user through building a professional prompt."""
    print("Let's build your perfect prompt step by step.")
    print("(Press Enter to accept defaults)\n")

    role = input("1. Who should the AI act as? (e.g., 'Senior Python Developer')\n> ").strip() or "Helpful Assistant"

    task = input("\n2. What is the main task or objective?\n> ").strip()
    if not task:
        print("Task is required!")
        sys.exit(1)

    context = input("\n3. What is the background or context? (Why this task?)\n> ").strip() or ""

    audience = input("\n4. Who is the target audience for the output?\n> ").strip() or "General audience"

    fmt = input("\n5. What format do you want? (table, list, report, JSON, markdown)\n> ").strip() or "Well-structured text"

    constraints = input("\n6. Any constraints? (tone, length, things to avoid - comma separated)\n> ").strip()

    prompt = f"""# Role
You are an expert {role}.

# Task
{task}

# Context
{context or "Please provide a high-quality response based on your expertise."}

# Target Audience
{audience}

# Constraints & Rules"""
    if constraints:
        for c in [c.strip() for c in constraints.split(",")]:
            prompt += f"\n- {c}"
    else:
        prompt += "\n- Provide accurate and specific information"
        prompt += "\n- Use clear, professional language"

    prompt += f"""

# Output Format
Present your response as {fmt}. Use appropriate structure with headings, sections, and formatting for clarity.
"""
    return prompt


def main():
    print_header()

    mode = input("Choose mode:\n1. Build new prompt\n2. Improve existing prompt (paste/load file)\n> ").strip()

    if mode == "2":
        src = input("Enter file path or paste prompt below (end with --- on new line):\n").strip()
        if Path(src).exists():
            text = Path(src).read_text(encoding="utf-8")
        else:
            lines = [src]
            while True:
                line = input()
                if line.strip() == "---":
                    break
                lines.append(line)
            text = "\n".join(lines)

        analyzer = PromptAnalyzer()
        report = analyzer.analyze(text)
        suggester = SuggestionEngine()
        plan = suggester.generate_plan(report, text)

        print("\n" + "=" * 60)
        print(f"  ANALYSIS: {report.overall_score:.1f}/100")
        print("=" * 60)
        for s in plan.suggestions:
            print(f"  [{s.priority.upper()}] {s.recommendation}")
        print()

        rewrite = input("Generate improved version? (y/n): ").strip().lower()
        if rewrite == "y":
            rewriter = PromptRewriter()
            improved = rewriter.rewrite_enhanced(text, report)
            print("\n" + "=" * 60)
            print("  IMPROVED PROMPT:")
            print("=" * 60)
            print(improved)
            text = improved

        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == "y":
            fname = input("Filename: ").strip() or "improved_prompt.md"
            Path(fname).write_text(text, encoding="utf-8")
            print(f"Saved to {fname}")
    else:
        text = build_prompt_interactive()
        print("\n" + "=" * 60)
        print("  YOUR PROMPT:")
        print("=" * 60)
        print(text)

        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == "y":
            fname = input("Filename: ").strip() or "my_prompt.md"
            Path(fname).write_text(text, encoding="utf-8")
            print(f"Saved to {fname}")

        analyze_now = input("\nAnalyze this prompt? (y/n): ").strip().lower()
        if analyze_now == "y":
            analyzer = PromptAnalyzer()
            report = analyzer.analyze(text)
            from .analyze import print_report
            print_report(report)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
