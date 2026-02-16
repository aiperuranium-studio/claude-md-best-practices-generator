# tests/ — Scoped Instructions

## Framework

pytest (not unittest). Stdlib + pytest only — no external test dependencies.

## Running Tests

Use the project virtualenv (`.venv/`) or `uv run`:

```bash
.venv/bin/pytest tests/ -v                                # all tests
.venv/bin/pytest tests/test_sprint1_catalog_foundation.py -v  # single file
uv run pytest tests/ -v                                   # alternative via uv
```

**IMPORTANT**: Do not use bare `pytest` — it is not installed system-wide.

## Naming Convention

`test_sprint{N}_{feature}.py` — each file covers one sprint's acceptance criteria.

## Current Test Files

- `test_sprint1_catalog_foundation.py` — catalog/sources.json schema, local source directory structure, SOURCE-SCHEMA.md
- `test_sprint1_5_guidelines_enrichment.py` — skill files, script functions, reference parsing, output schemas, gitignore entries

## Conventions

- Test files use `PROJECT_ROOT = Path(__file__).resolve().parent.parent` for path resolution
- Scripts are loaded as modules via `importlib.util` to avoid `__main__` side-effects (`test_sprint1_5_guidelines_enrichment.py:19-30`)
- Mock external I/O (network, filesystem) — tests must run offline
