# claude-md-best-practices-generator Development Patterns

> Auto-generated skill from repository analysis

## Overview

This repository demonstrates best practices for developing Claude AI skills and plugins. It uses Python as the primary language with a focus on generating markdown documentation, maintaining code quality, and establishing robust CI/CD workflows. The codebase emphasizes automated skill development with comprehensive testing and clear documentation patterns.

## Coding Conventions

### File Naming
- Use **camelCase** for file names
- Test files follow pattern: `*.test.*`
- Skill documentation: `SKILL.md` and `CLAUDE.md`
- Reference files stored in `references/` subdirectories

### Import Style
```python
# Mixed import style is used throughout the codebase
import os
from pathlib import Path
import json
```

### Project Structure
```
skills/
├── skill-name/
│   ├── SKILL.md
│   ├── CLAUDE.md
│   ├── references/
│   └── scripts/
tests/
├── test_*.py
├── fixtures/
└── CLAUDE.md
```

## Workflows

### Version Release
**Trigger:** When someone wants to release a new version
**Command:** `/release-version`

1. Update version in `pyproject.toml`
2. Update version in `.claude-plugin/plugin.json`
3. Update version in `.claude-plugin/marketplace.json`
4. Create or update `CHANGELOG.md` or `RELEASE-NOTES-v*.md`
5. Update version references in code (USER_AGENT strings)
6. Commit with message format: `feat: release version X.Y.Z`

### Gitignore Maintenance
**Trigger:** When someone needs to exclude files from git tracking
**Command:** `/update-gitignore`

1. Identify files/directories that should be ignored
2. Add appropriate patterns to `.gitignore`
3. Test ignore behavior with `git status`
4. Refine patterns to avoid over-broad exclusions
5. Commit changes with descriptive message

### Skill Development
**Trigger:** When someone wants to add a new skill/automation
**Command:** `/new-skill`

1. Create new directory under `skills/[skill-name]/`
2. Write `SKILL.md` with step-by-step instructions
3. Add `CLAUDE.md` for comprehensive skill documentation
4. Create reference files in `references/` subdirectory
5. Add helper scripts in `scripts/` if needed
6. Write behavioral tests in `tests/test_*.py`
7. Update main `CLAUDE.md` and `README.md`

### Test Coverage Expansion
**Trigger:** When someone wants to add test coverage for new functionality
**Command:** `/add-tests`

1. Create test fixtures in `tests/fixtures/`
2. Write behavioral tests in `test_*.py` files
3. Add test documentation to `tests/CLAUDE.md`
4. Run test suite to ensure all tests pass
5. Update commit messages with test count information
6. Ensure comprehensive coverage of edge cases

### Code Quality Fixes
**Trigger:** When ruff or other linters report violations
**Command:** `/fix-lint`

1. Run linter to identify specific violations
   ```bash
   ruff check .
   ```
2. Fix line length violations (E501) and other issues
3. Split long lines or add `# noqa` suppressions where appropriate
4. Verify all tests still pass after changes
5. Ensure clean ruff status before committing

### GitHub Actions Setup
**Trigger:** When someone wants to set up continuous integration
**Command:** `/setup-ci`

1. Create workflow YAML files in `.github/workflows/`
2. Configure test job with Python matrix testing
3. Set up lint job with ruff checks
4. Implement security hardening with pinned action versions
5. Configure appropriate permissions and triggers
6. Add specialized workflows (freshness checks, dependency updates)

## Testing Patterns

### Test Organization
- Tests located in `tests/` directory
- Fixtures stored in `tests/fixtures/`
- Test documentation in `tests/CLAUDE.md`

### Test Naming Convention
```python
def test_specific_behavior():
    """Test description focusing on behavior, not implementation."""
    # Arrange
    # Act  
    # Assert
```

### Behavioral Testing
Focus on testing behaviors and outcomes rather than implementation details. Use descriptive test names that explain what should happen under specific conditions.

## Commit Message Patterns

- **Average length:** ~58 characters
- **Common prefixes:** `fix:`, `feat:`
- **Style:** Freeform with descriptive messages
- **Examples:**
  - `feat: add new skill for automated testing`
  - `fix: resolve linting violations in test files`

## Commands

| Command | Purpose |
|---------|---------|
| `/release-version` | Release new version with consistent metadata updates |
| `/update-gitignore` | Refine gitignore rules for better file exclusion |
| `/new-skill` | Create comprehensive new skill with documentation |
| `/add-tests` | Expand test coverage with fixtures and behavioral tests |
| `/fix-lint` | Resolve code quality issues and linting violations |
| `/setup-ci` | Configure GitHub Actions for automated testing |