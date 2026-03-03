# Release Notes — v3.1

**Date**: 2026-03-03
**Sprints covered**: 1, 2, 3

---

## Overview

First full enrichment-refactor-scaffold cycle run against the live project using all three skills added in v3.0. All three skills (`/refresh-guidelines`, `/refactor-claude-md`, `/scaffold-claude-md`) were executed in sequence in a single session, producing updated SOTA guidelines, a fully compliant root `CLAUDE.md`, and a new scoped `CLAUDE.md` for the plugin directory. No code logic changes — documentation and configuration only.

---

## Sprint 1: Refresh CLAUDE-MD-SOTA Guidelines

Ran `/refresh-guidelines` against all 10 curated web sources (all fresh and reachable) and the user's `/insights` report (0 days old, 35 sessions analyzed). Applied 5 approved changes to the guidelines files.

### Delivered

- **`docs/CLAUDE-MD-SOTA.md`** — Three targeted updates to the seed file:
  - **§3.5 Headless & Batch Mode**: Added `--output-format stream-json` flag for real-time streaming output when integrating `claude -p` with pipelines. Source: T1-002 (novel).
  - **§1.4 Formatting Rules**: Tightened size guidance — "ideal target: under 80 lines (beyond this, Claude starts deprioritizing parts); HumanLayer keeps theirs under 60 lines. Absolute max: 300 lines." Previously: vague "<300 lines max" upper bound only. Source: T3-002 (reinforcing).
  - **§2.3 Anti-Patterns**: Renamed "Blanket @-imports" to **"Flat context loading (Progressive Disclosure)"** and added cross-reference to §3.6. Explicitly names the principle for easier reference and cross-linking. Source: T2-001 (reinforcing/naming).
  - Source attribution dates updated to 2026-03-03 across all 9 source rows.

- **`docs/CLAUDE-MD-SOTA.enriched.md`** (new, gitignored) — Seed content plus two `/insights`-sourced additions:
  - **§4.8 Action-First Execution** (new section): For projects with structured sprints or explicit task scopes, instruct Claude to act immediately on write/execute requests rather than exploring extensively. Derived from `/insights` CLAUDE.md Recommendations (novel).
  - **§2.1 What to Include**: Added "Explicit tooling paths" bullet — name the virtual environment and invocation method (e.g., `.venv/bin/pytest` or `uv run pytest`); do not rely on Claude inferring the runner. Derived from `/insights` Friction Points (novel).

---

## Sprint 2: Refactor Root CLAUDE.md

Ran `/refactor-claude-md` against the seed enriched guidelines. Pre-audit: 16 pass, 5 partial, 4 fail, 11 N/A. All 9 proposed changes approved. Post-audit: 0 fail, 0 partial remaining (one intentional partial retained: Code Style section minimal, project-appropriate).

### Delivered

- **`CLAUDE.md`** (57 → 67 lines) — Nine changes applied:
  - **`## Gotchas & Known Issues`** (new section): Three bullets documenting `parse-insights.py`'s dependency on `~/.claude/usage-data/report.html`, the requirement to run scripts from the project root, and the `--docs-dir docs` standard argument pattern. Fixes FAIL F1 (§2.1 gotchas).
  - **Tech Stack**: Added "Scripts use Python stdlib only — run with system `python3` or `.venv/bin/python3`." Fixes FAIL F4 (§2.1 explicit tooling paths).
  - **Workflow Preferences — "Read before modifying"** (new bullet): "Read existing skill SKILL.md files and scripts before proposing changes." Fixes FAIL F3 (§4.2 Explore-Then-Plan).
  - **Workflow Preferences — "File discipline"** (new bullet): "Prefer editing existing files to creating new ones." Fixes PARTIAL P2 (§4.5 File Discipline).
  - **Workflow Preferences — "Maintenance"** (new bullet): Update trigger guidance, `CLAUDE.local.md` personal overrides mention, and self-improvement shortcut ("Update CLAUDE.md so you don't repeat that mistake"). Fixes FAIL F2 + PARTIAL P1 + PARTIAL P3 (§5.1 Review Triggers, §1.5 Placement, §5.2 Self-Improving Pattern).
  - **Project Structure — `.claude/rules/` row**: Extended description to "stable categorical rules; project-wide context stays in CLAUDE.md". Fixes PARTIAL P4 (§3.3 CLAUDE.md vs rules/).
  - **`## Installed Skills`** (new section): Skills list extracted from Common Commands into its own section, per §1.3 recommended section order (Installed Entities after Workflow Preferences). Common Commands now contains script invocations only. Fixes PARTIAL P5 (§1.3 Installed Entities).

---

## Sprint 3: Scaffold Plugin Directory

Ran `/scaffold-claude-md`. Scanned 15 directories; 10 skipped (covered by parents, trivially small, or ephemeral); 1 recommended.

### Delivered

- **`.claude-plugin/CLAUDE.md`** (new, 35 lines) — Scoped instructions for the plugin manifest directory:
  - **Purpose**: 2-sentence description of directory contents.
  - **Key Files**: Table mapping `plugin.json`, `marketplace.json`, `PLUGIN_SCHEMA_NOTES.md`, `README.md` to their roles.
  - **Before Editing `plugin.json`**: Critical validator constraints (arrays required for all component fields; agents need explicit file paths; skills/commands use directory paths; paths resolve from repo root; `version` required; no `hooks` field).
  - **Validation command**: `claude plugin validate .claude-plugin/plugin.json`.
  - **Installation sequence**: `plugin marketplace add` → `plugin install` (direct URL install fails).

---

## Post-Sprint Notes

The root `CLAUDE.md` Project Structure table already had a `.claude-plugin/` row and a general "Each subdirectory has its own scoped CLAUDE.md" statement — no update required after scaffold.

`docs/CLAUDE-MD-SOTA.enriched.md` is gitignored and user-local. It must be regenerated each session via `/refresh-guidelines` to incorporate fresh `/insights` data.

---

## Known Limitations

- **Enriched file not shared** — `CLAUDE-MD-SOTA.enriched.md` is gitignored. Team members each need to run `/refresh-guidelines` locally to produce their enriched version from their own `/insights` report.
- **Compliance audit is manual** — The `/refactor-claude-md` audit (Step 3) is LLM-driven with no automated test. A future sprint could add a pytest check that validates structural properties of the root CLAUDE.md (sections present, line count, IMPORTANT keyword usage).
- **Scaffold idempotency not tested** — Re-running `/scaffold-claude-md` should detect existing CLAUDE.md files and skip them; this is by design but not covered by any automated test.

---

## What's Next

| Area | Description |
|------|-------------|
| Test coverage for refactor/scaffold outputs | Add pytest assertions: root CLAUDE.md section presence, line count within budget, `.claude-plugin/CLAUDE.md` existence |
| Periodic guidelines refresh | Re-run `/refresh-guidelines` as Anthropic documentation evolves to keep `CLAUDE-MD-SOTA.md` current |
| Regenerate `docs/CODEMAPS/` | Run `/everything-claude-code:update-codemaps` to reflect the updated project structure (new `.claude-plugin/CLAUDE.md`, refactored root) |
| `/refactor-claude-md` on scoped files | Apply `/refactor-claude-md` to existing child-directory CLAUDE.md files to verify they also comply with the updated SOTA |
