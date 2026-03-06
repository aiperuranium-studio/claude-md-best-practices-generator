# CLAUDE.md Best Practices Generator

A tool for enriching CLAUDE.md generation guidelines from curated web sources and Claude Code `/insights` behavioral data. Attach it to any Claude Code session to make `/refresh-guidelines` available.

---

## Prerequisites

- **Python 3.10+** — for the pipeline scripts
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)** — the tool this enriches

---

## Installation

Attach the tool to your Claude Code session so its `.claude/` directory is merged alongside your project.

### Option A — `--add-dir` (recommended)

```bash
git clone https://github.com/aiperuranium-studio/claude-md-best-practices-generator ~/claude-md-best-practices
claude --add-dir ~/claude-md-best-practices
```

The `/refresh-guidelines` skill becomes available in every session.

### Option B — Shell alias

```bash
alias claude-bp='claude --add-dir ~/claude-md-best-practices'
```

### Option C — Claude Code plugin (no clone required)

```bash
claude plugin marketplace add https://github.com/aiperuranium-studio/claude-md-best-practices-generator
claude plugin install claude-md-best-practices
```

The skill is namespaced as `/claude-md-best-practices:refresh-guidelines` in plugin mode.

---

## Quick Start

```bash
# 1. Clone once
git clone https://github.com/aiperuranium-studio/claude-md-best-practices-generator ~/claude-md-best-practices

# 2. Open any project
cd ~/my-project
claude --add-dir ~/claude-md-best-practices

# 3. Enrich CLAUDE.md guidelines (run first)
/refresh-guidelines

# 4. Audit and refactor your root CLAUDE.md
/refactor-claude-md

# 4b. Audit a scoped CLAUDE.md in a subdirectory (optional target path)
/refactor-claude-md docs/CLAUDE.md

# 5. Scaffold scoped CLAUDE.md files across subdirectories
/scaffold-claude-md
```

`/refresh-guidelines` will:
1. Fetch curated web sources (Anthropic docs, community guides, templates)
2. Parse any exported `/insights` data from your Claude Code sessions
3. Produce `docs/CLAUDE-MD-SOTA.enriched.md` — a merged reference for writing CLAUDE.md files

`/refactor-claude-md` will:
1. Audit any `CLAUDE.md` against the current SOTA guidelines — root or any scoped file
2. Present a compliance report (pass / partial / fail per category)
3. Rewrite the file with your approval

Pass an optional path to target a scoped file: `/refactor-claude-md src/CLAUDE.md`

`/scaffold-claude-md` will:
1. Scan your directory tree for directories that need scoped CLAUDE.md files
2. Draft focused content for each recommended directory
3. Write the files with your approval

---

## Skills Reference

| Skill (direct mode) | Skill (plugin mode) | Description |
|---------------------|---------------------|-------------|
| `/refresh-guidelines` | `/claude-md-best-practices:refresh-guidelines` | Enriches `docs/CLAUDE-MD-SOTA.md` from curated web sources + `/insights` data. Produces `docs/CLAUDE-MD-SOTA.enriched.md`. |
| `/refactor-claude-md` | `/claude-md-best-practices:refactor-claude-md` | Audits root `CLAUDE.md` against current SOTA guidelines. Presents a compliance scorecard and rewrites the file with approval. |
| `/scaffold-claude-md` | `/claude-md-best-practices:scaffold-claude-md` | Scans the directory tree, identifies subdirectories that need scoped `CLAUDE.md` files, and generates focused content with approval. |

---

## Pipeline Output Files

| File | Contents | Git status |
|------|----------|------------|
| `docs/CLAUDE-MD-SOTA.md` | Web-sourced best practices (seed) | Tracked |
| `docs/CLAUDE-MD-SOTA.enriched.md` | Seed + `/insights` data merged | Gitignored |
| `docs/guidelines-raw.json` | Raw fetched source content | Gitignored |
| `docs/insights-parsed.json` | Parsed `/insights` report | Gitignored |
| `docs/freshness-report.json` | URL reachability + staleness report | Gitignored |
