# Claude Code Project Igniter — Unified Plan

> Merges [IGNITER-PLAN.md](old/IGNITER-PLAN.md) (architecture & components) + [CLAUDE-MD-SOTA-PLAN.md](old/CLAUDE-MD-SOTA-PLAN.md) (`/refresh-guidelines` skill & CLAUDE-MD-SOTA.md enrichment) into a single authoritative reference.

---

## 1. Context & Design Principles

### Problem

Every new project requires manually configuring Claude Code (agents, skills, rules, hooks, CLAUDE.md). Community repos like `everything-claude-code` offer battle-tested configs, but they're monolithic — you get everything or nothing, with no intelligent selection based on your actual tech stack.

### Solution

Build a "Project Igniter" — a standalone tool that maintains a downloadable catalog of Claude Code entities and uses an AI-driven `/ignite` skill to intelligently select, specialize, and install only the relevant entities after architecture decisions are made.

### Outcome

Run `/ignite` after planning your new project's architecture, and get a fully tailored Claude Code configuration in seconds — with transparent gap reporting for technologies not covered.

### CLAUDE.md Quality Gap

The CLAUDE.md generation reference uses a **seed + enriched** two-file model:

- **[CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md)** (seed, git-tracked) — contains web-sourced best practices only (Tiers 1-3). Ships with the repo as the baseline reference.
- **`CLAUDE-MD-SOTA.enriched.md`** (gitignored) — merges the seed with user-specific `/insights` data. Produced locally by `/refresh-guidelines`.

`/ignite` reads the enriched version if present, falling back to the seed. This split ensures the repo ships a useful baseline while keeping user-specific behavioral patterns local.

**Rationale for the split**: The seed contains universal best practices sourced from official Anthropic docs and community guides — these are the same for all users and belong in version control. `/insights` data (real behavioral patterns parsed from `~/.claude/usage-data/report.html` by `parse-insights.py`) is inherently user-specific and would create noisy git diffs if tracked. The enriched file adds this personalization layer without polluting the tracked seed.

### Design Principles

1. **Hybrid catalog**: Entities live in a local catalog directory, downloaded from remote repos. Only activated entities go into `.claude/`. This avoids context token bloat while keeping everything available locally.

2. **AI-driven specialization, not template variables**: Since entities are natural-language Markdown, Claude adapts them intelligently rather than through rigid `{{VARIABLE}}` substitution.

3. **Structured manifest for reliable matching**: A `manifest.json` with tags (languages, frameworks, categories, scope) enables precise entity selection rather than relying on filename conventions or content scanning at ignition time.

4. **Individual hook granularity**: Instead of all-or-nothing hook installation, each hook in the source `hooks.json` is individually tagged and selectable.

5. **Provenance tracking**: Every installed entity is marked with its source and specialization context, making it auditable and updatable.

6. **Gap analysis as a first-class feature**: Structured gap reports with coverage levels (none, partial, full) and actionable recommendations.

7. **Dual-source guidelines enrichment**: `/refresh-guidelines` combines `/insights` tips (real usage patterns) and a tiered web source registry (official docs + community guides) with automated fetching, Claude-driven semantic dedup/merge, and human approval.

8. **Scoped child-directory CLAUDE.md files**: Per CLAUDE-MD-SOTA.md §1.1, subdirectories with enough content get their own `CLAUDE.md` providing scoped instructions loaded on-demand. This keeps the root file lean (~100 lines) while giving Claude deep context where it matters (doc classification rules in `docs/`, schema conventions in `catalog/`, pipeline details in `refresh-guidelines/`, test conventions in `tests/`).

### Documentation Code of Conduct

The following rules apply whenever any file under `docs/` or `docs/old/` is created or modified during a session:

1. **Cross-referencing**: Check all files in `docs/` and `docs/old/` and add hyperlink references to related files when missing. Every doc file should link to the other docs it relates to (e.g., the plan links to the dev agenda and sub-products; sub-products cross-link each other).
2. **Sub-product isolation**: Files classified as *sub-products* (`CLAUDE-MD-SOTA.md`, `CLAUDE-MD-SOTA.enriched.md`, `SOURCE-SCHEMA.md`) must **only** contain hyperlinks to other sub-products — never to internal dev docs (`IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`, `IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`, `docs/old/*`). Internal dev docs may freely reference anything.

---

