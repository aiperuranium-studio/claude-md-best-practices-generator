"""
Refactor & Scaffold Skills — Unit Tests

Validates:
  - /refactor-claude-md skill files exist and are well-formed
  - /scaffold-claude-md skill files exist and are well-formed
  - Reference files exist and contain expected structure
  - Compliance checklist is a derivation procedure (no hardcoded §-references)
  - Directory assessment criteria cover RECOMMEND/SKIP/OPTIONAL
  - rules/claude-md-standards.md exists with pointer-based design
  - plugin.json includes all three skills
  - Root CLAUDE.md documents all three skills
"""

import json
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# /refactor-claude-md skill paths
REFACTOR_SKILL_DIR = (
    PROJECT_ROOT / "skills" / "refactor-claude-md"
)
REFACTOR_SKILL_MD = REFACTOR_SKILL_DIR / "SKILL.md"
REFACTOR_CLAUDE_MD = REFACTOR_SKILL_DIR / "CLAUDE.md"
REFACTOR_CHECKLIST = REFACTOR_SKILL_DIR / "references" / "compliance-checklist.md"

# /scaffold-claude-md skill paths
SCAFFOLD_SKILL_DIR = (
    PROJECT_ROOT / "skills" / "scaffold-claude-md"
)
SCAFFOLD_SKILL_MD = SCAFFOLD_SKILL_DIR / "SKILL.md"
SCAFFOLD_CLAUDE_MD = SCAFFOLD_SKILL_DIR / "CLAUDE.md"
SCAFFOLD_ASSESSMENT = SCAFFOLD_SKILL_DIR / "references" / "directory-assessment.md"

# Shared paths
RULES_FILE = PROJECT_ROOT / "rules" / "claude-md-standards.md"
PLUGIN_MANIFEST = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
ROOT_CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"


# ===================================================================
# 1. /refactor-claude-md — File existence and structure
# ===================================================================


class TestRefactorSkillFileExists(unittest.TestCase):
    """SKILL.md for /refactor-claude-md exists with required structure."""

    def test_skill_md_exists(self):
        self.assertTrue(REFACTOR_SKILL_MD.exists(), f"Missing: {REFACTOR_SKILL_MD}")

    def test_skill_md_not_empty(self):
        self.assertGreater(len(REFACTOR_SKILL_MD.read_text().strip()), 0)

    def test_claude_md_exists(self):
        self.assertTrue(REFACTOR_CLAUDE_MD.exists(), f"Missing: {REFACTOR_CLAUDE_MD}")

    def test_references_dir_exists(self):
        refs_dir = REFACTOR_SKILL_DIR / "references"
        self.assertTrue(refs_dir.is_dir(), f"Missing: {refs_dir}")

    def test_compliance_checklist_exists(self):
        self.assertTrue(REFACTOR_CHECKLIST.exists(), f"Missing: {REFACTOR_CHECKLIST}")

    def test_compliance_checklist_not_empty(self):
        self.assertGreater(len(REFACTOR_CHECKLIST.read_text().strip()), 0)


class TestRefactorSkillFrontmatter(unittest.TestCase):
    """Validate /refactor-claude-md SKILL.md has proper YAML frontmatter."""

    @classmethod
    def setUpClass(cls):
        cls.content = REFACTOR_SKILL_MD.read_text()
        cls.lines = cls.content.splitlines()

    def test_starts_with_yaml_delimiter(self):
        self.assertEqual(
            self.lines[0], "---",
            "SKILL.md must start with --- (YAML frontmatter block)",
        )

    def test_has_closing_yaml_delimiter(self):
        closing_indices = [i for i, line in enumerate(self.lines[1:], 1) if line == "---"]
        self.assertGreater(
            len(closing_indices), 0, "SKILL.md must have a closing --- for frontmatter"
        )

    def test_frontmatter_has_name(self):
        self.assertIn("name:", self.content)

    def test_frontmatter_name_value(self):
        for line in self.lines:
            if line.strip().startswith("name:"):
                self.assertIn("refactor-claude-md", line)
                return
        self.fail("name key not found in frontmatter")

    def test_frontmatter_has_description(self):
        self.assertIn("description:", self.content)

    def test_frontmatter_has_disable_model_invocation(self):
        self.assertIn("disable-model-invocation:", self.content)

    def test_disable_model_invocation_is_true(self):
        for line in self.lines:
            if "disable-model-invocation:" in line:
                self.assertIn(
                    "true", line.lower(),
                    "disable-model-invocation must be set to true",
                )
                return
        self.fail("disable-model-invocation key not found in SKILL.md")

    def test_frontmatter_has_allowed_tools(self):
        self.assertIn("allowed-tools:", self.content)


