# Every Awesome Repo

**Find what already exists. Understand what it can do. Build something new.**

Every Awesome Repo is an **open, searchable discovery index of curated GitHub collections, developer resources, and open-source ecosystems**. Its purpose is to make the world's reusable software knowledge accessible to people and coding agents **before** they select a framework, commit to a stack, or rebuild an existing solution.

This is **not** a collection of source code copied from hundreds of independent projects. We link to original upstream repositories, preserve attribution, and treat upstream authors as the source of truth. This repository supplies the *index, categorization, discovery metadata, workflows and instructions* that make those resources usable together.

> **Core principle:** Organize resources by what they are and what capabilities they might offer—not by a fixed list of apps someone might someday build. Begin with an application idea; discover the building blocks afterward.

## What this repository contains

- **27 primary subject categories**, from OSINT, public data and geospatial intelligence to UI/UX, frontend, backend, AI agents, MCP, voice, commerce, security, Web3, robotics and developer tooling.
- **273 unique linked repositories** across **275 category placements**. A repository can appear in multiple relevant categories without duplicating its record.
- **All 34 collections from the original research screenshots**, including five that had been omitted from the initial top-ten shortlist.
- **No ten-item cap**: each category can grow without requiring an arbitrary ranking cutoff.
- **[Complete human-readable directory](docs/CATALOG.md)** with linked upstream sources and snapshot star counts.
- **[Machine-readable catalog](data/catalog.json)**, **[CSV export](data/catalog.csv)**, candidate discovery tags and original-source provenance.
- **[Search script](scripts/search_catalog.py)** to find potential matches from a project idea; **[agent instructions](AGENTS.md)** for Codex or other coding assistants.
- **[Metadata refresh script](scripts/sync_metadata.py)** and scheduled GitHub Actions workflow to keep GitHub repository metadata current.

## What it is for

When you have an idea—say, a business website with voice booking, live inventory, CRM, maps, automations and an AI concierge—the agent should *search this entire index*, locate relevant collections and then inspect their upstream contents to shortlist actual components.

The intended workflow is **idea → required capabilities → catalog search → upstream inspection → compatibility / licensing / security / cost assessment → architecture → implementation**.

This catalog is a **starting point, not evidence that any specific tool is secure, license-compatible, active, or fit for production**. Stars show interest, not suitability. A linked Awesome list may itself contain dozens or thousands of tools; those individual dependencies must be inspected before adoption.

## Quick start

```bash
git clone https://github.com/jamesrwatsonx-creator/Every-Awesome-Repo.git
cd Every-Awesome-Repo

# Search across titles, categories and discovery tags
python scripts/search_catalog.py "voice assistant restaurant booking payments"

# Structured JSON output for downstream agents
python scripts/search_catalog.py "geospatial map realtime data" --json --limit 20

# Refresh stars, descriptions, license indicators and activity from GitHub (optional)
# Requires internet access; set GITHUB_TOKEN to increase the API rate limit
python scripts/sync_metadata.py
```

You can also open **[the full directory](docs/CATALOG.md)** and browse by category. Read **[AGENTS.md](AGENTS.md)** to give an AI coding agent a disciplined discovery-and-evaluation workflow.

## Browse the 27 categories

