# Release Notes — v1.0

**Date**: 2026-02-16
**Sprints covered**: 0, 1, 1.5

---

## Overview

First milestone release of the Claude Code Project Igniter. Establishes the project foundation, catalog infrastructure, and the guidelines enrichment pipeline — everything needed to produce high-quality CLAUDE.md generation references before the `/ignite` skill is built.

---

## Sprint 0: Project Scaffolding

Established the project skeleton, development conventions, and Claude Code configuration.

### Delivered

- **`CLAUDE.md`** (project root) — Working instructions for the igniter itself, with behavioral rules (write-first, no preemptive execution, no scope creep, clarify before acting), tech stack, common commands, project structure, and authoritative document references.
- **`.gitignore`** — Configured to ignore `catalog/sources/*/` (downloaded remote repos) while preserving `catalog/sources/local/` (user custom entities). Python ignores (`__pycache__/`, `*.pyc`, `.venv/`) included.
- **`.claude/settings.json`** — Minimal valid settings file establishing the `.claude/` directory.
- **Directory skeleton** — All planned directories created with `.gitkeep` placeholders:
  - `.claude/skills/ignite/references/`, `.claude/skills/ignite/scripts/`
  - `.claude/skills/sync-catalog/scripts/`
  - `.claude/skills/add-source/`
  - `.claude/agents/`
  - `catalog/sources/local/` with entity type subdirectories (`agents/`, `skills/`, `commands/`, `rules/`)

---

## Sprint 1: Catalog Foundation

Created the source registry and local entity directory structure, establishing a well-defined schema for the catalog.

### Delivered

- **`catalog/sources.json`** — Source registry with two entries:
  - `everything-claude-code` (priority 10) — Primary remote source pointing to `github.com/affaan-m/everything-claude-code.git`.
  - `local` (priority 1, `url: null`) — User's custom entities, never synced from remote, always wins conflicts.
- **`catalog/sources/local/README.md`** — Explains the purpose and usage of the local entity directory.
- **`docs/SOURCE-SCHEMA.md`** — Complete field reference for `sources.json`, documenting all fields (`id`, `url`, `branch`, `pin`, `priority`, `entityPaths`), valid values, and priority resolution rules.

---

## Sprint 1.5: Guidelines Enrichment Pipeline

Built the `/refresh-guidelines` skill and populated the CLAUDE.md generation reference using a dual-source seed + enriched two-file model.

### Delivered

#### Skill Definition

- **`.claude/skills/refresh-guidelines/SKILL.md`** — Entrypoint for `/refresh-guidelines` with a 10-step procedure: run scripts, read sources, classify content, produce enrichment report, get human approval, output two files.

#### Reference Files

- **`references/curated-sources.md`** — Tiered URL registry:
  - **Tier 1** (highest precedence): Official Anthropic docs (`code.claude.com/docs/en/memory`, `code.claude.com/docs/en/best-practices`, `claude.com/blog/using-claude-md-files`).
  - **Tier 2**: Established community guides (HumanLayer, Dometrain, Tembo, Arize).
  - **Tier 3**: Community templates and GitHub repos.
- **`references/enrichment-procedure.md`** — 3-phase merge algorithm (classification, conflict resolution, integration) with source precedence rules and conflict handling.

#### Scripts

- **`scripts/fetch-guidelines.py`** — Python 3.10+, stdlib only. Reads curated-sources.md, fetches web content from all tiers, outputs `docs/guidelines-raw.json` with themed content blocks. Fault-tolerant (skips failed URLs, follows redirects).
- **`scripts/parse-insights.py`** — Python 3.10+, stdlib only. Parses `/insights` report from `~/.claude/usage-data/report.html` (+ facets and session-meta JSON), outputs `docs/insights-parsed.json`. Extracts 7 report sections (CLAUDE.md Recommendations, Friction Points, Working Workflows, Feature Recommendations, Usage Patterns, Future Workflows, Usage Narrative). Handles missing report gracefully (exits 0, minimal JSON). Warns on stale reports (>7 days).

#### Generation Reference (Two-File Model)

