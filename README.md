<div align="center">
  <h1> Prompt Toolkit v2</h1>
  <p><b>Advanced AI Prompt Engineering System & Python Toolchain</b></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/AI-Ready-success.svg" alt="AI Ready" />
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
    <img src="https://img.shields.io/badge/Status-Production-orange.svg" alt="Status" />
  </p>
</div>

---

## Overview

**Prompt Toolkit v2** is a complete overhaul of the original prompt engineering system, evolved from a Proof of Concept into a professional-grade application. It provides multi-dimensional prompt analysis, smart improvement suggestions, AI provider integration, a desktop GUI, and a fully searchable prompt library.

### What's New in v2

- **Multi-Dimensional Analysis**: 8 scoring dimensions instead of simple regex checks
- **Smart Improvement Engine**: Automatic suggestions and prompt rewriting
- **AI Provider Integration**: Unified interface for OpenAI, Gemini, and Ollama
- **Desktop GUI**: Professional tkinter-based application with dark theme
- **Prompt Library**: Categorized storage with search and filtering
- **Comprehensive Metrics**: Token estimation, readability, complexity scoring
- **Clean Architecture**: Well-structured Python package with separation of concerns
- **Full Test Suite**: Unit and integration tests for all core modules

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/s11754754-stack/prompt-sys
cd prompt-sys

# Install core package
pip install -e .

# Optional: Install AI provider support
pip install -e ".[all]"

# Or for specific providers:
pip install -e ".[openai]"    # OpenAI support
pip install -e ".[gemini]"    # Gemini support
```

### GUI Mode (Desktop Application)

```bash
python -m prompt_toolkit.gui.app
# Or: prompt-gui
```

### CLI Analysis

```bash
python -m prompt_toolkit.cli.analyze my_prompt.md
# Or: prompt-analyze my_prompt.md

# JSON output for programmatic use
python -m prompt_toolkit.cli.analyze my_prompt.md --json
```

### Interactive CLI Builder

```bash
python -m prompt_toolkit.cli.interactive
# Or: prompt-interactive
```

### Legacy CLI Tools (Backward Compatible)

```bash
cd tools
python prompt_analyzer.py my_prompt.md
python token_optimizer.py my_prompt.md
python interactive_cli.py
```

---

## Architecture

```
prompt-sys/
├── prompt_toolkit/              # Main Python package
│   ├── __init__.py              # Package metadata
│   ├── config.py                # Configuration management
│   ├── analyzer/                # Multi-dimensional analysis engine
│   │   ├── engine.py            # Core orchestrator
│   │   ├── dimensions.py        # 8 scoring dimensions
│   │   └── metrics.py           # Token, readability, complexity
│   ├── improver/                # Smart improvement system
│   │   ├── suggestions.py       # Targeted improvement suggestions
│   │   └── rewriter.py          # Prompt restructuring & enhancement
│   ├── providers/               # Unified AI provider layer
│   │   ├── base.py              # Abstract base provider
│   │   ├── factory.py           # Provider factory
│   │   ├── openai_provider.py   # OpenAI API integration
│   │   ├── gemini_provider.py   # Gemini API integration
│   │   └── ollama_provider.py   # Local Ollama integration
│   ├── library/                 # Prompt library management
│   │   ├── storage.py           # JSON-based persistence
│   │   └── catalog.py           # Built-in prompt templates
│   ├── cli/                     # Command-line interfaces
│   │   ├── analyze.py           # CLI analysis tool
│   │   └── interactive.py       # Interactive prompt builder
│   └── gui/                     # Desktop GUI application
│       ├── app.py               # Main window
│       ├── editor.py            # Prompt text editor
│       ├── analyzer_panel.py    # Analysis results display
│       └── library_panel.py     # Library browser
├── tests/                       # Comprehensive test suite
│   ├── test_analyzer.py         # Tests for analysis engine
│   ├── test_library.py          # Tests for library storage
│   └── test_config.py           # Tests for configuration
├── tools/                       # Legacy CLI wrappers (backward compat)
│   ├── prompt_analyzer.py
│   ├── token_optimizer.py
│   ├── interactive_cli.py
│   └── requirements.txt
├── prompts/                     # Prompt templates and meta-prompts
│   ├── 00-interactive-prompt-engineer.md
│   └── legacy/
├── requirements.txt
├── setup.py / pyproject.toml
└── README.md
```

---

## Features

### 1. Multi-Dimensional Prompt Analyzer

Analyzes prompts across 8 quality dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Clarity | 1.0x | Specific vs vague language detection |
| Role | 1.2x | Clear AI persona/role definition |
| Task | 1.5x | Well-defined objectives with steps |
| Context | 1.0x | Background information provided |
| Constraints | 1.3x | Rules, limitations, and boundaries |
| Examples | 0.8x | Sample outputs for guidance |
| Output Format | 1.2x | Clear response structure specification |
| Detail Level | 1.0x | Appropriate depth and length |

### 2. Smart Improvement Engine

- **Suggestion Engine**: Generates targeted, priority-ranked improvements
- **Prompt Rewriter**: Automatic restructuring into professional format
- **Bilingual Support**: Full Arabic and English analysis and suggestions
- **AI-Assisted**: Optional integration with LLMs for intelligent rewriting

### 3. AI Provider Integration

```python
from prompt_toolkit.providers.factory import create_provider

