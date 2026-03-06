# tests/ — Scoped Instructions

## Framework

pytest (not unittest). Stdlib + pytest only — no external test dependencies.

## Running Tests

Use the project virtualenv (`.venv/`) or `uv run`:

```bash
.venv/bin/pytest tests/ -v                                    # all tests
.venv/bin/pytest tests/test_sprint1_5_guidelines_enrichment.py -v  # single file
uv run pytest tests/ -v                                       # alternative via uv
```

**IMPORTANT**: Do not use bare `pytest` — it is not installed system-wide.

## Naming Convention

`test_sprint{N}_{feature}.py` — each file covers one sprint's acceptance criteria.

## Current Test Files

- `test_sprint1_5_guidelines_enrichment.py` — skill files, script functions, reference parsing, output schemas, gitignore entries
- `test_refactor_scaffold_skills.py` — /refactor-claude-md and /scaffold-claude-md skill structure, frontmatter, pointer-based design, plugin manifest, root CLAUDE.md documentation
- `test_metadata_consistency.py` — plugin.json / marketplace.json / pyproject.toml version alignment, USER_AGENT version check (Sprint 1)
- `test_fetch_behavioral.py` — HTMLTextExtractor, extract_content_blocks, main() end-to-end with mocked HTTP, check_freshness_main() with mocked check_url_status, edge cases (Sprint 2)
- `test_insights_behavioral.py` — InsightsHTMLParser, parse_facets, parse_session_meta, main() end-to-end with fixture report, missing report degradation, stale report detection (Sprint 2)

## Fixtures

`tests/fixtures/` holds offline test data (Sprint 2):
- `sample-source.html` — HTML page exercising HTMLTextExtractor SKIP_TAGS
- `sample-report.html` — /insights report.html with all 7 section types + claude-md-item
- `facets/sample.json` — representative facets data
- `session-meta/sample.json` — representative session metadata

Update this list when new sprint test files are added.

## Conventions

- Test files use `PROJECT_ROOT = Path(__file__).resolve().parent.parent` for path resolution
- Scripts are loaded as modules via `importlib.util` to avoid `__main__` side-effects (`test_sprint1_5_guidelines_enrichment.py:19-30`)
- **IMPORTANT**: Mock external I/O (network, filesystem) — tests must run offline