- **`docs/CLAUDE-MD-SOTA.md`** (seed, git-tracked) — Web-sourced best practices only (Tiers 1-3). 5-part structure:
  1. Structural Standards — file hierarchy, @-imports, recommended sections, formatting rules
  2. Content Guidelines — what to include/exclude, anti-patterns
  3. Integration Guidelines — CLAUDE.md vs hooks vs skills vs rules, MCP servers, headless mode
  4. Behavioral Patterns — verification, explore-then-plan, scope discipline, parallel sessions
  5. Maintenance Guidelines — review triggers, self-improving pattern, autonomous workflows
- **`docs/CLAUDE-MD-SOTA.enriched.md`** (gitignored) — Seed content merged with `/insights` behavioral data from 29 real Claude Code sessions. Adds empirical tips on friction points, working workflows, and batch operations.

#### Scoped Child-Directory CLAUDE.md Files

Per CLAUDE-MD-SOTA.md structural standards (file hierarchy, child-directory scoping):

- **`docs/CLAUDE.md`** (~24 lines) — Document classification (3 categories), sub-product isolation, cross-referencing, renumbering rules.
- **`catalog/CLAUDE.md`** (~33 lines) — sources.json schema pointer, priority model, local entity conventions, manifest.json warning.
- **`.claude/skills/refresh-guidelines/CLAUDE.md`** (~37 lines) — Pipeline overview, script inventory, reference files, output conventions (seed vs enriched).
- **`tests/CLAUDE.md`** (~33 lines) — pytest conventions, run commands (`.venv/bin/pytest`, `uv run`), naming convention, current test files.

#### Supporting Files

- **`docs/insights-raw.md`** — Placeholder with instructions header for supplementary manual `/insights` tips.
- **`.gitignore` updates** — Added entries for `docs/guidelines-raw.json`, `docs/insights-raw.md`, `docs/insights-parsed.json`, `docs/CLAUDE-MD-SOTA.enriched.md`, `catalog/manifest.json`.

---

## Post-Sprint CLAUDE.md Restructuring

After Sprint 1.5, all 5 CLAUDE.md files were analyzed against the CLAUDE-MD-SOTA.enriched.md guidelines and restructured:

| File | Change | Lines |
|------|--------|-------|
| Root `CLAUDE.md` | Replaced verbose blockquoted workflow rules with tight bullets; added `IMPORTANT` emphasis on critical rules; replaced stale-prone project structure code block with table; moved doc-separation details to `docs/CLAUDE.md`; removed generic "Task Management" section; added pytest to Common Commands | 99 → 59 |
| `docs/CLAUDE.md` | Removed duplicated rules (pointers over copies, renumbering from root); added `IMPORTANT` to sub-product isolation | 28 → 24 |
| `catalog/CLAUDE.md` | Replaced inline validation command with pointer to root | 37 → 33 |
| `tests/CLAUDE.md` | Added `IMPORTANT` to bare-pytest warning | 33 → 33 |
| `refresh-guidelines/CLAUDE.md` | No changes needed — already well-structured | 37 → 37 |

---

## Known Limitations

- **No catalog sync yet** — `catalog/sources/everything-claude-code/` is not populated. Requires Sprint 2 (`sync-catalog.sh`).
- **No manifest** — `catalog/manifest.json` cannot be generated until sources are synced (Sprint 2) and the builder is written (Sprint 3).
- **No `/ignite` skill** — The core ignition workflow is planned for Sprint 5.
- **Web source content may drift** — Fetched content in `guidelines-raw.json` reflects the state of web sources at fetch time. Re-run `/refresh-guidelines` periodically.

---

## What's Next

| Sprint | Name | Key Deliverable |
|--------|------|-----------------|
| 2 | Catalog Sync Pipeline | `sync-catalog.sh` — clones/pulls remote sources |
| 3 | Manifest Builder | `build-manifest.py` — indexes all entities with tags |
| 4 | Sync-Catalog & Add-Source Skills | `/sync-catalog`, `/add-source` skill wrappers, `catalog-inspector` agent |
| 5 | Ignite Skill & Reference Docs | `/ignite` SKILL.md + workflow/specialization/gap-analysis guides |
| 6 | Integration Testing & Polish | Archetype tests, README, end-to-end validation |