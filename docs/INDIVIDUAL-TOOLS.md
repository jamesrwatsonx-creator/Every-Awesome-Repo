# Individual tools and evidence

Every Awesome Repo works **independently**. Its original 273-repository, 27-category collection index remains canonical and unchanged. This extension provides a separate child-tool index, suitable for data-only projects as well as UI, AI, or any other application.

## The difference between the two indexes

| Index | Contains | Authority |
| --- | --- | --- |
| `data/catalog.json` | Curated Awesome collections and their categories | Discovery only |
| `data/tools.json` | Individual projects, APIs and data sources linked *inside* selected collections | Pinned list mention and optional upstream documentation evidence |

Neither index copies external code or implies installability, ownership, quality or license clearance.

### Evidence levels

- `LISTED_ONLY` — an original curated collection lists the project. The record preserves the collection name, pinned commit, README path, line, section, and exact link. The collection's description is a claim, **not proof**.
- `UPSTREAM_DOCUMENTED_NOT_TESTED` — in addition to the list mention, the tool's own GitHub README contains a quoted supporting statement at a pinned source line. Metadata such as the repository's license identifier is recorded as reported by GitHub. This is **not a runtime test, security audit, guaranteed API availability or independently verified feature**.

Only GitHub repository candidates can currently receive upstream README evidence automatically. External API websites are indexed as listed URLs, but this tool will not crawl arbitrary domains or assert that their API terms, authentication or availability have been checked.

## Use without Maliky

Browse the full Awesome collections normally:

```bash
python scripts/search_catalog.py "public real time datasets"
```

Search individual data APIs, geospatial libraries or source projects:

```bash
python scripts/search_tools.py "realtime transport data"
python scripts/search_tools.py "spatial database raster SQL" --json
python scripts/search_tools.py "market data" --collection bytewax/awesome-public-real-time-datasets
python scripts/search_tools.py "geospatial" --documented-only
```

One-off indexed source collection; this **only writes `data/tools.json` in your local checkout**, never the source collection:

```bash
python scripts/index_tools.py --collection bytewax/awesome-public-real-time-datasets --limit 100
python scripts/index_tools.py --collection sacrdini/Awesome-Geospatial --limit 100
```

To inspect and attach a quoted README statement from a selected downstream project:

```bash
python scripts/index_tools.py --collection sacrdini/Awesome-Geospatial --limit 100 --enrich-repo ahuarte47/duckdb-raster
```

API token: optional `GITHUB_TOKEN`; public GitHub anonymous rate limits may apply. Source pins are fixed per run; the tool index doesn't automatically imply these remain current.

## Working with Maliky

Maliky can optionally fetch the **public `data/tools.json` output** and show individual external candidates separately from its owned-asset intelligence. This is an adapter, not a fork, rewrite, or shared database. Either repository remains fully usable when the other is unavailable.

## Scope and next iterations

The seed indexes selected entries from public real-time data and geospatial collections. This is **not** a complete crawl of every child linked by all 273 curated lists. Extend incrementally when a particular app idea requires another category. An evidence-linked result still needs compatibility, license, API, maintenance and security checks before implementation.
