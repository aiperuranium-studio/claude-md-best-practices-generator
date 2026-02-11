# Claude Code Project Igniter — Development Agenda

This document defines the sprint-by-sprint development plan for the Claude Code Project Igniter. Each sprint is self-contained, produces testable output, and builds logically on previous sprints.

**Reference documents**: [IGNITER-PLAN.md](IGNITER-PLAN.md) (architecture) · [CLAUDE-MD-LIFECYCLE.md](CLAUDE-MD-LIFECYCLE.md) (behavioral rules)

**Estimated total effort**: 12–18 Claude Code sessions across 7 sprints.

---

## Sprint Overview

| Sprint | Name | Sessions | Dependencies |
|--------|------|----------|--------------|
| 0 | Project Scaffolding | 1 | None |
| 1 | Catalog Foundation | 1–2 | Sprint 0 |
| 2 | Catalog Sync Pipeline | 2–3 | Sprint 1 |
| 3 | Manifest Builder | 2–3 | Sprint 2 |
| 4 | Sync-Catalog & Add-Source Skills | 1–2 | Sprint 3 |
| 5 | Ignite Skill & Reference Docs | 2–3 | Sprint 4 |
| 6 | Integration Testing & Polish | 2–3 | Sprint 5 |

---

## Sprint 0: Project Scaffolding

**Goal**: Establish the project skeleton, development conventions, and Claude Code configuration so that all subsequent sprints have a consistent foundation to build on.

### Tasks

1. **Create `CLAUDE.md`** (project root)
   - Instructions for working ON this project (not generated output).
   - Include core behavioral rules from `docs/CLAUDE-MD-LIFECYCLE.md` (write-first, no preemptive execution, no scope creep, clarify before acting).
   - Include project-specific conventions: Python 3.10+ for scripts, POSIX shell for `.sh` scripts, Markdown for all documentation and skill/agent definitions.
   - Reference `docs/IGNITER-PLAN.md` and `docs/CLAUDE-MD-LIFECYCLE.md` as authoritative design documents.

2. **Update `.gitignore`**
   - Keep existing `.idea` entry.
   - Add `catalog/sources/*/` (downloaded remote repos, gitignored).
   - Explicitly un-ignore `catalog/sources/local/` with `!catalog/sources/local/`.
   - Add common Python ignores: `__pycache__/`, `*.pyc`, `.venv/`.

3. **Create `.claude/settings.json`**
   - Minimal valid settings file. Hooks array will be populated in later sprints.
   - This establishes the `.claude/` directory that all skills and agents will live under.

4. **Create directory skeleton** (empty directories with `.gitkeep` where needed)
   - `.claude/skills/ignite/references/`
   - `.claude/skills/ignite/scripts/`
   - `.claude/skills/sync-catalog/scripts/`
   - `.claude/skills/add-source/`
   - `.claude/agents/`
   - `catalog/sources/local/agents/`
   - `catalog/sources/local/skills/`
   - `catalog/sources/local/commands/`
   - `catalog/sources/local/rules/`

### Acceptance Criteria

- [x] `CLAUDE.md` exists at project root and contains all four behavioral rules from `docs/CLAUDE-MD-LIFECYCLE.md`.
- [x] `.gitignore` correctly ignores `catalog/sources/*/` but allows `catalog/sources/local/`.
- [x] `.claude/settings.json` is valid JSON.
- [x] All directories listed in the target structure exist (may contain only `.gitkeep` placeholders).
- [x] `git status` shows a clean working tree after committing.

### Dependencies

None — this is the starting sprint.

---

## Sprint 1: Catalog Foundation

**Goal**: Create the source registry (`sources.json`) and the local entity directory structure, so that the catalog has a well-defined schema before any sync or manifest tooling is built.

### Tasks

1. **Create `catalog/sources.json`**
   - JSON file defining the source registry.
   - Include the primary source entry:
     ```json
     {
       "sources": [
         {
           "id": "everything-claude-code",
           "url": "https://github.com/affaan-m/everything-claude-code.git",
           "branch": "main",
           "pin": null,
           "priority": 10,
           "entityPaths": {
             "agents": "agents",
             "skills": "skills",
             "commands": "commands",
             "rules": "rules",
             "hooks": "hooks"
           }
         },
         {
           "id": "local",
           "url": null,
           "branch": null,
           "pin": null,
           "priority": 1,
           "entityPaths": {
             "agents": "agents",
             "skills": "skills",
             "commands": "commands",
             "rules": "rules"
           }
         }
       ]
     }
     ```
   - The `local` source has `url: null` (never synced from remote) and priority 1 (always wins).

