# Implementation Plan: Making the CLAUDE.md Best Practices Generator a Claude Code Plugin

**Date:** 2026-03-01 **Status:** Draft — awaiting user confirmation

---

## 1. Requirements Restatement

**What is a Claude Code plugin?**

A Claude Code plugin is a self-contained directory bundling any combination of skills (slash commands), custom agents, hooks, MCP servers, LSP servers, and default settings. Plugins are identified by a `.claude-plugin/plugin.json` manifest at the plugin root. Skills inside a plugin are namespaced: a plugin named `claude-md-best-practices` with a skill `refresh-guidelines` becomes `/claude-md-best-practices:refresh-guidelines`. Plugins are installable via `claude plugin install <name>@<marketplace>`.

**What the current project does:**

The project is already partially plugin-compatible. It uses the `--add-dir` installation model: users clone the repo and run `claude --add-dir ~/claude-md-best-practices`. This loads `.claude/skills/refresh-guidelines/` and makes `/refresh-guidelines` available. The pipeline consists of:

- Python scripts (`fetch-guidelines.py`, `parse-insights.py`) that fetch and parse data.
- A 10-step skill procedure defined in `SKILL.md` that Claude follows interactively.
- Reference files (`curated-sources.md`, `enrichment-procedure.md`) consulted during the procedure.
- Two output files (`CLAUDE-MD-SOTA.md` tracked, `CLAUDE-MD-SOTA.enriched.md` gitignored).

The existing `.claude/skills/refresh-guidelines/` directory maps almost directly onto the `skills/refresh-guidelines/` structure required inside a plugin. The missing piece is the `.claude-plugin/plugin.json` manifest and a few structural adjustments.

---

## 2. Current State Analysis

| Component | Current path | Plugin-compatible? |
|-----------|-------------|-------------------|
| Skill definition | `.claude/skills/refresh-guidelines/SKILL.md` | Yes — maps directly |
| Skill scripts | `.claude/skills/refresh-guidelines/scripts/` | Yes — maps directly |
| Skill references | `.claude/skills/refresh-guidelines/references/` | Yes — maps directly |
| Skill CLAUDE.md | `.claude/skills/refresh-guidelines/CLAUDE.md` | Dev instruction only; not plugin content |
| Rules | `.claude/rules/` | Dev rules; not plugin components |
| Agents dir | `.claude/agents/` (empty) | Nothing to migrate |
| Settings/hooks | `.claude/settings.json` | Dev utility hooks; not plugin features |
| Python scripts | stdlib only, no deps | Good — no packaging complications |
| Tests | `tests/` | Stay in repo root; not bundled in plugin |
| Seed doc | `docs/CLAUDE-MD-SOTA.md` | Stays in repo; skill writes to user's `docs/` |

**Current SKILL.md gap:** The `refresh-guidelines/SKILL.md` has no YAML frontmatter block, meaning Claude Code derives the name from the directory (acceptable) but has no description and no `disable-model-invocation` guard.

---

## 3. Gap Analysis

| Gap | Description | Priority |
|-----|-------------|----------|
| **Gap 1** | Missing `.claude-plugin/plugin.json` manifest | CRITICAL |
| **Gap 2** | SKILL.md missing YAML frontmatter (name, description, `disable-model-invocation: true`) | HIGH |
| **Gap 3** | Script path resolution breaks inside plugin cache (`Path(__file__).parent.parents[3]` walks to wrong root) | HIGH |
| **Gap 4** | SKILL.md procedure calls scripts with hardcoded `.claude/skills/...` paths | HIGH |
| **Gap 5** | No marketplace registry for distribution | MEDIUM |
| **Gap 6** | README has no "Plugin Installation" section | MEDIUM |
| **Gap 7** | Namespace change from `/refresh-guidelines` to `/claude-md-best-practices:refresh-guidelines` breaks existing `--add-dir` users | LOW |
| **Gap 8** | Tests don't cover new `--docs-dir` flag or plugin manifest validation | LOW |

