"""Local storage backend for the Prompt Library using JSON."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import get_library_path, ensure_config_dir


class PromptEntry:
    """A single prompt entry in the library.

    Attributes:
        id: Unique identifier.
        title: Prompt title.
        content: The full prompt text.
        category: Domain/use case category.
        tags: List of searchable tags.
        language: Primary language ('ar', 'en', 'mixed').
        score: Last analysis score (0-100).
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of last update.
        is_favorite: Whether marked as favorite.
    """

    def __init__(
        self,
        title: str = "",
        content: str = "",
        category: str = "general",
        tags: Optional[List[str]] = None,
        language: str = "en",
        score: float = 0.0,
        prompt_id: Optional[str] = None,
    ):
        self.id = prompt_id or str(uuid.uuid4())[:8]
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags or []
        self.language = language
        self.score = score
        self.is_favorite = False
        now = datetime.utcnow().isoformat()
        self.created_at = now
        self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "language": self.language,
            "score": self.score,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PromptEntry":
        entry = cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            language=data.get("language", "en"),
            score=data.get("score", 0.0),
            prompt_id=data.get("id"),
        )
        entry.is_favorite = data.get("is_favorite", False)
        entry.created_at = data.get("created_at", entry.created_at)
        entry.updated_at = data.get("updated_at", entry.updated_at)
        return entry


class PromptLibrary:
    """Manages the prompt library with persist, search, and categorize."""

    CATEGORIES = [
        "general",
        "coding",
        "writing",
        "marketing",
        "analysis",
        "education",
        "business",
        "creative",
        "technical",
        "other",
    ]

    def __init__(self):
        self._entries: List[PromptEntry] = []
        self._dirty = False
        self._load()

    def _load(self) -> None:
        """Load library from disk."""
        path = get_library_path()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self._entries = [PromptEntry.from_dict(e) for e in data]
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def save(self) -> None:
        """Persist library to disk."""
        ensure_config_dir()
        data = [e.to_dict() for e in self._entries]
        get_library_path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._dirty = False

    def add(self, entry: PromptEntry) -> str:
        """Add a new prompt entry.

        Args:
            entry: The PromptEntry to add.

        Returns:
            The ID of the new entry.
        """
        self._entries.append(entry)
        self._dirty = True
        self.save()
        return entry.id

    def update(self, entry_id: str, updates: dict) -> bool:
        """Update an existing entry.

        Args:
            entry_id: ID of the entry to update.
            updates: Dict of fields to update.

        Returns:
            True if found and updated.
        """
        for entry in self._entries:
            if entry.id == entry_id:
                for key, val in updates.items():
                    if hasattr(entry, key):
                        setattr(entry, key, val)
                entry.updated_at = datetime.utcnow().isoformat()
                self._dirty = True
                self.save()
                return True
        return False

    def delete(self, entry_id: str) -> bool:
        """Delete an entry by ID.

        Returns:
            True if found and deleted.
        """
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                del self._entries[i]
                self._dirty = True
                self.save()
                return True
        return False

    def get(self, entry_id: str) -> Optional[PromptEntry]:
        """Get a single entry by ID."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def search(self, query: str = "", category: str = "", tags: Optional[List[str]] = None) -> List[PromptEntry]:
        """Search prompts by query, category, and tags.

        Args:
            query: Text to search in title and content.
            category: Filter by category.
            tags: Filter by tags (matches any).

        Returns:
            Filtered list of PromptEntry.
        """
        results = list(self._entries)
        q = query.lower().strip()

        if q:
            results = [
                e for e in results
                if q in e.title.lower() or q in e.content.lower()
            ]

        if category:
            results = [e for e in results if e.category == category]

        if tags:
            tag_set = set(t.lower() for t in tags)
            results = [e for e in results if tag_set & set(t.lower() for t in e.tags)]

        results.sort(key=lambda e: e.updated_at, reverse=True)
        return results

    def get_categories(self) -> Dict[str, int]:
        """Get category distribution.

        Returns:
            Dict mapping category names to entry counts.
        """
        counts = {}
        for entry in self._entries:
            counts[entry.category] = counts.get(entry.category, 0) + 1
        return counts

    def all(self) -> List[PromptEntry]:
        """Return all entries sorted by update time (newest first)."""
        return sorted(self._entries, key=lambda e: e.updated_at, reverse=True)

    @property
    def count(self) -> int:
        return len(self._entries)
