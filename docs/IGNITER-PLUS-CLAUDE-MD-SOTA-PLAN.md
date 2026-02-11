# Claude Code Project Igniter — Unified Plan

> Merges [IGNITER-PLAN.md](IGNITER-PLAN.md) (architecture & components) + [CLAUDE-MD-SOTA-PLAN.md](CLAUDE-MD-SOTA-PLAN.md) (`/refresh-guidelines` skill & CLAUDE-MD-SOTA.md enrichment) into a single authoritative reference.

---

## 1. Context

**Problem**: Every new project requires manually configuring Claude Code (agents, skills, rules, hooks, CLAUDE.md). Community repos like `everything-claude-code` offer battle-tested configs, but they're monolithic — you get everything or nothing, with no intelligent selection based on your actual tech stack.

**Solution**: Build a "Project Igniter" — a standalone tool that maintains a downloadable catalog of Claude Code entities and uses an AI-driven `/ignite` skill to intelligently select, specialize, and install only the relevant entities after architecture decisions are made.

**Outcome**: Run `/ignite` after planning your new project's architecture, and get a fully tailored Claude Code configuration in seconds — with transparent gap reporting for technologies not covered.

**CLAUDE.md quality gap**: `docs/CLAUDE-MD-SOTA.md` currently holds only 4 behavioral rules and a few domain-specific conditional rules. Its intended role is much larger: it should be the **authoritative reference** governing how target project CLAUDE.md files are structured, what content they include/exclude, how they integrate with hooks/skills/rules, and how they're maintained over time. A rich body of CLAUDE.md best practices (from official Anthropic docs, established community guides, and templates) is not yet captured. A repeatable `/refresh-guidelines` skill solves this.

---

## 2. Concept Validation & Key Improvements

**Your original idea is sound.** The two-phase approach (general catalog → project-specific specialization) is the right pattern. Key improvements over the raw concept:

1. **Hybrid catalog (your choice)**: Entities live in a local catalog directory, downloaded from remote repos. Only activated entities go into `.claude/`. This avoids context token bloat while keeping everything available locally.

2. **AI-driven specialization, not template variables**: Since entities are natural-language Markdown, Claude adapts them intelligently rather than through rigid `{{VARIABLE}}` substitution. This is more flexible and handles edge cases better.

3. **Structured manifest for reliable matching**: A `manifest.json` with tags (languages, frameworks, categories, scope) enables precise entity selection rather than relying on filename conventions or content scanning at ignition time.

4. **Individual hook granularity**: Instead of all-or-nothing hook installation, each hook in the source `hooks.json` is individually tagged and selectable.

5. **Provenance tracking**: Every installed entity is marked with its source and specialization context, making it auditable and updatable.

6. **Gap analysis as a first-class feature**: Not just "we don't have that" — structured gap reports with coverage levels (none, partial, full) and actionable recommendations.

7. **Guidelines enrichment pipeline**: A curated hybrid approach (`/refresh-guidelines`) that combines a tiered source registry, automated web fetching, Claude-driven semantic dedup/merge, and human approval — ensuring `/ignite` generates high-quality, standards-compliant CLAUDE.md files.

---

## 3. Architecture Overview

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
│   │   ├── add-source/
│   │   │   └── SKILL.md              # /add-source entrypoint
│   │   └── refresh-guidelines/
│   │       ├── SKILL.md              # /refresh-guidelines entrypoint
│   │       ├── references/
│   │       │   ├── curated-sources.md        # Tiered URL registry
│   │       │   └── enrichment-procedure.md   # Merge/dedup/conflict algorithm
│   │       └── scripts/
│   │           └── fetch-guidelines.py       # Stdlib-only web fetcher
│   └── agents/
│       └── catalog-inspector.md      # Optional: deep entity inspection
│
├── docs/
│   ├── IGNITER-PLAN.md               # Original architecture plan
│   ├── CLAUDE-MD-SOTA-PLAN.md        # Original /refresh-guidelines plan
│   ├── CLAUDE-MD-SOTA.md        # Authoritative CLAUDE.md generation reference
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md         # Sprint-based development plan
│   └── guidelines-raw.json           # Output of fetch-guidelines.py (gitignored)
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

### Operational Model

The Project Igniter is a **standalone external tool** — it lives on your filesystem independently from any target project. It is never part of the projects it provisions. Two separate `.claude/` directories and two separate `CLAUDE.md` files are involved:

| | Igniter (this repo) | Target project |
|---|---|---|
| **Location** | e.g. `~/tools/claude-code-project-igniter/` | e.g. `~/projects/my-new-app/` |
| **`.claude/`** | Contains `/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines` skills, `catalog-inspector` agent, build/sync scripts | Populated by `/ignite` with specialized agents, skills, hooks tailored to the project's tech stack |
| **`CLAUDE.md`** | Instructions for working on the igniter itself | Generated by `/ignite` — behavioral rules, domain-specific rules, installed entity registry, gap report |

