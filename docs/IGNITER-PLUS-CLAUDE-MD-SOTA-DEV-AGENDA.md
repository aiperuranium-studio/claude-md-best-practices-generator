# Claude Code Project Igniter — Development Agenda

This document defines the sprint-by-sprint development plan for the Claude Code Project Igniter. Each sprint is self-contained, produces testable output, and builds logically on previous sprints.

**Reference documents**: [IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md](IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md) (unified plan) · [CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md) (authoritative CLAUDE.md generation reference — starts blank, populated via `/refresh-guidelines`)

**Estimated total effort**: 13–20 Claude Code sessions across 8 sprints.

---

## Sprint Overview

| Sprint | Name | Sessions | Dependencies |
|--------|------|----------|--------------|
| 0 | Project Scaffolding | 1 | None |
| 1 | Catalog Foundation | 1–2 | Sprint 0 |
| 1.5 | Guidelines Enrichment Pipeline | 1–2 | Sprint 0 |
| 2 | Catalog Sync Pipeline | 2–3 | Sprint 1 |
| 3 | Manifest Builder | 2–3 | Sprint 2 |
| 4 | Sync-Catalog & Add-Source Skills | 1–2 | Sprint 3 |
| 5 | Ignite Skill & Reference Docs | 2–3 | Sprint 4, Sprint 1.5 |
| 6 | Integration Testing & Polish | 2–3 | Sprint 5 |

---

## Sprint 0: Project Scaffolding

**Goal**: Establish the project skeleton, development conventions, and Claude Code configuration so that all subsequent sprints have a consistent foundation to build on.

### Tasks

1. **Create `CLAUDE.md`** (project root)
   - Instructions for working ON this project (not generated output).
   - Include core behavioral rules as project-specific conventions (write-first, no preemptive execution, no scope creep, clarify before acting).
   - Include project-specific conventions: Python 3.10+ for scripts, POSIX shell for `.sh` scripts, Markdown for all documentation and skill/agent definitions.
   - Reference `docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md` and `docs/CLAUDE-MD-SOTA.md` as authoritative design documents. (`CLAUDE-MD-SOTA.md` starts blank and is populated via `/refresh-guidelines`.)

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

- [x] `CLAUDE.md` exists at project root and contains all four behavioral rules (project-specific conventions, not sourced from `docs/CLAUDE-MD-SOTA.md`).
- [x] `.gitignore` correctly ignores `catalog/sources/*/` but allows `catalog/sources/local/`.
- [x] `.claude/settings.json` is valid JSON.
- [x] All directories listed in the target structure exist (may contain only `.gitkeep` placeholders).
- [x] `git status` shows a clean working tree after committing.

### Dependencies

None — this is the starting sprint.

### Retroactive Note

Sprint 0 was completed when `docs/CLAUDE-MD-SOTA.md` still contained hardcoded behavioral rules. The model has since changed: CLAUDE-MD-SOTA.md now **starts blank** and is populated via `/refresh-guidelines` from `/insights` tips + web sources. The igniter's own `CLAUDE.md` behavioral rules (write-first, no preemptive execution, no scope creep, clarify before acting) exist independently — they are project-specific conventions for working on the igniter, not sourced from CLAUDE-MD-SOTA.md.

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
   - Add a [`SOURCE-SCHEMA.md`](SOURCE-SCHEMA.md) describing each field in `sources.json`, valid values, and how priority resolution works.

### Acceptance Criteria

- [x] `catalog/sources.json` is valid JSON and contains exactly two sources (`everything-claude-code` and `local`).
- [x] `catalog/sources/local/README.md` exists and explains the purpose of the local source.
- [x] `catalog/sources/local/` subdirectories exist for all entity types.
- [x] `docs/SOURCE-SCHEMA.md` documents all fields in the source schema.
- [x] Running `python3 -c "import json; json.load(open('catalog/sources.json'))"` succeeds.

### Dependencies

Sprint 0 (directory skeleton must exist).

---

## Sprint 1.5: Guidelines Enrichment Pipeline

**Goal**: Build the `/refresh-guidelines` skill and populate [`docs/CLAUDE-MD-SOTA.md`](CLAUDE-MD-SOTA.md) from blank into a 6-part authoritative reference — using `/insights` tips and web-sourced best practices as dual input sources — so that Sprint 5's `/ignite` generates high-quality, standards-compliant CLAUDE.md files from the start.

**Rationale for early placement**: Having the enriched [CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md) before the `/ignite` skill is built means all subsequent work aligns with it. Sprint 1.5 runs in parallel with Sprint 1 (no dependency between them — both depend only on Sprint 0).

### Tasks

1. **Create `.claude/skills/refresh-guidelines/SKILL.md`**
   - Skill entrypoint for `/refresh-guidelines`.
   - Procedure (10 steps):
     1. Run `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` to collect raw web content.
     2. Run `python3 .claude/skills/refresh-guidelines/scripts/parse-insights.py` to extract structured data from the user's `/insights` report. Warn if report is missing or stale (>7 days).
     3. Read `docs/guidelines-raw.json` output (web sources).
     4. Read `docs/insights-parsed.json` (parsed /insights report). Also read `docs/insights-raw.md` if it has manual tips (supplement, not replace).
     5. Read current `docs/CLAUDE-MD-SOTA.md` (may be blank on first run).
     6. Per theme section: classify incoming blocks from all sources (duplicate/novel/reinforcing/conflicting).
     7. Produce enrichment report showing all proposed changes with source attribution.
     8. Present report for human approval.
     9. On approval: populate/update CLAUDE-MD-SOTA.md with approved changes.
     10. Update Source Attribution section.