2. **Create `catalog/sources/local/` placeholder entities**
   - Add a `README.md` inside `catalog/sources/local/` explaining that users place their custom entities here.
   - Ensure subdirectories (`agents/`, `skills/`, `commands/`, `rules/`) contain `.gitkeep` files.

3. **Document the source schema**
   - Add a `docs/SOURCE-SCHEMA.md` describing each field in `sources.json`, valid values, and how priority resolution works.

### Acceptance Criteria

- [ ] `catalog/sources.json` is valid JSON and contains exactly two sources (`everything-claude-code` and `local`).
- [ ] `catalog/sources/local/README.md` exists and explains the purpose of the local source.
- [ ] `catalog/sources/local/` subdirectories exist for all entity types.
- [ ] `docs/SOURCE-SCHEMA.md` documents all fields in the source schema.
- [ ] Running `python3 -c "import json; json.load(open('catalog/sources.json'))"` succeeds.

### Dependencies

Sprint 0 (directory skeleton must exist).

---

## Sprint 2: Catalog Sync Pipeline

**Goal**: Build the shell script that clones or updates remote sources based on `sources.json`, creating the raw material that the manifest builder will later index.

### Tasks

1. **Create `.claude/skills/sync-catalog/scripts/sync-catalog.sh`**
   - Reads `catalog/sources.json` using `jq` (with `python3 -c` fallback).
   - For each source with a non-null `url`:
     - If `catalog/sources/{id}/` does not exist: `git clone --branch {branch} --single-branch {url} catalog/sources/{id}/`.
     - If it already exists: `cd catalog/sources/{id}/ && git fetch origin && git checkout {branch} && git pull origin {branch}`.
     - If `pin` is set: `git checkout {pin}` after clone/pull.
   - Writes `catalog/sources/{id}/.source-meta.json` after sync with: `id`, `synced_at` (ISO 8601), `commit` (current HEAD SHA), `branch`, `pin`, `url`.
   - Skips the `local` source (url is null).
   - Exits with informative error messages on failure.

2. **Make the script executable and POSIX-compatible**
   - `#!/usr/bin/env bash` shebang.
   - Accept an optional `--source <id>` flag to sync only a single source.

3. **Document `.source-meta.json` schema**
   - Append the sync metadata format to `docs/SOURCE-SCHEMA.md`.

### Acceptance Criteria

- [ ] Running `bash .claude/skills/sync-catalog/scripts/sync-catalog.sh` from the project root clones `everything-claude-code` into `catalog/sources/everything-claude-code/`.
- [ ] `catalog/sources/everything-claude-code/.source-meta.json` exists after sync with valid JSON containing all required fields.
- [ ] Running the script a second time performs a pull (not a fresh clone) and updates `.source-meta.json`.
- [ ] The `local` source directory is untouched by the sync script.
- [ ] `catalog/sources/everything-claude-code/` is ignored by git (verify with `git status`).
- [ ] The script exits with non-zero status and a clear error message if the network is unavailable.

### Dependencies

Sprint 1 (`sources.json` must exist).

---

## Sprint 3: Manifest Builder

**Goal**: Build `build-manifest.py`, the most complex component, which scans all synced sources and generates `catalog/manifest.json` with tagged, classified entity metadata.

### Tasks

1. **Create `.claude/skills/ignite/scripts/build-manifest.py`**
   - Python 3.10+, no external dependencies beyond the standard library (`json`, `os`, `pathlib`, `re`, `datetime`). If YAML frontmatter parsing is needed, document `pyyaml` as an optional dependency.
   - **Input**: Reads `catalog/sources.json` to discover sources and their `entityPaths`.
   - **Output**: Writes `catalog/manifest.json`.

2. **Entity discovery logic**
   - For each source (including `local`), iterate over each entity type directory.
   - Entity types to scan: `agents`, `skills`, `commands`, `rules`, `hooks`.
   - Agents: scan `.md` files in the agents directory.
   - Skills: scan directories containing `SKILL.md` (fallback to `.md` files).
   - Commands: scan `.md` files.
   - Rules: scan `.md` files, respecting subdirectory structure (e.g., `rules/common/`, `rules/TypeScript/`).
   - Hooks: parse `hooks.json` if present, treating each hook entry as an individual entity.

