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
git clone https://github.com/your-org/claude-code-best-practices ~/claude-md-best-practices
claude --add-dir ~/claude-md-best-practices
```

The `/refresh-guidelines` skill becomes available in every session.

### Option B — Shell alias

```bash
alias claude-bp='claude --add-dir ~/claude-md-best-practices'
```

---

## Quick Start

```bash
# 1. Clone once
git clone https://github.com/your-org/claude-code-best-practices ~/claude-md-best-practices

# 2. Open any project
cd ~/my-project
claude --add-dir ~/claude-md-best-practices

# 3. Enrich CLAUDE.md guidelines
/refresh-guidelines
```

`/refresh-guidelines` will:
1. Fetch curated web sources (Anthropic docs, community guides, templates)
2. Parse any exported `/insights` data from your Claude Code sessions
3. Produce `docs/CLAUDE-MD-SOTA.enriched.md` — a merged reference for writing CLAUDE.md files

---

## Skills Reference

| Skill | Description |
|-------|-------------|
| `/refresh-guidelines` | Enriches `docs/CLAUDE-MD-SOTA.md` from curated web sources + `/insights` data. Produces `docs/CLAUDE-MD-SOTA.enriched.md`. |

---

## Pipeline Output Files

| File | Contents | Git status |
|------|----------|------------|
| `docs/CLAUDE-MD-SOTA.md` | Web-sourced best practices (seed) | Tracked |
| `docs/CLAUDE-MD-SOTA.enriched.md` | Seed + `/insights` data merged | Gitignored |
| `docs/guidelines-raw.json` | Raw fetched source content | Gitignored |
| `docs/insights-parsed.json` | Parsed `/insights` report | Gitignored |
| `docs/freshness-report.json` | URL reachability + staleness report | Gitignored |
