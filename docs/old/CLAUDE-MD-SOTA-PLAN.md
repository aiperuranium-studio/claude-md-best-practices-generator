# Plan: `/refresh-guidelines` Skill & CLAUDE-MD-SOTA.md Enrichment

> **Archived.** This document has been merged into the [unified plan](../IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md) together with [IGNITER-PLAN.md](IGNITER-PLAN.md). See the [development agenda](../IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md) for the current sprint plan. Kept for historical reference only.

## Context

[`docs/CLAUDE-MD-SOTA.md`](../CLAUDE-MD-SOTA.md) currently holds only 4 behavioral rules and a few domain-specific conditional rules. But its intended role in the `/ignite` pipeline is much larger: it should be the **authoritative reference** that governs how target project CLAUDE.md files are structured, what content they include/exclude, how they integrate with hooks/skills/rules, and how they're maintained over time.

Web research reveals a rich body of CLAUDE.md best practices (from official Anthropic docs, established community guides, and templates) that are not yet captured in this document. The user wants a repeatable procedure to harvest these guidelines, deduplicate them, detect conflicts, and merge them into CLAUDE-MD-SOTA.md — so that `/ignite` can generate higher-quality, standards-compliant CLAUDE.md files.

## Approach: New `/refresh-guidelines` Skill (Curated Hybrid)

Create a new skill that combines **curated source registry** + **automated fetching** + **Claude-driven semantic merge**.

Why a separate skill (not part of `/sync-catalog`):
- `/sync-catalog` handles entity synchronization (git repos). Guidelines enrichment is a different concern (web content curation).
- One-concern-per-skill aligns with existing project patterns.
- Guidelines refresh is infrequent (monthly or on-demand), unlike catalog sync.

Why curated hybrid (not pure scraping or pure manual):
- **Curated source list** avoids scraping random sites — only verified, high-quality URLs.
- **Python fetcher** handles mechanical HTTP + text extraction (stdlib only).
- **Claude** handles semantic dedup/conflict detection (judgment-based, not algorithmic).
- **Human** approves the final merge (quality gate).

## Sprint Placement: Sprint 1.5 (between Catalog Foundation and Catalog Sync Pipeline)

