# Release Notes — v2.0

**Date**: 2026-02-27
**Sprints covered**: 2, 3, 4, 5, 6

---

## Overview

Second milestone release — completes the Claude Code Project Igniter to its full planned scope. Builds on the catalog infrastructure and guidelines pipeline delivered in v1.0 to produce a working end-to-end ignition system: catalog sync, manifest generation, and the `/ignite` skill that selects, specialises, and installs Claude Code entities into any target project. Integration-tested against six project archetypes and shipped with a user-facing README.

---

## Sprint 2: Catalog Sync Pipeline

Builds the shell script that clones or updates remote sources defined in `sources.json`, populating `catalog/sources/` with raw entity material for the manifest builder.

### Delivered

- **`.claude/skills/sync-catalog/scripts/sync-catalog.sh`** — Bash script (`#!/usr/bin/env bash`, POSIX-compatible) that syncs all remote sources:
  - For new sources: `git clone --branch {branch} --single-branch {url}`.
  - For existing sources: `git fetch origin && git checkout {branch} && git pull`.
  - If `pin` is set: `git checkout {pin}` after clone/pull.
  - Writes `catalog/sources/{id}/.source-meta.json` after each sync: `id`, `synced_at` (ISO 8601), `commit` (HEAD SHA), `branch`, `pin`, `url`.
  - Accepts `--source <id>` flag to sync a single source. Skips the `local` source (null URL). Exits with informative error on failure.
- **`docs/SOURCE-SCHEMA.md`** (modified) — Appended `.source-meta.json` schema documentation: all six fields, ISO 8601 convention for `synced_at`, HEAD SHA for `commit`.
- **`tests/test_sprint2_catalog_sync.py`** — Covers: script existence and executability, bash shebang and `set` flags, source JSON parsing, local source skipping, `.source-meta.json` schema, `--source` flag support, error handling (missing `sources.json`, unknown argument, missing flag value).

---

## Sprint 3: Manifest Builder

Builds `build-manifest.py`, the core indexing engine that scans all synced sources and generates `catalog/manifest.json` with tagged, classified entity metadata.

### Delivered

- **`.claude/skills/ignite/scripts/build-manifest.py`** — Python 3.10+, stdlib only. Input: `catalog/sources.json`. Output: `catalog/manifest.json`.
  - **Entity discovery**: scans five entity types (`agents`, `skills`, `commands`, `rules`, `hooks`) across all sources. Skills detected via `SKILL.md` presence (fallback to `.md`). Hooks parsed from `hooks.json` per-entry.
  - **Tag classification engine**: keyword maps for languages (Python, TypeScript, JavaScript, Go, Java, Rust, and more), frameworks (Django, FastAPI, React, Next.js, Spring, Express, and more), and categories (testing, security, code-review, documentation, etc.). Classifies by filename, directory path, and first 200 lines of content. Determines `scope`: `universal`, `language-specific`, or `framework-specific`.
  - **Core entity identification**: fuzzy name matching (normalised hyphens, underscores, case) against the predefined core list — 5 agents, 4 skills, 5 commands, all `common/` rules.
  - **Adaptation detection**: `requiresAdaptation: true` for non-universal entities; core entities default to `false`.
  - **Manifest output schema**: composite `id` (`{source}::{type}::{name}`), `source`, `type`, `name`, `path`, `tags` object, `coreEntity`, `requiresAdaptation`, `metadata`. Top-level fields: `entities[]`, `coverage` summary (unique languages/frameworks/categories), `generatedAt` (ISO 8601), `sources`.
  - Deterministic output (sorted). Progress to stderr. Skips malformed files with warnings. Non-zero exit only on fatal errors.
- **`tests/test_sprint3_manifest_builder.py`** — Covers: script existence and module loading, `normalize_name`, `is_core_entity`, `classify_tags`, `discover_agents`, entity discovery for all five types, manifest output schema, composite ID format, coverage summary, determinism across two runs.
- **`RELEASE-NOTES-v1.0.md`** — First release notes document, covering Sprints 0, 1, and 1.5.

---

## Sprint 4: Sync-Catalog & Add-Source Skills

Wraps the sync and manifest-build scripts in Claude Code skills and creates the `/add-source` skill for registering new remote sources. All deliverables are documentation files — no new Python scripts or automated tests. The 307 existing tests for Sprints 1–3 continue to validate the underlying infrastructure.

### Delivered

#### `/sync-catalog` Skill

- **`.claude/skills/sync-catalog/SKILL.md`** — Entrypoint for `/sync-catalog`. Three-step procedure: (1) run `sync-catalog.sh` (with optional `--source <id>`), (2) run `build-manifest.py`, (3) report results (sources synced/skipped/failed, entities indexed by type, coverage). Four constraints: never touch `catalog/sources/local/`, never hand-edit `manifest.json`, report errors and continue, both scripts must be attempted even if the first fails.

