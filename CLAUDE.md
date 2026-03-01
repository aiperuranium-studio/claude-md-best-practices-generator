# CLAUDE.md Best Practices Generator

A tool for enriching CLAUDE.md generation guidelines from curated web sources and Claude Code `/insights` behavioral data. The sole skill is `/refresh-guidelines`, which produces `docs/CLAUDE-MD-SOTA.enriched.md` — the authoritative reference for writing high-quality CLAUDE.md files.

## Tech Stack

- **Python 3.10+**, standard library only (external deps documented explicitly when unavoidable).
- **Markdown** for documentation and skill definitions.

## Common Commands

- `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py` — Fetch raw content from curated web sources into `docs/guidelines-raw.json`.
- `python3 .claude/skills/refresh-guidelines/scripts/fetch-guidelines.py --check-freshness` — Check source URL reachability and staleness, write `docs/freshness-report.json`.
- `python3 .claude/skills/refresh-guidelines/scripts/parse-insights.py` — Parse `/insights` report into `docs/insights-parsed.json`. Manual tips go in `docs/insights-raw.md`.
- `.venv/bin/pytest tests/ -v` — Run all tests (or `uv run pytest tests/ -v`).

Skills (invoked within Claude Code):
- `/refresh-guidelines` — Direct mode (`--add-dir`): enriches CLAUDE-MD-SOTA writing guidelines from web sources + `/insights` data.
- `/claude-md-best-practices:refresh-guidelines` — Plugin mode: same skill, namespaced after `claude plugin install claude-md-best-practices`.

## Project Structure

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, prerequisites, installation, quick-start |
| `docs/` | CLAUDE-MD-SOTA generation reference |
| `docs/CODEMAPS/` | Auto-generated architecture docs — regenerate with `/everything-claude-code:update-codemaps` |
| `.claude/skills/refresh-guidelines/` | `/refresh-guidelines` skill definition and scripts |
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
- **Clarify before acting** — When unclear on a request (especially Italian or domain-specific terms), ask rather than guess.
- **Proportional response** — For simple changes, act directly without entering plan mode. Reserve plan mode for genuinely complex, multi-approach decisions.
- **Verification** — Run `.venv/bin/pytest tests/<specific_file.py> -v` after code changes; full suite (`.venv/bin/pytest tests/ -v`) as final gate only. Run `ruff check` on Python changes before reporting completion.
- **One-section-at-a-time** — Complete one document/section fully before moving to the next. Do not scatter partial edits.

## Authoritative Documents

- **CLAUDE.md generation rules**: [docs/CLAUDE-MD-SOTA.md](docs/CLAUDE-MD-SOTA.md) (seed) / `docs/CLAUDE-MD-SOTA.enriched.md` (enriched, gitignored)
