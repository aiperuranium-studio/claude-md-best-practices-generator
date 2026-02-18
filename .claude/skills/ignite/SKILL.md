# /ignite

Intelligently select, specialize, and install Claude Code entities (agents, skills, rules, hooks) into a target project based on its technology profile. Generates a tailored `CLAUDE.md` with installed entity registry and gap analysis for uncovered technologies.

## When to Use

- **New project setup**: After planning a new project's architecture in conversation, run `/ignite` to get a fully tailored Claude Code configuration.
- **Existing project enhancement**: When adding Claude Code configuration to an existing project that lacks agents, skills, or hooks.
- **Re-ignition**: After updating the catalog (`/sync-catalog`) or changing project technologies, re-run to update the configuration.

## Prerequisites

- The igniter repo must be attached to the Claude Code session via `claude --add-dir <path-to-igniter>`.
- `catalog/manifest.json` must exist. If it doesn't, run `/sync-catalog` first.
- The target project directory must exist and be the primary working directory in the Claude Code session.
- Python 3.10+ available on PATH (for manifest reading utilities).

## Technology Profile Schema

Step 1 extracts a Technology Profile from the target project. This is a structured summary of the project's technology stack used for entity matching.

```json
{
  "languages": ["python"],
  "frameworks": ["fastapi"],
  "packageManagers": ["uv"],
  "buildTools": ["make"],
  "testFrameworks": ["pytest"],
  "ciCd": ["github-actions"],
  "docker": true,
  "projectType": "api-service"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `languages` | string[] | Programming languages detected (e.g., python, typescript, go, java, rust) |
| `frameworks` | string[] | Frameworks detected (e.g., fastapi, django, react, nextjs, spring, express) |
| `packageManagers` | string[] | Package managers (e.g., uv, pip, npm, pnpm, yarn, cargo, go-modules) |
| `buildTools` | string[] | Build tools (e.g., make, gradle, maven, webpack, vite, docker) |
| `testFrameworks` | string[] | Test frameworks (e.g., pytest, jest, vitest, go-test, junit) |
| `ciCd` | string[] | CI/CD systems (e.g., github-actions, gitlab-ci, jenkins, circleci) |
| `docker` | boolean | Whether Docker/container configuration is present |
| `projectType` | string | Classification (e.g., api-service, web-app, cli-tool, library, monorepo, microservice) |

## Procedure

Follow these 6 steps in order. Details for each step are in `references/ignite-workflow.md`. Do NOT skip steps or auto-approve — human review is required at Steps 1 and 4.

### Step 1 — Read context and build Technology Profile

Scan the target project to build a Technology Profile. Read these files if they exist:

**Language/framework signals:**
- `package.json`, `tsconfig.json` — JavaScript/TypeScript, Node.js frameworks
- `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile` — Python
- `go.mod`, `go.sum` — Go
- `Cargo.toml` — Rust
- `pom.xml`, `build.gradle`, `build.gradle.kts` — Java/Kotlin
- `Gemfile` — Ruby
- `composer.json` — PHP
- `Package.swift` — Swift

**Infrastructure signals:**
- `docker-compose.yml`, `Dockerfile` — Docker presence
- `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` — CI/CD
- `Makefile`, `justfile` — Build tools

**Existing configuration:**
- `CLAUDE.md` — Preserve existing content (if updating, merge rather than overwrite)
- `.claude/` directory — Existing agents, skills, hooks already installed
- Conversation history — Architecture decisions, tech stack discussions

Present the Technology Profile to the user for confirmation. Ask them to correct or supplement if needed.

> **Wait for user confirmation before proceeding.**

### Step 2 — Read manifest

Load the entity catalog from the igniter's `catalog/manifest.json`.

- Resolve the path relative to the igniter directory (not the target project).
- Validate that the manifest has `entities`, `coverage`, `generatedAt`, and `sources` top-level fields.
- Check staleness: if `generatedAt` is more than 30 days old, warn the user and suggest running `/sync-catalog`.
- If the manifest doesn't exist, stop and instruct the user to run `/sync-catalog`.

### Step 3 — Select entities

Apply the selection algorithm to choose which entities to install. See `references/ignite-workflow.md` for the full algorithm.

**Selection pipeline** (in order):

1. **Core entities** — always included regardless of tech stack:
   - Agents: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `build-error-resolver`
   - Skills: `tdd-workflow`, `coding-standards`, `verification-loop`, `security-review`
   - Commands (→ converted to skills): `plan`, `tdd`, `code-review`, `build-fix`, `verify`
   - Rules: all entries from `common/` directory

2. **Language-matched** — entities tagged with languages in the Technology Profile.

3. **Framework-matched** — entities tagged with frameworks in the Technology Profile.

4. **Category-matched** — entities whose categories align with the project type and needs. Use judgment:
   - API project → include `api`, `database` categories
   - Web app → include `performance`, `accessibility` categories
   - Library → include `documentation`, `testing` categories

5. **Hook evaluation** — assess each hook individually:
   - Check if the hook's file matchers apply to the project's file types
   - Check if the hook's tool paths are available or adaptable
   - Include relevant hooks, skip irrelevant ones

6. **Exclusion** — remove entities that:
   - Target languages/frameworks not in the Technology Profile
   - Duplicate functionality of an already-selected higher-priority entity
   - Are hooks with file matchers that don't apply to any project files

**Priority resolution**: When multiple sources provide the same entity type+name, the source with the lower priority number wins (e.g., `local` priority 1 beats `everything-claude-code` priority 10).

### Step 4 — Present selection report

Present the selection report to the user for approval. Format:

```
## /ignite Selection Report