class TestRefactorSkillProcedure(unittest.TestCase):
    """Validate /refactor-claude-md SKILL.md contains required procedure steps."""

    @classmethod
    def setUpClass(cls):
        cls.content = REFACTOR_SKILL_MD.read_text()

    def test_has_step_0_source_selection(self):
        self.assertIn("Step 0", self.content)
        self.assertIn("ource selection", self.content)  # "Source selection" case-insensitive start

    def test_has_step_1_read_guidelines(self):
        self.assertIn("Step 1", self.content)

    def test_has_step_5_human_approval(self):
        self.assertIn("Step 5", self.content)
        self.assertIn("approval", self.content.lower())

    def test_has_step_7_verify(self):
        self.assertIn("Step 7", self.content)

    def test_references_compliance_checklist(self):
        self.assertIn("compliance-checklist.md", self.content)

    def test_never_auto_approve_instruction(self):
        self.assertIn("Never auto-approve", self.content)


# ===================================================================
# 2. /scaffold-claude-md — File existence and structure
# ===================================================================


class TestScaffoldSkillFileExists(unittest.TestCase):
    """SKILL.md for /scaffold-claude-md exists with required structure."""

    def test_skill_md_exists(self):
        self.assertTrue(SCAFFOLD_SKILL_MD.exists(), f"Missing: {SCAFFOLD_SKILL_MD}")

    def test_skill_md_not_empty(self):
        self.assertGreater(len(SCAFFOLD_SKILL_MD.read_text().strip()), 0)

    def test_claude_md_exists(self):
        self.assertTrue(SCAFFOLD_CLAUDE_MD.exists(), f"Missing: {SCAFFOLD_CLAUDE_MD}")

    def test_references_dir_exists(self):
        refs_dir = SCAFFOLD_SKILL_DIR / "references"
        self.assertTrue(refs_dir.is_dir(), f"Missing: {refs_dir}")

    def test_directory_assessment_exists(self):
        self.assertTrue(SCAFFOLD_ASSESSMENT.exists(), f"Missing: {SCAFFOLD_ASSESSMENT}")

    def test_directory_assessment_not_empty(self):
        self.assertGreater(len(SCAFFOLD_ASSESSMENT.read_text().strip()), 0)


class TestScaffoldSkillFrontmatter(unittest.TestCase):
    """Validate /scaffold-claude-md SKILL.md has proper YAML frontmatter."""

    @classmethod
    def setUpClass(cls):
        cls.content = SCAFFOLD_SKILL_MD.read_text()
        cls.lines = cls.content.splitlines()

    def test_starts_with_yaml_delimiter(self):
        self.assertEqual(
            self.lines[0], "---",
            "SKILL.md must start with --- (YAML frontmatter block)",
        )

    def test_has_closing_yaml_delimiter(self):
        closing_indices = [i for i, line in enumerate(self.lines[1:], 1) if line == "---"]
        self.assertGreater(
            len(closing_indices), 0, "SKILL.md must have a closing --- for frontmatter"
        )

    def test_frontmatter_has_name(self):
        self.assertIn("name:", self.content)

    def test_frontmatter_name_value(self):
        for line in self.lines:
            if line.strip().startswith("name:"):
                self.assertIn("scaffold-claude-md", line)
                return
        self.fail("name key not found in frontmatter")

    def test_frontmatter_has_description(self):
        self.assertIn("description:", self.content)

    def test_frontmatter_has_disable_model_invocation(self):
        self.assertIn("disable-model-invocation:", self.content)

    def test_disable_model_invocation_is_true(self):
        for line in self.lines:
            if "disable-model-invocation:" in line:
                self.assertIn(
                    "true", line.lower(),
                    "disable-model-invocation must be set to true",
                )
                return
        self.fail("disable-model-invocation key not found in SKILL.md")

    def test_frontmatter_has_allowed_tools(self):
        self.assertIn("allowed-tools:", self.content)