2. **Create `.claude/skills/refresh-guidelines/references/curated-sources.md`**
   - Tiered source registry with authoritative URLs:
     - **Tier 1** (highest precedence): Official Anthropic docs — `code.claude.com/docs/en/memory`, `code.claude.com/docs/en/best-practices`, `claude.com/blog/using-claude-md-files`.
     - **Tier 2** (medium): Established community guides — HumanLayer, Builder.io, Dometrain, Tembo, Arize.
     - **Tier 3** (lowest): Community templates — ruvnet/claude-flow, abhishekray07/claude-md-templates, awesome-claude-code repos.
   - Each entry: source name, URL, theme tags (structural, content, anti-patterns, integration, maintenance), last-verified date.

3. **Create `.claude/skills/refresh-guidelines/references/enrichment-procedure.md`**
   - Defines the 3-phase merge algorithm Claude follows:
     - **Source precedence** (highest → lowest): T1 official docs > `/insights` tips > T2 community guides > T3 templates.
     - **Phase 1 — Classification**: For each incoming block from either source, classify as `novel` (insert), `duplicate` (skip), `reinforcing` (merge with citation), or `conflicting` (flag for human). On first run with blank document, all content is `novel`.
     - **Phase 2 — Conflict Resolution**: Higher-precedence sources win by default. Conflicts never auto-resolved — always presented for human decision. Report format: table of all changes with source attribution.
     - **Phase 3 — Integration**: Claude proposes populated/updated CLAUDE-MD-SOTA.md. Human reviews diff and approves. Source Attribution updated.

4. **Create `.claude/skills/refresh-guidelines/scripts/fetch-guidelines.py`**
   - Python 3.10+, stdlib only (`urllib.request`, `json`, `re`, `html.parser`, `pathlib`, `datetime`).
   - **Input**: reads `curated-sources.md` to extract URLs + theme tags.
   - **Output**: writes `docs/guidelines-raw.json` with structured content blocks.
   - Fault-tolerant: skips failed URLs with warnings, produces partial results.
   - Follows redirects. Handles both HTML (strip tags) and raw markdown (GitHub).
   - Output schema per entry:
     ```json
     {
       "source_url": "...",
       "source_name": "...",
       "tier": 1,
       "last_fetched": "2026-02-11T...",
       "content_blocks": [
         { "theme": "size-constraints", "heading": "...", "text": "..." }
       ]
     }
     ```

5. **Create `.claude/skills/refresh-guidelines/scripts/parse-insights.py`**
   - Python 3.10+, stdlib only (`html.parser`, `json`, `pathlib`, `datetime`, `re`, `os`).
   - **Input**: reads `~/.claude/usage-data/report.html` (HTML report generated by `/insights`) + `~/.claude/usage-data/facets/*.json` (per-session analysis) + `~/.claude/usage-data/session-meta/*.json` (per-session metadata).
   - **Output**: writes `docs/insights-parsed.json` with structured content blocks.
   - Extracts 7 report sections: CLAUDE.md Recommendations, Friction Points, Working Workflows, Feature Recommendations, Usage Patterns, Future Workflows, Usage Narrative.
   - Each section mapped to themes (content, behavioral, anti-patterns, integration, maintenance) and target CLAUDE-MD-SOTA.md parts.
   - Staleness detection: report older than 7 days marked as `is_stale: true`.
   - Fault-tolerant: missing report produces minimal JSON with empty entries (exits 0).
   - Output schema mirrors `guidelines-raw.json` structure for pipeline consistency.

6. **Reset `docs/CLAUDE-MD-SOTA.md` to blank**
   - Start with an empty file (no hardcoded rules or seed content).
   - After running `/refresh-guidelines`, populated into 6-part authoritative reference (under 300 lines):
     - **Purpose & Scope**: Role of document, dual-source enrichment model, how `/ignite` consumes it.
     - **Part 1: Structural Standards**: Size constraints, recommended sections, file hierarchy strategy, formatting rules (from web sources).
     - **Part 2: Content Guidelines**: What to include, what to exclude, anti-patterns (from web sources + /insights).
     - **Part 3: Integration Guidelines**: Hooks vs CLAUDE.md, Skills vs CLAUDE.md, Rules directory (from web sources).
     - **Part 4: Behavioral Patterns**: Workflow rules, coding patterns, interaction preferences (from /insights + web sources — emergent, not hardcoded).
     - **Part 5: Maintenance Guidelines**: Review cadence, self-improving pattern, versioning (from web sources + /insights).
     - **Source Attribution**: Web URLs, /insights session references, last-verified dates.
   - All content emerges from dual sources via `/refresh-guidelines` — nothing is pre-defined.

