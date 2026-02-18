# /add-source

Register a new remote entity source in `catalog/sources.json`. After adding, optionally sync it immediately with `/sync-catalog` to make its entities available in the catalog.

## When to Use

- When the user wants to add a third-party repository of Claude Code entities (agents, skills, commands, rules, hooks).
- When the user has their own remote repository of custom entities they want to integrate.

## Prerequisites

- `catalog/sources.json` must exist (created in Sprint 1).

## Procedure

Follow these steps in order.

### Step 1 — Gather source details

Prompt the user for the following fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `id` | Yes | — | Unique identifier (lowercase alphanumeric + hyphens). Used as directory name under `catalog/sources/`. |
| `url` | Yes | — | Git clone URL (HTTPS or SSH). |
| `branch` | No | `main` | Git branch to track. |
| `priority` | No | `50` | Priority for conflict resolution (2–99). Lower = higher precedence. |
| `entityPaths` | No | See below | Mapping of entity types to directory paths within the source repo. |

Default `entityPaths` if not specified:

```json
{
  "agents": "agents",
  "skills": "skills",
  "commands": "commands",
  "rules": "rules"
}
```

Ask if the source also provides hooks. If yes, add `"hooks": "hooks"` to `entityPaths`.

### Step 2 — Validate inputs

Apply all validation rules before proceeding. If any fail, report the issue and ask the user to correct it.

### Step 3 — Add to sources.json

1. Read `catalog/sources.json`.
2. Append the new source object to the `sources` array.
3. Write back with 2-space indentation and a trailing newline.
4. Validate the result: `python3 -c "import json; json.load(open('catalog/sources.json'))"`.

### Step 4 — Optional immediate sync

Ask the user: _"Source added. Would you like to sync it now?"_

If yes, run `/sync-catalog --source <new-id>` (invoke the sync-catalog skill with the new source ID).

## Validation Rules

All checks must pass before writing to `sources.json`:

1. **Unique ID**: The `id` must not already exist in `sources.json`.
2. **Valid ID format**: Lowercase letters, digits, and hyphens only. Must start with a letter. No underscores or spaces.
3. **Valid URL**: Must look like a git-cloneable URL — starts with `https://`, `http://`, `git@`, or `ssh://`. Must end with `.git` or be a recognizable git host URL.
4. **Priority range**: Must be an integer between 2 and 99 inclusive. Priority 1 is reserved for `local`.
5. **Branch non-empty**: If provided, must be a non-empty string.
6. **entityPaths valid**: Keys must be from the set: `agents`, `skills`, `commands`, `rules`, `hooks`. Values must be non-empty strings.

## References

- `catalog/sources.json` — The file being modified. Full schema in `docs/SOURCE-SCHEMA.md`.
- `docs/SOURCE-SCHEMA.md` — Schema documentation for all source fields, priority ranges, and entity paths.
- `/sync-catalog` — Skill to sync the newly added source.

## Constraints

- **Never modify existing source entries** — only append new ones.
- **Never assign priority 1** — reserved exclusively for the `local` source.
- **Never create a source with `id: local`** — it already exists and has special semantics.
- **Preserve JSON formatting** — 2-space indentation, consistent with the existing file style.