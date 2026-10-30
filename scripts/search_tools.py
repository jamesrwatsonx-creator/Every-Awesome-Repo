"""Search individual data sources and tools extracted from Awesome collections.

All searches are local and do not modify the collection index or upstream
projects. Documentation evidence and list mentions are reported separately.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "data" / "tools.json"
STOPWORDS = {"a", "an", "and", "app", "application", "build", "create",
             "for", "from", "i", "in", "is", "of", "on", "or", "the",
             "to", "using", "with", "want", "that"}
ALIASES = {
    "map": ("geospatial", "gis", "maps"),
    "maps": ("geospatial", "gis", "map"),
    "live": ("real", "time", "streaming", "realtime"),
    "realtime": ("streaming", "real", "time"),
    "data": ("dataset", "datasets", "api", "database"),
    "finance": ("market", "stock", "financial", "crypto"),
    "transport": ("traffic", "transit", "rail", "train", "bus"),
    "weather": ("climate", "forecast", "noaa"),
    "raster": ("geospatial", "geo", "raster"),
    "realestate": ("real", "estate", "housing"),
}

def tokens(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", str(value or "").lower())
            if len(x) > 1 and x not in STOPWORDS}

def search(index: dict, query: str, *, limit: int = 20,
           collection: str | None = None,
           documented_only: bool = False) -> list[dict]:
    if index.get("schema_version") != "1.0.0" or not isinstance(index.get("tools"), list):
        raise ValueError("Invalid individual tool index")
    wanted = tokens(query)
    expanded = set(wanted)
    for term in wanted:
        expanded.update(ALIASES.get(term, ()))
    hits = []
    for item in index["tools"]:
        if not isinstance(item, dict):
            continue
        if documented_only and item.get("evidence_status") != "UPSTREAM_DOCUMENTED_NOT_TESTED":
            continue
        sources = item.get("source_collections", [])
        if collection and not any(
            str(s.get("repository", "")).lower() == collection.lower()
            for s in sources if isinstance(s, dict)
        ):
            continue
        name = tokens(item.get("name"))
        desc = tokens(item.get("description"))
        sections = tokens(" ".join(item.get("topics") or []))
        upstream = tokens(" ".join(
            e.get("documented_statement", "") for e in item.get("upstream_evidence", [])
            if isinstance(e, dict)
        ))
        direct = wanted & (name | desc | sections | upstream)
        related = expanded & (name | desc | sections | upstream)
        score = (9 * len(direct & name)
                 + 5 * len(direct & desc)
                 + 3 * len(direct & sections)
                 + 4 * len(direct & upstream)
                 + len(related - direct))
        if score == 0:
            continue
        hits.append({
            **item,
            "match_score": score,
            "matched_terms": sorted(related),
        })
    hits.sort(key=lambda x: (-x["match_score"],
                             x.get("evidence_status") != "UPSTREAM_DOCUMENTED_NOT_TESTED",
                             x.get("name", "").lower(),
                             x.get("url", "")))
    return hits[:max(0, min(int(limit), 100))]

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", help="Idea or capability; e.g. realtime transport data")
    p.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    p.add_argument("--collection", help="Limit to an upstream curated collection owner/repo")
    p.add_argument("--documented-only", action="store_true")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    data = json.loads(args.index.read_text(encoding="utf-8"))
    hits = search(data, args.query, limit=args.limit, collection=args.collection,
                  documented_only=args.documented_only)
    if args.json:
        print(json.dumps({"query": args.query, "count": len(hits), "results": hits},
                         ensure_ascii=False, indent=2))
    else:
        print(f"Found {len(hits)} candidate tools/data sources:")
        for item in hits:
            print(f"\n- {item['name']} [{item['evidence_status']}]")
            print(f"  {item['url']}")
            print(f"  {item.get('description') or '(no list description)'}")
            src = item.get("source_collections", [])
            if src:
                print(f"  Listed at: {src[0]['evidence_url']}")
            docs = item.get("upstream_evidence", [])
            if docs:
                print(f"  Upstream statement: {docs[0]['documented_statement']}")
                print(f"  Source: {docs[0]['evidence_url']}")
        print("\nA list mention is not tool validation. Documentation is not runtime verification.")

if __name__ == "__main__":
    main()