| # | Category | Linked collections |
|---|---|---:|
| 1 | [OSINT & information discovery](docs/CATALOG.md#osint-information-discovery) | 10 |
| 2 | [MCP servers & integrations](docs/CATALOG.md#mcp-servers-integrations) | 12 |
| 3 | [AI agents & specialized tools](docs/CATALOG.md#ai-agents-specialized-tools) | 12 |
| 4 | [Scraping & extraction](docs/CATALOG.md#scraping-extraction) | 10 |
| 5 | [APIs & public datasets](docs/CATALOG.md#apis-public-datasets) | 11 |
| 6 | [Geographic intelligence](docs/CATALOG.md#geographic-intelligence) | 10 |
| 7 | [Competitive & change intelligence](docs/CATALOG.md#competitive-change-intelligence) | 10 |
| 8 | [Data engineering & relational joins](docs/CATALOG.md#data-engineering-relational-joins) | 10 |
| 9 | [Additional specialized intelligence](docs/CATALOG.md#additional-specialized-intelligence) | 10 |
| 10 | [UI, UX & design systems](docs/CATALOG.md#ui-ux-design-systems) | 10 |
| 11 | [Frontend & interactive experiences](docs/CATALOG.md#frontend-interactive-experiences) | 10 |
| 12 | [Mobile, desktop & cross-platform apps](docs/CATALOG.md#mobile-desktop-crossplatform-apps) | 10 |
| 13 | [Backend & full-stack development](docs/CATALOG.md#backend-fullstack-development) | 10 |
| 14 | [AI models, machine learning & RAG](docs/CATALOG.md#ai-models-machine-learning-rag) | 10 |
| 15 | [Generative media & creative AI](docs/CATALOG.md#generative-media-creative-ai) | 10 |
| 16 | [Voice, speech & real-time communication](docs/CATALOG.md#voice-speech-realtime-communication) | 10 |
| 17 | [Automation & workflow orchestration](docs/CATALOG.md#automation-workflow-orchestration) | 10 |
| 18 | [Databases, analytics & visualization](docs/CATALOG.md#databases-analytics-visualization) | 10 |
| 19 | [E-commerce, payments & fintech](docs/CATALOG.md#ecommerce-payments-fintech) | 10 |
| 20 | [Marketing, growth & creator infrastructure](docs/CATALOG.md#marketing-growth-creator-infrastructure) | 10 |
| 21 | [DevOps, cloud & self-hosting](docs/CATALOG.md#devops-cloud-selfhosting) | 10 |
| 22 | [Cybersecurity, identity & software quality](docs/CATALOG.md#cybersecurity-identity-software-quality) | 10 |
| 23 | [Blockchain, Web3 & decentralized systems](docs/CATALOG.md#blockchain-web3-decentralized-systems) | 10 |
| 24 | [Gaming, simulation & spatial computing](docs/CATALOG.md#gaming-simulation-spatial-computing) | 10 |
| 25 | [Robotics, hardware & physical AI](docs/CATALOG.md#robotics-hardware-physical-ai) | 10 |
| 26 | [Education, science & specialized industries](docs/CATALOG.md#education-science-specialized-industries) | 10 |
| 27 | [Developer productivity & knowledge tools](docs/CATALOG.md#developer-productivity-knowledge-tools) | 10 |

## How search works

- **Storage:** a canonical entry per upstream repository in `data/catalog.json`, with one primary category and zero or more additional categories.
- **Discovery:** category-level candidate tags, searchable names and later GitHub-provided descriptions. A tag is a discovery hint, *not a validated feature*.
- **Selection:** a coding agent retrieves upstream READMEs, documentation, releases and licenses, then checks actual APIs, maintenance, security and compatibility against the app requirements.
- **Extension:** add a new resource without changing the architecture. The index can expand from Awesome collections to individual tools, MCP servers, APIs, design systems and reusable components over time.

This design avoids prematurely organizing every resource around imagined app templates. It also avoids having to keep 200+ external repositories forked or copied inside one Git tree.

## Data accuracy, provenance and ranking

The initial star counts are a **2026-10-29 snapshot** and can change. The catalog combines the previous 270 selected category entries with the complete set of 34 screenshot-supplied collections; five entries had been missing. These are **candidate curated lists**, not 273 individually audited software products, and not a guaranteed exhaustive top-10 ranking across GitHub.

Fields such as `license_spdx_id`, `archived`, `pushed_at` and `description` are blank until refreshed or reviewed. The catalog intentionally does **not** claim that an unreviewed collection or its child repositories carry a particular license. The catalog can grow and be reviewed collaboratively.

## Contribution and maintenance

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for adding collections, verifying URLs, resolving duplicates, improving tags, updating metadata and avoiding unlicensed code copies. `scripts/sync_metadata.py` refreshes metadata against GitHub without downloading upstream source. The weekly automation commits updated data and directory files when changed.

## Ownership and boundaries

Each linked repository remains owned and licensed by its respective maintainer. This project contains only the original index, metadata and automation code—not mirrors of third-party repositories, forks, redistributed bundles or implied endorsements. Before integrating any source into a product, check its license and relevant data/API terms separately.

**Repository description (GitHub About):** Searchable open-source discovery index: 27 categories of Awesome lists, AI agents, MCP, APIs, UI and developer tools—organized for building any app.