#### `/add-source` Skill

- **`.claude/skills/add-source/SKILL.md`** — Entrypoint for `/add-source`. Four-step procedure: (1) gather `id`, `url`, `branch` (default: `main`), `priority` (default: 50), `entityPaths` from user, (2) validate all inputs, (3) append to `catalog/sources.json` with 2-space indentation and re-validate JSON, (4) offer immediate sync via `/sync-catalog --source <new-id>`. Six validation rules (unique ID, ID format, URL format, priority range 2–99, non-empty branch, valid entityPaths keys). Three hard constraints: never modify existing entries, never use priority 1 (reserved for `local`), never create `id: local`.

#### `catalog-inspector` Agent

- **`.claude/agents/catalog-inspector.md`** — Sub-agent specialised for catalog inspection. System prompt defines four capabilities: summarise entities (grouped by type, core highlighted, scope labelled), compare across sources (read actual entity files, note priority winner, explain differences), identify gaps (Full/Partial/None coverage levels with actionable suggestions), recommend for tech stack (ranked by relevance: exact framework match > language match > universal, flags `requiresAdaptation`). Tools: `Read`, `Grep`, `Glob`. Model: `sonnet`.

---

## Sprint 5: Ignite Skill & Reference Docs

Builds the core `/ignite` skill and its three reference documents defining the complete ignition workflow, specialisation rules, and gap analysis methodology. All deliverables are documentation files — the skill orchestrates existing infrastructure through Claude's natural language understanding of the reference documents. Completed in the same session as Sprint 4.

### Delivered

#### `/ignite` Skill Definition

- **`.claude/skills/ignite/SKILL.md`** (~270 lines) — Entrypoint for `/ignite`. Six-step procedure (details delegated to reference docs). Inline Technology Profile schema (8 fields: `languages`, `frameworks`, `packageManagers`, `buildTools`, `testFrameworks`, `ciCd`, `docker`, `projectType`). Full selection pipeline (core → language → framework → category → hook evaluation → exclusion). Complete selection report format with tables for selected entities, excluded entities, and gap analysis. CLAUDE.md generation rules mapping CLAUDE-MD-SOTA.md Parts 1–5 to generation decisions. Provenance header template: `<!-- Installed by claude-code-project-igniter from {source}::{type}::{name} on {YYYY-MM-DD} -->`. Six hard constraints: never auto-install, preserve existing content, report gaps transparently, mark provenance, respect priority, rules stay in CLAUDE.md.

#### Reference Documents

- **`references/ignite-workflow.md`** — Detailed expansion of all six steps: technology signal files to scan, manifest validation and staleness check (30-day threshold), full selection algorithm, report format spec, file copy + specialisation trigger + hook merging into `settings.json`, CLAUDE.md generation per the five-part generation reference structure.
- **`references/specialization-guide.md`** — Adaptation rules for all five entity types: agents (system prompt descriptions, domain vocabulary), skills (code examples, file paths, irrelevant section removal), commands→skills (conversion to SKILL.md format, build command updates), rules (language filter, embed in CLAUDE.md), hooks (file matchers, tool paths). Four inviolable constraints: preserve core purpose, never remove security content, additive over subtractive, mark provenance.
- **`references/gap-analysis-guide.md`** — Three coverage levels (Full/Partial/None). Gap report structure: technology name, coverage level, existing entities, missing entities, impact assessment, recommendation. Four recommendation actions: accept partial coverage, create custom entity in `local/`, request upstream, add new source via `/add-source`. Surfacing thresholds: always surface for primary languages/frameworks; only surface None for minor tools.

---

## Sprint 6: Integration Testing & Polish

Validates the full pipeline end-to-end against six project archetypes, documents actual entity selection and gap analysis results, and finalises user-facing materials. Catalog baseline: **125 entities** from `everything-claude-code` (13 agents, 31 commands, 42 skills, 15 hooks, 22 rules).

### Delivered

#### Test Archetype Descriptions (`docs/test-archetypes/`)

Six archetype files, each defining a simulated project context (tech stack, representative files, conversation history):

- **`python-django.md`** — Python 3.12 · Django 5.x · PostgreSQL · Docker Compose · pytest · Poetry · api-service
- **`typescript-react-nextjs.md`** — TypeScript · React 18 · Next.js 14 · Tailwind CSS · pnpm · Vitest · web-app
- **`go-microservice.md`** — Go 1.22 · gRPC · PostgreSQL · Docker · Make · microservice
- **`java-spring-boot.md`** — Java 21 · Spring Boot 3.x · Spring Data JPA · Gradle · JUnit 5 · Docker · api-service
- **`polyglot-python-ts.md`** — Python 3.12 (FastAPI) + TypeScript (React) · PostgreSQL · Docker Compose · monorepo
- **`empty-project.md`** — No code files; two sub-cases: vague description (core-only fallback) and Python scraping tool described in conversation

