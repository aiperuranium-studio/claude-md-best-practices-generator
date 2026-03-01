# Release Notes — v3.0

**Date**: 2026-03-01
**Sprints covered**: 1, 2, 3

---

## Overview

Major scope reduction — renames the project from **Claude Code Project Igniter** to **CLAUDE.md Best Practices Generator** and removes all entity catalog infrastructure built across Sprints 1–6. The entire catalog pipeline (source registry, manifest builder, `/ignite`, `/sync-catalog`, `/add-source`, `catalog-inspector`) is superseded by the Everything Claude Code (ECC) plugin, whose `/configure-ecc` command covers entity selection and installation out of the box. The sole surviving product is the `/refresh-guidelines` pipeline: web scraping + `/insights` parsing + synthesis into `CLAUDE-MD-SOTA.enriched.md`. Three cleanup sprints execute the reduction: bulk deletion, documentation rewrite, and final verification.

---

## Sprint 1: Delete Catalog Infrastructure

Bulk deletion of all entity catalog code, scripts, tests, and documentation. No new files are added. The 177 guidelines enrichment tests are run after deletion to confirm no regressions.

### Removed

#### `/ignite` Skill

- **`.claude/skills/ignite/SKILL.md`** (269 lines) — Entrypoint for the entity selection, specialisation, and installation workflow. Six-step procedure, Technology Profile schema, full selection pipeline, CLAUDE.md generation rules, and six hard constraints.
- **`.claude/skills/ignite/scripts/build-manifest.py`** (651 lines) — Core indexing engine: entity discovery across five types, tag classification (languages, frameworks, categories), core entity identification via fuzzy name matching, `requiresAdaptation` detection, deterministic `catalog/manifest.json` output.
- **`.claude/skills/ignite/references/ignite-workflow.md`** (328 lines) — Detailed expansion of all six ignition steps: technology signal scanning, manifest staleness check, selection algorithm, report format, file copy + specialisation + hook merging, CLAUDE.md generation.
- **`.claude/skills/ignite/references/specialization-guide.md`** (198 lines) — Adaptation rules for all five entity types: agents (system prompt), skills (code examples, file paths), commands→skills conversion, rules (language filter, CLAUDE.md embed), hooks (file matchers, tool paths).
- **`.claude/skills/ignite/references/gap-analysis-guide.md`** (141 lines) — Three coverage levels (Full/Partial/None), gap report structure, four recommendation actions, surfacing thresholds.

#### `/sync-catalog` Skill

- **`.claude/skills/sync-catalog/SKILL.md`** — Entrypoint for `/sync-catalog`. Three-step procedure: run `sync-catalog.sh`, run `build-manifest.py`, report results.
- **`.claude/skills/sync-catalog/scripts/sync-catalog.sh`** (169 lines) — Bash script (`#!/usr/bin/env bash`, POSIX-compatible) that clones or pulls all sources defined in `sources.json`, writes `.source-meta.json` after each sync, accepts `--source <id>` for single-source mode.

#### `/add-source` Skill

- **`.claude/skills/add-source/SKILL.md`** (82 lines) — Entrypoint for `/add-source`. Four-step procedure: gather inputs, validate, append to `catalog/sources.json`, offer immediate sync. Six validation rules; three hard constraints (never modify existing entries, never use priority 1, never create `id: local`).

#### `catalog-inspector` Agent

- **`.claude/agents/catalog-inspector.md`** (74 lines) — Sub-agent for catalog inspection. Four capabilities: summarise entities, compare across sources, identify gaps, recommend for tech stack. Tools: `Read`, `Grep`, `Glob`.

#### Catalog Directory

- **`catalog/sources.json`** — Source registry: URL, branch, priority, and `entityPaths` per source.
- **`catalog/sources/local/`** — User custom entity stubs (`agents/`, `skills/`, `commands/`, `rules/` `.gitkeep` files + `README.md`). Priority 1 — always wins over remote sources.
- **`catalog/sources/everything-claude-code/`** — Cloned ECC repo (gitignored; large).
- **`catalog/CLAUDE.md`** — Scoped instructions for the catalog subtree.