class TestScaffoldSkillProcedure(unittest.TestCase):
    """Validate /scaffold-claude-md SKILL.md contains required procedure steps."""

    @classmethod
    def setUpClass(cls):
        cls.content = SCAFFOLD_SKILL_MD.read_text()

    def test_has_step_0_load_guidelines(self):
        self.assertIn("Step 0", self.content)

    def test_has_step_1_scan_project(self):
        self.assertIn("Step 1", self.content)
        self.assertIn("can project", self.content)  # "Scan project"

    def test_has_step_5_present_proposals(self):
        self.assertIn("Step 5", self.content)
        self.assertIn("approval", self.content.lower())

    def test_has_step_6_write(self):
        self.assertIn("Step 6", self.content)

    def test_references_directory_assessment(self):
        self.assertIn("directory-assessment.md", self.content)

    def test_never_auto_approve_instruction(self):
        self.assertIn("Never auto-approve", self.content)

    def test_never_overwrite_existing(self):
        self.assertIn("Never overwrite", self.content)


# ===================================================================
# 3. Compliance checklist — Pointer-based design
# ===================================================================


class TestComplianceChecklistDesign(unittest.TestCase):
    """Validate compliance-checklist.md is a derivation procedure, not a static list."""

    @classmethod
    def setUpClass(cls):
        cls.content = REFACTOR_CHECKLIST.read_text()

    def test_describes_derivation_procedure(self):
        # Must describe a procedure, not a fixed checklist
        self.assertIn("procedure", self.content.lower())

    def test_no_hardcoded_section_references(self):
        # Must NOT contain §-style references like §1.3, §2.1, etc.
        import re
        matches = re.findall(r"§\d+\.\d+", self.content)
        self.assertEqual(
            len(matches), 0,
            f"Compliance checklist must not contain hardcoded §-references, found: {matches}",
        )

    def test_has_structural_category(self):
        self.assertIn("Structural", self.content)

    def test_has_content_category(self):
        self.assertIn("Content", self.content)

    def test_has_integration_category(self):
        self.assertIn("Integration", self.content)

    def test_has_behavioral_category(self):
        self.assertIn("Behavioral", self.content)

    def test_has_rating_scale(self):
        self.assertIn("PASS", self.content)
        self.assertIn("PARTIAL", self.content)
        self.assertIn("FAIL", self.content)
        self.assertIn("N/A", self.content)

    def test_references_sota_parts(self):
        # Should reference SOTA Part numbers generically (Part 1, Part 2, etc.)
        self.assertIn("Part 1", self.content)
        self.assertIn("Part 2", self.content)

    def test_has_report_format(self):
        self.assertIn("Report Format", self.content)


# ===================================================================
# 4. Directory assessment — Criteria structure
# ===================================================================


class TestDirectoryAssessmentCriteria(unittest.TestCase):
    """Validate directory-assessment.md covers all classification types."""

    @classmethod
    def setUpClass(cls):
        cls.content = SCAFFOLD_ASSESSMENT.read_text()

    def test_has_recommend_section(self):
        self.assertIn("RECOMMEND", self.content)

    def test_has_skip_section(self):
        self.assertIn("SKIP", self.content)

    def test_has_optional_section(self):
        self.assertIn("OPTIONAL", self.content)

    def test_no_hardcoded_section_references(self):
        import re
        matches = re.findall(r"§\d+\.\d+", self.content)
        self.assertEqual(
            len(matches), 0,
            f"Directory assessment must not contain hardcoded §-references, found: {matches}",
        )

    def test_defers_to_sota_for_placement(self):
        # Must indicate that SOTA placement rules take precedence
        self.assertIn("supplement", self.content.lower())

    def test_has_content_scope_guidance(self):
        self.assertIn("Content Scope", self.content)