3. **Tag classification engine**
   - Build keyword maps for auto-classification:
     - **Languages**: python, typescript, javascript, go, java, rust, c++, ruby, php, swift, kotlin, etc.
     - **Frameworks**: django, flask, fastapi, react, next/nextjs, vue, angular, spring, express, rails, laravel, etc.
     - **Categories**: testing, tdd, security, code-review, documentation, ci-cd, database, api, devops, architecture, planning, debugging, refactoring, performance, etc.
   - Classify by scanning: entity filename, directory path, and file content (first 200 lines).
   - Determine `scope`: `universal` (no language/framework tags), `language-specific` (language tags only), `framework-specific` (has framework tags).

4. **Core entity identification**
   - Mark entities as `coreEntity: true` based on the predefined list from IGNITER-PLAN.md:
     - Agents: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `build-error-resolver`
     - Skills: `tdd-workflow`, `coding-standards`, `verification-loop`, `security-review`
     - Commands: `plan`, `tdd`, `code-review`, `build-fix`, `verify`
     - Rules in `common/` directory
   - Use fuzzy name matching (normalize hyphens, underscores, case).

5. **Manifest output schema**
   - Each entity entry:
     ```json
     {
       "id": "{source}::{type}::{name}",
       "source": "everything-claude-code",
       "type": "agent",
       "name": "code-reviewer",
       "path": "catalog/sources/everything-claude-code/agents/code-reviewer.md",
       "tags": {
         "languages": [],
         "frameworks": [],
         "categories": ["code-review"],
         "scope": "universal"
       },
       "coreEntity": true,
       "requiresAdaptation": true,
       "metadata": {}
     }
     ```
   - Top-level `coverage` summary: unique languages, frameworks, categories across all entities.
   - Top-level `generatedAt` ISO 8601 timestamp.
   - Top-level `sources`: each scanned source with its `.source-meta.json` data.

6. **Adaptation detection**
   - `requiresAdaptation: true` for entities with non-empty language or framework tags and non-universal scope.
   - Core entities default to `requiresAdaptation: false`.

7. **Error handling**
   - Progress to stderr. Skip malformed files with warnings. Non-zero exit only on fatal errors.

### Acceptance Criteria

- [ ] Running `python3 .claude/skills/ignite/scripts/build-manifest.py` produces `catalog/manifest.json`.
- [ ] The manifest is valid JSON with entries from `everything-claude-code`.
- [ ] Every entity has all required fields: `id`, `source`, `type`, `name`, `path`, `tags`, `coreEntity`, `requiresAdaptation`, `metadata`.
- [ ] Composite IDs follow `{source}::{type}::{name}` format.
- [ ] Core entities are correctly identified with `coreEntity: true`.
- [ ] The `coverage` summary lists discovered languages, frameworks, and categories.
- [ ] Language-specific entities have correct language tags.
- [ ] Running the script twice produces identical output (deterministic).
- [ ] Runs without external pip dependencies (or clearly documents `pyyaml` as optional).

### Dependencies

Sprint 2 (synced sources must exist in `catalog/sources/`).

---

## Sprint 4: Sync-Catalog & Add-Source Skills

**Goal**: Wrap the sync and manifest-build scripts in Claude Code skills, and create the `/add-source` skill for registering new remote sources.

### Tasks

1. **Create `.claude/skills/sync-catalog/SKILL.md`**
   - Skill entrypoint for `/sync-catalog`.
   - Procedure:
     1. Run `bash .claude/skills/sync-catalog/scripts/sync-catalog.sh`.
     2. Run `python3 .claude/skills/ignite/scripts/build-manifest.py`.
     3. Report results: sources synced, entities indexed, errors/warnings.
   - Accept optional `--source <id>` argument.

2. **Create `.claude/skills/add-source/SKILL.md`**
   - Skill entrypoint for `/add-source`.
   - Procedure:
     1. Prompt user for: source `id`, `url`, `branch` (default: `main`), `priority` (default: 50), `entityPaths` mapping.
     2. Validate inputs (URL format, unique ID, priority range 2–99).
     3. Read `catalog/sources.json`, append new source, write back.
     4. Optionally run `/sync-catalog --source <new-id>` to immediately sync.

3. **Create `.claude/agents/catalog-inspector.md`**
   - Agent for deep inspection of catalog entities.
   - System prompt: read and summarize entity content, compare similar entities across sources, identify overlaps and gaps, recommend entities for a given tech stack.

4. **Verify `.claude/settings.json`** is still valid and compatible with the skills directory structure.

### Acceptance Criteria

- [ ] Running `/sync-catalog` in Claude Code triggers the sync script and manifest build, reporting results.
- [ ] Running `/add-source` prompts for all required fields and adds a valid entry to `catalog/sources.json`.
- [ ] The `/add-source` skill rejects duplicate source IDs and invalid URLs.
- [ ] `.claude/agents/catalog-inspector.md` exists with a well-formed agent system prompt.
- [ ] All `SKILL.md` files have clear descriptions suitable for Claude's skill discovery.

