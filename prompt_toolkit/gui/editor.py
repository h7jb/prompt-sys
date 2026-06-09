"""Prompt text editor widget with syntax features."""

import tkinter as tk
from tkinter import ttk


class PromptEditor(ttk.Frame):
    """A text editor widget for writing and editing prompts.

    Provides line numbers, basic formatting, and
    a clean editing experience.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_editor()

    def _build_editor(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=10,
            pady=10,
            bg="#1e1e2e",
            fg="#cdd6f4",
            insertbackground="#f5e0dc",
            selectbackground="#45475a",
            selectforeground="#cdd6f4",
            relief=tk.FLAT,
            borderwidth=0,
            undo=True,
            maxundo=50,
        )

        line_numbers = tk.Text(
            text_frame,
            width=4,
            font=("Consolas", 11),
            padx=5,
            pady=10,
            bg="#181825",
            fg="#6c7086",
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor="arrow",
        )

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self._on_scroll)
        self.text.config(yscrollcommand=self._sync_scroll)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.line_numbers = line_numbers
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._update_line_numbers)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Button-4>", self._on_mousewheel)
        self.text.bind("<Button-5>", self._on_mousewheel)

        self._update_line_numbers()

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _sync_scroll(self, first, last, *args):
        self.text.yview_moveto(first)
        self.line_numbers.yview_moveto(first)

    def _on_modified(self, event=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)

    def _update_line_numbers(self, event=None):
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        line_count = self.text.index("end-1c").split(".")[0]
        numbers = "\n".join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state=tk.DISABLED)

        self.line_numbers.yview_moveto(self.text.yview()[0])

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.text.yview_scroll(-1, "units")
        elif event.num == 5:
            self.text.yview_scroll(1, "units")
        elif hasattr(event, "delta"):
            self.text.yview_scroll(-1 * (event.delta // 120), "units")
        self._update_line_numbers()

    def get_text(self) -> str:
        """Get the current editor content."""
        return self.text.get("1.0", tk.END).strip()

    def set_text(self, text: str):
        """Set the editor content.

        Args:
            text: New text content for the editor.
        """
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self._update_line_numbers()

    def clear(self):
        """Clear the editor content."""
        self.text.delete("1.0", tk.END)
        self._update_line_numbers()

    def insert(self, text: str):
        """Insert text at the current cursor position."""
        self.text.insert(tk.INSERT, text)
        self._update_line_numbers()