# ===================================================================
# 5. Rules file — Pointer-based design
# ===================================================================


class TestRulesFileDesign(unittest.TestCase):
    """Validate rules/claude-md-standards.md uses pointer-based approach."""

    def test_rules_file_exists(self):
        self.assertTrue(RULES_FILE.exists(), f"Missing: {RULES_FILE}")

    def test_rules_file_not_empty(self):
        self.assertGreater(len(RULES_FILE.read_text().strip()), 0)

    def test_points_to_enriched_file(self):
        content = RULES_FILE.read_text()
        self.assertIn("CLAUDE-MD-SOTA.enriched.md", content)

    def test_points_to_seed_file(self):
        content = RULES_FILE.read_text()
        self.assertIn("CLAUDE-MD-SOTA.md", content)

    def test_no_hardcoded_section_references(self):
        import re
        content = RULES_FILE.read_text()
        matches = re.findall(r"§\d+\.\d+", content)
        self.assertEqual(
            len(matches), 0,
            f"Rules file must not contain hardcoded §-references, found: {matches}",
        )

    def test_no_hardcoded_line_count(self):
        content = RULES_FILE.read_text()
        # Should NOT hardcode "300 lines" or "<300" — that's a SOTA rule
        self.assertNotIn("300 lines", content)
        self.assertNotIn("<300", content)

    def test_has_cross_referencing_convention(self):
        content = RULES_FILE.read_text()
        self.assertIn("cross-referenc", content.lower())


# ===================================================================
# 6. Plugin manifest — All skills registered
# ===================================================================


class TestPluginManifestAllSkills(unittest.TestCase):
    """Validate plugin.json includes all three skills."""

    @classmethod
    def setUpClass(cls):
        if not PLUGIN_MANIFEST.exists():
            raise unittest.SkipTest(
                ".claude-plugin/plugin.json not present"
            )
        with open(PLUGIN_MANIFEST) as f:
            cls.manifest = json.load(f)

    def test_skills_field_is_list(self):
        self.assertIn("skills", self.manifest)
        self.assertIsInstance(self.manifest["skills"], list)

    def test_has_refresh_guidelines_skill(self):
        skills = self.manifest["skills"]
        self.assertTrue(
            any("refresh-guidelines" in s for s in skills),
            "plugin.json must include refresh-guidelines skill",
        )

    def test_has_refactor_claude_md_skill(self):
        skills = self.manifest["skills"]
        self.assertTrue(
            any("refactor-claude-md" in s for s in skills),
            "plugin.json must include refactor-claude-md skill",
        )

    def test_has_scaffold_claude_md_skill(self):
        skills = self.manifest["skills"]
        self.assertTrue(
            any("scaffold-claude-md" in s for s in skills),
            "plugin.json must include scaffold-claude-md skill",
        )

    def test_skill_paths_start_with_dot_slash(self):
        for skill_path in self.manifest["skills"]:
            self.assertTrue(
                skill_path.startswith("./"),
                f"Skill path must start with ./ — got: {skill_path}",
            )


# ===================================================================
# 7. Root CLAUDE.md — Documents all skills
# ===================================================================


class TestRootClaudeMdSkillDocumentation(unittest.TestCase):
    """Validate root CLAUDE.md documents all three skills."""

    @classmethod
    def setUpClass(cls):
        cls.content = ROOT_CLAUDE_MD.read_text()

    def test_documents_refresh_guidelines(self):
        self.assertIn("/refresh-guidelines", self.content)

    def test_documents_refactor_claude_md(self):
        self.assertIn("/refactor-claude-md", self.content)

    def test_documents_scaffold_claude_md(self):
        self.assertIn("/scaffold-claude-md", self.content)

    def test_project_structure_lists_refactor_skill_dir(self):
        self.assertIn("skills/refactor-claude-md/", self.content)

    def test_project_structure_lists_scaffold_skill_dir(self):
        self.assertIn("skills/scaffold-claude-md/", self.content)

    def test_project_structure_lists_rules_dir(self):
        self.assertIn("rules/", self.content)


if __name__ == "__main__":
    unittest.main()