### Workflow

**1. One-time setup** (performed once on the igniter repo)

```
Clone igniter repo to a permanent location (e.g. ~/tools/)
→ run /sync-catalog
→ remote sources cloned into catalog/sources/
→ manifest.json generated from all discovered entities
```

**1b. Guidelines enrichment** (on-demand, recommended before first ignition)

```
→ run /refresh-guidelines
→ fetch-guidelines.py collects content from curated web sources
→ Claude classifies, deduplicates, and proposes enrichments
→ Human approves → CLAUDE-MD-SOTA.md updated
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
→ target project's CLAUDE.md generated/updated (per CLAUDE-MD-SOTA.md)
→ gap report surfaced for uncovered technologies
```

---

## 4. Key Components

### 4.1 Source Registry (`catalog/sources.json`)

Defines where entities come from. Each source has: `id`, `url`, `branch`, `pin` (optional version lock), `priority` (lower = higher precedence), `entityPaths` (maps entity types to directories in the source repo).

Primary source: `everything-claude-code` (priority 10). Local custom entities: `local` (priority 1, always wins).

### 4.2 Manifest (`catalog/manifest.json`)

Auto-generated by `build-manifest.py`. Contains every entity with:
- **Composite ID**: `{source}::{type}::{name}` (e.g., `everything-claude-code::agent::code-reviewer`)
- **Tags**: `languages[]`, `frameworks[]`, `categories[]`, `scope` (universal/language-specific/framework-specific)
- **`coreEntity`**: boolean — always installed regardless of tech stack
- **`requiresAdaptation`**: boolean — needs specialization during install
- **Type-specific metadata**: agent model/tools, skill structure, hook events/matchers
- **Coverage summary**: aggregated list of all languages, frameworks, categories covered

Tags are auto-classified by the manifest builder using keyword analysis of entity names, descriptions, and content.

### 4.3 The `/ignite` Skill

**6-step procedure:**

