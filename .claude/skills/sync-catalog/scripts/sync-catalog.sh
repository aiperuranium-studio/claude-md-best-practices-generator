#!/usr/bin/env bash
# sync-catalog.sh — Clone or update remote sources from catalog/sources.json
#
# Usage:
#   bash .claude/skills/sync-catalog/scripts/sync-catalog.sh [--source <id>]
#
# Options:
#   --source <id>   Sync only the specified source (by ID)

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SOURCES_JSON="$PROJECT_ROOT/catalog/sources.json"
SOURCES_DIR="$PROJECT_ROOT/catalog/sources"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
FILTER_SOURCE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --source)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --source requires a source ID argument" >&2
                exit 1
            fi
            FILTER_SOURCE="$2"
            shift 2
            ;;
        *)
            echo "Error: unknown argument: $1" >&2
            echo "Usage: sync-catalog.sh [--source <id>]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validate prerequisites
# ---------------------------------------------------------------------------
if [[ ! -f "$SOURCES_JSON" ]]; then
    echo "Error: sources.json not found at $SOURCES_JSON" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Read sources from JSON via Python (no jq dependency)
# Output: one line per source — id|url|branch|pin
# ---------------------------------------------------------------------------
read_sources() {
    python3 -c "
import json, sys
with open('$SOURCES_JSON') as f:
    data = json.load(f)
filter_id = '$FILTER_SOURCE'
for src in data['sources']:
    if filter_id and src['id'] != filter_id:
        continue
    url = src.get('url') or ''
    branch = src.get('branch') or ''
    pin = src.get('pin') or ''
    print(f\"{src['id']}|{url}|{branch}|{pin}\")
"
}

# ---------------------------------------------------------------------------
# Write .source-meta.json for a synced source
# ---------------------------------------------------------------------------
write_source_meta() {
    local source_id="$1"
    local url="$2"
    local branch="$3"
    local pin="$4"
    local source_dir="$5"

    local commit
    commit="$(git -C "$source_dir" rev-parse HEAD)"

    python3 -c "
import json, datetime
meta = {
    'id': '$source_id',
    'url': '$url',
    'branch': '$branch',
    'pin': $(if [[ -z "$pin" ]]; then echo "None"; else echo "'$pin'"; fi),
    'commit': '$commit',
    'synced_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
}
with open('$source_dir/.source-meta.json', 'w') as f:
    json.dump(meta, f, indent=2)
    f.write('\n')
"
}

# ---------------------------------------------------------------------------
# Main sync loop
# ---------------------------------------------------------------------------
synced=0
skipped=0
failed=0
errors=""

while IFS='|' read -r src_id src_url src_branch src_pin; do
    # Skip sources with no URL (e.g., local)
    if [[ -z "$src_url" ]]; then
        echo "Skipping '$src_id' (no remote URL)"
        skipped=$((skipped + 1))
        continue
    fi

    target_dir="$SOURCES_DIR/$src_id"
    echo "--- Syncing '$src_id' from $src_url ---"

    # Clone or pull
    if [[ ! -d "$target_dir/.git" ]]; then
        echo "  Cloning (branch: ${src_branch:-main})..."
        if ! git clone --branch "${src_branch:-main}" --single-branch "$src_url" "$target_dir" 2>&1; then
            echo "Error: failed to clone '$src_id'" >&2
            failed=$((failed + 1))
            errors="${errors}  - Failed to clone '$src_id'\n"
            continue
        fi
    else
        echo "  Updating (branch: ${src_branch:-main})..."
        if ! (cd "$target_dir" && git fetch origin && git checkout "${src_branch:-main}" && git pull origin "${src_branch:-main}") 2>&1; then
            echo "Error: failed to update '$src_id'" >&2
            failed=$((failed + 1))
            errors="${errors}  - Failed to update '$src_id'\n"
            continue
        fi
    fi

    # Apply pin if set
    if [[ -n "$src_pin" ]]; then
        echo "  Pinning to ref: $src_pin"
        if ! git -C "$target_dir" checkout "$src_pin" 2>&1; then
            echo "Error: failed to checkout pin '$src_pin' for '$src_id'" >&2
            failed=$((failed + 1))
            errors="${errors}  - Failed to pin '$src_id' to '$src_pin'\n"
            continue
        fi
    fi

    # Write sync metadata
    write_source_meta "$src_id" "$src_url" "${src_branch:-main}" "$src_pin" "$target_dir"
    echo "  Done. Metadata written to $target_dir/.source-meta.json"
    synced=$((synced + 1))

done < <(read_sources)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=== Sync complete ==="
echo "  Synced:  $synced"
echo "  Skipped: $skipped"
echo "  Failed:  $failed"

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "Errors:" >&2
    echo -e "$errors" >&2
    exit 1
fi
