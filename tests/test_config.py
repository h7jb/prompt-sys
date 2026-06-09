"""Unit tests for configuration management."""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prompt_toolkit.config import (
    DEFAULT_CONFIG,
    load_config,
    save_config,
    get_config_path,
    ensure_config_dir,
)


class TestConfig(unittest.TestCase):
    """Test configuration loading, saving, and defaults."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.orig_config_path = get_config_path()

        import prompt_toolkit.config as config_mod
        self._orig_get_path = config_mod.get_config_path
        config_mod.get_config_path = lambda: Path(self.tmp_dir) / "config.json"

    def tearDown(self):
        import prompt_toolkit.config as config_mod
        config_mod.get_config_path = self._orig_get_path
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_default_config(self):
        self.assertIn("openai_api_key", DEFAULT_CONFIG)
        self.assertIn("default_provider", DEFAULT_CONFIG)
        self.assertEqual(DEFAULT_CONFIG["default_provider"], "none")

    def test_load_default_config(self):
        config = load_config()
        self.assertEqual(config["openai_api_key"], "")
        self.assertEqual(config["default_provider"], "none")

    def test_save_and_load(self):
        save_config({"openai_api_key": "test-key-123", "default_provider": "openai"})
        loaded = load_config()
        self.assertEqual(loaded["openai_api_key"], "test-key-123")
        self.assertEqual(loaded["default_provider"], "openai")

    def test_load_merges_with_defaults(self):
        save_config({"openai_api_key": "my-key"})
        loaded = load_config()
        self.assertEqual(loaded["openai_api_key"], "my-key")
        self.assertIn("gemini_model", loaded)

    def test_ensure_config_dir(self):
        test_dir = Path(self.tmp_dir) / "subdir" / "config"
        import prompt_toolkit.config as config_mod
        config_mod.get_config_path = lambda: test_dir / "config.json"
        ensure_config_dir()
        self.assertTrue(test_dir.exists())

    def test_save_ignores_unknown_keys(self):
        save_config({"unknown_key": "value"})
        loaded = load_config()
        self.assertNotIn("unknown_key", loaded)


if __name__ == "__main__":
    unittest.main()
