# Contributing to Every Awesome Repo

This is a **discovery index**, not a mirror of third-party repositories. Contributions should make it easier for a human or coding agent to locate, verify and combine suitable upstream resources.

## Add a collection

1. Check whether `owner/repo` already appears in `data/catalog.json` (case-insensitive). If present, extend its `categories` and candidate `discovery_tags` rather than duplicating the entry.
2. If new, add one canonical GitHub repository URL, an existing primary category, one or more category names, and candidate tags. Set `review_status` to `linked-not-audited` until independently checked.
3. Keep `original_screenshot` unchanged for the 34 original research collections. New additions should have this flag set to `false`.
4. Obtain metadata from GitHub using `python scripts/sync_metadata.py`; don't guess star counts, maintenance, licenses, or compatibility.
5. Regenerate `docs/CATALOG.md` and `data/catalog.csv` by running the sync script. Run `python -m unittest discover -s tests -v`.
6. Submit a PR describing the category choices, overlap, and why the collection is useful.

## Editorial policy

- Favor original upstream maintainers and genuinely useful, well-maintained curated collections over scraped duplicates, spam, abandoned forks or misleading self-promotion.
- Categories are broad browsing families. The same repo may appear in more than one category via a single canonical record.
- Tags help discovery but **do not constitute proof of capability**. If a tag requires inspection, add a reviewer note in the PR.
- Star counts are snapshots and must be dated; they are not quality, security or permission indicators.
- Never copy the contents of a linked project without checking its license, permissions and attribution requirements. Never commit API keys, credentials or user data.
- An Awesome collection may contain tools with different licenses or usage policies. Evaluate **individual child tools** before product use.
- Check link health, repository moves, archived state, licenses, release cadence, documentation and security where relevant.

## Security

Don't execute third-party repositories during catalog maintenance. The scheduled metadata sync only makes HTTPS requests to GitHub's public repository metadata API, retains prior data on errors, and does not download source code.

## License

Linked upstream projects retain their own copyright and licensing. Do not infer a license for a child project from its parent's Awesome list. This catalog has no blanket permission to sublicense upstream source.