---

## 4. Implementation Phases

### Phase 0: Architectural Decision

**Decision: Repo root becomes the plugin root (Option A).**

The plugin manifest's `skills` field can reference `"./.claude/skills/"` so no files need to move. Tests, docs, and dev infrastructure remain in place. The plugin and the dev project coexist in the same repo. This has zero churn to existing file paths and keeps `--add-dir` users unaffected.

### Phase 1: Add Plugin Manifest (Gap 1)

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "claude-md-best-practices",
  "version": "3.0.0",
  "description": "Enriches CLAUDE.md generation guidelines from curated web sources and /insights behavioral data. Provides /claude-md-best-practices:refresh-guidelines.",
  "author": {
    "name": "<author>",
    "url": "https://github.com/<author>/claude-md-best-practices-generator"
  },
  "repository": "https://github.com/<author>/claude-md-best-practices-generator",
  "license": "MIT",
  "keywords": ["claude-md", "best-practices", "guidelines", "anthropic"],
  "skills": "./.claude/skills/"
}
```

**Manual test gate:** Run `claude --plugin-dir .` and verify `/claude-md-best-practices:refresh-guidelines` appears.

### Phase 2: Add SKILL.md Frontmatter (Gap 2)

Add YAML frontmatter to the top of `.claude/skills/refresh-guidelines/SKILL.md`:

```yaml
---
name: refresh-guidelines
description: Enriches CLAUDE.md generation guidelines from curated Anthropic docs, community guides, and /insights session data. Produces docs/CLAUDE-MD-SOTA.md (web sources) and docs/CLAUDE-MD-SOTA.enriched.md (/insights merged). Invoke explicitly; has file-write and network side effects.
disable-model-invocation: true
allowed-tools: Bash, Read, WebSearch, WebFetch, Write
---
```

Key decisions:
- `disable-model-invocation: true` — The 10-step procedure requires human approval at multiple gates (Step 8). Auto-invocation by Claude would be incorrect.
- `allowed-tools` — Scoped to what the skill genuinely needs.

### Phase 3: Fix Script Path Resolution (Gap 3)

Both scripts use `Path(__file__).resolve().parent.parents[3]` to locate the project root and write to `<project-root>/docs/`. In a plugin cache (`~/.claude/plugins/cache/<plugin-name>/`), this walks to the wrong directory.

**Fix:** Add `--docs-dir PATH` CLI argument to both scripts, defaulting to `Path.cwd() / "docs"`.

Script signature changes:
```
fetch-guidelines.py [--check-freshness] [--docs-dir PATH]
parse-insights.py [--docs-dir PATH]
```

### Phase 4: Update SKILL.md Procedure Paths (Gap 4)

Update all script references in `SKILL.md` from:
```bash
python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py
```
to:
```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/fetch-guidelines.py" --docs-dir docs
```

Also update `references/` file paths in the procedure text to use `$CLAUDE_PLUGIN_ROOT/references/` so Claude reads the plugin-local copies.

> **Note:** Verify that `$CLAUDE_PLUGIN_ROOT` is available in the environment when Claude runs Bash tool commands from a SKILL.md. If not, use a wrapper shell script at `scripts/run-fetch.sh` that resolves its own directory via `$(dirname "$0")`.

### Phase 5: Update Tests (Gap 8)

After Phase 3, update `tests/test_sprint1_5_guidelines_enrichment.py`:
- Update existing tests that check output paths to pass `--docs-dir <tmpdir>`.
- Add `test_fetch_guidelines_accepts_docs_dir_flag`.
- Add `test_parse_insights_accepts_docs_dir_flag`.
- Add `test_plugin_manifest_valid` — verifies `.claude-plugin/plugin.json` is valid JSON with required `name` field.
- Add `test_skill_md_has_frontmatter` — verifies SKILL.md starts with `---` YAML block containing `disable-model-invocation: true`.

### Phase 6: Add Marketplace Registry (Gap 5)

Create `.claude-plugin/marketplace.json` for community distribution:

```json
{
  "name": "claude-md-best-practices marketplace",
  "description": "CLAUDE.md best practices generator plugin",
  "plugins": [
    {
      "name": "claude-md-best-practices",
      "description": "Enriches CLAUDE.md guidelines from web sources and /insights data",
      "source": ".",
      "version": "3.0.0"
    }
  ]
}
```

Users install via:
```bash
claude plugin marketplace add <github-username>/claude-md-best-practices-generator
claude plugin install claude-md-best-practices
```

### Phase 7: Update README (Gap 6)

Add a "Plugin Installation" section to `README.md` explaining both installation modes:

- **Plugin mode:** `claude plugin install claude-md-best-practices` → invoke as `/claude-md-best-practices:refresh-guidelines`
- **Direct mode:** `claude --add-dir ./` → invoke as `/refresh-guidelines` (existing, unchanged)

Both coexist and use the same underlying `SKILL.md`.

### Phase 8: Update Developer Docs (Gap 7 mitigation)

Update root `CLAUDE.md` Common Commands section to include the plugin invocation form. Update `.claude/skills/refresh-guidelines/CLAUDE.md` to note the path differences between dev mode and plugin mode.

---

## 5. Risk Assessment

| Risk | Level | Impact | Mitigation |
|------|-------|--------|------------|
| Script path resolution breaks in plugin cache | HIGH | Silent wrong-directory output or crash | Phase 3 fix (add `--docs-dir`); covered by Phase 5 tests |
| `$CLAUDE_PLUGIN_ROOT` not available in Bash tool | MEDIUM | Script calls fail with empty path | Fallback: wrapper shell script that resolves `$(dirname "$0")` |
| Namespace change breaks `--add-dir` users | LOW | Muscle memory; both forms continue to work | Phase 7 README clearly documents both modes |
| Plugin manifest `skills` custom path not honoured | LOW | Skills not discovered by plugin runtime | Verify with `claude --plugin-dir .` in Phase 1 gate |
| Tests bundled in plugin cache (wasteful) | LOW | Cache size only; no correctness impact | Out of scope; add `.pluginignore` later if needed |

---

## 6. Implementation Sequencing

Execute in this order with testing gates between phases:

1. **Phase 3** — Script `--docs-dir` argument (correctness fix, independent)
2. **Phase 5** — Update/add tests (verify Phase 3 before proceeding)
3. **Phase 2** — SKILL.md frontmatter
4. **Phase 4** — SKILL.md procedure path updates (depends on Phase 3)
5. **Phase 1** — Add `plugin.json` manifest → **manual test gate**
6. **Phase 6** — Marketplace registry
7. **Phase 7** — README update
8. **Phase 8** — Developer docs update

---

## 7. Critical Files

| File | Change |
|------|--------|
| `.claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` | Add `--docs-dir` argument; fix path resolution |
| `.claude/skills/refresh-guidelines/scripts/parse-insights.py` | Add `--docs-dir` argument; fix path resolution |
| `.claude/skills/refresh-guidelines/SKILL.md` | Add YAML frontmatter; update script path references |
| `.claude-plugin/plugin.json` | **New file** — plugin manifest |
| `.claude-plugin/marketplace.json` | **New file** — marketplace registry |
| `tests/test_sprint1_5_guidelines_enrichment.py` | Add `--docs-dir` tests; add manifest/frontmatter validation tests |
| `README.md` | Add Plugin Installation section |
| `CLAUDE.md` | Add plugin invocation to Common Commands |

---

**WAITING FOR CONFIRMATION:** Proceed with this plan? Reply "yes" to start implementation, "modify: [changes]" to adjust, or "skip phase N" to reorder.
