"""Library browser panel for browsing, searching, and managing prompts."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from ..library.storage import PromptLibrary, PromptEntry


class LibraryPanel(ttk.Frame):
    """Panel for browsing the prompt library with search and categories."""

    def __init__(self, parent, library: PromptLibrary, on_select: Callable[[PromptEntry], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.library = library
        self.on_select = on_select
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._do_search())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=(10, 0))
        self.cat_var = tk.StringVar(value="")
        self.cat_combo = ttk.Combobox(
            search_frame,
            textvariable=self.cat_var,
            values=[""] + PromptLibrary.CATEGORIES,
            state="readonly",
            width=15,
        )
        self.cat_combo.pack(side=tk.LEFT, padx=5)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self._do_search())

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self._delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Search", command=self._clear_search).pack(side=tk.LEFT, padx=2)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("title", "category", "score", "language")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("title", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("score", text="Score")
        self.tree.heading("language", text="Lang")

        self.tree.column("title", width=200)
        self.tree.column("category", width=100)
        self.tree.column("score", width=60, anchor="center")
        self.tree.column("language", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

        self._entries_map: dict[str, PromptEntry] = {}

    def refresh(self):
        """Reload the library listing."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._entries_map.clear()

        self._do_search()

    def _do_search(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._entries_map.clear()

        query = self.search_var.get().strip()
        category = self.cat_var.get().strip()

        results = self.library.search(query=query, category=category)

        for entry in results:
            score_text = f"{entry.score:.0f}" if entry.score else "-"
            lang = {"ar": "AR", "en": "EN", "mixed": "BI"}.get(entry.language, entry.language)
            item_id = self.tree.insert(
                "", tk.END,
                values=(entry.title[:50], entry.category, score_text, lang),
            )
            self._entries_map[item_id] = entry

    def _on_double_click(self, event):
        selected = self.tree.selection()
        if selected:
            entry = self._entries_map.get(selected[0])
            if entry:
                self.on_select(entry)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        entry = self._entries_map.get(selected[0])
        if entry and messagebox.askyesno("Confirm", f"Delete '{entry.title}'?"):
            self.library.delete(entry.id)
            self.refresh()

    def _clear_search(self):
        self.search_var.set("")
        self.cat_var.set("")
        self.refresh()
