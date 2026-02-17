# refresh-guidelines/ — Scoped Instructions

## Purpose

Dual-source enrichment pipeline: fetches web best practices + `/insights` behavioral data, classifies incoming content, and produces CLAUDE.md generation reference files.

## Scripts

- **`scripts/fetch-guidelines.py`** — Reads `references/curated-sources.md` for URLs, fetches each source, writes `docs/guidelines-raw.json`. With `--check-freshness`: checks URL reachability and "Last verified" staleness, writes `docs/freshness-report.json`.
- **`scripts/parse-insights.py`** — Reads `~/.claude/usage-data/report.html` (+ `facets/*.json`, `session-meta/*.json`), writes `docs/insights-parsed.json`

Both scripts: Python 3.10+, stdlib only, no external dependencies.

## Reference Files

- **`references/curated-sources.md`** — Tiered URL registry (Tier 1: official Anthropic, Tier 2: community guides, Tier 3: templates)
- **`references/enrichment-procedure.md`** — Classification algorithm (novel / duplicate / reinforcing / conflicting)

## Output Conventions

Two output files, never conflate them:

| File | Contains | Git Status |
|------|----------|------------|
| `docs/CLAUDE-MD-SOTA.md` | Web-sourced content only (Tiers 1-3) | Tracked (seed) |
| `docs/CLAUDE-MD-SOTA.enriched.md` | Seed + `/insights` merged | Gitignored |

Both files are sub-products — they must **never** reference internal dev docs.

## Skill Definition

Full procedure and constraints: `SKILL.md` in this directory.

## Tests

`tests/test_sprint1_5_guidelines_enrichment.py` — covers script functions, reference file parsing, output schema, and gitignore entries.
