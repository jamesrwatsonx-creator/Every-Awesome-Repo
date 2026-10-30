#!/usr/bin/env python3
"""Add or recategorize a GitHub collection without creating duplicate entries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "catalog.json"

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo", help="GitHub owner/repository")
    p.add_argument("--category", required=True, help="An existing category name (exact match)")
    p.add_argument("--tags", default="", help="Additional comma-separated discovery tags")
    args = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        p.error("Repository must be owner/repo, e.g. org/awesome-topic")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    categories = {c["name"]: c for c in data["categories"]}
    if args.category not in categories:
        p.error("Unknown category; choose one from data/catalog.json")
    tags = set(categories[args.category].get("discovery_tags", []))
    tags.update(s.strip() for s in args.tags.split(",") if s.strip())
    current = next((r for r in data["repositories"] if r["repository"].lower() == args.repo.lower()), None)
    if current:
        current["categories"] = list(dict.fromkeys(current["categories"] + [args.category]))
        current["discovery_tags"] = sorted(set(current.get("discovery_tags", [])) | tags)
        print(f"Updated existing entry: {current['repository']}")
    else:
        data["repositories"].append({
            "repository": args.repo,
            "url": "https://github.com/" + args.repo,
            "primary_category": args.category,
            "categories": [args.category],
            "discovery_tags": sorted(tags),
            "stars": 0,
            "stars_checked_at": None,
            "original_screenshot": False,
            "source_kind": "external-curated-collection",
            "review_status": "linked-not-audited",
            "description": None,
            "license_spdx_id": None,
            "archived": None,
            "pushed_at": None
        })
        print(f"Added: {args.repo}. Verify URL before merging.")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_metadata.py"), "--offline"], check=True)

if __name__ == "__main__":
    main()
