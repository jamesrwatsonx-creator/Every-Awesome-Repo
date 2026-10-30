"""Bounded, read-only GitHub Awesome-list extraction and evidence indexing.

A collection mention is evidence of inclusion only, NOT proof that the named
project does what the list claims. Upstream README excerpts can be added using
--enrich-repo for specific GitHub implementations. No upstream code is executed.
Only the local data/tools.json index is written.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "tools.json"
API_BASE = "https://api.github.com/repos/"
MAX_README_BYTES = 3_000_000
MAX_ENTRIES = 20_000
GITHUB_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ENTRY_RE = re.compile(
    r"^\s*[-*+]\s+\[([^\]\n]+)\]\((https?://[^\s)]+)\)\s*(.*)$"
)
HEADER_RE = re.compile(r"^#{2,5}\s+(.+?)\s*#*\s*$")


class IndexError(ValueError):
    """Malformed input or unsafe source data."""


def utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def github_identity(url: str) -> str | None:
    u = urlparse(url)
    if u.scheme != "https" or u.netloc.lower() not in ("github.com", "www.github.com"):
        return None
    parts = u.path.strip("/").split("/")
    if len(parts) != 2 or u.query or u.fragment or u.params:
        return None
    candidate = "/".join(parts)
    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    return candidate if GITHUB_REPO_RE.fullmatch(candidate) else None


def normalize_url(url: str) -> str | None:
    if not isinstance(url, str) or len(url) > 1800:
        return None
    u = urlparse(url)
    if u.scheme not in ("https", "http") or not u.hostname or u.username or u.password:
        return None
    if u.hostname in ("localhost",) or u.hostname.endswith(".localhost"):
        return None
    if u.hostname.startswith(("127.", "10.", "192.168.", "169.254.", "172.16.")):
        return None
    # These URLs are recorded only; they are never fetched or executed.
    return url.split("#", 1)[0].rstrip("/")


def source_permalink(repo: str, sha: str, path: str, line: int) -> str:
    return f"https://github.com/{repo}/blob/{sha}/{quote(path, safe='/')}#L{line}"


def cleaned(text: str, limit: int = 500) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    return value[:limit]


def extract_markdown(
    source: str, sha: str, path: str, markdown: str, *, limit: int = 100
) -> list[dict]:
    """Extract external project links in actual Markdown list entries.

    We deliberately ignore TOC anchors, inline unrelated links, and nested
    Markdown page contents. The listed sentence is the only catalog evidence.
    """
    if not GITHUB_REPO_RE.fullmatch(source):
        raise IndexError("Invalid collection owner/repo")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise IndexError("A pinned, 40-character Git commit is required")
    if path.startswith("/") or ".." in Path(path).parts or not path.lower().endswith((".md", ".markdown")):
        raise IndexError("Only a relative Markdown source path is accepted")
    section = ""
    results = []
    for number, line in enumerate(markdown.splitlines(), 1):
        heading = HEADER_RE.match(line)
        if heading:
            section = cleaned(heading.group(1), 120)
            continue
        match = ENTRY_RE.match(line)
        if not match:
            continue
        title, raw_url, remainder = match.groups()
        url = normalize_url(raw_url)
        if not url:
            continue
        title = cleaned(title, 160)
        if not title or title.lower().startswith(("badge", "awesome")):
            continue
        identity = github_identity(url)
        # A stable identifier permits the same child tool to appear in
        # multiple Awesome collections without duplicate canonical entries.
        key = identity.lower() if identity else url.lower()
        entry = {
            "id": "tool:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24],
            "name": title,
            "url": url,
            "github_repository": identity,
            "description": cleaned(remainder.lstrip(" -–—:")) or None,
            "topics": [section] if section else [],
            "evidence_status": "LISTED_ONLY",
            "source_collections": [{
                "repository": source,
                "path": path,
                "commit": sha,
                "line": number,
                "section": section,
                "evidence_url": source_permalink(source, sha, path, number),
                "listed_claim": cleaned(line, 450),
                "evidence_type": "AWESOME_LIST_MENTION"
            }],
            "upstream_evidence": [],
            "license_spdx_id": None,
            "last_documentation_review": None
        }
        results.append(entry)
        if len(results) >= max(0, limit):
            break
    return results


def merge(current: dict, incoming: list[dict]) -> dict:
    if not isinstance(current, dict) or current.get("schema_version") != "1.0.0":
        raise IndexError("Unsupported tool index schema")
    old = current.get("tools")
    if not isinstance(old, list):
        raise IndexError("Missing tools array")
    index = {r["id"]: r for r in old}
    if len(index) != len(old):
        raise IndexError("Duplicate canonical tool IDs")
    for item in incoming:
        prev = index.get(item["id"])
        if not prev:
            index[item["id"]] = item
            continue
        prev["topics"] = sorted(set(prev.get("topics", []) + item["topics"]))
        if not prev.get("description") and item.get("description"):
            prev["description"] = item["description"]
        keys = {(x["repository"].lower(), x["path"], x["commit"], x["line"])
                for x in prev.get("source_collections", [])}
        for src in item["source_collections"]:
            k = (src["repository"].lower(), src["path"], src["commit"], src["line"])
            if k not in keys:
                prev["source_collections"].append(src)
                keys.add(k)
        prev["source_collections"].sort(
            key=lambda r: (r["repository"].lower(), r["path"], r["line"])
        )
    if len(index) > MAX_ENTRIES:
        raise IndexError("Tool index exceeds configured size")
    return {
        **current,
        "tools": sorted(index.values(), key=lambda r: r["id"])
    }


def gh_get(endpoint: str, token: str | None = None) -> dict:
    if not endpoint.startswith("repos/"):
        raise IndexError("Only GitHub repository endpoints are allowed")
    url = "https://api.github.com/" + endpoint
    req = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "Every-Awesome-Repo-Tool-Indexer",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": "Bearer " + token} if token else {})
    })
    try:
        with urlopen(req, timeout=18) as response:
            raw = response.read(MAX_README_BYTES * 2 + 1)
        if len(raw) > MAX_README_BYTES * 2:
            raise IndexError("GitHub response is too large")
        return json.loads(raw)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise IndexError(f"GitHub request failed: {exc}") from exc


def fetch_readme(repo: str, *, path: str = "README.md",
                 ref: str | None = None, token: str | None = None) -> tuple[str, str, dict]:
    if not GITHUB_REPO_RE.fullmatch(repo):
        raise IndexError("Invalid GitHub repository identity")
    meta = gh_get("repos/" + repo, token)
    sha = ref or gh_get("repos/" + repo + "/commits/" + quote(meta["default_branch"], safe=""), token)["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise IndexError("GitHub did not provide a pinned commit")
    if path.startswith("/") or ".." in Path(path).parts:
        raise IndexError("Invalid README path")
    content = gh_get("repos/" + repo + "/contents/" + quote(path, safe="/") + "?ref=" + sha, token)
    if content.get("encoding") != "base64" or not isinstance(content.get("content"), str):
        raise IndexError("Unsupported GitHub content encoding")
    data = base64.b64decode(content["content"])
    if len(data) > MAX_README_BYTES:
        raise IndexError("README exceeds maximum allowed size")
    return sha, data.decode("utf-8-sig"), meta


def enrich_github(entry: dict, *, token: str | None = None) -> bool:
    """Record a literal upstream README statement, not an executable verification.

    The statement documents how upstream describes the project; it is not a
    test result or proof of fitness, support, operational access or licensing.
    """
    repo = entry.get("github_repository")
    if not repo:
        return False
    sha, markdown, meta = fetch_readme(repo, token=token)
    lines = markdown.splitlines()
    # Prefer descriptive prose over headings, badges, code, README navigation.
    excerpt = None
    line_no = None
    for number, line in enumerate(lines[:100], 1):
        candidate = cleaned(line, 350)
        if (45 <= len(candidate) <= 350 and
            not line.lstrip().startswith(("#", "[", "!", "<", "|", "-", "*", ">", chr(96))) and
            re.search(r"\b(is|are|provides|supports|allows|enables|offers|extension|library|database|data)\b",
                      candidate, re.IGNORECASE)):
            excerpt, line_no = candidate, number
            break
    if excerpt is None:
        return False
    evidence = {
        "evidence_type": "UPSTREAM_README_STATEMENT",
        "repository": repo,
        "path": "README.md",
        "commit": sha,
        "line": line_no,
        "evidence_url": source_permalink(repo, sha, "README.md", line_no),
        "documented_statement": excerpt
    }
    entry["upstream_evidence"] = [evidence]
    entry["evidence_status"] = "UPSTREAM_DOCUMENTED_NOT_TESTED"
    entry["last_documentation_review"] = utc_date()
    license_data = meta.get("license")
    entry["license_spdx_id"] = license_data.get("spdx_id") if isinstance(license_data, dict) else None
    entry["github_metadata"] = {
        "stars": meta.get("stargazers_count"),
        "archived": bool(meta.get("archived", False)),
        "pushed_at": meta.get("pushed_at"),
        "license_checked_at": utc_date()
    }
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True, help="Curated list owner/repository")
    parser.add_argument("--path", default="README.md")
    parser.add_argument("--source-file", type=Path,
                        help="Optional local Markdown fixture (requires --source-sha)")
    parser.add_argument("--source-sha", help="Pinned source SHA for local file")
    parser.add_argument("--limit", type=int, default=100, help="Max links per collection (1-1000)")
    parser.add_argument("--enrich-repo", action="append", default=[],
                        help="Only enrich selected GitHub child repositories")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.limit <= 1000:
        parser.error("--limit must be between 1 and 1000")
    if args.source_file:
        if not args.source_sha:
            parser.error("--source-sha is required with --source-file")
        sha, content = args.source_sha, args.source_file.read_text(encoding="utf-8")
    else:
        sha, content, _ = fetch_readme(
            args.collection, path=args.path, token=os.getenv("GITHUB_TOKEN"))
    entries = extract_markdown(args.collection, sha, args.path, content, limit=args.limit)
    existing = (json.loads(args.output.read_text(encoding="utf-8"))
                if args.output.exists()
                else {"schema_version": "1.0.0", "project": "Every Awesome Repo Tools",
                      "tools": []})
    data = merge(existing, entries)
    requested = {r.lower() for r in args.enrich_repo}
    if requested:
        token = os.getenv("GITHUB_TOKEN")
        for item in data["tools"]:
            if str(item.get("github_repository", "")).lower() in requested:
                try:
                    enrich_github(item, token=token)
                except IndexError as exc:
                    print(f"Upstream review unavailable for {item['name']}: {exc}", file=sys.stderr)
    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"collection": args.collection, "source_commit": sha,
                      "extracted": len(entries), "total_unique": len(data["tools"]),
                      "upstream_documented": sum(x["evidence_status"] == "UPSTREAM_DOCUMENTED_NOT_TESTED"
                                                 for x in data["tools"]),
                      "dry_run": args.dry_run}))


if __name__ == "__main__":
    main()
