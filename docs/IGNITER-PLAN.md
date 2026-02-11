# Claude Code Project Igniter — Implementation Plan

## Context

**Problem**: Every new project requires manually configuring Claude Code (agents, skills, rules, hooks, CLAUDE.md). Community repos like `everything-claude-code` offer battle-tested configs, but they're monolithic — you get everything or nothing, with no intelligent selection based on your actual tech stack.

**Solution**: Build a "Project Igniter" — a standalone tool that maintains a downloadable catalog of Claude Code entities and uses an AI-driven `/ignite` skill to intelligently select, specialize, and install only the relevant entities after architecture decisions are made.

**Outcome**: Run `/ignite` after planning your new project's architecture, and get a fully tailored Claude Code configuration in seconds — with transparent gap reporting for technologies not covered.

---

## Concept Validation & Key Improvements

**Your original idea is sound.** The two-phase approach (general catalog → project-specific specialization) is the right pattern. Key improvements over the raw concept:

1. **Hybrid catalog (your choice)**: Entities live in a local catalog directory, downloaded from remote repos. Only activated entities go into `.claude/`. This avoids context token bloat while keeping everything available locally.

2. **AI-driven specialization, not template variables**: Since entities are natural-language Markdown, Claude adapts them intelligently rather than through rigid `{{VARIABLE}}` substitution. This is more flexible and handles edge cases better.

3. **Structured manifest for reliable matching**: A `manifest.json` with tags (languages, frameworks, categories, scope) enables precise entity selection rather than relying on filename conventions or content scanning at ignition time.

4. **Individual hook granularity**: Instead of all-or-nothing hook installation, each hook in the source `hooks.json` is individually tagged and selectable.

5. **Provenance tracking**: Every installed entity is marked with its source and specialization context, making it auditable and updatable.

6. **Gap analysis as a first-class feature**: Not just "we don't have that" — structured gap reports with coverage levels (none, partial, full) and actionable recommendations.

---

## Architecture Overview

### Project Structure

```
claude-code-project-igniter/
├── CLAUDE.md                          # Instructions for working ON this project
├── .gitignore                         # Ignores catalog/sources/*/ (downloaded content)
│
├── .claude/
│   ├── settings.json
│   ├── skills/
│   │   ├── ignite/
│   │   │   ├── SKILL.md              # /ignite entrypoint (<500 lines)
│   │   │   ├── references/
│   │   │   │   ├── ignite-workflow.md        # Detailed step-by-step procedure
│   │   │   │   ├── specialization-guide.md   # How to adapt entities
│   │   │   │   └── gap-analysis-guide.md     # How to assess coverage
│   │   │   └── scripts/
│   │   │       └── build-manifest.py         # Generates manifest.json
│   │   ├── sync-catalog/
│   │   │   ├── SKILL.md              # /sync-catalog entrypoint
│   │   │   └── scripts/
│   │   │       └── sync-catalog.sh   # Clones/pulls remote sources
│   │   └── add-source/
│   │       └── SKILL.md              # /add-source entrypoint
│   └── agents/
│       └── catalog-inspector.md      # Optional: deep entity inspection
│
├── catalog/
│   ├── sources.json                  # Registry of remote sources
│   ├── manifest.json                 # Auto-generated entity index
│   └── sources/                      # Downloaded repos (gitignored)
│       ├── everything-claude-code/   # Primary source
│       │   ├── .source-meta.json     # Sync metadata
│       │   ├── agents/
│       │   ├── skills/
│       │   ├── commands/
│       │   ├── rules/
│       │   └── hooks/
│       └── local/                    # User's custom entities (not gitignored)
│           ├── agents/
│           ├── skills/
│           ├── commands/
│           └── rules/
```

### Workflow

```
1. ONE-TIME SETUP
   Clone igniter repo → run /sync-catalog → catalog populated

2. PER-PROJECT
   Create project → start Claude with --add-dir ~/tools/igniter
   → plan architecture → run /ignite
   → Claude reads manifest → selects entities → presents selection
   → user approves → entities installed + specialized → gaps reported
```

---

## Key Components

### 1. Source Registry (`catalog/sources.json`)

Defines where entities come from. Each source has: `id`, `url`, `branch`, `pin` (optional version lock), `priority` (lower = higher precedence), `entityPaths` (maps entity types to directories in the source repo).

Primary source: `everything-claude-code` (priority 10). Local custom entities: `local` (priority 1, always wins).

### 2. Manifest (`catalog/manifest.json`)

Auto-generated by `build-manifest.py`. Contains every entity with:
- **Composite ID**: `{source}::{type}::{name}` (e.g., `everything-claude-code::agent::code-reviewer`)
- **Tags**: `languages[]`, `frameworks[]`, `categories[]`, `scope` (universal/language-specific/framework-specific)
- **`coreEntity`**: boolean — always installed regardless of tech stack
- **`requiresAdaptation`**: boolean — needs specialization during install
- **Type-specific metadata**: agent model/tools, skill structure, hook events/matchers
- **Coverage summary**: aggregated list of all languages, frameworks, categories covered

Tags are auto-classified by the manifest builder using keyword analysis of entity names, descriptions, and content.

### 3. The `/ignite` Skill

**6-step procedure:**