#### Tests

- **`tests/test_sprint1_catalog_foundation.py`** (317 lines) — Covers: `catalog/sources.json` schema, local source directory structure, `SOURCE-SCHEMA.md` presence and content.
- **`tests/test_sprint2_catalog_sync.py`** (287 lines) — Covers: `sync-catalog.sh` existence and executability, bash shebang, source JSON parsing, local source skipping, `.source-meta.json` schema, `--source` flag, error handling.
- **`tests/test_sprint3_manifest_builder.py`** (892 lines) — Covers: `build-manifest.py` module loading, `normalize_name`, `is_core_entity`, `classify_tags`, `discover_agents`, all five entity types, manifest schema, composite ID format, coverage summary, determinism.

#### Documentation

- **`docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`** — Original architecture plan.
- **`docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`** — Sprint development agenda.
- **`docs/SOURCE-SCHEMA.md`** — JSON schema reference for `sources.json` and `.source-meta.json`.
- **`docs/test-archetypes/`** — Six project archetype descriptions (python-django, typescript-react-nextjs, go-microservice, java-spring-boot, polyglot-python-ts, empty-project) and `RESULTS.md`.
- **`docs/old/`** — Superseded planning documents (`CLAUDE-MD-SOTA-PLAN.md`, `IGNITER-PLAN.md`).
- **`RELEASE-NOTES-v1.0.md`**, **`RELEASE-NOTES-v2.0.md`** — Superseded release notes.

#### `.gitignore` entries removed

Two catalog-specific ignore rules deleted: `catalog/sources/*/` (large cloned repos) and `catalog/manifest.json` (auto-generated index). Guidelines enrichment ignores retained unchanged.

---

## Sprint 2: Rewrite Documentation and Identity

Updates all remaining files to reflect the new single-purpose identity. No code logic changes — documentation only.

### Delivered

- **`README.md`** (complete rewrite) — Removes all catalog/ignite/sync-catalog/add-source documentation. New content: project description as CLAUDE.md best practices generator, two installation options (`--add-dir` recommended, shell alias), three-step quick start (`clone` → attach → `/refresh-guidelines`), skills reference table (one row), pipeline output file table.

- **`CLAUDE.md`** (major rewrite) — Removes: `python3 -c "import json; json.load(...)"` sources.json validation command; `/sync-catalog`, `/add-source`, `/ignite` from Skills section; catalog-related Project Structure rows (`catalog/`, `docs/SOURCE-SCHEMA.md`, ignite/sync-catalog/add-source skill dirs, `catalog-inspector`, `docs/test-archetypes/`); entire **Installed Entities** section (agents, skills, hooks tables); entire **Known Gaps** section; stale Authoritative Documents links (plan, agenda, source schema). Updates: Tech Stack (removes Bash and JSON as primary items); project description line.

- **`docs/CLAUDE.md`** — Removes `SOURCE-SCHEMA.md` from sub-products list; removes `IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`, `IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`, and `docs/old/` from internal dev docs list; simplifies sub-product isolation rule (single sub-product: `CLAUDE-MD-SOTA.md`).

- **`tests/CLAUDE.md`** — Removes sprint 1/2/3 test files from Current Test Files list; updates running-tests example to reference the single remaining test file.

- **`pyproject.toml`** — `name`: `claude-code-project-igniter` → `claude-md-best-practices`; `version`: `0.1.0` → `3.0.0`; `description` updated to reflect the narrowed scope.

- **`docs/CLAUDE-MD-SOTA.md`** — Removes all `/ignite` references: rewrites Purpose & Scope (seed file described as a standalone reference, not as `/ignite` input); removes "How `/ignite` consumes this document" table; removes `/ignite`-generated annotations from §1.1 File Hierarchy; removes `/ignite` attribution from §1.3 Recommended Sections items 7–8; removes `/ignite` mention from §5.4 Bootstrapping.

