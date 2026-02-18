# Claude Code Project Igniter

An AI-driven tool that maintains a catalog of Claude Code entities (agents, skills, rules, hooks) and intelligently selects, specializes, and installs only the relevant ones into a target project. Run `/ignite` after planning a new project's architecture to get a fully tailored Claude Code configuration — with transparent gap reporting for uncovered technologies.

## Tech Stack

- **Python 3.10+**, standard library only (external deps documented explicitly when unavoidable).
- **Bash** (`#!/usr/bin/env bash`), POSIX-compatible where possible.
- **Markdown** for documentation, skill definitions, and agent definitions.
- **JSON** for configuration (`sources.json`, `manifest.json`, `settings.json`).

## Common Commands

- `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` — Fetch raw content from curated web sources into `docs/guidelines-raw.json`.
- `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py --check-freshness` — Check source URL reachability and staleness, write `docs/freshness-report.json`.
- `python3 .claude/skills/refresh-guidelines/scripts/parse-insights.py` — Parse `/insights` report into `docs/insights-parsed.json`. Manual tips go in `docs/insights-raw.md`.
- `python3 -c "import json; json.load(open('catalog/sources.json'))"` — Validate `sources.json` syntax.
- `.venv/bin/pytest tests/ -v` — Run all tests (or `uv run pytest tests/ -v`).

Skills (invoked within Claude Code):
- `/refresh-guidelines` — Enriches CLAUDE-MD-SOTA writing guidelines from web sources + `/insights` data.
- `/sync-catalog` — Clones/pulls remote sources and rebuilds the manifest (Sprint 2+).
- `/add-source` — Registers a new remote entity source (Sprint 4+).
- `/ignite` — Selects, specializes, and installs entities into a target project (Sprint 5+).

## Project Structure

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, prerequisites, installation, quick-start |
| `docs/` | Architecture plan, dev agenda, CLAUDE-MD-SOTA generation reference, source schema |
| `docs/test-archetypes/` | Sprint 6 archetype descriptions + `RESULTS.md` (integration testing) |
| `.claude/skills/` | `/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines` skill definitions |
| `.claude/agents/` | `catalog-inspector` agent (Sprint 4+) |
| `catalog/sources.json` | Source registry — where entities come from |
| `catalog/manifest.json` | Auto-generated entity index (gitignored) |
| `catalog/sources/` | Downloaded repos (gitignored) + `local/` (user custom entities, tracked) |
| `tests/` | pytest test files, one per sprint |

Each subdirectory has its own scoped `CLAUDE.md` with directory-specific instructions.

## Coding Conventions

- **Prefer pointers to copies** — Don't embed code snippets in documentation; use `file:line` references to point at the authoritative source code.
- **Documentation rules** — See `docs/CLAUDE.md` for doc classification (internal dev docs vs sub-products vs generated artifacts), cross-referencing, and sub-product isolation rules.

## Workflow Preferences

- **IMPORTANT: Write-first, never chat-first** — When asked to write documentation or plans, write directly to a file. Do NOT present in chat first. Ask for a file path if none specified.
- **IMPORTANT: No preemptive execution** — Do NOT implement or run code unless explicitly asked. Wait for user approval after presenting plans.
- **IMPORTANT: No scope creep** — Do NOT extrapolate or expand scope beyond what was requested. Mention ideas briefly at the end only if relevant.
- **Clarify before acting** — When unclear on a request (especially Italian or domain-specific terms), ask rather than guess.
- **Proportional response** — For simple changes, act directly. Match complexity of approach to complexity of task.
- **One-section-at-a-time** — Complete one document/section fully before moving to the next. Do not scatter partial edits.

## Authoritative Documents

- **Architecture & design**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md)
- **CLAUDE.md generation rules**: [docs/CLAUDE-MD-SOTA.md](docs/CLAUDE-MD-SOTA.md) (seed) / `docs/CLAUDE-MD-SOTA.enriched.md` (enriched, gitignored)
- **Development agenda**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md)
- **Source schema**: [docs/SOURCE-SCHEMA.md](docs/SOURCE-SCHEMA.md)
