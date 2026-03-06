# Changelog

All notable changes to this project are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) — `Added`, `Changed`, `Removed`, `Fixed` subsections per release.

---

## [Unreleased]

---

## [3.3.0] — 2026-03-06

### Added
- **Sprint 1**: `tests/test_metadata_consistency.py` — 13 assertions verifying `plugin.json`, `marketplace.json`, and `pyproject.toml` version parity; `USER_AGENT` version sync; marketplace description covers all skills.
- **Sprint 1**: `setup.sh` — one-command dev environment setup (Python 3.10+ check, `.venv` creation, `uv`/`pip` install, smoke test).
- **Sprint 1**: `Makefile` — `setup`, `test`, `lint`, `fetch`, `freshness` targets wrapping existing commands.
- **Sprint 2**: `tests/fixtures/sample-source.html` — minimal HTML fixture for `HTMLTextExtractor` and `extract_content_blocks` tests.
- **Sprint 2**: `tests/fixtures/sample-report.html` — minimal `/insights` report fixture with all 7 section types.
- **Sprint 2**: `tests/fixtures/facets/sample.json`, `tests/fixtures/session-meta/sample.json` — JSON fixtures for `parse_facets()` and `parse_session_meta()`.
- **Sprint 2**: `tests/test_fetch_behavioral.py` — end-to-end behavioral tests for `fetch-guidelines.py`: `main()` with mocked HTTP, freshness check, edge cases, all fully offline.
- **Sprint 2**: `tests/test_insights_behavioral.py` — end-to-end behavioral tests for `parse-insights.py`: all 7 section types, graceful degradation, stale report detection.
- **Sprint 3**: "Scoped File Adjustments" section in `skills/refactor-claude-md/references/compliance-checklist.md` — scoped-file-specific audit rules.
- **Sprint 3**: `TestRefactorSkillScopedSupport` test class in `tests/test_refactor_scaffold_skills.py`.
- **Sprint 4**: `--dry-run` flag for `skills/refresh-guidelines/scripts/fetch-guidelines.py` — prints source summary without fetching or writing.
- **Sprint 4**: `TestDryRunMode` test class in `tests/test_fetch_behavioral.py` (5 tests).
- **Sprint 5**: T1-004 source (Claude Code GitLab CI/CD docs), T2-006/007/008 community guides in `curated-sources.md` — total 14 sources (up from 10).
- **Sprint 5**: `CHANGELOG.md` — replaces three individual release notes files.
- **Sprint 5**: `.github/workflows/ci.yml` — CI pipeline (push/PR: ruff check + pytest).
- **Sprint 5**: `.github/workflows/freshness-check.yml` — weekly cron freshness check; opens GitHub issue on BROKEN/STALE sources.

### Changed
- **Sprint 1**: `marketplace.json` version updated `3.0.0` → `3.2.0`; description extended to mention all three skills.
- **Sprint 1**: `fetch-guidelines.py` `USER_AGENT` reads version from `pyproject.toml` at import time instead of hardcoded `"3.0"`.
- **Sprint 3**: `skills/refactor-claude-md/SKILL.md` — Step 0.5 added for target path parameter; Step 3 updated for scoped-file expectations.
- **Sprint 3**: `skills/scaffold-claude-md/SKILL.md` — `--scan-only` mode documented (Sprint 4 delivery).
- **Sprint 4**: `skills/refresh-guidelines/SKILL.md` — optional Step -1 `--preview` mode documented.
- **Sprint 4**: `skills/refactor-claude-md/SKILL.md` — `--report-only` mode documented.
- **Sprint 4**: `skills/scaffold-claude-md/SKILL.md` — `--scan-only` mode documented.

### Removed
- **Sprint 5**: `RELEASE-NOTES-v3.0.md`, `RELEASE-NOTES-v3.1.md`, `RELEASE-NOTES-v3.2.md` — consolidated into this file.

---

## [3.2.0] — 2026-03-05

### Added
- `skills/` top-level directory — all three project-owned skills relocated from `.claude/skills/`.
- `rules/claude-md-standards.md` — relocated from `.claude/rules/`; added YAML frontmatter for auto-activation on CLAUDE.md edits.
- `.claude-plugin/CLAUDE.md` — scoped instructions for the plugin manifest directory.
- `docs/CODEMAPS/architecture.md`, `docs/CODEMAPS/dependencies.md` — regenerated via `/everything-claude-code:update-codemaps`.

### Changed
- `README.md` — Quick Start steps 4-5 added (`/refactor-claude-md`, `/scaffold-claude-md`); Skills Reference table expanded to 3 rows; plugin install URL corrected.
- `CLAUDE.md` — Common Commands paths corrected to `skills/refresh-guidelines/scripts/`; Project Structure table updated for new layout.
- `.claude-plugin/plugin.json` — skill paths corrected to `./skills/…`; version bumped to `3.2.0`.
- `.gitignore` — `.claude/rules/` and `.claude/skills/` gitignored (ECC-installed); `rules/` and `skills/` tracked (project-developed).
- `tests/test_refactor_scaffold_skills.py`, `tests/test_sprint1_5_guidelines_enrichment.py` — all path constants updated to `skills/` and `rules/`.

---

## [3.1.0] — 2026-03-03

### Added
- `docs/CLAUDE-MD-SOTA.enriched.md` (gitignored) — seed + `/insights` merged output; two novel sections: §4.8 Action-First Execution, §2.1 Explicit tooling paths.
- `CLAUDE.md §Gotchas & Known Issues` — three bullets for `parse-insights.py` dependency, project-root requirement, `--docs-dir` pattern.
- `CLAUDE.md §Installed Skills` — skills section extracted from Common Commands.
- `.claude-plugin/CLAUDE.md` — scoped instructions for the plugin manifest directory (35 lines).

### Changed
- `docs/CLAUDE-MD-SOTA.md` — §3.5 headless streaming flag added; §1.4 size guidance tightened (80-line ideal, 300-line max); §2.3 anti-pattern renamed to "Flat context loading".
- `CLAUDE.md` — Tech Stack extended with tooling path guidance; Workflow Preferences: "Read before modifying", "File discipline", "Maintenance" bullets added; Project Structure `.claude/rules/` row extended.

---

## [3.0.0] — 2026-03-01

### Changed
- Project renamed from **Claude Code Project Igniter** to **CLAUDE.md Best Practices Generator**.
- `pyproject.toml` `name` → `claude-md-best-practices`; `version` → `3.0.0`.
- `README.md` — complete rewrite for single-purpose identity.
- `CLAUDE.md` — major rewrite removing all catalog/ignite references.
- `fetch-guidelines.py` `USER_AGENT` updated: `claude-code-project-igniter/1.0` → `claude-md-best-practices/3.0`.

### Removed
- `/ignite` skill and all associated scripts, references, and documentation.
- `/sync-catalog` skill and `sync-catalog.sh`.
- `/add-source` skill.
- `catalog-inspector` agent.
- `catalog/` directory (sources, local stubs, manifest).
- `docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`, `docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`, `docs/SOURCE-SCHEMA.md`, `docs/test-archetypes/`, `docs/old/`.
- `RELEASE-NOTES-v1.0.md`, `RELEASE-NOTES-v2.0.md`.
- `tests/test_sprint1_catalog_foundation.py`, `tests/test_sprint2_catalog_sync.py`, `tests/test_sprint3_manifest_builder.py`.

### Fixed
- Dead code in `parse-insights.py` — `_card_evidence` field declared but never read, removed.
- Ruff E501 violations — 5 pre-existing line-too-long errors across `fetch-guidelines.py` and `parse-insights.py`.
