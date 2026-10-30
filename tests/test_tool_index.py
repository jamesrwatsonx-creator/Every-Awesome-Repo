"""Offline checks for the standalone evidence-aware child-tool index."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import index_tools as indexer
import search_tools as finder

SHA = "a" * 40
SAMPLE = """# Project

## Database
* [Raster SQL](https://github.com/example/raster) - Read and write raster data with SQL.
* [Live Market API](https://example.org/api) - Realtime stock prices for free.
* [Duplicate](https://github.com/example/raster) - Another mention.
* [Internal docs](#local-anchor) - Should be ignored.
"""

def empty():
    return {"schema_version": "1.0.0",
            "project": "Every Awesome Repo Tools", "tools": []}

class TestIndividualIndex(unittest.TestCase):
    def test_extract_precise_pinned_evidence(self):
        results = indexer.extract_markdown("source/awesome-data", SHA, "README.md", SAMPLE)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["github_repository"], "example/raster")
        self.assertEqual(results[0]["source_collections"][0]["line"], 4)
        self.assertEqual(results[0]["source_collections"][0]["section"], "Database")
        self.assertTrue(results[0]["source_collections"][0]["evidence_url"].endswith("#L4"))
        self.assertEqual(results[0]["evidence_status"], "LISTED_ONLY")
        self.assertFalse(results[0]["upstream_evidence"])
        self.assertIsNone(results[1]["github_repository"])

    def test_two_listings_are_deduplicated_and_keep_sources(self):
        entries = indexer.extract_markdown("source/awesome-data", SHA, "README.md", SAMPLE)
        merged = indexer.merge(empty(), entries)
        self.assertEqual(len(merged["tools"]), 2)
        raster = next(t for t in merged["tools"] if t["github_repository"] == "example/raster")
        self.assertEqual(len(raster["source_collections"]), 2)
        repeat = indexer.merge(merged, entries)
        self.assertEqual(len(repeat["tools"]), 2)
        self.assertEqual(len(next(t for t in repeat["tools"] if t["github_repository"] == "example/raster")["source_collections"]), 2)

    def test_distinct_collections_merge_without_copied_code(self):
        a = indexer.extract_markdown("source/one", SHA, "README.md", SAMPLE)
        b = indexer.extract_markdown("source/two", SHA, "README.md", SAMPLE)
        data = indexer.merge(indexer.merge(empty(), a), b)
        tool = next(t for t in data["tools"] if t["github_repository"] == "example/raster")
        self.assertEqual(len(tool["source_collections"]), 4)
        self.assertEqual(tool["evidence_status"], "LISTED_ONLY")

    def test_search_by_data_application_and_collection(self):
        data = indexer.merge(empty(), indexer.extract_markdown("source/awesome-data", SHA, "README.md", SAMPLE))
        results = finder.search(data, "realtime stock")
        self.assertTrue(results)
        self.assertEqual(results[0]["name"], "Live Market API")
        self.assertTrue(finder.search(data, "raster", collection="source/awesome-data"))
        self.assertFalse(finder.search(data, "raster", collection="other/collection"))
        self.assertFalse(finder.search(data, "raster", documented_only=True))

    def test_documented_requires_upstream_readme_statement(self):
        data = indexer.merge(empty(), indexer.extract_markdown("source/awesome-data", SHA, "README.md", SAMPLE))
        tool = next(t for t in data["tools"] if t["github_repository"] == "example/raster")
        upstream = (
            SHA, "# Raster\n\nRaster is a library for reading and writing images with SQL.\n",
            {"license": {"spdx_id": "MIT"}, "stargazers_count": 12, "pushed_at": None}
        )
        with patch.object(indexer, "fetch_readme", return_value=upstream):
            self.assertTrue(indexer.enrich_github(tool))
        self.assertEqual(tool["evidence_status"], "UPSTREAM_DOCUMENTED_NOT_TESTED")
        self.assertEqual(tool["license_spdx_id"], "MIT")
        self.assertTrue(tool["upstream_evidence"][0]["evidence_url"].endswith("#L3"))
        self.assertTrue(finder.search(data, "reading images", documented_only=True))

    def test_source_identity_and_path_validation(self):
        with self.assertRaises(indexer.IndexError):
            indexer.extract_markdown("bad-owner", SHA, "README.md", SAMPLE)
        with self.assertRaises(indexer.IndexError):
            indexer.extract_markdown("owner/repo", "HEAD", "README.md", SAMPLE)
        with self.assertRaises(indexer.IndexError):
            indexer.extract_markdown("owner/repo", SHA, "../README.md", SAMPLE)
        self.assertIsNone(indexer.normalize_url("javascript:alert(1)"))
        self.assertIsNone(indexer.normalize_url("http://localhost/admin"))
        self.assertIsNone(indexer.github_identity("https://github.com/o/r/tree/main"))

    def test_schema_rejects_untrusted_index(self):
        with self.assertRaises(indexer.IndexError):
            indexer.merge({"tools": []}, [])
        with self.assertRaises(ValueError):
            finder.search({"tools": []}, "query")

    def test_real_seed_if_present(self):
        path = ROOT / "data" / "tools.json"
        if not path.exists():
            self.skipTest("Tool seed has not been generated yet")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreater(len(data["tools"]), 10)
        ids = [t["id"] for t in data["tools"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(t.get("source_collections") for t in data["tools"]))

if __name__ == "__main__":
    unittest.main()
