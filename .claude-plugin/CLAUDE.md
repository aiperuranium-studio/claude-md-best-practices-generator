# .claude-plugin/ — Scoped Instructions

## Purpose

Plugin manifest for the Claude Code marketplace. Contains the plugin entry point (`plugin.json`), marketplace registration (`marketplace.json`), and validator constraint documentation.

## Key Files

| File | Role |
|------|------|
| `plugin.json` | Plugin entry point — skills, version, metadata |
| `marketplace.json` | Marketplace registration metadata |
| `PLUGIN_SCHEMA_NOTES.md` | **Read before editing `plugin.json`** — undocumented validator constraints |
| `README.md` | End-user installation instructions |

## Before Editing `plugin.json`

**IMPORTANT**: Read `PLUGIN_SCHEMA_NOTES.md` first. The validator enforces constraints that cause vague errors (`agents: Invalid input`) without indicating root cause.

Critical rules:
- All component fields (`skills`, `agents`, `commands`) must be **arrays**, never strings.
- `agents`: explicit **file paths** only (e.g., `"./agents/planner.md"`), not directories.
- `skills` and `commands`: **directory paths** (e.g., `"./.claude/skills/refresh-guidelines/"`).
- All paths start with `./` and resolve from the **repo root**, not from `.claude-plugin/`.
- `version` field is required.
- **Do NOT add a `hooks` field** — `hooks/hooks.json` is auto-loaded by convention; declaring it causes a duplicate error (regression history in `PLUGIN_SCHEMA_NOTES.md`).

## Validation

Run before committing any changes:

```bash
claude plugin validate .claude-plugin/plugin.json
```

## Installation (end users)

```bash
claude plugin marketplace add https://github.com/aiperuranium-studio/claude-md-best-practices-generator
claude plugin install claude-md-best-practices
```

Direct GitHub URL install fails — marketplace registration is required first.
