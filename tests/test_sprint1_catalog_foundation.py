"""
Sprint 1: Catalog Foundation — Unit Tests

Validates all acceptance criteria for Sprint 1:
  - catalog/sources.json is valid JSON with correct schema and sources
  - catalog/sources/local/README.md exists and has meaningful content
  - catalog/sources/local/ subdirectories exist for all entity types
  - docs/SOURCE-SCHEMA.md exists and documents all source fields
  - sources.json schema correctness (field types, values, constraints)
"""

import json
import unittest
from pathlib import Path

# Project root: tests/ lives one level below project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCES_JSON = PROJECT_ROOT / "catalog" / "sources.json"
LOCAL_SOURCE_DIR = PROJECT_ROOT / "catalog" / "sources" / "local"
LOCAL_README = LOCAL_SOURCE_DIR / "README.md"
SOURCE_SCHEMA_DOC = PROJECT_ROOT / "docs" / "SOURCE-SCHEMA.md"

# Required fields per source entry, with expected types
REQUIRED_SOURCE_FIELDS = {
    "id": str,
    "url": (str, type(None)),
    "branch": (str, type(None)),
    "pin": (str, type(None)),
    "priority": int,
    "entityPaths": dict,
}

# Entity types that must appear in the local source subdirectories
LOCAL_ENTITY_TYPES = ["agents", "skills", "commands", "rules"]

# All possible entity types recognized by the system
ALL_ENTITY_TYPES = ["agents", "skills", "commands", "rules", "hooks"]


class TestSourcesJsonExists(unittest.TestCase):
    """Verify sources.json exists and is valid JSON."""

    def test_file_exists(self):
        self.assertTrue(SOURCES_JSON.exists(), f"{SOURCES_JSON} does not exist")

    def test_valid_json(self):
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_has_sources_array(self):
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        self.assertIn("sources", data)
        self.assertIsInstance(data["sources"], list)


class TestSourcesJsonContent(unittest.TestCase):
    """Validate the content and schema of sources.json."""

    @classmethod
    def setUpClass(cls):
        with open(SOURCES_JSON) as f:
            cls.data = json.load(f)
        cls.sources = cls.data["sources"]
        cls.source_map = {s["id"]: s for s in cls.sources}

    def test_exactly_two_sources(self):
        self.assertEqual(len(self.sources), 2)

    def test_expected_source_ids(self):
        ids = {s["id"] for s in self.sources}
        self.assertEqual(ids, {"everything-claude-code", "local"})

    def test_unique_source_ids(self):
        ids = [s["id"] for s in self.sources]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate source IDs found")

    def test_all_required_fields_present(self):
        for source in self.sources:
            for field in REQUIRED_SOURCE_FIELDS:
                self.assertIn(
                    field, source, f"Source '{source.get('id', '?')}' missing field '{field}'"
                )

    def test_field_types(self):
        for source in self.sources:
            for field, expected_type in REQUIRED_SOURCE_FIELDS.items():
                self.assertIsInstance(
                    source[field],
                    expected_type,
                    f"Source '{source['id']}' field '{field}' has wrong type: "
                    f"expected {expected_type}, got {type(source[field])}",
                )


class TestEverythingClaudeCodeSource(unittest.TestCase):
    """Validate the everything-claude-code remote source entry."""

    @classmethod
    def setUpClass(cls):
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        cls.source = next(s for s in data["sources"] if s["id"] == "everything-claude-code")

    def test_has_url(self):
        self.assertIsNotNone(self.source["url"])
        self.assertTrue(
            self.source["url"].startswith("https://"),
            "URL should use HTTPS",
        )

    def test_url_is_git(self):
        self.assertTrue(
            self.source["url"].endswith(".git"),
            "URL should end with .git",
        )

    def test_branch_is_main(self):
        self.assertEqual(self.source["branch"], "main")

    def test_pin_is_null(self):
        self.assertIsNone(self.source["pin"])

    def test_priority_is_10(self):
        self.assertEqual(self.source["priority"], 10)

    def test_entity_paths_include_all_types(self):
        for entity_type in ALL_ENTITY_TYPES:
            self.assertIn(
                entity_type,
                self.source["entityPaths"],
                f"Missing entityPath for '{entity_type}'",
            )

    def test_entity_paths_are_strings(self):
        for key, value in self.source["entityPaths"].items():
            self.assertIsInstance(value, str, f"entityPath '{key}' should be a string")


