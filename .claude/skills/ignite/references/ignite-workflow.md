# /ignite Workflow — Detailed Step Reference

This document expands each of the 6 steps in the `/ignite` procedure with actionable implementation details. Read alongside [`SKILL.md`](../SKILL.md) which defines the high-level procedure.

---

## Step 1: Read Context and Build Technology Profile

### Files to Scan

Scan the target project root for these files. Each provides specific signals:

**JavaScript / TypeScript ecosystem:**
| File | Signals |
|------|---------|
| `package.json` | `dependencies`, `devDependencies` → frameworks, test runners, build tools. `scripts` → common commands. `engines` → Node version. |
| `tsconfig.json` | TypeScript presence, `strict` mode, `paths` aliases |
| `.eslintrc*`, `eslint.config.*` | Linting configuration, code style |
| `vite.config.*`, `webpack.config.*`, `next.config.*` | Build tools, frameworks |

**Python ecosystem:**
| File | Signals |
|------|---------|
| `pyproject.toml` | `[project.dependencies]` → frameworks. `[tool.*]` → test/lint config. `requires-python` → version. |
| `setup.py`, `setup.cfg` | Legacy Python project structure |
| `requirements.txt`, `Pipfile` | Dependencies → frameworks |
| `tox.ini`, `pytest.ini` | Test configuration |

**Go ecosystem:**
| File | Signals |
|------|---------|
| `go.mod` | Go version, module path, dependencies → frameworks |
| `go.sum` | Dependency verification |
| `Makefile` | Common build/test commands |

**Rust ecosystem:**
| File | Signals |
|------|---------|
| `Cargo.toml` | Edition, dependencies → frameworks (actix, tokio, serde) |
| `rust-toolchain.toml` | Rust version, components |

**Java / Kotlin ecosystem:**
| File | Signals |
|------|---------|
| `pom.xml` | Maven project, dependencies → frameworks (Spring, Jakarta) |
| `build.gradle`, `build.gradle.kts` | Gradle project, plugins → frameworks |
| `settings.gradle*` | Multi-module structure |

**Infrastructure:**
| File | Signals |
|------|---------|
| `Dockerfile`, `docker-compose.yml` | Docker presence, services (databases, caches) |
| `.github/workflows/*.yml` | GitHub Actions CI/CD |
| `.gitlab-ci.yml` | GitLab CI/CD |
| `Jenkinsfile` | Jenkins CI/CD |
| `Makefile`, `justfile` | Build automation |
| `.env.example`, `.env.template` | Environment configuration patterns |

### Signal Extraction Rules

For each detected file:
1. Read the file content.
2. Extract technology signals (framework names, tool names, version numbers).
3. Classify into the Technology Profile fields.
4. Note confidence level: **high** (explicit declaration like `"fastapi"` in dependencies) vs **inferred** (directory structure suggests a framework).

### Conversation History

Also scan the conversation history for:
- Architecture decisions ("we'll use FastAPI for the API layer")
- Technology choices ("let's go with PostgreSQL")
- Project type descriptions ("this is a CLI tool")

Conversation signals supplement file-based detection. If there's a conflict, ask the user.

### Existing CLAUDE.md

If the target project already has a `CLAUDE.md`:
1. Read it fully.
2. Extract any tech stack information already documented.
3. Note existing sections that should be preserved during Step 6.
4. Flag any installed entities already present (check for provenance headers).

### Profile Presentation

Present the assembled Technology Profile in a clear format and ask the user to confirm or correct it before proceeding.

---

## Step 2: Manifest Loading

### Path Resolution

The manifest lives in the **igniter** repo, not the target project:
- Path: `<igniter-root>/catalog/manifest.json`
- The igniter root is the directory attached via `claude --add-dir`.

### Validation

Check that the manifest contains these top-level fields:
- `entities` (array) — the entity index
- `coverage` (object) — aggregated languages, frameworks, categories
- `generatedAt` (string) — ISO 8601 timestamp
- `sources` (array) — source metadata

If any field is missing, warn and ask the user to run `/sync-catalog`.

### Staleness Check