### Dependencies

Sprint 3 (manifest builder must exist for `/sync-catalog` to chain into).

---

## Sprint 5: Ignite Skill & Reference Docs

**Goal**: Build the core `/ignite` skill and its three reference documents that define the complete ignition workflow, specialization rules, and gap analysis methodology.

### Tasks

1. **Create `.claude/skills/ignite/SKILL.md`** (under 500 lines)
   - Skill entrypoint for `/ignite`.
   - High-level 6-step procedure (details in references):
     1. Read context → build Technology Profile.
     2. Read `catalog/manifest.json` (warn if stale >30 days).
     3. Select entities: core (always) + tag-matched + Claude's judgment.
     4. Present selection report for user approval.
     5. Install and specialize approved entities into the target project.
     6. Generate/update the target project's `CLAUDE.md`.
   - Include Technology Profile schema inline (languages, frameworks, package managers, build tools, test frameworks, CI/CD, Docker, project type).
   - Include selection report output format.
   - Include provenance header template: `<!-- Installed by claude-code-project-igniter from {source}::{type}::{name} on {date} -->`.

2. **Create `.claude/skills/ignite/references/ignite-workflow.md`**
   - Detailed expansion of each of the 6 steps:
     - **Step 1**: Files to scan (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `docker-compose.yml`, `.github/workflows/`, `Makefile`, `tsconfig.json`, etc.). Signal extraction. Conversation history reading.
     - **Step 2**: Manifest loading, validation, staleness check.
     - **Step 3**: Selection algorithm (core → language → framework → category). Exclusion rules. Per-hook evaluation.
     - **Step 4**: Report format (selected grouped by type, excluded with reasons, gap summary, action prompt).
     - **Step 5**: File copy, directory creation, specialization trigger, hook merging into `settings.json`, provenance headers.
     - **Step 6**: Generated CLAUDE.md structure (project description, behavioral rules from `docs/CLAUDE-MD-LIFECYCLE.md`, domain-specific rules, installed entities, active hooks, gap report, user-added rules section).

3. **Create `.claude/skills/ignite/references/specialization-guide.md`**
   - Adaptation rules per entity type:
     - **Agents**: Update system prompt descriptions, replace generic examples, adjust domain vocabulary.
     - **Skills**: Swap code examples to project's framework, update file paths, remove irrelevant sections.
     - **Commands→Skills**: Convert to proper skills, update build/test commands to project's package manager.
     - **Rules**: Filter to relevant language, embed in CLAUDE.md for project-level scoping.
     - **Hooks**: Adjust file matchers, update tool paths (e.g., `npx prettier` → `ruff format`).
   - Inviolable constraints: preserve core purpose, never remove security content, additive over subtractive, provenance marking.

4. **Create `.claude/skills/ignite/references/gap-analysis-guide.md`**
   - Three coverage levels: Full, Partial, None.
   - Gap report structure: technology name, coverage level, existing entities, missing entities, impact assessment, recommendation.
   - Recommendations: accept partial, create custom in `local/`, request upstream, add new source via `/add-source`.
   - Surfacing thresholds: always surface for primary languages/frameworks; only surface `None` for minor tools.

### Acceptance Criteria

- [ ] `.claude/skills/ignite/SKILL.md` exists and is under 500 lines.
- [ ] SKILL.md contains a clear 6-step procedure referencing all three reference documents.
- [ ] `ignite-workflow.md` documents all 6 steps with actionable detail.
- [ ] `specialization-guide.md` covers all 5 entity types with specific adaptation rules.
- [ ] `gap-analysis-guide.md` defines the three coverage levels, report format, and recommendation actions.
- [ ] The specialization guide states all four constraints.
- [ ] CLAUDE.md generation references `docs/CLAUDE-MD-LIFECYCLE.md` behavioral and domain-specific rules.
- [ ] All reference documents are cross-referenced consistently.

### Dependencies

Sprint 4 (`/sync-catalog` must work so the manifest exists).

---

## Sprint 6: Integration Testing & Polish

**Goal**: Validate the entire pipeline end-to-end against multiple project archetypes, fix issues, and finalize documentation.

### Tasks

