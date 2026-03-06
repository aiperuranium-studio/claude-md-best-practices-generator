"""
Metadata Consistency Tests

Validates:
  - Version consistency across pyproject.toml, plugin.json, and marketplace.json
  - Marketplace skill coverage (all plugin.json skills appear in marketplace.json text)
  - USER_AGENT in fetch-guidelines.py is not a hardcoded stale version
"""

import json
import re
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"
PLUGIN_JSON = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = PROJECT_ROOT / ".claude-plugin" / "marketplace.json"
FETCH_GUIDELINES = PROJECT_ROOT / "skills" / "refresh-guidelines" / "scripts" / "fetch-guidelines.py"


def _extract_pyproject_version(text: str) -> str:
    """Extract version from pyproject.toml text using regex (stdlib only)."""
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise ValueError("version not found in pyproject.toml")
    return match.group(1)


# ===================================================================
# 1. Version consistency across pyproject.toml, plugin.json, marketplace.json
# ===================================================================


class TestVersionConsistency(unittest.TestCase):
    """Versions in pyproject.toml, plugin.json, and marketplace.json must agree."""

    @classmethod
    def setUpClass(cls):
        cls.pyproject_text = PYPROJECT_TOML.read_text(encoding="utf-8")
        cls.pyproject_version = _extract_pyproject_version(cls.pyproject_text)

        with open(PLUGIN_JSON, encoding="utf-8") as f:
            cls.plugin = json.load(f)

        with open(MARKETPLACE_JSON, encoding="utf-8") as f:
            cls.marketplace = json.load(f)

    def test_pyproject_version_not_empty(self):
        self.assertGreater(
            len(self.pyproject_version), 0,
            "pyproject.toml version must not be empty",
        )

    def test_plugin_json_version_not_empty(self):
        plugin_version = self.plugin.get("version", "")
        self.assertGreater(
            len(plugin_version), 0,
            "plugin.json version must not be empty",
        )

    def test_marketplace_json_version_not_empty(self):
        # marketplace.json may carry version at top-level or in plugins[0]
        marketplace_version = self.marketplace.get("version") or (
            self.marketplace.get("plugins", [{}])[0].get("version", "")
            if self.marketplace.get("plugins")
            else ""
        )
        self.assertGreater(
            len(str(marketplace_version)), 0,
            "marketplace.json must contain a version field (top-level or in plugins[0])",
        )

    def test_plugin_json_version_matches_pyproject(self):
        plugin_version = self.plugin.get("version", "")
        self.assertEqual(
            self.pyproject_version,
            plugin_version,
            f"plugin.json version ({plugin_version!r}) must match "
            f"pyproject.toml version ({self.pyproject_version!r})",
        )

    def test_marketplace_json_version_matches_pyproject(self):
        # Accept version at top-level or in plugins[0].version
        marketplace_version = self.marketplace.get("version")
        if marketplace_version is None and self.marketplace.get("plugins"):
            marketplace_version = self.marketplace["plugins"][0].get("version", "")

        self.assertEqual(
            self.pyproject_version,
            marketplace_version,
            f"marketplace.json version ({marketplace_version!r}) must match "
            f"pyproject.toml version ({self.pyproject_version!r})",
        )


# ===================================================================
# 2. Marketplace skill coverage
# ===================================================================