Rationale: having the enriched CLAUDE-MD-SOTA.md early means all subsequent sprint work (especially Sprint 5's `/ignite` and its reference docs) aligns with it from the start. Estimated effort: 1-2 sessions.

## Deliverables

### 1. Directory Structure

```
.claude/skills/refresh-guidelines/
├── SKILL.md                          # Skill entrypoint
├── references/
│   ├── curated-sources.md            # Registry of authoritative URLs (tiered)
│   └── enrichment-procedure.md       # Merge/dedup/conflict algorithm for Claude
└── scripts/
    └── fetch-guidelines.py           # Stdlib-only fetcher (urllib, html.parser, json)
```

### 2. `curated-sources.md` — Tiered Source Registry

A markdown table listing URLs organized by authority tier:

| Tier | Description | Conflict precedence |
|------|-------------|---------------------|
| **Tier 1** | Official Anthropic docs (code.claude.com, claude.com/blog) | Highest — always wins |
| **Tier 2** | Established community guides (HumanLayer, Builder.io, Dometrain, Tembo, Arize) | Medium |
| **Tier 3** | Community templates & examples (GitHub repos, blog posts) | Lowest |

Each entry includes: source name, URL, theme tags (structural, content, anti-patterns, integration, maintenance), last-verified date.

Initial sources (from web research):
- **T1**: code.claude.com/docs/en/memory, code.claude.com/docs/en/best-practices, claude.com/blog/using-claude-md-files, Anthropic internal guide PDF
- **T2**: humanlayer.dev, builder.io, dometrain.com, tembo.io, arize.com guides
- **T3**: ruvnet/claude-flow templates, abhishekray07/claude-md-templates, awesome-claude-code repos

### 3. `fetch-guidelines.py` — Content Fetcher

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

### 4. `enrichment-procedure.md` — Merge Algorithm Reference

Defines the procedure Claude follows during `/refresh-guidelines` execution:

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

### 5. `SKILL.md` — `/refresh-guidelines` Entrypoint

Procedure:
1. Run `fetch-guidelines.py` to collect raw content from curated sources.
2. Read `docs/guidelines-raw.json` output.
3. Read current `docs/CLAUDE-MD-SOTA.md`.
4. Per theme section: classify incoming blocks (duplicate/novel/reinforcing/conflicting).
5. Produce enrichment report showing all proposed changes.
6. Present report for human approval.
7. On approval: update CLAUDE-MD-SOTA.md with approved changes.
8. Update Source Attribution section.

### 6. Restructured [`docs/CLAUDE-MD-SOTA.md`](../CLAUDE-MD-SOTA.md)

Transform from a 4-rule behavioral doc into a 7-part authoritative reference:

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

Key principles for the restructuring:
- Parts 4 & 5 are **preserved verbatim** — no content changes to existing rules.
- Parts 1-3 & 6 are **new**, populated from web research via `/refresh-guidelines`.
- Part 7 provides **traceability** for all guideline sources.
- Total length target: under 300 lines (use @import references for detailed subsections if needed).

## How `/ignite` Consumes the Enriched Document

| CLAUDE-MD-SOTA.md Part | /ignite Usage |
|-----------------------------|---------------|
| Part 1: Structural Standards | Determines CLAUDE.md skeleton — sections, order, size budget |
| Part 2: Content Guidelines | Decides what goes in each section (e.g., linter rules → hooks, not CLAUDE.md) |
| Part 3: Integration Guidelines | Decides what goes where — CLAUDE.md vs hooks vs skills vs .claude/rules/ |
| Part 4: Behavioral Rules | Embedded verbatim in `## Behavioral Rules` section |
| Part 5: Domain-Specific Rules | Conditionally embedded based on detected project characteristics |
| Part 6: Maintenance Guidelines | Brief `## Maintenance` section or @import reference |

## Files to Create/Modify

| File | Action |
|------|--------|
| `.claude/skills/refresh-guidelines/SKILL.md` | **Create** |
| `.claude/skills/refresh-guidelines/references/curated-sources.md` | **Create** |
| `.claude/skills/refresh-guidelines/references/enrichment-procedure.md` | **Create** |
| `.claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` | **Create** |
| [`docs/CLAUDE-MD-SOTA.md`](../CLAUDE-MD-SOTA.md) | **Restructure** (expand from ~57 lines to 7-part reference) |
| [`docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`](../IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md) | **Modify** (insert Sprint 1.5) |
| [`docs/IGNITER-PLAN.md`](IGNITER-PLAN.md) | **Modify** (add `/refresh-guidelines` skill, update CLAUDE-MD-SOTA.md role description) |
| `CLAUDE.md` | **Modify** (add `/refresh-guidelines` to project structure) |

## Verification

1. `/refresh-guidelines` skill is invocable and Claude discovers it.
2. `fetch-guidelines.py` fetches content from at least Tier 1 sources without errors.
3. `docs/guidelines-raw.json` produced with valid JSON and themed content blocks.
4. CLAUDE-MD-SOTA.md restructured into 7 parts with substantive content in Parts 1-3, 6.
5. Parts 4-5 preserved verbatim from original.
6. Part 7 lists all sources with URLs and verification dates.
7. Enrichment report correctly classifies at least one duplicate, one novel, one reinforcing item.
8. No conflicting information merged without human review.
9. Document stays under 300 lines.

## Risks

| Risk | Mitigation |
|------|------------|
| Fetched web content structure changes | Defensive parsing with fallbacks; curated-sources records expected format |
| CLAUDE-MD-SOTA.md becomes too long | Use @import references for detailed subsections; keep main doc as structured index |
| Sources genuinely conflict | Enrichment procedure classifies conflicts explicitly, escalates to human; tier determines default |
| URL changes/redirects | `fetch-guidelines.py` follows redirects; curated-sources updated when URLs change |
| Network failures during fetch | Fault-tolerant: skip failed URLs, produce partial results, report errors |