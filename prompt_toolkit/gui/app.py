"""Main desktop application window for Prompt Toolkit."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
from typing import Optional

from ..analyzer.engine import PromptAnalyzer, AnalysisReport
from ..improver.suggestions import SuggestionEngine, ImprovementPlan
from ..improver.rewriter import PromptRewriter
from ..library.storage import PromptLibrary, PromptEntry
from ..library.catalog import seed_library
from ..config import load_config, save_config
from .editor import PromptEditor
from .analyzer_panel import AnalyzerPanel
from .library_panel import LibraryPanel


class PromptToolkitApp:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Prompt Toolkit - Professional Prompt Engineering")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 600)

        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self.analyzer = PromptAnalyzer()
        self.suggester = SuggestionEngine()
        self.rewriter = PromptRewriter()
        self.library = PromptLibrary()
        self.last_report: Optional[AnalysisReport] = None
        self.last_plan: Optional[ImprovementPlan] = None

        seed_library(self.library)
        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        try:
            self.root.option_add("*Font", ("Segoe UI", 10))
        except tk.TclError:
            self.root.option_add("*Font", ("TkDefaultFont", 10))
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        try:
            style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
            style.configure("Score.TLabel", font=("Segoe UI", 24, "bold"))
            style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
            style.configure("Status.TLabel", font=("Segoe UI", 10))
            style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        except tk.TclError:
            pass

        self._create_menu()
        self._create_main_paned()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save As...", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Analyze Prompt", command=self._analyze_current, accelerator="Ctrl+R")
        tools_menu.add_command(label="Improve Prompt", command=self._improve_current, accelerator="Ctrl+I")
        tools_menu.add_command(label="Rewrite Prompt", command=self._rewrite_current, accelerator="Ctrl+Shift+R")
        menubar.add_cascade(label="Tools", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Quick Guide", command=self._show_guide)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-r>", lambda e: self._analyze_current())
        self.root.bind("<Control-i>", lambda e: self._improve_current())
        self.root.bind("<Control-Shift-R>", lambda e: self._rewrite_current())

    def _create_main_paned(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        self._create_editor(left_frame)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        self._create_right_panel(right_frame)

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)

    def _create_editor(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        editor_tab = ttk.Frame(notebook)
        notebook.add(editor_tab, text="Prompt Editor")

        toolbar = ttk.Frame(editor_tab)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(toolbar, text="Analyze", command=self._analyze_current, style="Action.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Improve", command=self._improve_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Rewrite", command=self._rewrite_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save to Library", command=self._save_to_library).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear", command=self._clear_editor).pack(side=tk.LEFT, padx=2)

        self.editor = PromptEditor(editor_tab)
        self.editor.pack(fill=tk.BOTH, expand=True)

        lib_tab = ttk.Frame(notebook)
        notebook.add(lib_tab, text="Prompt Library")
        self.library_panel = LibraryPanel(lib_tab, self.library, self._on_library_select)
        self.library_panel.pack(fill=tk.BOTH, expand=True)

        self.root.bind("<Control-R>", lambda e: self._analyze_current())
        self.root.bind("<Control-I>", lambda e: self._improve_current())

    def _create_right_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        analysis_tab = ttk.Frame(notebook)
        notebook.add(analysis_tab, text="Analysis")
        self.analyzer_panel = AnalyzerPanel(analysis_tab)
        self.analyzer_panel.pack(fill=tk.BOTH, expand=True)

    def _set_status(self, text: str):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def _analyze_current(self):
        text = self.editor.get_text().strip()
        if not text:
            messagebox.showwarning("Empty Prompt", "Please enter or load a prompt first.")
            return

        self._set_status("Analyzing...")
        def work():
            try:
                report = self.analyzer.analyze(text)
                self.last_report = report
                plan = self.suggester.generate_plan(report, text)
                self.last_plan = plan
                self.root.after(0, lambda: self._display_results(report, plan))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error: {e}"))

        threading.Thread(target=work, daemon=True).start()

    def _display_results(self, report: AnalysisReport, plan: ImprovementPlan):
        self.analyzer_panel.display(report, plan)
        self._set_status(f"Analysis complete: {report.overall_score:.1f}/100")

    def _improve_current(self):
        text = self.editor.get_text().strip()
        if not text:
            messagebox.showwarning("Empty Prompt", "Please enter or load a prompt first.")
            return

        self._set_status("Improving...")
        def work():
            try:
                report = self.analyzer.analyze(text)
                improved = self.rewriter.rewrite_enhanced(text, report)
                self.root.after(0, lambda: self._apply_improvement(improved))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error: {e}"))

        threading.Thread(target=work, daemon=True).start()

    def _rewrite_current(self):
        text = self.editor.get_text().strip()
        if not text:
            messagebox.showwarning("Empty Prompt", "Please enter or load a prompt first.")
            return

        self._set_status("Rewriting...")
        def work():
            try:
                improved = self.rewriter.rewrite_template(text)
                self.root.after(0, lambda: self._apply_improvement(improved))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error: {e}"))

        threading.Thread(target=work, daemon=True).start()

    def _apply_improvement(self, improved_text: str):
        self.editor.set_text(improved_text)
        self.analyzer_panel.clear()
        self._set_status("Prompt improved. Run analysis to see new scores.")

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open Prompt File",
            filetypes=[("Text files", "*.txt *.md"), ("All files", "*.*")]
        )
        if path:
            try:
                text = Path(path).read_text(encoding="utf-8")
                self.editor.set_text(text)
                self._set_status(f"Loaded: {Path(path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read file: {e}")

    def _save_file(self):
        text = self.editor.get_text().strip()
        if not text:
            messagebox.showwarning("Empty", "Nothing to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Prompt",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All files", "*.*")]
        )
        if path:
            try:
                Path(path).write_text(text, encoding="utf-8")
                self._set_status(f"Saved: {Path(path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {e}")

    def _save_to_library(self):
        text = self.editor.get_text().strip()
        if not text:
            messagebox.showwarning("Empty", "Nothing to save.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Save to Library")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Title:").pack(pady=(10, 0))
        title_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=title_var, width=50).pack(pady=5)

        ttk.Label(dialog, text="Category:").pack()
        cat_var = tk.StringVar(value="general")
        cat_combo = ttk.Combobox(dialog, textvariable=cat_var, values=PromptLibrary.CATEGORIES, state="readonly")
        cat_combo.pack(pady=5)

        ttk.Label(dialog, text="Tags (comma separated):").pack()
        tags_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=tags_var, width=50).pack(pady=5)

        def do_save():
            entry = PromptEntry(
                title=title_var.get().strip() or "Untitled",
                content=text,
                category=cat_var.get(),
                tags=[t.strip() for t in tags_var.get().split(",") if t.strip()],
            )
            self.library.add(entry)
            self.library_panel.refresh()
            dialog.destroy()
            self._set_status("Saved to library")

        ttk.Button(dialog, text="Save", command=do_save, style="Action.TButton").pack(pady=20)

    def _clear_editor(self):
        self.editor.clear()
        self.analyzer_panel.clear()
        self._set_status("Cleared")

    def _on_library_select(self, entry: PromptEntry):
        self.editor.set_text(entry.content)
        self._set_status(f"Loaded: {entry.title}")

    def _show_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        config = load_config()
        vars_ = {}

        row = 0
        ttk.Label(dialog, text="AI Provider Settings", style="Header.TLabel").grid(row=row, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")
        row += 1

        sections = [
            ("OpenAI", "openai_api_key", "openai_model"),
            ("Gemini", "gemini_api_key", "gemini_model"),
            ("Ollama", "ollama_endpoint", "ollama_model"),
        ]

        for section_title, key_field, model_field in sections:
            ttk.Label(dialog, text=section_title, font=("Segoe UI", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(10, 0), padx=10, sticky="w")
            row += 1

            label_map = {
                "openai_api_key": "API Key:", "openai_model": "Model:",
                "gemini_api_key": "API Key:", "gemini_model": "Model:",
                "ollama_endpoint": "Endpoint:", "ollama_model": "Model:",
            }

            for field in (key_field, model_field):
                ttk.Label(dialog, text=label_map[field]).grid(row=row, column=0, padx=10, pady=3, sticky="e")
                var = tk.StringVar(value=config.get(field, ""))
                vars_[field] = var
                show_char = "" if "key" in field or "password" in field else None
                entry = ttk.Entry(dialog, textvariable=var, width=50, show=show_char)
                entry.grid(row=row, column=1, padx=10, pady=3, sticky="w")
                row += 1

        def do_save():
            new_config = load_config()
            for field, var in vars_.items():
                new_config[field] = var.get()
            save_config(new_config)
            dialog.destroy()
            self._set_status("Settings saved")

        ttk.Button(dialog, text="Save Settings", command=do_save, style="Action.TButton").grid(row=row, column=0, columnspan=2, pady=20)

    def _show_about(self):
        messagebox.showinfo(
            "About Prompt Toolkit",
            "Prompt Toolkit v2.0\n\n"
            "Advanced AI Prompt Engineering System\n\n"
            "Analyze, improve, and generate professional prompts\n"
            "for ChatGPT, Claude, Gemini, and local LLMs.\n\n"
            "https://github.com/s11754754-stack/prompt-sys"
        )

    def _show_guide(self):
        guide = """QUICK GUIDE:

1. Type or paste a prompt in the editor.
2. Click 'Analyze' to score it across 8 dimensions.
3. Click 'Improve' for automated enhancements.
4. Click 'Rewrite' to restructure the prompt.
5. Save good prompts to the Library.
6. Browse the Library tab for templates.

Keyboard Shortcuts:
  Ctrl+O: Open file  Ctrl+S: Save file
  Ctrl+R: Analyze    Ctrl+I: Improve
"""
        messagebox.showinfo("Quick Guide", guide)

    def run(self):
        self.root.mainloop()


def main():
    app = PromptToolkitApp()
    app.run()


if __name__ == "__main__":
    main()
