#!/usr/bin/env python3
"""Search the Every Awesome Repo index using only Python's standard library.

This is lexical discovery over repository names, categories, tags and (when refreshed)
GitHub descriptions. It is not an LLM, full-text index of downstream tools, or proof
that an upstream repo actually implements a discovered feature.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
STOPWORDS = {"a", "an", "and", "app", "application", "build", "create", "for",
             "i", "in", "into", "me", "my", "of", "on", "or", "the", "to",
             "that", "this", "using", "want", "website", "with"}
ALIASES = {
    "voice": {"speech", "tts", "audio", "conversational"},
    "assistant": {"agent", "agents", "ai"},
    "booking": {"scheduling", "calendar", "automation", "workflows"},
    "reservation": {"booking", "scheduling", "calendar"},
    "restaurant": {"commerce", "ecommerce", "hospitality", "payments"},
    "maps": {"geospatial", "gis", "map", "location"},
    "map": {"geospatial", "gis", "maps"},
    "location": {"geospatial", "maps", "gis"},
    "dashboard": {"visualization", "analytics", "ui"},
    "realtime": {"streaming", "real", "time"},
    "real-time": {"streaming", "realtime"},
    "chatbot": {"llm", "voice", "conversational"},
    "customer": {"crm", "commerce", "marketing"},
    "payments": {"fintech", "ecommerce", "commerce"},
    "shopping": {"ecommerce", "commerce"},
    "auth": {"authentication", "identity", "security"},
    "automation": {"workflow", "orchestration"},
    "website": {"frontend", "backend", "design"},
    "video": {"creative", "media", "generative"},
}

def tokenize(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(t) > 1 and t not in STOPWORDS}

def search(data: dict, query: str, limit: int = 20,
           category: str | None = None, original_only: bool = False) -> list[dict]:
    terms = tokenize(query)
    expanded = set(terms)
    for term in terms:
        expanded.update(ALIASES.get(term, ()))
    results = []
    for entry in data["repositories"]:
        if original_only and not entry.get("original_screenshot"):
            continue
        if category and not any(category.lower() in c.lower() for c in entry["categories"]):
            continue
        name = tokenize(entry["repository"])
        cats = tokenize(" ".join(entry["categories"]))
        tags = tokenize(" ".join(entry.get("discovery_tags", [])))
        desc = tokenize(entry.get("description") or "")
        # A repository name match is strongest; descriptions are weaker and may
        # reflect a broad collection rather than a specific software capability.
        direct = terms & (name | cats | tags | desc)
        matched = expanded & (name | cats | tags | desc)
        score = (sum(10 for x in direct if x in name)
                 + sum(6 for x in direct if x in tags)
                 + sum(4 for x in direct if x in cats)
                 + sum(2 for x in direct if x in desc)
                 + sum(1 for x in matched - direct))
        if not score:
            continue
        results.append({"score": score, "matched_terms": sorted(matched),
                        **entry})
    results.sort(key=lambda e: (-e["score"], -int(e.get("stars") or 0), e["repository"].lower()))
    return results[:limit]

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", help="An app idea or one or more candidate capabilities")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--category", help="Optional category-name substring")
    p.add_argument("--original-only", action="store_true", help="Only original screenshot sources")
    p.add_argument("--json", action="store_true", help="Output machine-readable results")
    p.add_argument("--catalog", type=Path, default=CATALOG)
    args = p.parse_args()
    with args.catalog.open(encoding="utf-8") as fh:
        data = json.load(fh)
    hits = search(data, args.query, max(1, args.limit), args.category, args.original_only)
    if args.json:
        print(json.dumps({"query": args.query, "count": len(hits), "results": hits}, indent=2, ensure_ascii=False))
    else:
        print(f"Found {len(hits)} potential collections for: {args.query!r}")
        for h in hits:
            print(f"  {h['score']:>3}  {h['repository']}  ({h.get('stars', 0):,} stars)")
            print(f"       {h['url']}  |  {', '.join(h['categories'])}")
        print("\nDiscovery matches are leads, not audited components. Inspect upstream source before use.")

if __name__ == "__main__":
    main()
