# Source Schema Reference

This document describes the schema for `catalog/sources.json`, the source registry used by the Claude Code Project Igniter.

## `sources.json` Structure

```json
{
  "sources": [ <source>, ... ]
}
```

The top-level object contains a single `sources` array. Each element is a **source object** as defined below.

## Source Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for the source. Used as the directory name under `catalog/sources/` and as the source component in entity composite IDs (`{source}::{type}::{name}`). Must be a valid directory name (lowercase alphanumeric, hyphens allowed). |
| `url` | string \| null | Yes | Git clone URL. Set to `null` for sources that are not fetched from a remote (e.g., `local`). |
| `branch` | string \| null | Yes | Git branch to track. Set to `null` when `url` is null. |
| `pin` | string \| null | Yes | Git commit SHA or tag to pin to after checkout. When set, the sync script checks out this exact ref after pulling the branch. Set to `null` for head-tracking. |
| `priority` | integer | Yes | Priority for conflict resolution (lower number = higher precedence). See [Priority Resolution](#priority-resolution). |
| `entityPaths` | object | Yes | Maps entity types to their directory paths within the source repository. See [Entity Paths](#entity-paths). |

## Entity Paths

The `entityPaths` object maps entity type names to relative directory paths within the source repository root.

| Key | Description |
|-----|-------------|
| `agents` | Directory containing agent definition files (`.md`). |
| `skills` | Directory containing skill definitions (directories with `SKILL.md` or standalone `.md` files). |
| `commands` | Directory containing command definitions (`.md`). |
| `rules` | Directory containing rule files (`.md`), optionally organized in subdirectories (e.g., `rules/common/`, `rules/TypeScript/`). |
| `hooks` | Directory containing hook definitions (`hooks.json`). Not all sources define hooks. |

Not all entity types are required. A source may define only a subset (e.g., the `local` source omits `hooks`).

## Priority Resolution

Priority is an integer where **lower values win**. When two sources provide an entity with the same type and name, the entity from the source with the lower priority number is selected.

| Range | Usage |
|-------|-------|
| 1 | Reserved for `local` (user overrides always win). |
| 2–9 | Reserved for future high-priority sources. |
| 10–49 | Primary remote sources. |
| 50–99 | Secondary / supplemental remote sources. |

The default priority for new sources added via `/add-source` is 50.

## Examples

### Remote source (primary)

```json
{
  "id": "everything-claude-code",
  "url": "https://github.com/affaan-m/everything-claude-code.git",
  "branch": "main",
  "pin": null,
  "priority": 10,
  "entityPaths": {
    "agents": "agents",
    "skills": "skills",
    "commands": "commands",
    "rules": "rules",
    "hooks": "hooks"
  }
}
```

### Local source (user overrides)

```json
{
  "id": "local",
  "url": null,
  "branch": null,
  "pin": null,
  "priority": 1,
  "entityPaths": {
    "agents": "agents",
    "skills": "skills",
    "commands": "commands",
    "rules": "rules"
  }
}
```

## Sync Metadata (`.source-meta.json`)

After syncing a remote source, the sync script writes a `.source-meta.json` file inside the source directory (`catalog/sources/{id}/.source-meta.json`). This file is **auto-generated** and should not be manually edited.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Source ID (matches the source entry). |
| `url` | string | Git clone URL. |
| `branch` | string | Branch that was checked out. |
| `pin` | string \| null | Pinned ref, if any. |
| `commit` | string | HEAD commit SHA after sync. |
| `synced_at` | string | ISO 8601 timestamp of the sync. |

### Example

```json
{
  "id": "everything-claude-code",
  "url": "https://github.com/affaan-m/everything-claude-code.git",
  "branch": "main",
  "pin": null,
  "commit": "abc1234def5678...",
  "synced_at": "2026-02-12T10:30:00Z"
}
```

This metadata is consumed by the manifest builder to record provenance information in `catalog/manifest.json`.