Parse `generatedAt` and compare to the current date:
- **Fresh** (≤30 days): proceed normally.
- **Stale** (>30 days): warn the user. Suggest running `/sync-catalog` to refresh. Proceed if they choose to continue with stale data.

### Missing Manifest

If `catalog/manifest.json` doesn't exist:
- Stop the procedure.
- Instruct: "No manifest found. Run `/sync-catalog` first to build the entity catalog."

---

## Step 3: Selection Algorithm

### Phase 1 — Core Entities

Always include entities with `coreEntity: true` in the manifest. These are:

**Agents:**
- `planner` — project planning and task decomposition
- `architect` — architecture decisions and system design
- `code-reviewer` — code quality and review
- `security-reviewer` — security assessment
- `build-error-resolver` — build and CI error resolution

**Skills:**
- `tdd-workflow` — test-driven development process
- `coding-standards` — code style and quality standards
- `verification-loop` — verify changes before committing
- `security-review` — security review checklist

**Commands (→ converted to skills):**
- `plan`, `tdd`, `code-review`, `build-fix`, `verify`

**Rules:**
- All entries from `common/` directory (universal rules that apply to any project)

Core entities are included regardless of the Technology Profile. They provide foundational development practices.

### Phase 2 — Language Matching

For each language in the Technology Profile:
1. Find entities where `tags.languages` contains that language.
2. Include them in the selection.
3. Note the reason: "Language match: {language}".

Examples:
- Python project → include `python-patterns`, `python-reviewer`, python-specific rules
- TypeScript project → include `typescript-patterns`, typescript-specific rules

### Phase 3 — Framework Matching

For each framework in the Technology Profile:
1. Find entities where `tags.frameworks` contains that framework.
2. Include them in the selection.
3. Note the reason: "Framework match: {framework}".

Examples:
- FastAPI project → include `fastapi-patterns`, framework-specific rules (e.g. `python/security` which carries a Django tag)
- React project → include `react-patterns`, `nextjs-patterns` (if Next.js detected), framework-specific rules

### Phase 4 — Category Matching

Based on the project type and characteristics, include entities whose categories align:

| Project Type | Relevant Categories |
|--------------|---------------------|
| API service | `api`, `database`, `security`, `performance` |
| Web application | `api`, `performance`, `testing`, `accessibility` |
| CLI tool | `testing`, `documentation` |
| Library | `documentation`, `testing`, `api` |
| Monorepo | `architecture`, `ci-cd`, `build` |
| Microservice | `api`, `database`, `devops`, `ci-cd`, `docker` |

Use judgment — not all category matches are appropriate. Consider whether the entity adds genuine value for this specific project.

### Phase 5 — Hook Evaluation

Assess each hook in the manifest individually:

1. **File matchers**: Does the hook's file pattern (e.g., `**/*.ts`) match files in the target project? If the project has no `.ts` files, skip.
2. **Tool availability**: Is the hook's tool (e.g., `npx prettier`) available or adaptable to the project's tooling?
3. **Event relevance**: Is the hook's event type (PreCommit, PostEdit, etc.) useful for this project?

Include hooks that pass all three checks. Skip those that don't apply.

### Phase 6 — Exclusion

Remove entities from the selection if they:
- Target languages not in the Technology Profile (e.g., Go-specific agent for a Python project)
- Target frameworks not in the Technology Profile
- Duplicate functionality of a higher-priority entity already selected
- Are hooks with file matchers that don't match any files in the project

### Priority Resolution

When the same entity (same type + name) exists in multiple sources:
- Select the one from the source with the **lowest priority number** (highest precedence).
- `local` (priority 1) always wins over remote sources.
- Document which version was selected and why in the report.

---

## Step 4: Selection Report

### Report Structure

Present the report in the format shown in `SKILL.md`. Key sections:

1. **Technology Profile** — confirmed profile from Step 1
2. **Selected Entities** — grouped by type (Agents, Skills, Hooks, Rules), with source and reason
3. **Excluded Entities** — top exclusions with reasons (don't list every irrelevant entity — focus on near-misses and notable exclusions)
4. **Gap Analysis** — technologies with Full/Partial/None coverage (see `references/gap-analysis-guide.md`)
5. **Action Prompt** — approve / modify / cancel

### User Interaction

Wait for explicit approval. The user may:
- **Approve**: proceed to Step 5
- **Add entities**: specify entity names to add (look up in manifest)
- **Remove entities**: specify entities to exclude
- **Cancel**: abort the ignition

If the user modifies the selection, update the report and re-present for confirmation.

---

## Step 5: Installation and Specialization

### Directory Creation

Create these directories in the target project if they don't exist:
- `.claude/agents/`
- `.claude/skills/`
- `.claude/settings.json` (create as `{}` if missing)

### Entity Installation

For each approved entity, in order (agents → skills → commands → rules → hooks):

1. **Read** the source file from the catalog path (the `path` field in the manifest entry).
2. **Add provenance header** as the first line.
3. **Specialize** the content per `references/specialization-guide.md`.
4. **Write** to the target location.

### Commands → Skills Conversion

Command `.md` files are simple markdown instructions. Convert them to proper `SKILL.md` format:
1. Read the command markdown.
2. Create a `SKILL.md` with:
   - `# /{command-name}` title
   - Summary extracted from the command description
   - `## Procedure` with the command's instructions adapted as skill steps
   - Update tool paths and commands to match the target project's package manager

### Hook Merging

Hooks are merged into the target project's `.claude/settings.json`:

1. Read the target's `.claude/settings.json` (or create `{}` if missing).
2. Ensure a `hooks` object exists at the top level.
3. For each selected hook, add it under the appropriate event key.
4. Adapt file matchers and tool paths per `references/specialization-guide.md`.
5. Write back with 2-space indentation.

### Rule Embedding

Rules cannot be installed as project-level files. Instead:

1. Read the rule content.
2. Extract the key guidelines and patterns.
3. Embed them in the appropriate CLAUDE.md section:
   - Language-specific coding rules → `## Coding Conventions`
   - Workflow rules → `## Workflow Preferences`
   - Security rules → embedded in the security reviewer agent's prompt
4. Keep embedded rules concise — reference the full rule text via `@` import if it's too long.

---

## Step 6: CLAUDE.md Generation

### Reference Loading

1. Check if `docs/CLAUDE-MD-SOTA.enriched.md` exists in the igniter directory.
2. If yes, use it as the generation reference (it includes user-specific behavioral patterns).
3. If no, fall back to `docs/CLAUDE-MD-SOTA.md` (seed, web-sourced best practices only).

### Section Generation

Generate the 8 recommended sections per CLAUDE-MD-SOTA.md §1.3:

1. **Project Overview** — 1-3 sentences from conversation context or inferred from project structure.
2. **Tech Stack** — from the confirmed Technology Profile.
3. **Common Commands** — build, test, lint, format, deploy commands. Detect from `package.json` scripts, `Makefile` targets, `pyproject.toml` scripts, etc. Only include non-obvious commands.
4. **Project Structure** — key directories and their purposes. Scan the actual directory structure.
5. **Coding Conventions** — embedded rules from the catalog + project-specific patterns detected from existing code (linting config, formatting config, etc.).
6. **Workflow Preferences** — behavioral patterns selected from CLAUDE-MD-SOTA Part 4, adapted to project needs.
7. **Installed Entities** — table of everything `/ignite` installed, with source attribution and brief descriptions.
8. **Known Gaps** — concise gap report from the selection report's gap analysis.

### Merge vs. Create

**If CLAUDE.md doesn't exist**: generate all 8 sections from scratch.

**If CLAUDE.md already exists**:
1. Preserve all existing user-written content.
2. Add new sections that don't exist yet (Installed Entities, Known Gaps).
3. Supplement existing sections (e.g., add new commands to Common Commands).
4. Never delete or overwrite user content.
5. Mark igniter-generated sections with a comment: `<!-- Generated by /ignite -->`

### Size Budget

Per CLAUDE-MD-SOTA.md §1.1:
- Root CLAUDE.md should be ~100 lines (practical target, not a hard limit).
- Use `@path/to/file.md` imports for detailed content.
- Consider child-directory `CLAUDE.md` files for large monorepos.

If the generated content exceeds ~150 lines, break out detailed sections into importable files and use `@` references.
