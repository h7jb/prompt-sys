"""Analysis results panel for displaying scores and suggestions."""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from ..analyzer.engine import AnalysisReport
from ..improver.suggestions import ImprovementPlan


class AnalyzerPanel(ttk.Frame):
    """Panel that displays prompt analysis results.

    Shows:
    - Overall score with color coding
    - Per-dimension scores with progress bars
    - Key metrics (words, tokens, reading time)
    - Improvement suggestions list
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self):
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollable = scrollable
        self.canvas = canvas
        self.results_frame = ttk.Frame(scrollable)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.score_label = ttk.Label(self.results_frame, text="Score: --", style="Score.TLabel")
        self.score_label.pack(pady=(10, 5))

        self.summary_label = ttk.Label(self.results_frame, text="Enter a prompt and click Analyze", wraplength=350)
        self.summary_label.pack(pady=(0, 10))

        self.dimensions_frame = ttk.LabelFrame(self.results_frame, text="Dimension Scores")
        self.dimensions_frame.pack(fill=tk.X, padx=5, pady=5)

        self.metrics_frame = ttk.LabelFrame(self.results_frame, text="Metrics")
        self.metrics_frame.pack(fill=tk.X, padx=5, pady=5)

        self.suggestions_frame = ttk.LabelFrame(self.results_frame, text="Suggestions")
        self.suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._dimension_bars = []
        self._suggestion_widgets = []

        self._bind_mousewheel()

    def _bind_mousewheel(self):
        def _on_mousewheel(event):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
            elif hasattr(event, "delta"):
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.canvas.bind("<Button-4>", _on_mousewheel)
        self.canvas.bind("<Button-5>", _on_mousewheel)

    def display(self, report: AnalysisReport, plan: ImprovementPlan):
        """Update the panel with analysis results.

        Args:
            report: The analysis report to display.
            plan: The improvement plan with suggestions.
        """
        self.clear()

        score = report.overall_score
        if score >= 90:
            color = "#a6e3a1"
        elif score >= 70:
            color = "#f9e2af"
        elif score >= 40:
            color = "#fab387"
        else:
            color = "#f38ba8"

        self.score_label.config(text=f"{score:.1f}/100", foreground=color)
        self.summary_label.config(text=report.summary)

        for dim in report.dimensions:
            frame = ttk.Frame(self.dimensions_frame)
            frame.pack(fill=tk.X, padx=5, pady=3)

            name = dim.name.split(" / ")[0]
            label = ttk.Label(frame, text=name, width=25, anchor="w")
            label.pack(side=tk.LEFT)

            pct = dim.score * 100
            bar = ttk.Progressbar(frame, length=150, value=pct)
            bar.pack(side=tk.LEFT, padx=5)

            val_label = ttk.Label(frame, text=f"{pct:.0f}%", width=5)
            val_label.pack(side=tk.LEFT)

            self._dimension_bars.append((frame, label, bar, val_label))

        m = report.metrics
        metrics_text = (
            f"Words: {m.word_count}  |  Chars: {m.char_count}  |  Sentences: {m.sentence_count}\n"
            f"Reading time: {m.reading_time_seconds:.0f}s ({m.reading_time_seconds/60:.1f} min)\n"
            f"Complexity: {m.complexity_score:.0%}\n"
            f"Est. tokens (GPT-4): {m.token_estimates.get('gpt4', 0)}"
        )
        ttk.Label(self.metrics_frame, text=metrics_text, justify=tk.LEFT).pack(padx=10, pady=10, anchor="w")

        for s in plan.suggestions:
            prefix = {"high": "⚠️ ", "medium": "📌 ", "low": "💡 "}.get(s.priority, "• ")
            lbl = ttk.Label(
                self.suggestions_frame,
                text=f"{prefix}{s.recommendation}",
                wraplength=380,
                justify=tk.LEFT,
            )
            lbl.pack(fill=tk.X, padx=10, pady=3, anchor="w")
            self._suggestion_widgets.append(lbl)

    def clear(self):
        """Clear all displayed results."""
        self.score_label.config(text="Score: --", foreground="")
        self.summary_label.config(text="")

        for widgets in self._dimension_bars:
            for w in widgets:
                w.destroy()
        self._dimension_bars.clear()

        for w in self._suggestion_widgets:
            w.destroy()
        self._suggestion_widgets.clear()

        for child in self.metrics_frame.winfo_children():
            child.destroy()

        for child in self.suggestions_frame.winfo_children():
            child.destroy()
        self._suggestion_widgets = []
