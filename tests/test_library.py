"""Unit tests for Prompt Library storage and search."""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prompt_toolkit.library.storage import PromptEntry, PromptLibrary


class TestPromptEntry(unittest.TestCase):
    """Test PromptEntry creation and serialization."""

    def test_create_entry(self):
        entry = PromptEntry(
            title="Test Prompt",
            content="You are an expert.",
            category="coding",
            tags=["python", "test"],
            language="en",
            score=85.0,
        )
        self.assertEqual(entry.title, "Test Prompt")
        self.assertEqual(entry.category, "coding")
        self.assertEqual(len(entry.id), 8)

    def test_to_dict(self):
        entry = PromptEntry(title="Test", content="Content", category="general")
        d = entry.to_dict()
        self.assertEqual(d["title"], "Test")
        self.assertEqual(d["content"], "Content")
        self.assertIn("id", d)
        self.assertIn("created_at", d)

    def test_from_dict(self):
        data = {
            "id": "abc123",
            "title": "Test",
            "content": "Content",
            "category": "coding",
            "tags": ["test"],
            "language": "en",
            "score": 90.0,
            "is_favorite": True,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        entry = PromptEntry.from_dict(data)
        self.assertEqual(entry.id, "abc123")
        self.assertEqual(entry.title, "Test")
        self.assertTrue(entry.is_favorite)

    def test_default_values(self):
        entry = PromptEntry()
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.title, "")
        self.assertEqual(entry.category, "general")
        self.assertEqual(entry.tags, [])


class TestPromptLibrary(unittest.TestCase):
    """Test PromptLibrary operations."""

    def setUp(self):
        # Use a temporary file for testing
        self.tmp_dir = tempfile.mkdtemp()
        self.orig_path = Path.home() / ".prompt_toolkit" / "library.json"
        self.test_path = Path(self.tmp_dir) / "library.json"

        import prompt_toolkit.library.storage as storage_mod
        self._orig_get_path = storage_mod.get_library_path
        storage_mod.get_library_path = lambda: self.test_path

        self.library = PromptLibrary()

    def tearDown(self):
        import prompt_toolkit.library.storage as storage_mod
        storage_mod.get_library_path = self._orig_get_path
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_add_and_count(self):
        entry = PromptEntry(title="Test", content="Test content")
        entry_id = self.library.add(entry)
        self.assertIsNotNone(entry_id)
        self.assertEqual(self.library.count, 1)

    def test_get_entry(self):
        entry = PromptEntry(title="Test", content="Content")
        entry_id = self.library.add(entry)
        fetched = self.library.get(entry_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Test")

    def test_get_nonexistent(self):
        result = self.library.get("nonexistent")
        self.assertIsNone(result)

    def test_update_entry(self):
        entry = PromptEntry(title="Original", content="Content")
        entry_id = self.library.add(entry)
        updated = self.library.update(entry_id, {"title": "Updated"})
        self.assertTrue(updated)
        self.assertEqual(self.library.get(entry_id).title, "Updated")

    def test_update_nonexistent(self):
        result = self.library.update("bad_id", {"title": "X"})
        self.assertFalse(result)

    def test_delete_entry(self):
        entry = PromptEntry(title="Test", content="Content")
        entry_id = self.library.add(entry)
        self.assertEqual(self.library.count, 1)
        deleted = self.library.delete(entry_id)
        self.assertTrue(deleted)
        self.assertEqual(self.library.count, 0)

    def test_delete_nonexistent(self):
        result = self.library.delete("bad_id")
        self.assertFalse(result)

    def test_search_by_query(self):
        self.library.add(PromptEntry(title="Python Code", content="def hello(): pass", category="coding"))
        self.library.add(PromptEntry(title="Marketing Plan", content="social media strategy", category="marketing"))

        results = self.library.search(query="python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Code")

    def test_search_by_category(self):
        self.library.add(PromptEntry(title="Code Review", content="Review code", category="coding"))
        self.library.add(PromptEntry(title="Blog Post", content="Write article", category="writing"))

        results = self.library.search(category="coding")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Code Review")

    def test_search_empty_library(self):
        results = self.library.search(query="anything")
        self.assertEqual(len(results), 0)

    def test_categories(self):
        self.library.add(PromptEntry(title="A", content="A", category="coding"))
        self.library.add(PromptEntry(title="B", content="B", category="writing"))
        self.library.add(PromptEntry(title="C", content="C", category="coding"))

        cats = self.library.get_categories()
        self.assertEqual(cats.get("coding"), 2)
        self.assertEqual(cats.get("writing"), 1)

    def test_persistence(self):
        entry = PromptEntry(title="Persistent", content="Content")
        self.library.add(entry)
        self.library.save()

        import prompt_toolkit.library.storage as storage_mod
        storage_mod.get_library_path = lambda: self.test_path
        lib2 = PromptLibrary()
        self.assertEqual(lib2.count, 1)
        self.assertEqual(lib2.all()[0].title, "Persistent")


if __name__ == "__main__":
    unittest.main()
