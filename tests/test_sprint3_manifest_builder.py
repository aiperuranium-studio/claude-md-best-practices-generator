"""
Sprint 3: Manifest Builder — Unit Tests

Validates:
  - build-manifest.py exists and is loadable as a module
  - normalize_name: hyphens, underscores, case, .md stripping
  - is_core_entity: known cores, common/ rules, non-cores
  - classify_tags: language/framework/category detection, scope, Go word-boundary
  - discover_agents: .md files, skips README
  - discover_skills: SKILL.md dirs, fallback to .md, skips README
  - discover_commands: .md files, skips README
  - discover_rules: recursive subdirs, preserves subdir context
  - discover_hooks: hooks.json parsing (nested format), handles missing/malformed
  - requires_adaptation: core=no, universal=no, language-specific=yes
  - build_coverage: aggregation, deduplication, empty input
  - Manifest output schema: required fields, composite IDs, determinism, sorting
  - main(): exit codes, error handling
"""

import importlib.util
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: load build-manifest.py as a module
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_MANIFEST_PATH = (
    PROJECT_ROOT / ".claude" / "skills" / "ignite" / "scripts" / "build-manifest.py"
)

_bm_module = None


def _load_bm():
    """Lazy-load build-manifest.py as a module."""
    global _bm_module
    if _bm_module is not None:
        return _bm_module
    spec = importlib.util.spec_from_file_location("build_manifest", BUILD_MANIFEST_PATH)
    _bm_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_bm_module)
    return _bm_module


# ---------------------------------------------------------------------------
# Test: Script existence and loadability
# ---------------------------------------------------------------------------

class TestScriptExists:
    def test_file_exists(self):
        assert BUILD_MANIFEST_PATH.exists(), "build-manifest.py must exist"

    def test_module_loads(self):
        bm = _load_bm()
        assert bm is not None

    def test_has_shebang(self):
        first_line = BUILD_MANIFEST_PATH.read_text().splitlines()[0]
        assert first_line.startswith("#!/usr/bin/env python3")

    def test_has_required_functions(self):
        bm = _load_bm()
        required = [
            "main", "load_sources", "discover_entities",
            "classify_tags", "is_core_entity", "normalize_name",
            "build_coverage", "discover_agents", "discover_skills",
            "discover_commands", "discover_rules", "discover_hooks",
            "load_source_meta", "requires_adaptation",
        ]
        for fn_name in required:
            assert hasattr(bm, fn_name), f"Missing function: {fn_name}"
            assert callable(getattr(bm, fn_name)), f"{fn_name} is not callable"


# ---------------------------------------------------------------------------
# Test: normalize_name
# ---------------------------------------------------------------------------

class TestNormalizeName:
    def test_lowercase(self):
        bm = _load_bm()
        assert bm.normalize_name("Code-Reviewer") == "code-reviewer"

    def test_underscores_to_hyphens(self):
        bm = _load_bm()
        assert bm.normalize_name("code_reviewer") == "code-reviewer"

    def test_strips_md_extension(self):
        bm = _load_bm()
        assert bm.normalize_name("planner.md") == "planner"

    def test_spaces_to_hyphens(self):
        bm = _load_bm()
        assert bm.normalize_name("code reviewer") == "code-reviewer"

    def test_already_normalized(self):
        bm = _load_bm()
        assert bm.normalize_name("tdd-workflow") == "tdd-workflow"

    def test_mixed_separators(self):
        bm = _load_bm()
        assert bm.normalize_name("My_Cool Agent.md") == "my-cool-agent"


# ---------------------------------------------------------------------------
# Test: is_core_entity
# ---------------------------------------------------------------------------