# Auto-detect available provider
provider = create_provider()
if provider:
    improved = provider.improve_prompt("Write code")
```

- **OpenAI**: GPT-4, GPT-3.5 with full API support
- **Gemini**: Google Gemini Pro integration
- **Ollama**: Local LLMs (Llama 2, Mistral, etc.)
- **Provider Factory**: Auto-detection and seamless switching

### 4. Professional Desktop GUI

- Modern dark theme with tkinter
- Real-time analysis with dimension progress bars
- Built-in prompt editor with line numbers
- Library browser with search and categories
- Settings panel for API key configuration

### 5. Prompt Library

- JSON-based local storage (no database setup required)
- 8 built-in prompt templates across categories
- Full-text search and category filtering
- Save, update, and delete prompts
- Favorite/bookmark support

### 6. Comprehensive Metrics

- Word, character, and sentence counts
- Token estimation for GPT-4, Claude, and Gemini
- Reading time calculation
- Vocabulary richness and complexity scoring
- Language detection (Arabic/English/Mixed)

---

## Usage Examples

### Analyze a Prompt Programmatically

```python
from prompt_toolkit.analyzer.engine import PromptAnalyzer

analyzer = PromptAnalyzer()
report = analyzer.analyze("""
You are an expert Python developer.
Write a REST API with authentication.
""")

print(f"Score: {report.overall_score:.1f}/100")
for dim in report.dimensions:
    print(f"{dim.name}: {dim.score:.0%}")
print(f"Suggestions: {len(report.all_suggestions)}")
```

### Improve a Prompt

```python
from prompt_toolkit.analyzer.engine import PromptAnalyzer
from prompt_toolkit.improver.rewriter import PromptRewriter

analyzer = PromptAnalyzer()
rewriter = PromptRewriter()

text = "Write documentation for my API"
report = analyzer.analyze(text)
improved = rewriter.rewrite_enhanced(text, report)
print(improved)
```

### Use AI Provider

```python
from prompt_toolkit.providers.factory import create_provider

provider = create_provider("openai")  # or "gemini", "ollama"
if provider and provider.is_available():
    response = provider.generate_response(
        system_prompt="You are a helpful assistant.",
        user_message="Explain prompt engineering."
    )
```

### Manage Library

```python
from prompt_toolkit.library.storage import PromptLibrary, PromptEntry

library = PromptLibrary()
entry = PromptEntry(
    title="My Analysis Prompt",
    content="Analyze this data...",
    category="analysis",
    tags=["data", "python"],
)
library.add(entry)

results = library.search(query="analysis", category="analysis")
for entry in results:
    print(f"{entry.title} ({entry.score}/100)")
```

---

## Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_analyzer -v
python -m unittest tests.test_library -v
python -m unittest tests.test_config -v
```

---

## Configuration

API keys and model settings are stored in `~/.prompt_toolkit/config.json`:

```json
{
  "openai_api_key": "sk-...",
  "openai_model": "gpt-4",
  "gemini_api_key": "...",
  "gemini_model": "gemini-pro",
  "ollama_endpoint": "http://localhost:11434",
  "ollama_model": "llama2",
  "default_provider": "openai",
  "language": "auto"
}
```

Environment variables are also supported: `OPENAI_API_KEY`, `GEMINI_API_KEY`.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass: `python -m unittest discover tests -v`
5. Submit a pull request

### Development Setup

```bash
pip install -e ".[all,dev]"
python -m unittest discover tests -v
```

---

## Future Development

- [ ] **Web Interface**: React-based web app with FastAPI backend
- [ ] **Plugin System**: Custom dimensions and scoring rules
- [ ] **Export Formats**: PDF, DOCX, HTML report export
- [ ] **Batch Analysis**: Process multiple prompts at once
- [ ] **Version History**: Track changes to prompts over time
- [ ] **Collaboration**: Share prompts and libraries via cloud sync
- [ ] **More AI Providers**: Anthropic Claude, Cohere, Hugging Face
- [ ] **Advanced Readability**: Flesch-Kincaid, Arabic readability indices
- [ ] **Prompt Templates**: Crowdsourced template marketplace

---

<div align="center">
  <i>Built with for the prompt engineering community</i>
</div>
