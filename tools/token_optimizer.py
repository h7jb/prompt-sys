"""Legacy wrapper - uses new Prompt Toolkit for token analysis + optimization."""

import sys
import io
import re
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, UnicodeDecodeError):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prompt_toolkit.analyzer.metrics import PromptMetrics


def analyze_and_optimize(file_path):
    """Analyze and optionally optimize token usage in a prompt file.

    Args:
        file_path: Path to a text or markdown file.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    metrics = PromptMetrics(content)

    optimized_content = re.sub(r' +', ' ', content)
    optimized_content = re.sub(r'\n{3,}', '\n\n', optimized_content)
    optimized_content = optimized_content.strip()

    opt_metrics = PromptMetrics(optimized_content)

    original_tokens = metrics.token_estimates.get("gpt4", 0)
    optimized_tokens = opt_metrics.token_estimates.get("gpt4", 0)
    saved_tokens = original_tokens - optimized_tokens
    save_pct = (saved_tokens / original_tokens * 100) if original_tokens else 0

    print()
    print("=" * 50)
    print("TOKEN OPTIMIZER REPORT")
    print("=" * 50)
    print(f"Original Tokens (GPT-4 est.): {original_tokens}")
    print(f"Optimized Tokens (GPT-4 est.): {optimized_tokens}")
    print(f"Tokens Saved:                 {saved_tokens} ({save_pct:.1f}%)")
    print(f"Original Characters:          {metrics.char_count}")
    print(f"Optimized Characters:         {opt_metrics.char_count}")
    if saved_tokens > 0:
        print(f"Estimated Cost Savings:       ${saved_tokens * 0.00001:.5f}")
    print("=" * 50)

    if saved_tokens > 0:
        save_path = Path(file_path).with_suffix('.optimized' + Path(file_path).suffix)
        save_path.write_text(optimized_content, encoding='utf-8')
        print(f"\nSaved optimized prompt to: {save_path.resolve()}")
    else:
        print("\nPrompt is already token-optimized! No extra spaces found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and optimize tokens for a prompt.")
    parser.add_argument("file", help="Path to the markdown or text file")
    args = parser.parse_args()
    analyze_and_optimize(args.file)