1. **Create test archetype descriptions** in `docs/test-archetypes/`
   - Each archetype is a markdown file describing a simulated project context (files, CLAUDE.md, conversation history):
     - **`python-django.md`**: Python 3.12, Django 5.x, PostgreSQL, Docker Compose, pytest, Poetry.
     - **`typescript-react-nextjs.md`**: TypeScript, React 18, Next.js 14, Tailwind CSS, pnpm, Vitest.
     - **`go-microservice.md`**: Go 1.22, gRPC, PostgreSQL, Docker, Make.
     - **`java-spring-boot.md`**: Java 21, Spring Boot 3.x, Gradle, JUnit 5, Docker.
     - **`polyglot-python-ts.md`**: Python backend (FastAPI) + TypeScript frontend (React), monorepo, Docker Compose.
     - **`empty-project.md`**: No code files, only a conversation describing planned architecture.

2. **Verify entity selection per archetype**
   - For each archetype, document expected vs. actual: core entities, language-matched, framework-matched, excluded, gaps reported.
   - Record in `docs/test-archetypes/RESULTS.md`.

3. **Verify specialization quality**
   - For `python-django` and `typescript-react-nextjs`: check agent descriptions, skill examples, hook matchers, provenance headers.

4. **Verify gap analysis accuracy**
   - For `go-microservice` (likely fewer catalog entities): verify correct gap identification and actionable recommendations.

5. **Edge case testing**
   - Empty project: `/ignite` installs only core entities or asks for more context.
   - Conflicting sources: `local` (priority 1) wins over `everything-claude-code` (priority 10).
   - Stale manifest: modify `generatedAt` >30 days old, verify warning.

6. **Final documentation pass**
   - Update `docs/IGNITER-PLAN.md` with any deviations.
   - Update `CLAUDE.md` with final project structure.
   - Ensure all `SKILL.md` descriptions are clear and discoverable.

7. **Create `README.md`** (project root)
   - Project overview, prerequisites (Git, Python 3.10+, Claude Code).
   - Installation: `--add-dir` (recommended), symlinks, shell alias.
   - Quick start: clone → `/sync-catalog` → target project → `/ignite`.

### Acceptance Criteria

- [ ] All 6 archetype descriptions exist in `docs/test-archetypes/`.
- [ ] `docs/test-archetypes/RESULTS.md` documents actual vs. expected results.
- [ ] Entity selection is correct for all archetypes.
- [ ] Specialization produces adapted content for at least 2 archetypes.
- [ ] Gap analysis correctly identifies missing coverage for Go microservice.
- [ ] Edge cases are handled gracefully.
- [ ] `README.md` exists with installation and quick-start instructions.
- [ ] Complete pipeline works: clone → `/sync-catalog` → `/ignite` → tailored configuration.

### Dependencies

Sprint 5 (all skills and reference docs must be complete).

---

## File Delivery Summary

| Sprint | Files Created / Modified |
|--------|--------------------------|
| 0 | `CLAUDE.md`, `.gitignore` (mod), `.claude/settings.json`, `.gitkeep` skeleton |
| 1 | `catalog/sources.json`, `catalog/sources/local/README.md`, `docs/SOURCE-SCHEMA.md` |
| 2 | `.claude/skills/sync-catalog/scripts/sync-catalog.sh`, `docs/SOURCE-SCHEMA.md` (mod) |
| 3 | `.claude/skills/ignite/scripts/build-manifest.py` |
| 4 | `.claude/skills/sync-catalog/SKILL.md`, `.claude/skills/add-source/SKILL.md`, `.claude/agents/catalog-inspector.md` |
| 5 | `.claude/skills/ignite/SKILL.md`, `.claude/skills/ignite/references/ignite-workflow.md`, `specialization-guide.md`, `gap-analysis-guide.md` |
| 6 | `README.md`, `docs/test-archetypes/*.md`, `docs/test-archetypes/RESULTS.md` |

---

## Risk Notes

| Risk | Sprint | Mitigation |
|------|--------|------------|
| `build-manifest.py` YAML parsing needs `pyyaml` | 3 | Try stdlib-only first. If YAML frontmatter is common, document `pip install pyyaml` as prerequisite. |
| `everything-claude-code` repo restructures | 2, 3 | `entityPaths` in `sources.json` decouples path assumptions. Manifest builder uses defensive scanning. |
| Skill description wording affects discoverability | 4, 5 | Test by invoking `/ignite`, `/sync-catalog`, `/add-source` and verifying Claude finds them. |
| Context window pressure during `/ignite` | 5 | Progressive disclosure: read only manifest for selection, then entity files one-by-one during install. |
| Rules cannot be installed at project level via files | 5 | Embed rules in generated `CLAUDE.md` as documented in specialization guide. |
