# Local Source

This directory holds your custom Claude Code entities. Entities placed here are **never overwritten** by the sync process and always take precedence over remote sources (priority 1, the highest).

## Directory Structure

```
local/
├── agents/    # Custom agent definitions (.md files)
├── skills/    # Custom skills (directories with SKILL.md or standalone .md files)
├── commands/  # Custom slash commands (.md files)
└── rules/     # Custom rules (.md files, may use subdirectories)
```

## How It Works

- The manifest builder (`build-manifest.py`) scans this directory alongside remote sources.
- Local entities are indexed in `catalog/manifest.json` with `"source": "local"`.
- During `/ignite`, local entities with the same name as a remote entity **win** due to lower priority number (priority 1 beats priority 10+).

## Adding Custom Entities

1. Place your `.md` files (or skill directories) in the appropriate subdirectory.
2. Run `/sync-catalog` to rebuild the manifest (sync only affects remote sources; your local files are untouched).
3. Run `/ignite` on your target project — your local entities will be included in selection.