class TestMarketplaceSkillCoverage(unittest.TestCase):
    """Each skill registered in plugin.json must appear in marketplace.json text."""

    @classmethod
    def setUpClass(cls):
        with open(PLUGIN_JSON, encoding="utf-8") as f:
            cls.plugin = json.load(f)

        with open(MARKETPLACE_JSON, encoding="utf-8") as f:
            cls.marketplace = json.load(f)

        # Use the full JSON text as the search corpus — covers all description fields
        cls.marketplace_text = MARKETPLACE_JSON.read_text(encoding="utf-8")

    def _skill_names(self):
        """Extract skill names from plugin.json skills list."""
        names = []
        for skill_path in self.plugin.get("skills", []):
            # e.g. "./skills/refresh-guidelines/" -> "refresh-guidelines"
            parts = [p for p in skill_path.replace("./", "").split("/") if p]
            # The skill name is the last non-empty path component under skills/
            if len(parts) >= 2 and parts[0] == "skills":
                names.append(parts[1])
        return names

    def test_skills_list_is_not_empty(self):
        self.assertGreater(
            len(self.plugin.get("skills", [])), 0,
            "plugin.json skills list must not be empty",
        )

    def test_refresh_guidelines_in_marketplace(self):
        self.assertIn(
            "refresh-guidelines",
            self.marketplace_text,
            "marketplace.json must mention 'refresh-guidelines'",
        )

    def test_refactor_claude_md_in_marketplace(self):
        self.assertIn(
            "refactor-claude-md",
            self.marketplace_text,
            "marketplace.json must mention 'refactor-claude-md'",
        )

    def test_scaffold_claude_md_in_marketplace(self):
        self.assertIn(
            "scaffold-claude-md",
            self.marketplace_text,
            "marketplace.json must mention 'scaffold-claude-md'",
        )

    def test_all_plugin_skills_covered(self):
        skill_names = self._skill_names()
        self.assertGreater(len(skill_names), 0, "Could not extract any skill names from plugin.json")
        for skill_name in skill_names:
            self.assertIn(
                skill_name,
                self.marketplace_text,
                f"marketplace.json must mention skill '{skill_name}' from plugin.json",
            )


# ===================================================================
# 3. USER_AGENT version in fetch-guidelines.py
# ===================================================================


class TestUserAgentVersion(unittest.TestCase):
    """USER_AGENT in fetch-guidelines.py must not contain a stale hardcoded version."""

    @classmethod
    def setUpClass(cls):
        cls.fetch_text = FETCH_GUIDELINES.read_text(encoding="utf-8")
        cls.pyproject_version = _extract_pyproject_version(
            PYPROJECT_TOML.read_text(encoding="utf-8")
        )

    def _find_user_agent_line(self) -> str | None:
        """Return the source line that defines USER_AGENT, or None."""
        for line in self.fetch_text.splitlines():
            if re.match(r"^USER_AGENT\s*=", line):
                return line
        return None

    def test_user_agent_line_exists(self):
        line = self._find_user_agent_line()
        self.assertIsNotNone(line, "fetch-guidelines.py must define USER_AGENT")

    def test_user_agent_not_hardcoded_old_version(self):
        """USER_AGENT must not reference a version older than the current pyproject version."""
        line = self._find_user_agent_line()
        if line is None:
            self.skipTest("USER_AGENT line not found")

        # Check for obviously stale versions (3.0, 3.1) that are behind current 3.2+
        stale_patterns = [r"/3\.0[^.]", r"/3\.1[^.]"]
        for pattern in stale_patterns:
            self.assertIsNone(
                re.search(pattern, line),
                f"USER_AGENT contains a stale version matching {pattern!r}: {line!r}. "
                f"Current project version is {self.pyproject_version!r}. "
                "Fix: make USER_AGENT dynamic (read from pyproject.toml) or update the literal.",
            )

    def test_user_agent_version_is_current_or_dynamic(self):
        """If USER_AGENT is a string literal, it must contain the current project version."""
        line = self._find_user_agent_line()
        if line is None:
            self.skipTest("USER_AGENT line not found")

        # If the line is a plain string assignment (not a function call / f-string building
        # the version dynamically), assert the current version is present.
        is_literal = re.search(r'USER_AGENT\s*=\s*["\']', line)
        is_dynamic = re.search(r'USER_AGENT\s*=\s*f["\']', line) or (
            # Non-literal: references a variable rather than a bare string
            re.search(r'USER_AGENT\s*=\s*\w+\s*\+', line)
            or re.search(r'USER_AGENT\s*=\s*[^"\']', line)
        )

        if is_literal and not is_dynamic:
            # It's a plain string literal — the version it embeds must match pyproject
            # Extract major.minor from pyproject version for comparison
            major_minor = ".".join(self.pyproject_version.split(".")[:2])
            self.assertIn(
                major_minor,
                line,
                f"USER_AGENT string literal must contain the current version "
                f"({major_minor!r} from pyproject.toml {self.pyproject_version!r}). "
                f"Got: {line!r}. Update the literal or make it dynamic.",
            )


if __name__ == "__main__":
    unittest.main()