#### Integration Results (`docs/test-archetypes/RESULTS.md`)

- **22 core entities** confirmed always-selected across all archetypes: 5 agents (`architect`, `build-error-resolver`, `code-reviewer`, `planner`, `security-reviewer`), 5 commands, 8 `common/` rules, 4 skills.
- **Per-archetype selection counts**: python-django ~43, typescript-react-nextjs ~38, go-microservice ~37, java-spring-boot ~31, polyglot-python-ts ~50 (largest), empty-project 22–36.
- **Specialisation validated** for python-django (`pytest`/`pytest-django` substitution, Django-specific CSRF/ORM security additions, `ruff`/`ruff format` hook adaptation) and typescript-react-nextjs (`pnpm` substitution throughout, `vitest` references, Next.js gap acknowledged inline in `frontend-patterns`).
- **Gap analysis validated** for go-microservice: gRPC/protobuf correctly identified as None-coverage, high-impact; surfacing thresholds confirmed correct (gRPC surfaced, testify not surfaced).
- **Three edge cases verified**: empty-project graceful degradation (prompts for context, falls back to 22 core entities), local-source priority override (priority 1 always wins over priority 10), stale manifest warning with user-deferred flow (warns, offers sync, continues on user choice).
- **End-to-end pipeline confirmed**: clone → `/sync-catalog` → `/ignite` → tailored `.claude/` and `CLAUDE.md`.

#### README

- **`README.md`** — User-facing overview, prerequisites (Git, Python 3.10+, Claude Code CLI), three installation options (`--add-dir` recommended, symlinks, shell alias), four-step quick start, skills reference table, catalog structure diagram with `local/` priority explanation, and catalog extension guide (custom entities in `local/`, remote sources via `/add-source`).

---

## Post-Sprint CLAUDE.md Refactoring

After Sprint 6, all 5 scoped CLAUDE.md files were audited against `docs/CLAUDE-MD-SOTA.enriched.md` and updated to apply emphasis keywords (§1.4), plan mode discipline (§4.9), and verification workflow (§4.1/W7):

| File | Change | Lines |
|------|--------|-------|
| Root `CLAUDE.md` | Strengthened "Proportional response" (explicit plan mode language); added "Verification" rule (single-file pytest first, full suite as final gate, `ruff check` before completion) | 62 → 63 |
| `docs/CLAUDE.md` | Added `IMPORTANT` to Cross-referencing and Renumbering & Reference Validation rules | 24 → 24 |
| `catalog/CLAUDE.md` | Added `IMPORTANT` to "Never overwritten by `/sync-catalog`"; rewrote manifest.json note as explicit `IMPORTANT: Never edit manually` | 32 → 32 |
| `.claude/skills/refresh-guidelines/CLAUDE.md` | Added `IMPORTANT` and explicit clarification to Output Conventions ("seed contains web sources only, enriched merges /insights") | 37 → 37 |
| `tests/CLAUDE.md` | Added `IMPORTANT` to "Mock external I/O" rule; added maintenance note at end of test file list | 35 → 37 |

---

## Known Limitations

- **Single remote source** — The catalog ships with one remote source (`everything-claude-code`). Coverage breadth depends entirely on that repo's entity set; use `/add-source` to extend.
- **No Next.js entities** — No catalog entity tagged `nextjs` or `next` exists in `everything-claude-code`. The highest-impact coverage gap for modern TypeScript projects (see RESULTS.md §2.2).
- **gRPC not covered** — No catalog entity for gRPC/protobuf conventions. High-impact gap for Go microservice projects.
- **No automated tests for Sprints 4–6** — All deliverables are documentation files validated through integration testing, not automated pytest coverage. Sprint 1–3 tests (310 total) remain the automated baseline.
- **`--add-dir` not persisted** — Users must re-attach the igniter each Claude Code session via `claude --add-dir <path>` or use the shell alias; no automatic persistence.

---

## What's Next

| Area | Description |
|------|-------------|
| Additional catalog sources | Register community entity repos via `/add-source` to expand coverage (especially Next.js, gRPC, Kubernetes) |
| Automated Sprint 4–6 tests | pytest tests for SKILL.md structure, agent definition schema, reference document completeness |
| Re-ignition workflow | Document and test the `/ignite` update flow for existing projects (merge vs. overwrite behaviour) |
| `/refresh-guidelines` cadence | Periodic re-runs as Anthropic documentation evolves to keep `CLAUDE-MD-SOTA.md` current |