class TestLocalSource(unittest.TestCase):
    """Validate the local source entry."""

    @classmethod
    def setUpClass(cls):
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        cls.source = next(s for s in data["sources"] if s["id"] == "local")

    def test_url_is_null(self):
        self.assertIsNone(self.source["url"], "Local source should have null url")

    def test_branch_is_null(self):
        self.assertIsNone(self.source["branch"], "Local source should have null branch")

    def test_pin_is_null(self):
        self.assertIsNone(self.source["pin"])

    def test_priority_is_1(self):
        self.assertEqual(
            self.source["priority"], 1, "Local source must have the highest priority (1)"
        )

    def test_local_priority_wins(self):
        """Local source priority must be lower (= higher precedence) than all others."""
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        for source in data["sources"]:
            if source["id"] != "local":
                self.assertLess(
                    self.source["priority"],
                    source["priority"],
                    f"Local priority ({self.source['priority']}) must be less than "
                    f"'{source['id']}' priority ({source['priority']})",
                )

    def test_entity_paths_include_core_types(self):
        for entity_type in LOCAL_ENTITY_TYPES:
            self.assertIn(
                entity_type,
                self.source["entityPaths"],
                f"Local source missing entityPath for '{entity_type}'",
            )

    def test_no_hooks_in_local(self):
        self.assertNotIn(
            "hooks",
            self.source["entityPaths"],
            "Local source should not define hooks entityPath",
        )


class TestPriorityConstraints(unittest.TestCase):
    """Validate priority values and ordering constraints."""

    @classmethod
    def setUpClass(cls):
        with open(SOURCES_JSON) as f:
            data = json.load(f)
        cls.sources = data["sources"]

    def test_all_priorities_are_positive(self):
        for source in self.sources:
            self.assertGreater(
                source["priority"], 0, f"Source '{source['id']}' has non-positive priority"
            )

    def test_unique_priorities(self):
        priorities = [s["priority"] for s in self.sources]
        self.assertEqual(len(priorities), len(set(priorities)), "Duplicate priority values found")

    def test_id_is_valid_directory_name(self):
        for source in self.sources:
            self.assertRegex(
                source["id"],
                r"^[a-z0-9][a-z0-9\-]*$",
                f"Source ID '{source['id']}' is not a valid directory name",
            )


class TestLocalSourceDirectory(unittest.TestCase):
    """Validate the local source directory structure."""

    def test_local_dir_exists(self):
        self.assertTrue(LOCAL_SOURCE_DIR.is_dir(), f"{LOCAL_SOURCE_DIR} does not exist")

    def test_subdirectories_exist(self):
        for entity_type in LOCAL_ENTITY_TYPES:
            subdir = LOCAL_SOURCE_DIR / entity_type
            self.assertTrue(subdir.is_dir(), f"{subdir} does not exist")

    def test_subdirectories_have_gitkeep(self):
        for entity_type in LOCAL_ENTITY_TYPES:
            gitkeep = LOCAL_SOURCE_DIR / entity_type / ".gitkeep"
            self.assertTrue(gitkeep.exists(), f"{gitkeep} does not exist")


class TestLocalReadme(unittest.TestCase):
    """Validate the local source README."""

    def test_readme_exists(self):
        self.assertTrue(LOCAL_README.exists(), f"{LOCAL_README} does not exist")

    def test_readme_is_not_empty(self):
        content = LOCAL_README.read_text()
        self.assertGreater(len(content.strip()), 0, "README.md is empty")

    def test_readme_has_title(self):
        content = LOCAL_README.read_text()
        self.assertTrue(content.startswith("# "), "README.md should start with a markdown heading")

    def test_readme_mentions_entity_types(self):
        content = LOCAL_README.read_text().lower()
        for entity_type in LOCAL_ENTITY_TYPES:
            self.assertIn(
                entity_type,
                content,
                f"README.md should mention '{entity_type}'",
            )

    def test_readme_explains_priority(self):
        content = LOCAL_README.read_text().lower()
        self.assertIn("priority", content, "README.md should explain priority behavior")


class TestSourceSchemaDoc(unittest.TestCase):
    """Validate the SOURCE-SCHEMA.md documentation."""

    @classmethod
    def setUpClass(cls):
        cls.content = SOURCE_SCHEMA_DOC.read_text()
        cls.content_lower = cls.content.lower()

    def test_file_exists(self):
        self.assertTrue(SOURCE_SCHEMA_DOC.exists(), f"{SOURCE_SCHEMA_DOC} does not exist")

    def test_not_empty(self):
        self.assertGreater(len(self.content.strip()), 0)

    def test_documents_all_source_fields(self):
        for field in REQUIRED_SOURCE_FIELDS:
            self.assertIn(
                f"`{field}`",
                self.content,
                f"SOURCE-SCHEMA.md should document the '{field}' field",
            )

    def test_documents_priority_resolution(self):
        self.assertIn(
            "priority",
            self.content_lower,
            "Should document priority resolution",
        )

    def test_documents_entity_paths(self):
        self.assertIn("entitypaths", self.content_lower)

    def test_documents_source_meta_json(self):
        self.assertIn(
            ".source-meta.json",
            self.content,
            "Should document the sync metadata file",
        )

    def test_documents_source_meta_fields(self):
        meta_fields = ["synced_at", "commit"]
        for field in meta_fields:
            self.assertIn(
                field,
                self.content,
                f"SOURCE-SCHEMA.md should document .source-meta.json field '{field}'",
            )


if __name__ == "__main__":
    unittest.main()
