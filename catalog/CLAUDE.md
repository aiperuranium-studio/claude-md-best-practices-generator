# catalog/ — Scoped Instructions

## sources.json

The source registry defining where entities come from. Full schema: [docs/SOURCE-SCHEMA.md](../docs/SOURCE-SCHEMA.md).

Each source entry has: `id`, `url`, `branch`, `pin`, `priority`, `entityPaths`. Validate after edits — see root `CLAUDE.md` Common Commands.

## Priority Model

Lower number = higher precedence in conflict resolution:

| Range | Usage |
|-------|-------|
| 1 | `local` — user overrides, always wins |
| 2–9 | Reserved for future high-priority sources |
| 10–49 | Primary remote sources |
| 50–99 | Secondary / supplemental remote sources |

Default priority for `/add-source`: 50.

## Local Entity Directory (`sources/local/`)

- Always tracked in git (not gitignored)
- Wins all conflicts via priority 1
- Never overwritten by `/sync-catalog`
- Subdirectories mirror entity types: `agents/`, `skills/`, `commands/`, `rules/`

## manifest.json

Auto-generated entity index — **do not edit manually**. Gitignored, rebuilt by `/sync-catalog`.
