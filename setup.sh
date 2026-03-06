#!/usr/bin/env bash
set -euo pipefail

# claude-md-best-practices — Development environment setup
# Run from the project root: bash setup.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "==> Checking Python version..."
python_bin=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            python_bin="$candidate"
            echo "    Found: $python_bin ($version)"
            break
        fi
    fi
done

if [ -z "$python_bin" ]; then
    echo "ERROR: Python 3.10+ required but not found." >&2
    exit 1
fi

echo "==> Creating virtual environment..."
if [ ! -d ".venv" ]; then
    "$python_bin" -m venv .venv
    echo "    Created .venv"
else
    echo "    Already exists, skipping"
fi

echo "==> Installing dev dependencies..."
if command -v uv &>/dev/null; then
    uv pip install --python .venv/bin/python -e ".[dev]"
else
    .venv/bin/pip install --quiet -e ".[dev]"
fi

echo "==> Running smoke tests..."
.venv/bin/pytest tests/ -v --tb=short -q

echo ""
echo "Setup complete. Quick start:"
echo "  source .venv/bin/activate"
echo "  make test           # run tests"
echo "  make lint           # run ruff"
echo "  make fetch          # fetch guidelines"
echo "  make freshness      # check source freshness"
