#!/usr/bin/env python3
"""Refresh public GitHub repository metadata and rebuild the exported catalog.

Runs using Python standard library only. No external repository code is fetched
or executed. Failed API calls preserve prior values instead of inventing data.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "catalog.json"
CSV = ROOT / "data" / "catalog.csv"
DOC = ROOT / "docs" / "CATALOG.md"
API = "https://api.github.com/repos/"

def metadata(fullname: str, token: str | None) -> dict:
    if fullname.count("/") != 1 or any(x in fullname for x in ("..", "?", "#", "%")):
        raise ValueError(f"Invalid repo name: {fullname}")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "Every-Awesome-Repo-catalog-sync",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + fullname, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def export(data: dict) -> tuple[str, str]:
    records = data["repositories"]
    categories = data["categories"]
    seen = {x["repository"].lower() for x in records}
    if len(seen) != len(records):
        raise ValueError("Duplicate repository identities in catalog")
    if any(c not in {x["name"] for x in categories} for r in records for c in r["categories"]):
        raise ValueError("Unknown category in catalog")

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["category", "repo", "stars_snapshot", "url", "original_screenshot", "discovery_tags"])
    lines = ["# Complete collection directory", "",
             "Discover potential resources; do not copy or execute untrusted upstream code.",
             "",
             f"**{len(categories)} categories · {sum(len(r['categories']) for r in records)} category placements · {len(records)} unique repositories · {sum(bool(r.get('original_screenshot')) for r in records)} original screenshot sources preserved**",
             "",
             "Star counts are snapshots. Inclusion is not an audit. Labels are candidate discovery tags, not verified features.",
             "", "## Categories", ""]
    for i, cat in enumerate(categories, 1):
        lines.append(f"{i}. [{cat['name']}](#category-{i:02d})")
    for i, cat in enumerate(categories, 1):
        name = cat["name"]
        items = sorted((r for r in records if name in r["categories"]),
                       key=lambda r: (-(r.get("stars") or 0), r["repository"].lower()))
        lines.extend(["", f'<a id="category-{i:02d}"></a>', f"## {i}. {name}", "",
                      "Discovery tags: " + " · ".join(f"`{t}`" for t in cat.get("discovery_tags", [])),
                      ""])
        for j, r in enumerate(items, 1):
            writer.writerow([name, r["repository"], r.get("stars") or 0, r["url"],
                             str(bool(r.get("original_screenshot"))).lower(),
                             ";".join(r.get("discovery_tags", []))])
            origin = " · **original screenshot source**" if r.get("original_screenshot") else ""
            stars = f"{(r.get('stars') or 0):,}"
            lines.append(f"{j}. [{r['repository']}]({r['url']}) — {stars} stars{origin}")
    lines.append("")
    return buf.getvalue(), "\n".join(lines)

def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true",
                        help="Regenerate CSV and Markdown only; make no network requests")
    parser.add_argument("--limit", type=int, default=0,
                        help="Maximum repositories to refresh (0: all)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit nonzero if any GitHub API request fails")
    parser.add_argument("--dry-run", action="store_true",
                        help="Perform refresh in memory without writing files")
    args = parser.parse_args()
    with DATA.open(encoding="utf-8") as f:
        catalog = json.load(f)
    token = os.environ.get("GITHUB_TOKEN")
    errors = []
    changed = 0
    if not args.offline:
        count = 0
        for rec in catalog["repositories"]:
            if args.limit and count >= args.limit:
                break
            count += 1
            try:
                value = metadata(rec["repository"], token)
                rec["repository"] = value.get("full_name") or rec["repository"]
                rec["url"] = value.get("html_url") or rec["url"]
                rec["stars"] = int(value["stargazers_count"])
                rec["description"] = value.get("description")
                rec["license_spdx_id"] = (value.get("license") or {}).get("spdx_id")
                rec["archived"] = bool(value.get("archived", False))
                rec["pushed_at"] = value.get("pushed_at")
                rec["stars_checked_at"] = datetime.now(timezone.utc).date().isoformat()
                changed += 1
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError) as exc:
                errors.append(f"{rec['repository']}: {exc}")
                print(f"Warning: {errors[-1]}", file=sys.stderr)
                # If rate-limited, avoid hammering the API; preserve existing metadata.
                if isinstance(exc, urllib.error.HTTPError) and exc.code in (403, 429):
                    print("GitHub rate limit or access error; stopping early.", file=sys.stderr)
                    break
            time.sleep(0.02)
        if changed:
            catalog["metadata_refreshed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            catalog["snapshot_date"] = datetime.now(timezone.utc).date().isoformat()
    text_csv, text_md = export(catalog)
    if args.dry_run:
        print(f"Dry run: {changed} fetched; {len(errors)} errors; {len(catalog['repositories'])} records")
    else:
        changed_paths = []
        for path, content in ((DATA, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"),
                              (CSV, text_csv), (DOC, text_md)):
            if write_if_changed(path, content):
                changed_paths.append(str(path.relative_to(ROOT)))
        print(f"Refreshed {changed} GitHub records; errors {len(errors)}; updated files: {', '.join(changed_paths) or '(none)'}")
    if errors and args.strict:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
