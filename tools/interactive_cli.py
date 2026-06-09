"""Legacy wrapper - uses new Prompt Toolkit interactive CLI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prompt_toolkit.cli.interactive import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted. Goodbye!")
        sys.exit(0)
