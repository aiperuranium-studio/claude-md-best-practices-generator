# Release Notes — v3.2

**Date**: 2026-03-05
**Sprints covered**: 1, 2, 3

---

## Overview

Structural refactor to promote project-owned skills and rules out of `.claude/` and into first-class repository directories (`skills/`, `rules/`). Includes a full README expansion covering all three skills, a tightened `claude-md-standards.md` rule with YAML frontmatter, path corrections across all tests and source references, and a fresh pass of architecture documentation via `/update-codemaps`. No changes to script logic or skill behaviour.

---

## Sprint 1: README Expansion

Updated `README.md` to document all three skills end-to-end. Previously the README only described `/refresh-guidelines`.

### Delivered

- **`README.md`** — Four additions:
  - **Quick Start steps 4–5**: Added `/refactor-claude-md` and `/scaffold-claude-md` commands with commentary, completing the three-step workflow (`/refresh-guidelines` → `/refactor-claude-md` → `/scaffold-claude-md`).
  - **Skill descriptions**: Added prose blocks for `/refactor-claude-md` (audit → compliance report → rewrite) and `/scaffold-claude-md` (scan → draft → write) matching the style of the existing `/refresh-guidelines` description.
  - **Skills Reference table**: Expanded from 1 to 3 rows; `/refactor-claude-md` and `/scaffold-claude-md` added with direct and plugin-mode invocations.
  - **Plugin install URL fix**: Corrected `claude plugin marketplace add` argument from bare GitHub shorthand to full `https://github.com/aiperuranium-studio/claude-md-best-practices-generator` URL.

---

## Sprint 2: Project Structure Refactor

Moved project-developed skills and the project-developed rule out of `.claude/` (Claude Code internal directory) and into explicit top-level repository directories, separating them clearly from ECC-installed (external) content.

### Delivered

- **`skills/`** (new top-level directory) — All three project-owned skills relocated:
  - `skills/refresh-guidelines/` ← `.claude/skills/refresh-guidelines/`
  - `skills/refactor-claude-md/` ← `.claude/skills/refactor-claude-md/`
  - `skills/scaffold-claude-md/` ← `.claude/skills/scaffold-claude-md/`
  - No content changes — renames only.

- **`rules/claude-md-standards.md`** ← `.claude/rules/claude-md-standards.md` — File moved and improved:
  - Added YAML frontmatter (`paths: ["**/CLAUDE.md", "**/CLAUDE.local.md"]`) so the rule auto-activates on CLAUDE.md edits.
  - Tightened prose: "ALWAYS load the current SOTA before creating or modifying any CLAUDE.md file" (imperative form, consistent with ECC rule style).
  - Removed redundant introductory sentence; renamed "Project Conventions (stable, not SOTA-derived)" → "Project Conventions".

- **`CLAUDE.md`** — Paths and structure table updated:
  - Common Commands: script paths corrected to `skills/refresh-guidelines/scripts/` (removed `.claude/` prefix).
  - Project Structure table: `skills/refresh-guidelines/`, `skills/refactor-claude-md/`, `skills/scaffold-claude-md/` rows updated; `rules/` row added for project-developed rule; `.claude/rules/` row added for ECC-installed rules (gitignored).

- **`.gitignore`** — Updated to gitignore `.claude/rules/` and `.claude/skills/` (ECC-installed content) while tracking `rules/` and `skills/` (project-developed content).

- **`tests/test_refactor_scaffold_skills.py`** — All path constants updated:
  - `REFACTOR_SKILL_DIR`, `SCAFFOLD_SKILL_DIR` → `PROJECT_ROOT / "skills" / …`
  - `RULES_FILE` → `PROJECT_ROOT / "rules" / "claude-md-standards.md"`
  - Docstring and class docstring references updated to reflect new paths.
  - Test assertions for `CLAUDE.md` project structure updated to match new path strings.

- **`tests/test_sprint1_5_guidelines_enrichment.py`** — All path constants updated:
  - `SCRIPT_PATH`, `PARSE_INSIGHTS_PATH`, `SKILL_MD`, `CURATED_SOURCES_MD`, `ENRICHMENT_PROCEDURE_MD` → `PROJECT_ROOT / "skills" / "refresh-guidelines" / …` (`.claude/` segment removed).

- **`.claude-plugin/plugin.json`** — Skill paths corrected:
  - `"./skills/refresh-guidelines/"`, `"./skills/refactor-claude-md/"`, `"./skills/scaffold-claude-md/"` (previously pointed into `.claude/skills/`).

- **`.claude-plugin/CLAUDE.md`** and **`PLUGIN_SCHEMA_NOTES.md`** — Minor prose corrections.

---

## Sprint 3: Architecture Docs Regeneration

Ran `/everything-claude-code:update-codemaps` and `/everything-claude-code:update-docs` to sync documentation with the restructured codebase.

### Delivered

- **`docs/CODEMAPS/architecture.md`** — Full regeneration (2026-03-01 → 2026-03-05):
  - Data flow diagram updated: shows all three skills as downstream consumers of `docs/CLAUDE-MD-SOTA.enriched.md`.
  - Entry points table expanded to cover all three skills in both direct and plugin modes.
  - Key directories tree updated: `skills/` directory with three subdirectories; `rules/` directory added; test file list updated to include `test_refactor_scaffold_skills.py`.
  - File count: 18 → 24; token estimate: ~600 → ~900.

- **`docs/CODEMAPS/dependencies.md`** — Freshness date bumped (2026-03-01 → 2026-03-05); no dependency changes.

- **`pyproject.toml`** and **`.claude-plugin/plugin.json`** — Version bumped to `3.2.0`.

---

## Post-Sprint Notes

`.claude/skills/` and `.claude/rules/` remain in place as the installation target for ECC (Everything Claude Code) external skills and rules. They are now gitignored — their contents are managed by `/everything-claude-code:configure-ecc`, not by this project's source. This session also ran `/configure-ecc` to update all installed ECC skills and rules to their latest versions.

All test path constants now resolve against `skills/` and `rules/` at the repo root. Running `.venv/bin/pytest tests/ -v` passes cleanly against the restructured layout.

---

## Known Limitations

- **Enriched file not shared** — `CLAUDE-MD-SOTA.enriched.md` is gitignored. Team members each need to run `/refresh-guidelines` locally to produce their enriched version from their own `/insights` report.
- **Compliance audit is manual** — The `/refactor-claude-md` audit (Step 3) is LLM-driven with no automated test. A future sprint could add pytest checks validating structural properties of the root CLAUDE.md.
- **Scaffold idempotency not tested** — Re-running `/scaffold-claude-md` should detect existing CLAUDE.md files and skip them; this is by design but not covered by any automated test.

---

## What's Next

| Area | Description |
|------|-------------|
| Test: compliance audit assertions | Add pytest checks: root CLAUDE.md section presence, line count within budget, IMPORTANT keyword usage |
| Periodic guidelines refresh | Re-run `/refresh-guidelines` as Anthropic documentation evolves to keep `CLAUDE-MD-SOTA.md` current |
| Apply `/refactor-claude-md` to scoped files | Verify child-directory CLAUDE.md files comply with updated SOTA |
| Publish v3.2 plugin | Run `claude plugin validate` and push updated `plugin.json` to marketplace |