| Step | Action |
|------|--------|
| **1. Read context** | Scan CLAUDE.md, conversation history, and project files (package.json, pyproject.toml, go.mod, docker-compose.yml, etc.) to build a Technology Profile |
| **2. Read manifest** | Load `catalog/manifest.json`. Warn if stale (>30 days) |
| **3. Select entities** | Core entities (always) + language-matched + framework-matched + category-based (Claude's judgment). Individual hook selection. Exclude irrelevant entities |
| **4. Present selection** | Structured report: what's selected and why, what's excluded, gap analysis. User can add/remove before proceeding |
| **5. Install & specialize** | Copy entities to project's `.claude/`, adapt descriptions/examples/paths/tools to the specific tech stack. Add provenance headers. Merge hooks into settings.json. Handle rules via CLAUDE.md embedding or agent prompt injection |
| **6. Update CLAUDE.md** | Document installed entities, active hooks, and known gaps |

### 4. Specialization Mechanism

Claude adapts entities intelligently (not template-based):
- **Agents**: Update descriptions with project-specific trigger contexts, adjust domain references
- **Skills**: Swap code examples to project's framework, update file paths, remove irrelevant sections
- **Commands→Skills**: Convert to proper skills, update build/test commands to project's package manager
- **Rules**: Filter to relevant language, embed in CLAUDE.md or agent prompts (rules can only live at `~/.claude/rules/` user-level, so project-level alternatives are used)
- **Hooks**: Adjust file pattern matchers, tool paths (e.g., `npx prettier` → `ruff format`)

**Constraints**: Preserve core purpose, never remove security content, additive over subtractive, mark with provenance.

### 5. Gap Analysis

Three coverage levels:
- **Full**: Dedicated entity exists for the technology
- **Partial**: Parent-language entity covers basics but no dedicated entity
- **None**: No coverage at all

Report includes: what exists, what's missing, impact assessment, and actionable recommendations (inline in CLAUDE.md, create custom skill, add source, request upstream).

### 6. Core vs Catalog Split

**Always installed (core):**
- Agents: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `build-error-resolver`
- Skills: `tdd-workflow`, `coding-standards`, `verification-loop`, `security-review`
- Commands: `plan`, `tdd`, `code-review`, `build-fix`, `verify`
- Rules: `common/`

**Selectively installed (catalog):** Everything else — language-specific agents/reviewers, framework-specific skills (Django, Spring Boot, Go, etc.), utility skills, hooks, orchestration commands.

---

## Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| **1** | `catalog/sources.json` | Source registry with primary source definition |
| **2** | `scripts/sync-catalog.sh` | Shell script to clone/pull sources |
| **3** | `scripts/build-manifest.py` | Manifest generator (YAML parsing, tag classification) — most complex piece |
| **4** | `/sync-catalog` skill | Claude-friendly wrapper around sync + manifest build |
| **5** | `/ignite` SKILL.md | Main skill entrypoint |
| **6** | `references/ignite-workflow.md` | Detailed 6-step procedure |
| **7** | `references/specialization-guide.md` | Adaptation rules and constraints |
| **8** | `references/gap-analysis-guide.md` | Coverage assessment methodology |
| **9** | `/add-source` skill | Register new remote sources |
| **10** | `CLAUDE.md` + `.gitignore` | Project documentation and git configuration |
| **11** | Testing | Test against archetypes: Python/Django, TS/React/Next.js, Go microservice, Java/Spring Boot, polyglot (Python+TS), empty project |

---

## Installation Options (for end users)

1. **`--add-dir` flag** (recommended): `claude --add-dir ~/tools/claude-code-project-igniter` — makes skills available per-session
2. **Symlinks to `~/.claude/skills/`**: Makes `/ignite`, `/sync-catalog`, `/add-source` globally available
3. **Shell alias**: `alias claude-ignite='claude --add-dir ~/tools/claude-code-project-igniter'`

---

## Verification Plan

1. **Unit**: Run `build-manifest.py` against a synced catalog and verify manifest accuracy (correct tags, complete entity list, valid JSON)
2. **Integration**: Run `/sync-catalog` end-to-end (clone, build manifest, verify `.source-meta.json`)
3. **Archetype tests**: Run `/ignite` against 5-6 project archetypes (see Phase 11) and verify:
   - Correct entity selection per tech stack
   - Specialization quality (adapted descriptions, correct paths)
   - Gap report accuracy
   - No installation of irrelevant entities
   - Hooks correctly merged into settings.json
   - CLAUDE.md correctly generated
4. **Edge cases**: Empty project (conversation-only context), project with no matching entities, project with conflicting sources

---

## CLAUDE.md Lifecycle Guidelines

> Full specification: [docs/CLAUDE-MD-LIFECYCLE.md](CLAUDE-MD-LIFECYCLE.md)

Defines the behavioral rules and domain-specific workflow rules that `/ignite` embeds into every project's `CLAUDE.md`. Includes core rules (write-first, no preemptive execution, no scope creep, clarify before acting) and conditionally-included domain sections (General Conventions, Document Validation, Task Management, Docker/Infrastructure, Grant Proposal Documents).

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Context window pressure during ignition | Progressive disclosure: read only manifest for selection, then entity files one-by-one during install |
| Rules only work at `~/.claude/rules/` (user level) | Embed in CLAUDE.md or agent prompts for project-level scoping |
| Hook scripts reference `${CLAUDE_PLUGIN_ROOT}` | Rewrite paths to `$CLAUDE_PROJECT_DIR/.claude/hooks/` during install |
| Auto-tag classification inaccuracy | Conservative defaults; user can override via `local/` source; manifest is regenerable |
| Source repo restructuring | `entityPaths` in sources.json decouples from source directory layout |
