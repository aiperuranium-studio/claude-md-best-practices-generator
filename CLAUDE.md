# Claude Code Project Igniter

An AI-driven tool that maintains a catalog of Claude Code entities (agents, skills, rules, hooks) and intelligently selects, specializes, and installs only the relevant ones into a target project. Run `/ignite` after planning a new project's architecture to get a fully tailored Claude Code configuration — with transparent gap reporting for uncovered technologies.

## Tech Stack

- **Python 3.10+**, standard library only (external deps documented explicitly when unavoidable).
- **Bash** (`#!/usr/bin/env bash`), POSIX-compatible where possible.
- **Markdown** for documentation, skill definitions, and agent definitions.
- **JSON** for configuration (`sources.json`, `manifest.json`, `settings.json`).

## Common Commands

- `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` — Fetch raw content from curated web sources into `docs/guidelines-raw.json`.
- `python3 .claude/skills/refresh-guidelines/scripts/parse-insights.py` — Parse `/insights` report into `docs/insights-parsed.json`.
- `python3 -c "import json; json.load(open('catalog/sources.json'))"` — Validate `sources.json` syntax.

Skills (invoked within Claude Code):
- `/refresh-guidelines` — Enriches CLAUDE-MD-SOTA writing guidelines from web sources + `/insights` data.
- `/sync-catalog` — Clones/pulls remote sources and rebuilds the manifest (Sprint 2+).
- `/add-source` — Registers a new remote entity source (Sprint 4+).
- `/ignite` — Selects, specializes, and installs entities into a target project (Sprint 5+).

## Project Structure

```
claude-code-project-igniter/
├── CLAUDE.md                              # This file — project working instructions
├── .gitignore
├── docs/
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md # Architecture & design (unified plan)
│   ├── CLAUDE-MD-SOTA.md             # Seed: web-sourced generation reference (tracked)
│   ├── CLAUDE-MD-SOTA.enriched.md    # Enriched: seed + /insights (gitignored)
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md  # Sprint-based development plan
│   ├── SOURCE-SCHEMA.md              # Source registry field reference
│   ├── guidelines-raw.json           # Output of fetch-guidelines.py (gitignored)
│   ├── insights-raw.md               # Accumulated /insights tips (gitignored)
│   ├── insights-parsed.json          # Output of parse-insights.py (gitignored)
│   └── old/                          # Archived pre-merge plans
├── .claude/
│   ├── settings.json
│   ├── skills/
│   │   ├── ignite/                   # /ignite skill (Sprint 5)
│   │   ├── sync-catalog/             # /sync-catalog skill (Sprint 4)
│   │   ├── add-source/               # /add-source skill (Sprint 4)
│   │   └── refresh-guidelines/       # /refresh-guidelines skill (Sprint 1.5)
│   └── agents/
│       └── catalog-inspector.md      # Deep entity inspection agent (Sprint 4)
├── catalog/
│   ├── sources.json                  # Source registry
│   ├── manifest.json                 # Auto-generated entity index (gitignored)
│   └── sources/                      # Downloaded repos (gitignored except local/)
│       └── local/                    # User's custom entities (tracked)
```

## Coding Conventions

- **Doc separation** — Files in `docs/` fall into three categories:
  - *Internal dev docs* (`IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`, `IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`, `old/`) — development-only, never shipped.
  - *Sub-products* (`CLAUDE-MD-SOTA.md`, `SOURCE-SCHEMA.md`) — application outputs tracked in git; **must never reference internal dev docs**, only other sub-products.
  - *Generated artifacts* (`CLAUDE-MD-SOTA.enriched.md`, `guidelines-raw.json`, `insights-parsed.json`, `insights-raw.md`) — produced locally by running the tool, gitignored.
- **Cross-referencing** — When any file in `docs/` is created or modified, check all other docs files and add hyperlink references where missing. Every doc should link to related docs.
- **Sub-product isolation** — Sub-products may **only** hyperlink to other sub-products. Internal dev docs may freely reference anything.
- **Prefer pointers to copies** — Don't embed code snippets in documentation; use `file:line` references to point at the authoritative source code.

## Workflow Preferences

**Write-first, never chat-first**
> When asked to create a plan, save it to a file, or write documentation, ALWAYS write it to a file immediately. Do NOT present it in plan mode or chat output first — write directly to the requested file path. If no path is specified, ask for one before proceeding.

**No preemptive execution**
> Do NOT start implementing or running code unless the user explicitly asks you to. When presenting a plan or analysis, wait for user approval before taking action.

**No scope creep**
> Do NOT extrapolate, suggest features, or expand scope beyond what was explicitly requested. If you have ideas, mention them briefly at the end but do not elaborate unless asked.

**Clarify before acting**
> When you don't understand a request (especially if it's in Italian or domain-specific), ASK for clarification rather than guessing and jumping into action. It's better to ask one question than to waste time on a wrong approach.

**Proportional response**
> For simple changes (e.g., a `.gitignore` entry), act directly — do not enter plan mode. Match complexity of approach to complexity of task.

**One-section-at-a-time**
> Complete one document/section fully (analysis + fixes) before moving to the next. Do not scatter partial edits across multiple files.

**Renumbering & cross-reference validation**
> After any insertion, deletion, or reordering of numbered sections/references, re-validate numbering. Never leave orphaned references.

## Authoritative Documents

- **Architecture & design**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md)
- **CLAUDE.md generation rules**: [docs/CLAUDE-MD-SOTA.md](docs/CLAUDE-MD-SOTA.md) (seed) / `docs/CLAUDE-MD-SOTA.enriched.md` (enriched, gitignored)
- **Development agenda**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md)
- **Source schema**: [docs/SOURCE-SCHEMA.md](docs/SOURCE-SCHEMA.md)

## Task Management

> For long multi-file tasks, use TodoWrite to create a checklist of all files/sections to process BEFORE starting work. Update the checklist as each item completes.