### Technology Profile
- Languages: Python 3.12
- Frameworks: FastAPI, SQLAlchemy
- ...

### Selected Entities

#### Agents (5)
| Entity | Source | Reason |
|--------|--------|--------|
| planner | everything-claude-code | Core entity |
| architect | everything-claude-code | Core entity |
| code-reviewer | everything-claude-code | Core entity |
| security-reviewer | everything-claude-code | Core entity |
| build-error-resolver | everything-claude-code | Core entity |

#### Skills (8)
| Entity | Source | Reason |
|--------|--------|--------|
| tdd-workflow | everything-claude-code | Core entity |
| coding-standards | everything-claude-code | Core entity |
| python-patterns | everything-claude-code | Language match: python |
| fastapi-patterns | everything-claude-code | Framework match: fastapi |
| ... | ... | ... |

#### Hooks (3)
| Hook | Event | Reason |
|------|-------|--------|
| pre-commit-lint | PreCommit | File matchers apply to *.py |
| ... | ... | ... |

#### Rules (embedded in CLAUDE.md)
- common/code-quality.md — Core rule
- python/type-hints.md — Language match: python

### Excluded Entities (showing top reasons)
| Entity | Type | Reason |
|--------|------|--------|
| go-reviewer | agent | Language not in profile: go |
| spring-boot-patterns | skill | Framework not in profile: spring |
| ... | ... | ... |

### Gap Analysis
| Technology | Coverage | Details |
|------------|----------|---------|
| FastAPI | Full | python-patterns + fastapi-patterns |
| SQLAlchemy | Partial | No dedicated entity; covered by python-patterns |
| Redis | None | No entities available |

### Actions
- [ ] Approve selection as-is
- [ ] Add entities: <specify>
- [ ] Remove entities: <specify>
- [ ] Cancel
```

> **Wait for user approval before proceeding. Do NOT auto-approve.**

The user may:
- Approve as-is
- Add specific entities (by name from the manifest)
- Remove entities from the selection
- Cancel the ignition

### Step 5 — Install and specialize

After approval, install the selected entities into the target project. See `references/specialization-guide.md` for adaptation rules.

**Installation targets in the target project:**

| Entity Type | Target Location |
|-------------|-----------------|
| Agents | `.claude/agents/{name}.md` |
| Skills | `.claude/skills/{name}/SKILL.md` |
| Commands → Skills | `.claude/skills/{name}/SKILL.md` (converted) |
| Rules | Embedded in CLAUDE.md `## Coding Conventions` or `## Workflow Preferences` |
| Hooks | Merged into `.claude/settings.json` |

