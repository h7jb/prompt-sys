<div align="center">
  <h1>✨ Ultimate Interactive Prompt Toolkit ✨</h1>
  <p><b>Advanced AI Prompt Engineering System & Python Toolchain</b></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/AI-Ready-success.svg" alt="AI Ready" />
    <img src="https://img.shields.io/badge/Token-Optimized-orange.svg" alt="Token Optimized" />
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  </p>
</div>

---

## 🚀 Overview

Welcome to the **Ultimate Interactive Prompt Toolkit**! This project has evolved from a simple set of markdown templates into a **highly advanced, token-economical, and interactive ecosystem** for generating perfect (100/100) prompts for any AI model (ChatGPT, Claude, Gemini, etc.).

Instead of filling out long templates manually, this system uses **Interactive State Tracking**. The AI will guide *you* step-by-step, ask thought-provoking questions, save tokens, and generate the ultimate prompt automatically.

## 🌟 Key Features

- **🧠 Interactive AI Prompt Engineer**: A universal meta-prompt that turns any LLM into your personal prompt consultant.
- **⚡ Token Economy**: Utilizes state-tracking variables to prevent the AI from repeating long texts, saving API costs and context length.
- **🐍 Python CLI Tools**: Analyze, score, and optimize your prompts locally using powerful Python scripts.
- **🔄 Any Model Supported**: Works flawlessly across OpenAI, Anthropic, Google, and Meta models.

---

## 🛠️ How to Use (The Modern Way)

### 1. The Interactive Meta-Prompt (Recommended)

To get started instantly without writing code:
1. Open [prompts/00-interactive-prompt-engineer.md](prompts/00-interactive-prompt-engineer.md).
2. Copy the entire text.
3. Paste it as your first message to ChatGPT, Claude, or Gemini.
4. Let the AI ask you 1-2 questions at a time. It will keep a short `### State Summary` to save tokens.
5. Watch it build the perfect prompt for you!

### 2. The Python Toolchain (For Power Users)

We provide Python scripts in the `tools/` directory to analyze and build prompts locally.

#### Installation
```bash
cd tools
pip install -r requirements.txt
```

#### A. Prompt Analyzer
Scores your prompt out of 100 based on standard prompt engineering rubrics (Role, Context, Constraints, etc.).
```bash
python prompt_analyzer.py path/to/your/prompt.md
```

#### B. Token Optimizer
Calculates the exact tokens your prompt will consume and optimizes it by removing unnecessary spaces and fillers.
```bash
python token_optimizer.py path/to/your/prompt.md
```

#### C. Local Interactive CLI
Build a perfect prompt directly from your terminal!
```bash
python interactive_cli.py
```

---

## 📂 Repository Structure

```text
📁 prompt-system-md
├── 📁 prompts/
│   ├── 00-interactive-prompt-engineer.md  # 🌟 The core interactive system
│   └── 📁 legacy/                         # Old static markdown templates
├── 📁 tools/
│   ├── prompt_analyzer.py                 # Evaluates prompt quality
│   ├── token_optimizer.py                 # Saves API costs
│   ├── interactive_cli.py                 # Terminal interactive builder
│   └── requirements.txt
└── README.md
```

## 🤝 Contributing
Want to add more rules to the Analyzer? Or improve the Meta-Prompt? 
Pull requests are highly welcome! Let's build the best open-source Prompt Engineering toolkit together.

---
<div align="center">
  <i>If this project helped you write better prompts or save tokens, please consider giving it a ⭐!</i>
</div>
