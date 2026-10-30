# Instructions for coding and research agents

## Mission

Treat **Every Awesome Repo** as a discovery database, not an architecture prescription. When the user gives an application idea, first translate the outcome into capabilities, then search across **all** collections, evaluate the underlying tools, and propose the simplest secure implementation. Do not default to a specific framework or invent tools that have not been verified.

## Preferred workflow

1. **Clarify the application outcome**: primary users, core workflow, required live data, integrations, budget, deployment constraints, success test.
2. **Decompose into capabilities**: UI/design/motion, APIs, identity, database, streaming data, AI/voice, MCP, agents, automation, payments, monitoring, security, mobile as relevant. Avoid assuming each capability requires a new vendor.
3. **Search the local catalog**, not merely a single category. Start with `python scripts/search_catalog.py "<idea> and key capabilities" --json --limit 30`. Search more specific terms as needed; browse `data/catalog.json` when exact matching is insufficient.
4. **Expand upstream collections**: Visit the relevant original README(s), identify the actual tools and implementation libraries inside them, and verify their upstream homepages. The current index links collections, not a fully audited inventory of their children.
5. **Evaluate before selecting**: confirm README and releases, license SPDX/terms, maintenance, security posture, compatibility with proposed stack, API access and rate limits, deployment requirements, reliability, cost, latency, and data privacy. Stars are an interest signal, not a recommendation score. License metadata at the collection level does not license linked child projects.
6. **Reuse existing user systems** when explicitly provided (GitHub projects, MCP servers, self-hosted assets, CRM, managed database, cloud infrastructure). Check whether an existing service solves the requirement before suggesting another paid subscription.
7. **Recommend an implementation stack** grouped by required capability, with upstream links, evidence, integration notes, substitution options, tradeoffs, and the smallest functional MVP.
8. **Implement only after selection**. Do not install arbitrary dependencies or execute untrusted third-party repo code just to catalog it. Validate outputs and document unresolved risks.

## Data model

- `data/catalog.json`: canonical repository records, categories, candidate discovery tags, snapshot stars and original-screenshot provenance.
- `docs/CATALOG.md`: human-readable browseable catalog generated from the data.
- `data/catalog.csv`: export generated from the data.
- `scripts/search_catalog.py`: local, standard-library lexical search.
- `scripts/sync_metadata.py`: optional GitHub API refresh; calls do not clone external repos.

Each `discovery_tags` value is a **candidate subject label**, not independently verified API or feature support. `review_status=linked-not-audited` explicitly prohibits treating inclusion as validation. `original_screenshot=true` preserves the user's initial reference set.

## Example query

> Build a multi-location restaurant website with cinematic scrolling, updated menus, voice booking, CRM integration, customer accounts and admin dashboard.

Search separately for `frontend animation design systems`, `voice assistant realtime`, `commerce payments`, `automation booking calendar`, `database identity`, and `crm marketing`; shortlist real components and validate their constraints. Do not force all six into one framework or assume a collection's name means a given feature exists.

## Contribution rules

Preserve upstream identity and attribution; never copy or fork dozens of repositories into this one. Avoid duplication by canonical `owner/repo`. Add multiple `categories` and candidate discovery tags when appropriate. Do not overwrite original-source flags. Test catalog validity before committing. Never claim that GitHub stars prove safety, quality, or maintenance.

The most important evaluation output is a **verified source-to-requirement mapping**: requirement → possible component → confirmed support → integration conditions → risk → decision.