**For each entity:**

1. Read the source entity file from the catalog.
2. Add a provenance header (see template below).
3. Specialize the content for the target project's tech stack per `references/specialization-guide.md`.
4. Write to the target location, creating directories as needed.

**Hook merging:**
- Read the target project's `.claude/settings.json` (create `{}` if missing).
- Add selected hooks to the `hooks` array, adapting file matchers and tool paths.
- Write back with consistent formatting.

**Provenance header** — add to the top of every installed file:

```
<!-- Installed by claude-code-project-igniter from {source}::{type}::{name} on {YYYY-MM-DD} -->
```

### Step 6 — Generate or update CLAUDE.md

Generate the target project's `CLAUDE.md` following the standards in `docs/CLAUDE-MD-SOTA.enriched.md` (if it exists in the igniter), falling back to `docs/CLAUDE-MD-SOTA.md` (seed).

**How to apply the generation reference:**

| Reference Part | CLAUDE.md Usage |
|----------------|-----------------|
| Part 1: Structural Standards | Determines skeleton — sections, order, size budget (~100 lines root) |
| Part 2: Content Guidelines | Decides what goes in each section, what to exclude |
| Part 3: Integration Guidelines | Decides what goes in CLAUDE.md vs hooks vs skills vs rules |
| Part 4: Behavioral Patterns | Selected and adapted based on project characteristics |
| Part 5: Maintenance Guidelines | Brief maintenance section or @import reference |

**Recommended sections** (per CLAUDE-MD-SOTA.md §1.3):

1. **Project Overview** — what the project is, 1-3 sentences
2. **Tech Stack** — from the Technology Profile
3. **Common Commands** — build, test, lint, deploy (non-obvious ones)
4. **Project Structure** — key directories and purposes
5. **Coding Conventions** — style rules, patterns, embedded rules
6. **Workflow Preferences** — verification steps, approach patterns
7. **Installed Entities** — registry of what `/ignite` installed (table with source attribution)
8. **Known Gaps** — technologies with partial/no coverage and recommended actions

**If CLAUDE.md already exists**: preserve existing content. Merge new sections. Add Installed Entities and Known Gaps sections. Update Tech Stack if it changed. Do not overwrite user-written content.

**Size budget**: aim for ~100 lines in the root CLAUDE.md. Use `@path/to/file.md` imports for detailed content. Consider child-directory CLAUDE.md files for large subtrees.

## References

- `references/ignite-workflow.md` — Detailed expansion of all 6 procedure steps.
- `references/specialization-guide.md` — How to adapt each entity type for the target project.
- `references/gap-analysis-guide.md` — Coverage assessment methodology and gap reporting.
- `scripts/build-manifest.py` — Manifest builder (run via `/sync-catalog`, not directly during ignition).
- `docs/CLAUDE-MD-SOTA.md` — Seed generation reference for CLAUDE.md standards.
- `docs/CLAUDE-MD-SOTA.enriched.md` — Enriched generation reference (seed + /insights, gitignored, preferred if available).

## Constraints

- **Never auto-install** — always present the selection report and wait for explicit user approval before installing anything.
- **Preserve existing content** — if the target project already has a CLAUDE.md or `.claude/` configuration, merge rather than overwrite. Respect user-written content.
- **Report gaps transparently** — always surface technologies with partial or no coverage. Never hide gaps to make the report look better.
- **Mark provenance** — every installed file gets a provenance header. Every entry in the Installed Entities section includes its source.
- **Respect priority** — when the same entity exists in multiple sources, always use the one from the higher-priority source (lower number).
- **Rules stay in CLAUDE.md** — rules cannot be installed as project-level files (they live at `~/.claude/rules/` which is user-level). Embed relevant rules in the CLAUDE.md or inject into agent prompts instead.
- **Commands become skills** — command `.md` files from the catalog are converted to proper `SKILL.md` format during installation, not copied as-is.