## 2. Architecture

### 2.1 Project Structure

```
claude-code-project-igniter/
├── CLAUDE.md                          # Instructions for working ON this project (root)
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
│   │   ├── add-source/
│   │   │   └── SKILL.md              # /add-source entrypoint
│   │   └── refresh-guidelines/
│   │       ├── CLAUDE.md             # Scoped: pipeline overview, scripts, output conventions
│   │       ├── SKILL.md              # /refresh-guidelines entrypoint
│   │       ├── references/
│   │       │   ├── curated-sources.md        # Tiered URL registry
│   │       │   └── enrichment-procedure.md   # Merge/dedup/conflict algorithm
│   │       └── scripts/
│   │           ├── fetch-guidelines.py       # Stdlib-only web fetcher
│   │           └── parse-insights.py         # Parses /insights HTML report
│   └── agents/
│       └── catalog-inspector.md      # Optional: deep entity inspection
│
├── docs/
│   ├── CLAUDE.md                              # Scoped: doc classification, sub-product isolation
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md  # Unified architecture plan (this file)
│   ├── CLAUDE-MD-SOTA.md             # Seed: web-sourced generation reference (tracked)
│   ├── CLAUDE-MD-SOTA.enriched.md    # Enriched: seed + /insights (gitignored)
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md  # Sprint-based development plan
│   ├── insights-raw.md               # User-accumulated /insights tips (gitignored)
│   ├── insights-parsed.json          # Output of parse-insights.py (gitignored)
│   ├── guidelines-raw.json           # Output of fetch-guidelines.py (gitignored)
│   └── old/                          # Archived pre-merge plans
│       ├── IGNITER-PLAN.md           # Original architecture plan
│       └── CLAUDE-MD-SOTA-PLAN.md    # Original /refresh-guidelines plan
│
├── tests/
│   └── CLAUDE.md                      # Scoped: pytest conventions, run commands, naming
│
├── catalog/
│   ├── CLAUDE.md                      # Scoped: sources.json schema, priority model, local conventions
│   ├── sources.json                  # Registry of remote sources
│   ├── manifest.json                 # Auto-generated entity index (gitignored)
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

### 2.2 Operational Model

The Project Igniter is a **standalone external tool** — it lives on your filesystem independently from any target project. It is never part of the projects it provisions. Two separate `.claude/` directories and two separate `CLAUDE.md` files are involved:

| | Igniter (this repo) | Target project |
|---|---|---|
| **Location** | e.g. `~/tools/claude-code-project-igniter/` | e.g. `~/projects/my-new-app/` |
| **`.claude/`** | Contains `/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines` skills, `catalog-inspector` agent, build/sync scripts | Populated by `/ignite` with specialized agents, skills, hooks tailored to the project's tech stack |
| **`CLAUDE.md`** | Instructions for working on the igniter itself | Generated by `/ignite` — guidelines-driven content, installed entity registry, gap report |

### 2.3 Workflow

**1. One-time setup** (performed once on the igniter repo)

```
Clone igniter repo to a permanent location (e.g. ~/tools/)
→ run /sync-catalog
→ remote sources cloned into catalog/sources/
→ manifest.json generated from all discovered entities
```

**1b. Guidelines enrichment** (on-demand, recommended before first ignition)

```
→ (recommended) run /insights beforehand so the report is fresh
→ run /refresh-guidelines
→ fetch-guidelines.py collects content from curated web sources
→ parse-insights.py extracts structured data from ~/.claude/usage-data/report.html
→ Claude reads all sources (insights-parsed.json + guidelines-raw.json + insights-raw.md)
→ classifies, deduplicates, and proposes enrichments
→ Human approves → two files produced:
     CLAUDE-MD-SOTA.md (seed, web-only, tracked)
     CLAUDE-MD-SOTA.enriched.md (seed + /insights, gitignored)
```

**2. Per-project ignition** (each time you start a new project)

```
Create new project directory
→ open Claude Code in the project with the igniter attached:
     claude --add-dir ~/tools/claude-code-project-igniter
