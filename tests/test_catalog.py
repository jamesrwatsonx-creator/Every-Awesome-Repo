"""Offline validity checks for the canonical Every Awesome Repo index."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "catalog.json"

class TestCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.items = cls.data["repositories"]
        cls.categories = {cat["name"] for cat in cls.data["categories"]}

    def test_category_coverage(self):
        self.assertGreaterEqual(len(self.categories), 27)
        self.assertGreaterEqual(len(self.items), 273)

    def test_original_screenshots_preserved(self):
        self.assertEqual(sum(bool(x.get("original_screenshot")) for x in self.items), 34)

    def test_no_duplicate_canonical_identities(self):
        identities = [x["repository"].lower() for x in self.items]
        self.assertEqual(len(identities), len(set(identities)))

    def test_all_items_valid(self):
        for entry in self.items:
            with self.subTest(repo=entry["repository"]):
                self.assertEqual(entry["repository"].count("/"), 1)
                u = urlparse(entry["url"])
                self.assertEqual(u.scheme, "https")
                self.assertEqual(u.netloc, "github.com")
                self.assertTrue(entry["categories"])
                self.assertIn(entry["primary_category"], entry["categories"])
                self.assertTrue(set(entry["categories"]).issubset(self.categories))
                self.assertIsInstance(entry.get("discovery_tags"), list)
                self.assertIsInstance(entry.get("stars"), int)
                self.assertGreaterEqual(entry["stars"], 0)

    def test_first_party_source_list_was_restored(self):
        expected = {"Christian-Sidak/awesome-mcp-tools",
                    "Sagargupta16/awesome-mcp-servers",
                    "ianwieds/awesome-ai-agents",
                    "korchasa/awesome-ai-agents",
                    "jasonniebauer/awesome-public-data-sources"}
        original = {x["repository"].lower() for x in self.items if x.get("original_screenshot")}
        self.assertTrue({r.lower() for r in expected}.issubset(original))

    def test_search_works_offline(self):
        p = subprocess.run([sys.executable, str(ROOT/"scripts"/"search_catalog.py"),
                            "voice automation", "--json", "--limit", "5"],
                           capture_output=True, text=True, check=True)
        output = json.loads(p.stdout)
        self.assertGreater(output["count"], 0)
        self.assertLessEqual(output["count"], 5)

if __name__ == "__main__":
    unittest.main()