class TestIsCoreEntity:
    def test_known_core_agents(self):
        bm = _load_bm()
        for name in ["planner", "architect", "code-reviewer", "security-reviewer", "build-error-resolver"]:
            assert bm.is_core_entity("agent", name), f"{name} should be core agent"

    def test_known_core_skills(self):
        bm = _load_bm()
        for name in ["tdd-workflow", "coding-standards", "verification-loop", "security-review"]:
            assert bm.is_core_entity("skill", name), f"{name} should be core skill"

    def test_known_core_commands(self):
        bm = _load_bm()
        for name in ["plan", "tdd", "code-review", "build-fix", "verify"]:
            assert bm.is_core_entity("command", name), f"{name} should be core command"

    def test_rules_common_is_core(self):
        bm = _load_bm()
        assert bm.is_core_entity("rule", "coding-style", dir_context="common")
        assert bm.is_core_entity("rule", "security", dir_context="common")

    def test_rules_non_common_not_core(self):
        bm = _load_bm()
        assert not bm.is_core_entity("rule", "coding-style", dir_context="typescript")

    def test_non_core_entity(self):
        bm = _load_bm()
        assert not bm.is_core_entity("agent", "database-reviewer")
        assert not bm.is_core_entity("skill", "django-patterns")
        assert not bm.is_core_entity("command", "orchestrate")

    def test_no_false_positive_substring(self):
        """Ensure 'plan' doesn't match 'multi-plan'."""
        bm = _load_bm()
        assert not bm.is_core_entity("command", "multi-plan")

    def test_no_false_positive_prefix(self):
        """Ensure 'coding-standards' doesn't match 'cpp-coding-standards'."""
        bm = _load_bm()
        assert not bm.is_core_entity("skill", "cpp-coding-standards")
        assert not bm.is_core_entity("skill", "java-coding-standards")

    def test_normalization_applies(self):
        bm = _load_bm()
        assert bm.is_core_entity("agent", "Code_Reviewer")
        assert bm.is_core_entity("command", "BUILD_FIX")

    def test_hooks_never_core(self):
        bm = _load_bm()
        assert not bm.is_core_entity("hook", "pretooluse-bash")


# ---------------------------------------------------------------------------
# Test: classify_tags
# ---------------------------------------------------------------------------

class TestClassifyTags:
    def test_python_from_name(self):
        bm = _load_bm()
        tags = bm.classify_tags("python-reviewer", "", "")
        assert "python" in tags["languages"]

    def test_typescript_from_path(self):
        bm = _load_bm()
        tags = bm.classify_tags("coding-style", "rules/typescript", "")
        assert "typescript" in tags["languages"]

    def test_go_from_name(self):
        bm = _load_bm()
        tags = bm.classify_tags("go-reviewer", "", "")
        assert "go" in tags["languages"]

    def test_go_no_false_positive(self):
        """Plain 'go' in English text should not trigger Go language tag."""
        bm = _load_bm()
        tags = bm.classify_tags("planner", "", "Let's go ahead and plan the project.")
        assert "go" not in tags["languages"]

    def test_django_framework(self):
        bm = _load_bm()
        tags = bm.classify_tags("django-patterns", "skills/", "Django is a web framework")
        assert "django" in tags["frameworks"]

    def test_testing_category(self):
        bm = _load_bm()
        tags = bm.classify_tags("e2e-testing", "", "")
        assert "testing" in tags["categories"]

    def test_security_category(self):
        bm = _load_bm()
        tags = bm.classify_tags("security-review", "", "")
        assert "security" in tags["categories"]

    def test_universal_scope(self):
        bm = _load_bm()
        tags = bm.classify_tags("planner", "", "Plan your project architecture")
        assert tags["scope"] == "universal"

    def test_language_specific_scope(self):
        bm = _load_bm()
        tags = bm.classify_tags("python-reviewer", "", "")
        assert tags["scope"] == "language-specific"

    def test_framework_specific_scope(self):
        bm = _load_bm()
        tags = bm.classify_tags("django-patterns", "", "")
        assert tags["scope"] == "framework-specific"

    def test_tags_are_sorted(self):
        bm = _load_bm()
        tags = bm.classify_tags("python-django-testing", "", "")
        assert tags["categories"] == sorted(tags["categories"])
        assert tags["languages"] == sorted(tags["languages"])
        assert tags["frameworks"] == sorted(tags["frameworks"])

    def test_required_tag_keys(self):
        bm = _load_bm()
        tags = bm.classify_tags("something", "", "")
        assert "languages" in tags
        assert "frameworks" in tags
        assert "categories" in tags
        assert "scope" in tags


# ---------------------------------------------------------------------------
# Test: discover_agents
# ---------------------------------------------------------------------------

