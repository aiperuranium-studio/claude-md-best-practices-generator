# /sync-catalog

Clone or update remote entity sources and rebuild the catalog manifest. This is the primary way to keep the entity catalog current — it fetches the latest entities from all registered remote sources and regenerates `catalog/manifest.json` so that `/ignite` has up-to-date material to work with.

## When to Use

- **First setup**: After cloning the igniter repo, run `/sync-catalog` to download all remote sources.
- **After `/add-source`**: Sync the newly registered source to make its entities available.
- **Periodic refresh**: When you want the latest upstream entities (new agents, skills, rules, etc.).
- **After modifying `catalog/sources.json`**: To reflect manual edits (branch change, pin update).

## Prerequisites

- Git available on PATH.
- Python 3.10+ available on PATH.
- Network access to reach remote source URLs (partial results on network failure).

## Arguments

- `--source <id>` (optional) — Sync only the specified source by its ID from `catalog/sources.json`. If omitted, all remote sources are synced.

## Procedure

Follow these steps in order.

### Step 1 — Sync remote sources

Run the sync script from the project root:

```
bash .claude/skills/sync-catalog/scripts/sync-catalog.sh
```

If the user specified a source ID, pass it through:

```
bash .claude/skills/sync-catalog/scripts/sync-catalog.sh --source <id>
```

The script will:
- Clone sources that don't exist locally yet.
- Pull updates for sources that already exist.
- Apply commit pins if configured.
- Write `.source-meta.json` metadata in each synced source directory.
- Skip the `local` source (no remote URL).

Capture and note the summary output (synced/skipped/failed counts).

### Step 2 — Rebuild the manifest

Run the manifest builder:

```
python3 .claude/skills/ignite/scripts/build-manifest.py
```

This scans all source directories (including `local/`) and produces `catalog/manifest.json` with classified, tagged entity metadata.

### Step 3 — Report results

Present a summary to the user:

1. **Sync results**: number of sources synced, skipped, and failed. If any failed, list them with error details.
2. **Manifest summary**: total entities indexed, broken down by type (agents, skills, commands, rules, hooks).
3. **Coverage**: languages, frameworks, and categories discovered across all entities (from the manifest's `coverage` section).
4. **Warnings**: any errors or issues from either step.

## References

- `scripts/sync-catalog.sh` — Bash script that clones/pulls remote sources.
- `.claude/skills/ignite/scripts/build-manifest.py` — Python script that scans sources and generates the manifest.
- `catalog/sources.json` — Source registry defining what to sync.
- `docs/SOURCE-SCHEMA.md` — Full schema documentation for sources.json and .source-meta.json.

## Constraints

- **Never modify `catalog/sources/local/`** — the sync script skips it and so should you.
- **Never edit `catalog/manifest.json` manually** — it is always regenerated from scratch by the manifest builder.
- **Report errors clearly** — if a source fails to sync, report the error and continue with the remaining sources.
- **Both scripts must succeed** — if the sync script exits non-zero, still attempt the manifest build (partial sync is better than no manifest update).