- **`.claude/skills/refresh-guidelines/SKILL.md`** — Removes line stating `/ignite` reads the enriched output; removes hardcoded deleted doc names from sub-product isolation constraint.

- **`.claude/skills/refresh-guidelines/references/enrichment-procedure.md`** — Removes hardcoded deleted doc names from QA checklist item on sub-product self-containment.

- **`.claude/skills/refresh-guidelines/scripts/fetch-guidelines.py`** — Updates `USER_AGENT`: `claude-code-project-igniter/1.0` → `claude-md-best-practices/3.0`.

---

## Sprint 3: Verify, Clean, and Tag

Final verification sweep, dead code removal, ruff fixes, and release tagging.

### Delivered

- **Grep sweep** — Zero hits for orphaned references (`ignite`, `sync-catalog`, `add-source`, `catalog-inspector`, `manifest.json`, `sources.json`, `SOURCE-SCHEMA`, `build-manifest`, `test-archetype`, `IGNITER-PLUS`, `DEV-AGENDA`, `RELEASE-NOTES`) across all tracked `.md`, `.py`, `.json`, `.toml`, and `.sh` files.

- **Dead code removal in `parse-insights.py`** — Deleted `self._card_evidence: str = ""` (declared but never read) and the corresponding per-card reset `self._card_evidence = ""` in `InsightsHTMLParser`. The remaining seven vulture findings are confirmed false positives: HTMLParser protocol overrides (`handle_starttag`, `handle_endtag`, `handle_data`) and a urllib opener error-handler (`http_error_308`) dispatched dynamically by their respective frameworks.

- **Ruff E501 fixes** — Five pre-existing line-too-long violations corrected across both scripts:
  - `fetch-guidelines.py`: `verified_re` regex compile call, HTML content-type conditional, `check_url_status` signature, summary `print` call.
  - `parse-insights.py`: staleness warning f-string.

- **`RELEASE-NOTES-v3.0.md`** — This file.

- **Tag `v3.0`** — Applied to commit `f076386` on `develop` branch.

---

## Post-Sprint CLAUDE.md Updates

After Sprint 3, `docs/CODEMAPS/` (auto-generated architecture documentation produced by `/everything-claude-code:update-codemaps` in the previous session) was deleted because it reflected the old project structure. It will be regenerated with accurate content via `/everything-claude-code:update-codemaps` in the next development session.

---

## Known Limitations

- **No automated tests for Sprint 2–3 deliverables** — All Sprint 2 changes are documentation; Sprint 3 verification was manual grep + vulture + ruff. The 177 guidelines enrichment tests remain the only automated baseline.
- **`--add-dir` not persisted** — Users must re-attach the tool each Claude Code session via `claude --add-dir <path>` or a shell alias; no automatic persistence.
- **ECC dev entities remain** — The 30+ ECC-installed skills and 14 rule files under `.claude/skills/` and `.claude/rules/` (installed by the previous `/ignite` run) are still present in the repository. They are useful for developing this project but are not part of the product and could be trimmed in a future cleanup sprint.
- **Single skill** — The project now exposes only `/refresh-guidelines`. Users who need entity catalog functionality must use ECC directly.

---

## What's Next

| Area | Description |
|------|-------------|
| ECC dev entity audit | Decide which ECC-installed skills and rules to keep for project development vs. remove for repo minimalism |
| Regenerate `docs/CODEMAPS/` | Run `/everything-claude-code:update-codemaps` after the refactor to produce accurate architecture docs |
| `/refresh-guidelines` cadence | Periodic re-runs as Anthropic documentation evolves to keep `CLAUDE-MD-SOTA.md` current |
| Test coverage for pipeline scripts | Add pytest coverage for the two remaining scripts beyond what `test_sprint1_5_guidelines_enrichment.py` already provides |
