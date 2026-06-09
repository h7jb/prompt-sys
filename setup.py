"""Setup script for Prompt Toolkit."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="prompt-toolkit",
    version="2.0.0",
    description="Advanced AI Prompt Engineering System - Analyze, improve, and generate professional prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Prompt Toolkit Team",
    url="https://github.com/s11754754-stack/prompt-sys",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "gemini": ["google-generativeai>=0.3.0"],
        "tokenizer": ["tiktoken>=0.7.0"],
        "all": ["openai>=1.0.0", "google-generativeai>=0.3.0", "tiktoken>=0.7.0"],
    },
    entry_points={
        "console_scripts": [
            "prompt-analyze=prompt_toolkit.cli.analyze:main",
            "prompt-interactive=prompt_toolkit.cli.interactive:main",
            "prompt-gui=prompt_toolkit.gui.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
    ],
)