→ plan architecture in conversation (tech stack, project type, etc.)
→ run /ignite
→ Claude reads catalog/manifest.json from the igniter
→ selects relevant entities (core + tag-matched + judgment-based)
→ presents selection report for user approval
→ user approves (with optional add/remove)
→ approved entities copied into the target project's .claude/
→ entities specialized to the project's tech stack
→ target project's CLAUDE.md generated/updated (per CLAUDE-MD-SOTA.enriched.md or seed)
→ gap report surfaced for uncovered technologies
```

---

## 3. Components

### 3.1 Source Registry (`catalog/sources.json`)

Defines where entities come from. Each source has: `id`, `url`, `branch`, `pin` (optional version lock), `priority` (lower = higher precedence), `entityPaths` (maps entity types to directories in the source repo). See [SOURCE-SCHEMA.md](SOURCE-SCHEMA.md) for the complete field reference.

Primary source: `everything-claude-code` (priority 10). Local custom entities: `local` (priority 1, always wins).

### 3.2 Manifest (`catalog/manifest.json`)

Auto-generated by `build-manifest.py`. Contains every entity with:
- **Composite ID**: `{source}::{type}::{name}` (e.g., `everything-claude-code::agent::code-reviewer`)
- **Tags**: `languages[]`, `frameworks[]`, `categories[]`, `scope` (universal/language-specific/framework-specific)
- **`coreEntity`**: boolean — always installed regardless of tech stack
- **`requiresAdaptation`**: boolean — needs specialization during install
- **Type-specific metadata**: agent model/tools, skill structure, hook events/matchers
- **Coverage summary**: aggregated list of all languages, frameworks, categories covered

Tags are auto-classified by the manifest builder using keyword analysis of entity names, descriptions, and content.

### 3.3 The `/ignite` Skill

**6-step procedure:**

| Step | Action |
|------|--------|
| **1. Read context** | Scan CLAUDE.md, conversation history, and project files (package.json, pyproject.toml, go.mod, docker-compose.yml, etc.) to build a Technology Profile |
| **2. Read manifest** | Load `catalog/manifest.json`. Warn if stale (>30 days) |
| **3. Select entities** | Core entities (always) + language-matched + framework-matched + category-based (Claude's judgment). Individual hook selection. Exclude irrelevant entities |
| **4. Present selection** | Structured report: what's selected and why, what's excluded, gap analysis. User can add/remove before proceeding |
| **5. Install & specialize** | Copy entities to project's `.claude/`, adapt descriptions/examples/paths/tools to the specific tech stack. Add provenance headers. Merge hooks into settings.json. Handle rules via CLAUDE.md embedding or agent prompt injection |
| **6. Update CLAUDE.md** | Generate per [CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md) — document installed entities, active hooks, and known gaps |

### 3.4 Specialization Mechanism

Claude adapts entities intelligently (not template-based):
- **Agents**: Update descriptions with project-specific trigger contexts, adjust domain references
- **Skills**: Swap code examples to project's framework, update file paths, remove irrelevant sections
- **Commands→Skills**: Convert to proper skills, update build/test commands to project's package manager
- **Rules**: Filter to relevant language, embed in CLAUDE.md or agent prompts (rules can only live at `~/.claude/rules/` user-level, so project-level alternatives are used)
- **Hooks**: Adjust file pattern matchers, tool paths (e.g., `npx prettier` → `ruff format`)

**Constraints**: Preserve core purpose, never remove security content, additive over subtractive, mark with provenance.

### 3.5 Gap Analysis

Three coverage levels:
- **Full**: Dedicated entity exists for the technology
- **Partial**: Parent-language entity covers basics but no dedicated entity
- **None**: No coverage at all

Report includes: what exists, what's missing, impact assessment, and actionable recommendations (inline in CLAUDE.md, create custom skill, add source, request upstream).

### 3.6 Core vs Catalog Split

**Always installed (core):**
- Agents: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `build-error-resolver`
- Skills: `tdd-workflow`, `coding-standards`, `verification-loop`, `security-review`
- Commands: `plan`, `tdd`, `code-review`, `build-fix`, `verify`
- Rules: `common/`

**Selectively installed (catalog):** Everything else — language-specific agents/reviewers, framework-specific skills (Django, Spring Boot, Go, etc.), utility skills, hooks, orchestration commands.

### 3.7 The `/refresh-guidelines` Skill

A **dual-source enrichment** skill combining `/insights` tips (real usage patterns) + tiered web source registry + automated fetching + Claude-driven semantic merge + human approval.

**Why a separate skill** (not part of `/sync-catalog`):
- `/sync-catalog` handles entity synchronization (git repos). Guidelines enrichment is a different concern (web content curation).
- One-concern-per-skill aligns with existing project patterns.
- Guidelines refresh is infrequent (monthly or on-demand), unlike catalog sync.

**Execution procedure:**
1. Run `fetch-guidelines.py` to collect raw content from curated web sources.
2. Run `parse-insights.py` to extract structured data from the user's `/insights` report at `~/.claude/usage-data/report.html` (+ `facets/*.json` and `session-meta/*.json`). Output: `docs/insights-parsed.json`. If the report is missing, skip with a warning. If stale (>7 days), warn user and suggest re-running `/insights`.
3. Read `docs/guidelines-raw.json` output (web sources).
4. Read `docs/insights-parsed.json` (parsed /insights report). Also read [`docs/insights-raw.md`](insights-raw.md) if it has manual tips beyond the header (supplement, not replace).
5. Read current [`docs/CLAUDE-MD-SOTA.md`](CLAUDE-MD-SOTA.md) (may be blank on first run).
6. Per theme section: classify incoming blocks from all sources (duplicate/novel/reinforcing/conflicting).
7. Produce enrichment report showing all proposed changes with source attribution.
8. Present report for human approval.
9. On approval: produce two files — seed (web-only, tracked) and enriched (seed + /insights, gitignored). If no /insights data, only the seed is updated.
10. Update Source Attribution section in both files.

**`/insights` report sections extracted** by `parse-insights.py`:

| Report Section | Source ID | Themes | Target Part |
|----------------|-----------|--------|-------------|
| CLAUDE.md Recommendations | `insights-claudemd-rec` | content, behavioral | Parts 2, 4 |
| Friction Points | `insights-friction` | anti-patterns, behavioral | Parts 2, 4 |
| Working Workflows (wins) | `insights-wins` | behavioral | Part 4 |
| Feature Recommendations | `insights-features` | integration | Part 3 |
| Usage Patterns | `insights-patterns` | behavioral, maintenance | Parts 4, 5 |
| Future Workflows (horizon) | `insights-horizon` | maintenance | Part 5 |
| Usage Narrative | `insights-usage` | behavioral | Part 4 |

**Curated web sources** are organized into three tiers:

| Tier | Description | Conflict precedence |
|------|-------------|---------------------|
| **Tier 1** | Official Anthropic docs (code.claude.com, claude.com/blog) | Highest — always wins |
| **Tier 2** | Established community guides (HumanLayer, Builder.io, Dometrain, Tembo, Arize) | Medium |
| **Tier 3** | Community templates & examples (GitHub repos, blog posts) | Lowest |

**Source precedence** (highest → lowest): T1 official docs > `/insights` data (source type `"insights"`) > T2 community guides > T3 templates. `/insights` data is not assigned a numeric tier — it is a distinct empirical source type, automatically parsed from the user's usage report. It ranks high because it reflects real usage patterns, but official documentation takes ultimate precedence. Within `/insights` data, internal priority for 300-line trimming: CLAUDE.md Recommendations > Friction > Wins > Features > Patterns > Horizon.

**Enrichment algorithm** (3 phases — detailed procedure in `enrichment-procedure.md`):
1. **Classification**: For each incoming block, classify as `novel` (insert), `duplicate` (skip), `reinforcing` (merge), or `conflicting` (flag for human). On first run with blank document, all content is `novel`.
2. **Conflict Resolution**: Higher-precedence sources win by default. Conflicts are never auto-resolved — always presented for human decision.
3. **Integration**: Claude produces two files — seed (web-only, tracked) and enriched (seed + /insights, gitignored). Human reviews diff and approves. Source Attribution updated in both.

### 3.8 CLAUDE-MD-SOTA.md Lifecycle

The generation reference uses a **seed + enriched** two-file model:

- **[CLAUDE-MD-SOTA.md](CLAUDE-MD-SOTA.md)** (seed, git-tracked) — web-sourced best practices only (Tiers 1-3). Ships with the repo.
- **`CLAUDE-MD-SOTA.enriched.md`** (gitignored) — seed content + `/insights` data merged. Produced locally by `/refresh-guidelines`.

Both files are populated via `/refresh-guidelines` from two sources:

1. **Web-sourced best practices** — official Anthropic docs, established community guides, and templates, fetched by `fetch-guidelines.py` into `docs/guidelines-raw.json`. Goes into **both** seed and enriched files.
2. **`/insights` data** — real behavioral patterns parsed from `~/.claude/usage-data/report.html` by `parse-insights.py` into `docs/insights-parsed.json`. Manual tips in [`docs/insights-raw.md`](insights-raw.md) supplement. Goes into the **enriched file only**.

**Target structure** for both files (under 300 lines each):

| Part | Content | Seed sources | Enriched adds |
|------|---------|--------------|---------------|
| Purpose & Scope | Role of document, seed/enriched model, how /ignite consumes it | — | — |
| Part 1: Structural Standards | Size constraints, recommended sections, file hierarchy, formatting | Web (T1, T2, T3) | — |
| Part 2: Content Guidelines | What to include/exclude, anti-patterns | Web (T1, T2, T3) | /insights (friction, claudemd-rec) |
| Part 3: Integration Guidelines | Hooks vs CLAUDE.md, Skills vs CLAUDE.md, Rules directory | Web (T1, T2) | /insights (features) |
| Part 4: Behavioral Patterns | Workflow rules, coding patterns, interaction preferences | Web (T1, T2, T3) | /insights (claudemd-rec, wins, patterns, usage) |
| Part 5: Maintenance Guidelines | Review cadence, self-improving patterns, versioning | Web (T1, T2) | /insights (patterns, horizon) |
| Source Attribution | Source URLs with tier labels, dates | Web sources only | Web + /insights references |

Key principles:
- **Seed is self-sufficient** — the repo ships a useful baseline even without running `/refresh-guidelines`.
- **Content is emergent** — behavioral rules, domain-specific patterns, and best practices are discovered from real sources rather than pre-defined.
- `/refresh-guidelines` is idempotent — running it again deduplicates and merges new content with existing.
- **`/insights` content stays local** — user-specific patterns never pollute the tracked seed.

**How `/ignite` consumes the reference:**

`/ignite` reads `CLAUDE-MD-SOTA.enriched.md` if present, falling back to `CLAUDE-MD-SOTA.md` (seed).

| Part | /ignite Usage |
|-----------------------------|---------------|
| Part 1: Structural Standards | Determines CLAUDE.md skeleton — sections, order, size budget |
| Part 2: Content Guidelines | Decides what goes in each section (e.g., linter rules → hooks, not CLAUDE.md) |
| Part 3: Integration Guidelines | Decides what goes where — CLAUDE.md vs hooks vs skills vs .claude/rules/ |
| Part 4: Behavioral Patterns | Selected and adapted based on project characteristics — nothing is unconditionally embedded |
| Part 5: Maintenance Guidelines | Brief `## Maintenance` section or @import reference |

---

## 4. Delivery & Usage

### 4.1 Sprint Overview

Development is organized into 8 sprints. See [IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md](IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md) for the canonical sprint-by-sprint breakdown with tasks, acceptance criteria, and file delivery summary.

| Sprint | Name | Key deliverables |
|--------|------|------------------|
| 0 | Project Scaffolding | CLAUDE.md, .gitignore, directory skeleton |
| 1 | Catalog Foundation | `sources.json`, local entity structure, source schema docs |
| 1.5 | Guidelines Enrichment | `/refresh-guidelines` skill, `fetch-guidelines.py`, seed + enriched two-file model |
| 2 | Catalog Sync Pipeline | `sync-catalog.sh`, `.source-meta.json` |
| 3 | Manifest Builder | `build-manifest.py` — most complex piece |
| 4 | Sync-Catalog & Add-Source Skills | `/sync-catalog`, `/add-source`, `catalog-inspector` agent |
| 5 | Ignite Skill & Reference Docs | `/ignite` SKILL.md, workflow/specialization/gap-analysis guides |
| 6 | Integration Testing & Polish | Archetype tests, README, final documentation |

Sprint 1.5 rationale: Having a populated CLAUDE-MD-SOTA.md early means all subsequent work (especially Sprint 5's `/ignite`) aligns with it from the start. The seed ships with web-sourced best practices; the enriched version adds user-specific `/insights` data locally.

### 4.2 Installation Options (for end users)

1. **`--add-dir` flag** (recommended): `claude --add-dir ~/tools/claude-code-project-igniter` — makes skills available per-session
2. **Symlinks to `~/.claude/skills/`**: Makes `/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines` globally available
3. **Shell alias**: `alias claude-ignite='claude --add-dir ~/tools/claude-code-project-igniter'`

---

## 5. Verification

### Catalog & Ignition
1. **Unit**: Run `build-manifest.py` against a synced catalog and verify manifest accuracy (correct tags, complete entity list, valid JSON).
2. **Integration**: Run `/sync-catalog` end-to-end (clone, build manifest, verify `.source-meta.json`).
3. **Archetype tests**: Run `/ignite` against 5-6 project archetypes and verify:
   - Correct entity selection per tech stack
   - Specialization quality (adapted descriptions, correct paths)
   - Gap report accuracy
   - No installation of irrelevant entities
   - Hooks correctly merged into settings.json
   - CLAUDE.md correctly generated
4. **Edge cases**: Empty project (conversation-only context), project with no matching entities, project with conflicting sources.

### Guidelines Enrichment
5. `/refresh-guidelines` skill is invocable and Claude discovers it.
6. `fetch-guidelines.py` fetches content from at least Tier 1 sources without errors.
7. `docs/guidelines-raw.json` produced with valid JSON and themed content blocks.
8. `parse-insights.py` produces valid `docs/insights-parsed.json` when `~/.claude/usage-data/report.html` is present.
9. `/insights` report sections (CLAUDE.md recs, friction, wins, features, patterns, horizon, usage) are correctly extracted into themed content blocks.
10. Staleness warning produced when `/insights` report is older than 7 days.
11. `parse-insights.py` handles missing report gracefully (exits 0, produces minimal JSON).
12. After `/refresh-guidelines`, the seed (`CLAUDE-MD-SOTA.md`) contains only web-sourced content (no `/insights` material).
13. After `/refresh-guidelines` with `/insights` data available, `CLAUDE-MD-SOTA.enriched.md` is produced with seed + `/insights` content merged.
14. `/insights` data correctly integrated into the enriched file from `docs/insights-parsed.json`; manual tips in `docs/insights-raw.md` also integrated when present.
15. Seed Source Attribution lists web sources only. Enriched Source Attribution lists both web sources and `/insights` references.
16. `CLAUDE-MD-SOTA.enriched.md` is gitignored. `CLAUDE-MD-SOTA.md` is tracked.
16. Enrichment report correctly classifies incoming content (novel on first run; duplicate/reinforcing on subsequent runs).
17. No conflicting information merged without human review.
18. Document stays under 300 lines.

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Context window pressure during ignition | Progressive disclosure: read only manifest for selection, then entity files one-by-one during install |
| Rules only work at `~/.claude/rules/` (user level) | Embed in CLAUDE.md or agent prompts for project-level scoping |
| Hook scripts reference `${CLAUDE_PLUGIN_ROOT}` | Rewrite paths to `$CLAUDE_PROJECT_DIR/.claude/hooks/` during install |
| Auto-tag classification inaccuracy | Conservative defaults; user can override via `local/` source; manifest is regenerable |
| Source repo restructuring | `entityPaths` in sources.json decouples from source directory layout |
| Fetched web content structure changes | Defensive parsing with fallbacks; curated-sources records expected format |
| CLAUDE-MD-SOTA.md becomes too long | Use @import references for detailed subsections; keep main doc as structured index |
| Sources genuinely conflict | Enrichment procedure classifies conflicts explicitly, escalates to human; tier determines default |
| URL changes/redirects | `fetch-guidelines.py` follows redirects; curated-sources updated when URLs change |
| Network failures during fetch | Fault-tolerant: skip failed URLs, produce partial results, report errors |
| /insights tips unavailable or low quality | Document can be fully populated from web sources alone; /insights enriches but isn't required. `/refresh-guidelines` works with whichever sources are available |
| `/insights` report HTML structure changes across Claude Code versions | `parse-insights.py` uses class-based extraction (`.big-win`, `.friction-category`, etc.) which is more stable than positional parsing. Graceful degradation: missing sections produce empty entries, not errors |
| No `/insights` report exists (first-time users) | `parse-insights.py` outputs minimal JSON with empty entries and `is_stale: true`. Pipeline proceeds with web sources only |
| `/insights` report covers all projects, not just current one | For CLAUDE-MD-SOTA.md (a universal reference), cross-project insights are desirable. `parse-insights.py` includes session-meta data for optional project filtering if needed in the future |
