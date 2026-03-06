# CLAUDE.md Best Practices Generator

A tool for generating, auditing, and maintaining CLAUDE.md files based on curated web sources and Claude Code `/insights` behavioral data. Three skills: `/refresh-guidelines` produces the authoritative reference, `/refactor-claude-md` audits and refactors existing CLAUDE.md files against it, and `/scaffold-claude-md` creates scoped CLAUDE.md files in subdirectories.

## Tech Stack

- **Python 3.10+**, standard library only (external deps documented explicitly when unavoidable).
- **Markdown** for documentation and skill definitions.
- Scripts use Python stdlib only — run with system `python3` or `.venv/bin/python3`.

## Common Commands

- `python3 skills/refresh-guidelines/scripts/fetch-guidelines.py` — Fetch raw content from curated web sources into `docs/guidelines-raw.json`.
- `python3 skills/refresh-guidelines/scripts/fetch-guidelines.py --check-freshness` — Check source URL reachability and staleness, write `docs/freshness-report.json`.
- `python3 skills/refresh-guidelines/scripts/parse-insights.py` — Parse `/insights` report into `docs/insights-parsed.json`. Manual tips go in `docs/insights-raw.md`.
- `.venv/bin/pytest tests/ -v` — Run all tests (or `uv run pytest tests/ -v`).

## Gotchas & Known Issues

- `parse-insights.py` requires `~/.claude/usage-data/report.html` — if missing, the script degrades gracefully (insights step skipped).
- All scripts must be run from the project root — paths are relative to root.
- Pass `--docs-dir docs` to fetch/parse scripts; this is the standard argument pattern.

## Project Structure

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, prerequisites, installation, quick-start |
| `docs/` | CLAUDE-MD-SOTA generation reference |
| `docs/CODEMAPS/` | Auto-generated architecture docs — regenerate with `/everything-claude-code:update-codemaps` |
| `skills/refresh-guidelines/` | `/refresh-guidelines` skill definition and scripts |
| `skills/refactor-claude-md/` | `/refactor-claude-md` skill definition and compliance checklist procedure |
| `skills/scaffold-claude-md/` | `/scaffold-claude-md` skill definition and directory assessment criteria |
| `rules/` | Project-developed rule — `claude-md-standards.md` (CLAUDE.md quality standards) |
| `.claude/rules/` | ECC-installed rules (common, golang, python, typescript, swift) — not project-developed, gitignored |
| `.claude-plugin/` | Claude Code plugin manifest (`plugin.json`) and marketplace registry (`marketplace.json`) |
| `tests/` | pytest test files |

Each subdirectory has its own scoped `CLAUDE.md` with directory-specific instructions.

## Coding Conventions

- **Prefer pointers to copies** — Don't embed code snippets in documentation; use `file:line` references to point at the authoritative source code.
- **Documentation rules** — See `docs/CLAUDE.md` for doc classification (sub-products vs generated artifacts), cross-referencing, and isolation rules.

## Workflow Preferences

- **IMPORTANT: Write-first, never chat-first** — When asked to write documentation or plans, write directly to a file. Do NOT present in chat first. Ask for a file path if none specified.
- **IMPORTANT: No preemptive execution** — Do NOT implement or run code unless explicitly asked. Wait for user approval after presenting plans.
- **IMPORTANT: No scope creep** — Do NOT extrapolate or expand scope beyond what was requested. Mention ideas briefly at the end only if relevant.
- **Read before modifying** — Read existing skill SKILL.md files and scripts before proposing changes.
- **File discipline** — Prefer editing existing files to creating new ones.
- **Clarify before acting** — When unclear on a request (especially Italian or domain-specific terms), ask rather than guess.
- **Proportional response** — For simple changes, act directly without entering plan mode. Reserve plan mode for genuinely complex, multi-approach decisions.
- **Verification** — Run `.venv/bin/pytest tests/<specific_file.py> -v` after code changes; full suite (`.venv/bin/pytest tests/ -v`) as final gate only. Run `ruff check` on Python changes before reporting completion.
- **One-section-at-a-time** — Complete one document/section fully before moving to the next. Do not scatter partial edits.
- **Maintenance** — Update this CLAUDE.md when skills are added/renamed or recurring mistakes emerge. Use `CLAUDE.local.md` (gitignored) for personal overrides. After corrections, end with "Update CLAUDE.md so you don't repeat that mistake."

## Installed Skills

- `/refresh-guidelines` — Enriches CLAUDE-MD-SOTA writing guidelines from web sources + `/insights` data.
- `/refactor-claude-md` — Audits any CLAUDE.md (root or scoped) against current CLAUDE-MD-SOTA guidelines, produces a compliant refactored version. Accepts an optional target path: `/refactor-claude-md docs/CLAUDE.md`.
- `/scaffold-claude-md` — Scans subdirectories, identifies which need CLAUDE.md files, generates scoped content.
- Plugin mode: prefix with `claude-md-best-practices:` after `claude plugin install claude-md-best-practices`.

## Authoritative Documents

- **CLAUDE.md generation rules**: [docs/CLAUDE-MD-SOTA.md](docs/CLAUDE-MD-SOTA.md) (seed) / `docs/CLAUDE-MD-SOTA.enriched.md` (enriched, gitignored)