class TestDiscoverAgents:
    def test_discovers_md_files(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "planner.md").write_text("# Planner Agent")
            (d / "architect.md").write_text("# Architect Agent")

            result = bm.discover_agents(d)
            names = [e["name"] for e in result]
            assert "planner" in names
            assert "architect" in names

    def test_skips_readme(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "README.md").write_text("# Agents")
            (d / "planner.md").write_text("# Planner")

            result = bm.discover_agents(d)
            names = [e["name"] for e in result]
            assert "README" not in names
            assert len(result) == 1

    def test_empty_dir(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = bm.discover_agents(Path(tmpdir))
            assert result == []

    def test_nonexistent_dir(self):
        bm = _load_bm()
        result = bm.discover_agents(Path("/nonexistent"))
        assert result == []

    def test_entity_has_required_fields(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "test-agent.md").write_text("# Test Agent\nDoes testing.")

            result = bm.discover_agents(d)
            assert len(result) == 1
            entity = result[0]
            assert "name" in entity
            assert "path" in entity
            assert "content_preview" in entity

    def test_ignores_non_md(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "agent.md").write_text("# Agent")
            (d / "script.py").write_text("print('hello')")
            (d / "config.json").write_text("{}")

            result = bm.discover_agents(d)
            assert len(result) == 1


# ---------------------------------------------------------------------------
# Test: discover_skills
# ---------------------------------------------------------------------------

class TestDiscoverSkills:
    def test_discovers_skill_md_directories(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "tdd-workflow").mkdir()
            (d / "tdd-workflow" / "SKILL.md").write_text("# TDD Workflow")
            (d / "coding-standards").mkdir()
            (d / "coding-standards" / "SKILL.md").write_text("# Coding Standards")

            result = bm.discover_skills(d)
            names = [e["name"] for e in result]
            assert "tdd-workflow" in names
            assert "coding-standards" in names

    def test_fallback_to_md_files(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            # No SKILL.md directories, just .md files
            (d / "my-skill.md").write_text("# My Skill")

            result = bm.discover_skills(d)
            names = [e["name"] for e in result]
            assert "my-skill" in names

    def test_skips_readme_in_fallback(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "README.md").write_text("# Skills")
            (d / "my-skill.md").write_text("# My Skill")

            result = bm.discover_skills(d)
            assert len(result) == 1
            assert result[0]["name"] == "my-skill"

    def test_prefers_skill_md_dirs_over_files(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "tdd-workflow").mkdir()
            (d / "tdd-workflow" / "SKILL.md").write_text("# TDD Workflow")
            # Also a loose .md file — should be ignored since we have SKILL.md dirs
            (d / "extra.md").write_text("# Extra")

            result = bm.discover_skills(d)
            names = [e["name"] for e in result]
            assert "tdd-workflow" in names
            assert "extra" not in names

    def test_empty_dir(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = bm.discover_skills(Path(tmpdir))
            assert result == []


# ---------------------------------------------------------------------------
# Test: discover_commands
# ---------------------------------------------------------------------------

class TestDiscoverCommands:
    def test_discovers_md_files(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "plan.md").write_text("# Plan")
            (d / "tdd.md").write_text("# TDD")

            result = bm.discover_commands(d)
            names = [e["name"] for e in result]
            assert "plan" in names
            assert "tdd" in names

    def test_skips_readme(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "README.md").write_text("# Commands")
            (d / "plan.md").write_text("# Plan")

            result = bm.discover_commands(d)
            assert len(result) == 1


# ---------------------------------------------------------------------------
# Test: discover_rules
# ---------------------------------------------------------------------------

class TestDiscoverRules:
    def test_discovers_in_subdirectories(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "common").mkdir()
            (d / "common" / "security.md").write_text("# Security Rules")
            (d / "python").mkdir()
            (d / "python" / "coding-style.md").write_text("# Python Style")

            result = bm.discover_rules(d)
            names = [e["name"] for e in result]
            assert "common/security" in names
            assert "python/coding-style" in names

    def test_preserves_subdir_context(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "common").mkdir()
            (d / "common" / "testing.md").write_text("# Testing")

            result = bm.discover_rules(d)
            assert len(result) == 1
            assert result[0]["dir_context"] == "common"

    def test_skips_readme(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "README.md").write_text("# Rules")
            (d / "common").mkdir()
            (d / "common" / "README.md").write_text("# Common Rules")
            (d / "common" / "security.md").write_text("# Security")

            result = bm.discover_rules(d)
            names = [e["name"] for e in result]
            assert all("readme" not in n.lower() for n in names)

    def test_empty_dir(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = bm.discover_rules(Path(tmpdir))
            assert result == []


# ---------------------------------------------------------------------------
# Test: discover_hooks
# ---------------------------------------------------------------------------

class TestDiscoverHooks:
    def test_parses_nested_hooks_json(self):
        """Test the actual hooks.json format: { "hooks": { "EventType": [...] } }"""
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            hooks_data = {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [{"type": "command", "command": "echo hello"}],
                            "description": "Test hook",
                        }
                    ]
                }
            }
            (d / "hooks.json").write_text(json.dumps(hooks_data))

            result = bm.discover_hooks(d)
            assert len(result) == 1
            assert result[0]["name"] == "pretooluse-bash"

    def test_multiple_events(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            hooks_data = {
                "hooks": {
                    "PreToolUse": [
                        {"matcher": "Bash", "hooks": [], "description": "Pre bash"},
                    ],
                    "PostToolUse": [
                        {"matcher": "Edit", "hooks": [], "description": "Post edit"},
                    ],
                }
            }
            (d / "hooks.json").write_text(json.dumps(hooks_data))

            result = bm.discover_hooks(d)
            names = [e["name"] for e in result]
            assert "pretooluse-bash" in names
            assert "posttooluse-edit" in names

    def test_duplicate_matchers_get_suffix(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            hooks_data = {
                "hooks": {
                    "PreToolUse": [
                        {"matcher": "Bash", "hooks": [], "description": "First"},
                        {"matcher": "Bash", "hooks": [], "description": "Second"},
                    ]
                }
            }
            (d / "hooks.json").write_text(json.dumps(hooks_data))

            result = bm.discover_hooks(d)
            names = [e["name"] for e in result]
            assert "pretooluse-bash" in names
            assert "pretooluse-bash-2" in names

    def test_missing_hooks_json(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = bm.discover_hooks(Path(tmpdir))
            assert result == []

    def test_malformed_hooks_json(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "hooks.json").write_text("not valid json{{{")

            result = bm.discover_hooks(d)
            assert result == []

    def test_hook_entity_has_metadata(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            hooks_data = {
                "hooks": {
                    "Stop": [
                        {"matcher": "*", "hooks": [], "description": "Check logs"},
                    ]
                }
            }
            (d / "hooks.json").write_text(json.dumps(hooks_data))

            result = bm.discover_hooks(d)
            assert len(result) == 1
            meta = result[0]["metadata"]
            assert meta["event"] == "Stop"
            assert meta["matcher"] == "*"
            assert meta["description"] == "Check logs"


# ---------------------------------------------------------------------------
# Test: requires_adaptation
# ---------------------------------------------------------------------------

class TestRequiresAdaptation:
    def test_core_entity_no_adaptation(self):
        bm = _load_bm()
        tags = {"languages": ["python"], "frameworks": [], "categories": [], "scope": "language-specific"}
        assert bm.requires_adaptation(tags, is_core=True) is False

    def test_universal_no_adaptation(self):
        bm = _load_bm()
        tags = {"languages": [], "frameworks": [], "categories": ["planning"], "scope": "universal"}
        assert bm.requires_adaptation(tags, is_core=False) is False

    def test_language_specific_needs_adaptation(self):
        bm = _load_bm()
        tags = {"languages": ["python"], "frameworks": [], "categories": [], "scope": "language-specific"}
        assert bm.requires_adaptation(tags, is_core=False) is True

    def test_framework_specific_needs_adaptation(self):
        bm = _load_bm()
        tags = {"languages": [], "frameworks": ["django"], "categories": [], "scope": "framework-specific"}
        assert bm.requires_adaptation(tags, is_core=False) is True


# ---------------------------------------------------------------------------
# Test: build_coverage
# ---------------------------------------------------------------------------

class TestBuildCoverage:
    def test_aggregates_languages(self):
        bm = _load_bm()
        entities = [
            {"tags": {"languages": ["python"], "frameworks": [], "categories": []}},
            {"tags": {"languages": ["typescript"], "frameworks": [], "categories": []}},
        ]
        cov = bm.build_coverage(entities)
        assert "python" in cov["languages"]
        assert "typescript" in cov["languages"]

    def test_aggregates_frameworks(self):
        bm = _load_bm()
        entities = [
            {"tags": {"languages": [], "frameworks": ["django"], "categories": []}},
            {"tags": {"languages": [], "frameworks": ["react"], "categories": []}},
        ]
        cov = bm.build_coverage(entities)
        assert "django" in cov["frameworks"]
        assert "react" in cov["frameworks"]

    def test_deduplicates(self):
        bm = _load_bm()
        entities = [
            {"tags": {"languages": ["python"], "frameworks": [], "categories": ["testing"]}},
            {"tags": {"languages": ["python"], "frameworks": [], "categories": ["testing"]}},
        ]
        cov = bm.build_coverage(entities)
        assert cov["languages"].count("python") == 1
        assert cov["categories"].count("testing") == 1

    def test_empty_entities(self):
        bm = _load_bm()
        cov = bm.build_coverage([])
        assert cov == {"languages": [], "frameworks": [], "categories": []}

    def test_sorted_output(self):
        bm = _load_bm()
        entities = [
            {"tags": {"languages": ["typescript", "python"], "frameworks": [], "categories": []}},
        ]
        cov = bm.build_coverage(entities)
        assert cov["languages"] == sorted(cov["languages"])


# ---------------------------------------------------------------------------
# Test: load_source_meta
# ---------------------------------------------------------------------------

class TestLoadSourceMeta:
    def test_loads_valid_meta(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            meta = {"id": "test", "commit": "abc123", "synced_at": "2026-01-01T00:00:00+00:00"}
            (d / ".source-meta.json").write_text(json.dumps(meta))

            result = bm.load_source_meta(d)
            assert result is not None
            assert result["id"] == "test"
            assert result["commit"] == "abc123"

    def test_returns_none_on_missing(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = bm.load_source_meta(Path(tmpdir))
            assert result is None

    def test_returns_none_on_invalid_json(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / ".source-meta.json").write_text("not json{{{")

            result = bm.load_source_meta(d)
            assert result is None


# ---------------------------------------------------------------------------
# Test: Manifest output schema (integration)
# ---------------------------------------------------------------------------

class TestManifestOutputSchema:
    """Integration test using temp dirs with synthetic entity files."""

    @pytest.fixture
    def synthetic_catalog(self, tmp_path):
        """Create a minimal synthetic catalog for integration testing."""
        bm = _load_bm()

        # Create sources.json
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        sources_dir = catalog_dir / "sources"
        sources_dir.mkdir()

        sources = {
            "sources": [
                {
                    "id": "test-source",
                    "url": "https://example.com/test.git",
                    "branch": "main",
                    "pin": None,
                    "priority": 10,
                    "entityPaths": {
                        "agents": "agents",
                        "skills": "skills",
                        "commands": "commands",
                        "rules": "rules",
                        "hooks": "hooks",
                    },
                }
            ]
        }
        (catalog_dir / "sources.json").write_text(json.dumps(sources))

        # Create source directory with entities
        src_dir = sources_dir / "test-source"
        src_dir.mkdir()

        # .source-meta.json
        meta = {
            "id": "test-source",
            "url": "https://example.com/test.git",
            "branch": "main",
            "pin": None,
            "commit": "abc123",
            "synced_at": "2026-01-01T00:00:00+00:00",
        }
        (src_dir / ".source-meta.json").write_text(json.dumps(meta))

        # Agents
        agents_dir = src_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "planner.md").write_text("# Planner\nPlan project architecture.")
        (agents_dir / "python-reviewer.md").write_text("# Python Reviewer\nReview Python code quality.")

        # Skills
        skills_dir = src_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "tdd-workflow").mkdir()
        (skills_dir / "tdd-workflow" / "SKILL.md").write_text("# TDD Workflow\nTest-driven development.")

        # Commands
        commands_dir = src_dir / "commands"
        commands_dir.mkdir()
        (commands_dir / "plan.md").write_text("# Plan\nRun planning phase.")

        # Rules
        rules_dir = src_dir / "rules"
        rules_dir.mkdir()
        (rules_dir / "common").mkdir()
        (rules_dir / "common" / "security.md").write_text("# Security\nSecurity guidelines.")

        # Hooks
        hooks_dir = src_dir / "hooks"
        hooks_dir.mkdir()
        hooks_data = {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo"}], "description": "Pre bash"},
                ]
            }
        }
        (hooks_dir / "hooks.json").write_text(json.dumps(hooks_data))

        return tmp_path, bm

    def _run_manifest(self, synthetic_catalog):
        tmp_path, bm = synthetic_catalog
        catalog_dir = tmp_path / "catalog"

        # Patch paths to use temp directory
        with patch.object(bm, "SOURCES_JSON", catalog_dir / "sources.json"), \
             patch.object(bm, "SOURCES_DIR", catalog_dir / "sources"), \
             patch.object(bm, "OUTPUT_FILE", catalog_dir / "manifest.json"), \
             patch.object(bm, "PROJECT_ROOT", tmp_path):
            result = bm.main()

        assert result == 0
        manifest = json.loads((catalog_dir / "manifest.json").read_text())
        return manifest

    def test_output_has_required_top_level_fields(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        assert "entities" in manifest
        assert "coverage" in manifest
        assert "generatedAt" in manifest
        assert "sources" in manifest

    def test_entity_has_required_fields(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        required_fields = {"id", "source", "type", "name", "path", "tags", "coreEntity", "requiresAdaptation", "metadata"}
        for entity in manifest["entities"]:
            missing = required_fields - set(entity.keys())
            assert not missing, f"Entity {entity.get('id', '?')} missing fields: {missing}"

    def test_composite_id_format(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        for entity in manifest["entities"]:
            parts = entity["id"].split("::")
            assert len(parts) == 3, f"ID should have 3 parts: {entity['id']}"
            assert parts[0] == entity["source"]
            assert parts[1] == entity["type"]
            assert parts[2] == entity["name"]

    def test_tags_have_required_keys(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        for entity in manifest["entities"]:
            tags = entity["tags"]
            assert "languages" in tags
            assert "frameworks" in tags
            assert "categories" in tags
            assert "scope" in tags
            assert tags["scope"] in ("universal", "language-specific", "framework-specific")

    def test_core_entities_identified(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        core_ids = {e["id"] for e in manifest["entities"] if e["coreEntity"]}
        assert "test-source::agent::planner" in core_ids
        assert "test-source::command::plan" in core_ids
        assert "test-source::skill::tdd-workflow" in core_ids
        assert "test-source::rule::common/security" in core_ids

    def test_entities_sorted_by_id(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        ids = [e["id"] for e in manifest["entities"]]
        assert ids == sorted(ids)

    def test_coverage_lists_sorted(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        cov = manifest["coverage"]
        assert cov["languages"] == sorted(cov["languages"])
        assert cov["frameworks"] == sorted(cov["frameworks"])
        assert cov["categories"] == sorted(cov["categories"])

    def test_deterministic_output(self, synthetic_catalog):
        m1 = self._run_manifest(synthetic_catalog)
        m2 = self._run_manifest(synthetic_catalog)
        # Remove generatedAt for comparison
        m1.pop("generatedAt")
        m2.pop("generatedAt")
        assert m1 == m2

    def test_source_meta_included(self, synthetic_catalog):
        manifest = self._run_manifest(synthetic_catalog)
        assert "test-source" in manifest["sources"]
        assert manifest["sources"]["test-source"]["commit"] == "abc123"


# ---------------------------------------------------------------------------
# Test: main() error handling
# ---------------------------------------------------------------------------

class TestMainFunction:
    def test_returns_0_on_success(self):
        """main() returns 0 when run against real project sources."""
        bm = _load_bm()
        # Uses the real sources.json — requires at least sources.json to exist
        if not bm.SOURCES_JSON.exists():
            pytest.skip("sources.json not present")
        result = bm.main()
        assert result == 0

    def test_exits_on_missing_sources_json(self):
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(bm, "SOURCES_JSON", Path(tmpdir) / "nonexistent.json"):
                with pytest.raises(SystemExit) as exc_info:
                    bm.main()
                assert exc_info.value.code == 1

    def test_handles_empty_source_directories(self):
        """Sources with empty entity directories should produce 0 entities, not errors."""
        bm = _load_bm()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            catalog_dir = tmp / "catalog"
            catalog_dir.mkdir()
            sources_dir = catalog_dir / "sources"
            sources_dir.mkdir()

            # Create a source with empty dirs
            src_dir = sources_dir / "empty-source"
            src_dir.mkdir()
            for d in ["agents", "skills", "commands", "rules"]:
                (src_dir / d).mkdir()

            sources = {
                "sources": [
                    {
                        "id": "empty-source",
                        "url": None,
                        "branch": None,
                        "pin": None,
                        "priority": 1,
                        "entityPaths": {
                            "agents": "agents",
                            "skills": "skills",
                            "commands": "commands",
                            "rules": "rules",
                        },
                    }
                ]
            }
            (catalog_dir / "sources.json").write_text(json.dumps(sources))

            with patch.object(bm, "SOURCES_JSON", catalog_dir / "sources.json"), \
                 patch.object(bm, "SOURCES_DIR", sources_dir), \
                 patch.object(bm, "OUTPUT_FILE", catalog_dir / "manifest.json"), \
                 patch.object(bm, "PROJECT_ROOT", tmp):
                result = bm.main()

            assert result == 0
            manifest = json.loads((catalog_dir / "manifest.json").read_text())
            assert len(manifest["entities"]) == 0