| Step | Action |
|------|--------|
| **1. Read context** | Scan CLAUDE.md, conversation history, and project files (package.json, pyproject.toml, go.mod, docker-compose.yml, etc.) to build a Technology Profile |
| **2. Read manifest** | Load `catalog/manifest.json`. Warn if stale (>30 days) |
| **3. Select entities** | Core entities (always) + language-matched + framework-matched + category-based (Claude's judgment). Individual hook selection. Exclude irrelevant entities |
| **4. Present selection** | Structured report: what's selected and why, what's excluded, gap analysis. User can add/remove before proceeding |
| **5. Install & specialize** | Copy entities to project's `.claude/`, adapt descriptions/examples/paths/tools to the specific tech stack. Add provenance headers. Merge hooks into settings.json. Handle rules via CLAUDE.md embedding or agent prompt injection |
| **6. Update CLAUDE.md** | Generate per `docs/CLAUDE-MD-SOTA.md` — document installed entities, active hooks, and known gaps |

### 4.4 Specialization Mechanism

Claude adapts entities intelligently (not template-based):
- **Agents**: Update descriptions with project-specific trigger contexts, adjust domain references
- **Skills**: Swap code examples to project's framework, update file paths, remove irrelevant sections
- **Commands→Skills**: Convert to proper skills, update build/test commands to project's package manager
- **Rules**: Filter to relevant language, embed in CLAUDE.md or agent prompts (rules can only live at `~/.claude/rules/` user-level, so project-level alternatives are used)
- **Hooks**: Adjust file pattern matchers, tool paths (e.g., `npx prettier` → `ruff format`)

**Constraints**: Preserve core purpose, never remove security content, additive over subtractive, mark with provenance.

### 4.5 Gap Analysis

Three coverage levels:
- **Full**: Dedicated entity exists for the technology
- **Partial**: Parent-language entity covers basics but no dedicated entity
- **None**: No coverage at all

Report includes: what exists, what's missing, impact assessment, and actionable recommendations (inline in CLAUDE.md, create custom skill, add source, request upstream).

### 4.6 Core vs Catalog Split

**Always installed (core):**
- Agents: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `build-error-resolver`
- Skills: `tdd-workflow`, `coding-standards`, `verification-loop`, `security-review`
- Commands: `plan`, `tdd`, `code-review`, `build-fix`, `verify`
- Rules: `common/`

**Selectively installed (catalog):** Everything else — language-specific agents/reviewers, framework-specific skills (Django, Spring Boot, Go, etc.), utility skills, hooks, orchestration commands.

### 4.7 The `/refresh-guidelines` Skill

A **curated hybrid** approach combining tiered source registry + automated fetching + Claude-driven semantic merge + human approval.

**Why a separate skill** (not part of `/sync-catalog`):
- `/sync-catalog` handles entity synchronization (git repos). Guidelines enrichment is a different concern (web content curation).
- One-concern-per-skill aligns with existing project patterns.
- Guidelines refresh is infrequent (monthly or on-demand), unlike catalog sync.

**Skill directory structure:**

```
.claude/skills/refresh-guidelines/
├── SKILL.md                          # Skill entrypoint
├── references/
│   ├── curated-sources.md            # Registry of authoritative URLs (tiered)
│   └── enrichment-procedure.md       # Merge/dedup/conflict algorithm for Claude
└── scripts/
    └── fetch-guidelines.py           # Stdlib-only fetcher (urllib, html.parser, json)
```

**Execution procedure:**
1. Run `fetch-guidelines.py` to collect raw content from curated sources.
2. Read `docs/guidelines-raw.json` output.
3. Read current `docs/CLAUDE-MD-SOTA.md`.
4. Per theme section: classify incoming blocks (duplicate/novel/reinforcing/conflicting).
5. Produce enrichment report showing all proposed changes.
6. Present report for human approval.
7. On approval: update CLAUDE-MD-SOTA.md with approved changes.
8. Update Source Attribution section.

#### 4.7.1 Curated Sources — Tiered Registry

| Tier | Description | Conflict precedence |
|------|-------------|---------------------|
| **Tier 1** | Official Anthropic docs (code.claude.com, claude.com/blog) | Highest — always wins |
| **Tier 2** | Established community guides (HumanLayer, Builder.io, Dometrain, Tembo, Arize) | Medium |
| **Tier 3** | Community templates & examples (GitHub repos, blog posts) | Lowest |

Each entry includes: source name, URL, theme tags (structural, content, anti-patterns, integration, maintenance), last-verified date.

Initial sources:
- **T1**: code.claude.com/docs/en/memory, code.claude.com/docs/en/best-practices, claude.com/blog/using-claude-md-files
- **T2**: humanlayer.dev, builder.io, dometrain.com, tembo.io, arize.com guides
- **T3**: ruvnet/claude-flow templates, abhishekray07/claude-md-templates, awesome-claude-code repos

#### 4.7.2 `fetch-guidelines.py` — Content Fetcher

- **Input**: reads `curated-sources.md` to extract URLs + theme tags.
- **Output**: writes `docs/guidelines-raw.json` with structured content blocks.
- Python 3.10+, stdlib only (`urllib.request`, `json`, `re`, `html.parser`, `pathlib`, `datetime`).
- Fault-tolerant: skips failed URLs with warnings, produces partial results.
- Follows redirects. Handles both HTML (strip tags) and raw markdown (GitHub).
- Assigns theme tags from the curated-sources entry + keyword auto-tagging.

Output schema per entry:
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

#### 4.7.3 Enrichment Procedure — Semantic Merge Algorithm

**Phase 1 — Classification**: For each incoming content block, compare against existing CLAUDE-MD-SOTA.md guidelines and classify as:
- `duplicate` — already covered → skip, note in report
- `novel` — new information → propose insertion at correct section
- `reinforcing` — adds nuance to existing guideline → propose merge, cite both sources
- `conflicting` — contradicts existing guideline → flag for human review, recommend higher-tier source

**Phase 2 — Conflict Resolution**:
- Higher-tier sources win by default (T1 > T2 > T3)
- Conflicts are never auto-resolved — always presented for human decision
- Report format: table of all changes (added/merged/skipped/flagged)

**Phase 3 — Integration**:
- Claude proposes updated CLAUDE-MD-SOTA.md
- Human reviews diff and approves/edits
- Source Attribution section updated with URLs + dates

---

## 5. CLAUDE-MD-SOTA.md as Authoritative Reference

### Current State

`docs/CLAUDE-MD-SOTA.md` currently holds ~57 lines: 4 core behavioral rules, 5 domain-specific conditional rule blocks, and a brief "How These Rules Are Applied" section. It serves as a rule source for `/ignite` but lacks structural standards, content guidelines, integration guidance, and maintenance advice.

### Target: 7-Part Structure

Transform into a comprehensive reference (under 300 lines):

```
# CLAUDE.md Lifecycle Guidelines

## Purpose & Scope
  Role of this document, how /ignite consumes it

## Part 1: Structural Standards
  1.1 Size Constraints (target <80 lines, hard max 300, ~150 instruction limit)
  1.2 Recommended Sections (in order: overview, tech stack, commands, structure,
      conventions, workflow, domain terms, installed entities, gap report)
  1.3 File Hierarchy Strategy (CLAUDE.md, CLAUDE.local.md, .claude/rules/,
      child directories, @imports)
  1.4 Formatting Rules (bullets > prose, specific > vague, headings for scan)

## Part 2: Content Guidelines
  2.1 What to Include (non-obvious commands, architectural decisions, gotchas,
      domain terms, env quirks)
  2.2 What to Exclude (linter rules, standard conventions, stale code snippets,
      task-specific instructions, secrets, personality, generic advice)
  2.3 Anti-Patterns (kitchen sink, over-specification, @-mention abuse,
      auto-generated without curation)

## Part 3: Integration Guidelines
  3.1 Hooks vs CLAUDE.md (hooks = mandatory/deterministic, CLAUDE.md = advisory)
  3.2 Skills vs CLAUDE.md (skills = task-specific on-demand, CLAUDE.md = universal)
  3.3 Rules Directory (.claude/rules/ for modular topic-specific rules)

## Part 4: Behavioral Rules (always embedded — preserved verbatim)
  1. Write-first, never chat-first
  2. No preemptive execution
  3. No scope creep
  4. Clarify before acting

## Part 5: Domain-Specific Conditional Rules (preserved verbatim)
  General Conventions, Document Validation, Task Management,
  Docker/Infrastructure, Grant Proposal Documents

## Part 6: Maintenance Guidelines
  6.1 Review cadence (on recurring mistakes, on tech stack changes)
  6.2 Self-improving pattern (abstract mistake → add rule → verify)
  6.3 Versioning (git-tracked, team-reviewed)

## Part 7: Source Attribution
  Authoritative sources with URLs and last-verified dates

## How /ignite Uses This Document
  Mapping: which parts → which sections of generated CLAUDE.md
```

Key principles:
- Parts 4 & 5 are **preserved verbatim** — no content changes to existing rules.
- Parts 1-3 & 6 are **new**, populated from web research via `/refresh-guidelines`.
- Part 7 provides **traceability** for all guideline sources.
- Total length target: under 300 lines (use @import references for detailed subsections if needed).

### How `/ignite` Consumes the Enriched Document

| CLAUDE-MD-SOTA.md Part | /ignite Usage |
|-----------------------------|---------------|
| Part 1: Structural Standards | Determines CLAUDE.md skeleton — sections, order, size budget |
| Part 2: Content Guidelines | Decides what goes in each section (e.g., linter rules → hooks, not CLAUDE.md) |
| Part 3: Integration Guidelines | Decides what goes where — CLAUDE.md vs hooks vs skills vs .claude/rules/ |
| Part 4: Behavioral Rules | Embedded verbatim in `## Behavioral Rules` section |
| Part 5: Domain-Specific Rules | Conditionally embedded based on detected project characteristics |
| Part 6: Maintenance Guidelines | Brief `## Maintenance` section or @import reference |

---

## 6. Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| **1** | `catalog/sources.json` | Source registry with primary source definition |
| **1.5** | `/refresh-guidelines` skill | Curated sources registry, fetch script, enrichment procedure, restructured CLAUDE-MD-SOTA.md |
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

**Phase 1.5 rationale**: Having the enriched CLAUDE-MD-SOTA.md early means all subsequent sprint work (especially Phase 5's `/ignite` and its reference docs) aligns with it from the start. Estimated effort: 1-2 sessions.

---

## 7. Installation Options (for end users)

1. **`--add-dir` flag** (recommended): `claude --add-dir ~/tools/claude-code-project-igniter` — makes skills available per-session
2. **Symlinks to `~/.claude/skills/`**: Makes `/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines` globally available
3. **Shell alias**: `alias claude-ignite='claude --add-dir ~/tools/claude-code-project-igniter'`

---

## 8. Files to Create/Modify

| File | Action |
|------|--------|
| `.claude/skills/refresh-guidelines/SKILL.md` | **Create** — skill entrypoint |
| `.claude/skills/refresh-guidelines/references/curated-sources.md` | **Create** — tiered URL registry |
| `.claude/skills/refresh-guidelines/references/enrichment-procedure.md` | **Create** — merge algorithm reference |
| `.claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` | **Create** — stdlib-only web fetcher |
| `docs/CLAUDE-MD-SOTA.md` | **Restructure** — expand from ~57 lines to 7-part reference |
| `docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md` | **Modify** — insert Sprint 1.5 |
| `CLAUDE.md` | **Modify** — add `/refresh-guidelines` to project structure |

---

## 9. Verification Plan

### Igniter Core
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
8. CLAUDE-MD-SOTA.md restructured into 7 parts with substantive content in Parts 1-3, 6.
9. Parts 4-5 preserved verbatim from original.
10. Part 7 lists all sources with URLs and verification dates.
11. Enrichment report correctly classifies at least one duplicate, one novel, one reinforcing item.
12. No conflicting information merged without human review.
13. Document stays under 300 lines.

---

## 10. Risks & Mitigations

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