7. **Update project files**
   - `CLAUDE.md`: add `refresh-guidelines/` to project structure, add `parse-insights.py` and `insights-parsed.json` references.
   - `.gitignore`: add `docs/guidelines-raw.json`, `docs/insights-raw.md`, and `docs/insights-parsed.json`.
   - Create `docs/insights-raw.md`: empty placeholder with instructions header for supplementary manual `/insights` tips.

### Acceptance Criteria

- [x] `/refresh-guidelines` skill is invocable and Claude discovers it.
- [x] `fetch-guidelines.py` fetches content from at least Tier 1 sources without errors.
- [x] `docs/guidelines-raw.json` produced with valid JSON and themed content blocks.
- [x] `docs/CLAUDE-MD-SOTA.md` starts blank and contains no hardcoded content.
- [x] After `/refresh-guidelines`, CLAUDE-MD-SOTA.md is populated into the 6-part structure with substantive content.
- [x] `/insights` tips correctly integrated when present in `docs/insights-raw.md`.
- [x] Source Attribution lists all sources (web URLs + /insights references) with dates.
- [x] Enrichment report correctly classifies incoming content (novel on first run; duplicate/reinforcing on subsequent runs).
- [x] No conflicting information merged without human review.
- [x] CLAUDE-MD-SOTA.md stays under 300 lines.
- [x] `parse-insights.py` exists and produces valid `docs/insights-parsed.json` when `~/.claude/usage-data/report.html` is present.
- [x] `/insights` report sections (CLAUDE.md recs, friction, wins, features, patterns, horizon, usage) are correctly extracted into themed content blocks.
- [x] Staleness warning produced when `/insights` report is older than 7 days.
- [x] `parse-insights.py` handles missing report gracefully (exits 0, produces minimal JSON).
- [x] SKILL.md references `parse-insights.py` and `insights-parsed.json`.

### Dependencies

Sprint 0 (directory skeleton must exist). Runs in parallel with Sprint 1.

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
   - Append the sync metadata format to [`SOURCE-SCHEMA.md`](SOURCE-SCHEMA.md).

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
   - Mark entities as `coreEntity: true` based on the predefined list from [IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md](IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md):
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
     - **Step 6**: Generated CLAUDE.md structure per [`docs/CLAUDE-MD-SOTA.md`](CLAUDE-MD-SOTA.md) (structural standards → skeleton, content guidelines → section content, integration guidelines → placement decisions, behavioral patterns → selected and adapted per project, maintenance section, installed entities, active hooks, gap report).

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
- [ ] CLAUDE.md generation references [`docs/CLAUDE-MD-SOTA.md`](CLAUDE-MD-SOTA.md) emergent content structure (Parts 1–5: structural standards, content guidelines, integration guidelines, behavioral patterns, maintenance).
- [ ] All reference documents are cross-referenced consistently.

### Dependencies

Sprint 4 (`/sync-catalog` must work so the manifest exists) and Sprint 1.5 (enriched [CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md) must exist for Step 6).

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
   - Update [`docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`](IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md) with any deviations.
   - Update `CLAUDE.md` with final project structure.
   - Ensure all `SKILL.md` descriptions (including `/refresh-guidelines`) are clear and discoverable.

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
| 0 | `CLAUDE.md`, `.gitignore` (mod), `.claude/settings.json`, `.gitkeep` skeleton, `docs/old/` (archived pre-merge plans) |
| 1 | `catalog/sources.json`, `catalog/sources/local/README.md`, `docs/SOURCE-SCHEMA.md` |
| 1.5 | `.claude/skills/refresh-guidelines/SKILL.md`, `references/curated-sources.md`, `references/enrichment-procedure.md`, `scripts/fetch-guidelines.py`, `scripts/parse-insights.py`, `docs/CLAUDE-MD-SOTA.md` (reset to blank, populated via `/refresh-guidelines`), `docs/insights-raw.md`, `docs/insights-parsed.json` (gitignored), `CLAUDE.md` (mod), `.gitignore` (mod) |
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
| Fetched web content structure changes | 1.5 | Defensive parsing with fallbacks; `curated-sources.md` records expected format per URL. |
| CLAUDE-MD-SOTA.md becomes too long | 1.5 | Use @import references for detailed subsections; keep main doc as structured index under 300 lines. |
| Curated source URLs change or break | 1.5 | `fetch-guidelines.py` follows redirects, skips failures; curated-sources updated when URLs change. |
| Guidelines sources genuinely conflict | 1.5 | Enrichment procedure classifies conflicts explicitly, escalates to human; higher tier wins by default. |
| /insights tips unavailable or low quality | 1.5 | Document can be fully populated from web sources alone; /insights enriches but isn't required. `/refresh-guidelines` works with whichever sources are available. |
| `/insights` report HTML structure changes across versions | 1.5 | `parse-insights.py` uses class-based extraction (`.big-win`, `.friction-category`, etc.); graceful degradation on missing sections. |
| No `/insights` report exists (first-time users) | 1.5 | `parse-insights.py` outputs minimal JSON with empty entries (exits 0). Pipeline proceeds with web sources only. |
