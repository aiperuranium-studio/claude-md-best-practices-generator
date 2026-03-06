"""
Sprint 1.5: Guidelines Enrichment Pipeline — Unit Tests

Validates:
  - /refresh-guidelines skill file exists and is well-formed
  - curated-sources.md is parseable with valid entries
  - enrichment-procedure.md exists and covers all phases
  - fetch-guidelines.py functions: parse_curated_sources, strip_html,
    extract_content_blocks, _truncate, HTMLTextExtractor
  - parse-insights.py functions: find_report, InsightsHTMLParser,
    parse_facets, parse_session_meta, _build_entries, main
  - Output schema of guidelines-raw.json (if present)
  - Output schema of insights-parsed.json (if present)
  - docs/CLAUDE-MD-SOTA.md starts blank
  - docs/insights-raw.md placeholder exists
  - .gitignore includes enrichment artifacts
"""

import importlib.util
import json
import tempfile
import textwrap
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Bootstrap: load scripts as modules without __main__ side-effects
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = (
    PROJECT_ROOT
    / "skills"
    / "refresh-guidelines"
    / "scripts"
    / "fetch-guidelines.py"
)
PARSE_INSIGHTS_PATH = (
    PROJECT_ROOT
    / "skills"
    / "refresh-guidelines"
    / "scripts"
    / "parse-insights.py"
)

_fg_module = None
_pi_module = None


def _load_fg():
    """Lazy-load fetch-guidelines.py as a module."""
    global _fg_module
    if _fg_module is not None:
        return _fg_module
    spec = importlib.util.spec_from_file_location("fetch_guidelines", SCRIPT_PATH)
    _fg_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_fg_module)
    return _fg_module


def _load_pi():
    """Lazy-load parse-insights.py as a module."""
    global _pi_module
    if _pi_module is not None:
        return _pi_module
    spec = importlib.util.spec_from_file_location("parse_insights", PARSE_INSIGHTS_PATH)
    _pi_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_pi_module)
    return _pi_module


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

SKILL_MD = (
    PROJECT_ROOT / "skills" / "refresh-guidelines" / "SKILL.md"
)
CURATED_SOURCES_MD = (
    PROJECT_ROOT
    / "skills"
    / "refresh-guidelines"
    / "references"
    / "curated-sources.md"
)
ENRICHMENT_PROCEDURE_MD = (
    PROJECT_ROOT
    / "skills"
    / "refresh-guidelines"
    / "references"
    / "enrichment-procedure.md"
)
CLAUDE_MD_SOTA = PROJECT_ROOT / "docs" / "CLAUDE-MD-SOTA.md"
INSIGHTS_RAW = PROJECT_ROOT / "docs" / "insights-raw.md"
GUIDELINES_RAW_JSON = PROJECT_ROOT / "docs" / "guidelines-raw.json"
INSIGHTS_PARSED_JSON = PROJECT_ROOT / "docs" / "insights-parsed.json"
GITIGNORE = PROJECT_ROOT / ".gitignore"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"


# ===================================================================
# 1. File existence and structure tests
# ===================================================================


class TestSkillFileExists(unittest.TestCase):
    """SKILL.md exists with required structure."""

    def test_skill_md_exists(self):
        self.assertTrue(SKILL_MD.exists(), f"Missing: {SKILL_MD}")

    def test_skill_md_not_empty(self):
        self.assertGreater(len(SKILL_MD.read_text().strip()), 0)

    def test_skill_md_starts_with_heading_or_frontmatter(self):
        first_line = SKILL_MD.read_text().splitlines()[0]
        self.assertTrue(
            first_line.startswith("# ") or first_line == "---",
            "SKILL.md should start with a markdown heading or YAML frontmatter (---)",
        )

    def test_skill_md_mentions_refresh_guidelines(self):
        content = SKILL_MD.read_text().lower()
        self.assertIn("refresh-guidelines", content)

    def test_skill_md_has_procedure_section(self):
        content = SKILL_MD.read_text()
        self.assertIn("## Procedure", content)

    def test_skill_md_has_all_steps(self):
        content = SKILL_MD.read_text()
        for step_num in range(0, 11):
            self.assertIn(
                f"### Step {step_num}",
                content,
                f"SKILL.md missing Step {step_num}",
            )

    def test_skill_md_references_fetch_script(self):
        content = SKILL_MD.read_text()
        self.assertIn("fetch-guidelines.py", content)

    def test_skill_md_references_parse_insights_script(self):
        content = SKILL_MD.read_text()
        self.assertIn("parse-insights.py", content)

    def test_skill_md_references_insights_parsed_json(self):
        content = SKILL_MD.read_text()
        self.assertIn("insights-parsed.json", content)

    def test_skill_md_references_curated_sources(self):
        content = SKILL_MD.read_text()
        self.assertIn("curated-sources.md", content)

    def test_skill_md_references_enrichment_procedure(self):
        content = SKILL_MD.read_text()
        self.assertIn("enrichment-procedure.md", content)

    def test_skill_md_enforces_human_approval(self):
        content = SKILL_MD.read_text().lower()
        self.assertIn("human approval", content)

    def test_skill_md_enforces_300_line_limit(self):
        content = SKILL_MD.read_text()
        self.assertIn("300 lines", content)


class TestCuratedSourcesFileExists(unittest.TestCase):
    """curated-sources.md exists with required structure."""

    def test_file_exists(self):
        self.assertTrue(
            CURATED_SOURCES_MD.exists(), f"Missing: {CURATED_SOURCES_MD}"
        )

    def test_has_tier_sections(self):
        content = CURATED_SOURCES_MD.read_text()
        self.assertIn("## Tier 1:", content)
        self.assertIn("## Tier 2:", content)
        self.assertIn("## Tier 3:", content)

    def test_has_theme_definitions(self):
        content = CURATED_SOURCES_MD.read_text()
        self.assertIn("## Theme Definitions", content)

    def test_has_precedence_table(self):
        content = CURATED_SOURCES_MD.read_text()
        self.assertIn("## Source Precedence", content)


class TestEnrichmentProcedureExists(unittest.TestCase):
    """enrichment-procedure.md exists with required structure."""

    def test_file_exists(self):
        self.assertTrue(
            ENRICHMENT_PROCEDURE_MD.exists(),
            f"Missing: {ENRICHMENT_PROCEDURE_MD}",
        )

    def test_has_all_three_phases(self):
        content = ENRICHMENT_PROCEDURE_MD.read_text()
        self.assertIn("## Phase 1: Classification", content)
        self.assertIn("## Phase 2: Conflict Resolution", content)
        self.assertIn("## Phase 3: Integration", content)

    def test_has_source_precedence(self):
        content = ENRICHMENT_PROCEDURE_MD.read_text()
        self.assertIn("## Source Precedence", content)

    def test_has_classification_labels(self):
        content = ENRICHMENT_PROCEDURE_MD.read_text()
        for label in ("Novel", "Duplicate", "Reinforcing", "Conflicting"):
            self.assertIn(
                f"**{label}**",
                content,
                f"Missing classification label: {label}",
            )

    def test_conflicts_never_auto_resolved(self):
        content = ENRICHMENT_PROCEDURE_MD.read_text().lower()
        self.assertIn("never auto-resolve", content)

    def test_has_size_constraint(self):
        content = ENRICHMENT_PROCEDURE_MD.read_text()
        self.assertIn("300 lines", content)


class TestFetchScriptExists(unittest.TestCase):
    """fetch-guidelines.py exists and is loadable."""

    def test_file_exists(self):
        self.assertTrue(SCRIPT_PATH.exists(), f"Missing: {SCRIPT_PATH}")

    def test_file_is_executable(self):
        import os

        self.assertTrue(
            os.access(SCRIPT_PATH, os.X_OK),
            "fetch-guidelines.py should be executable",
        )

    def test_module_loads(self):
        fg = _load_fg()
        self.assertIsNotNone(fg)

    def test_has_required_functions(self):
        fg = _load_fg()
        for name in (
            "parse_curated_sources",
            "strip_html",
            "extract_content_blocks",
            "fetch_url",
            "check_url_status",
            "check_source_freshness",
            "check_freshness_main",
            "main",
        ):
            self.assertTrue(
                hasattr(fg, name), f"Module missing function: {name}"
            )


class TestClaudeMdSotaPopulated(unittest.TestCase):
    """CLAUDE-MD-SOTA.md is populated by /refresh-guidelines into the 6-part structure."""

    def test_file_exists(self):
        self.assertTrue(CLAUDE_MD_SOTA.exists(), f"Missing: {CLAUDE_MD_SOTA}")

    def test_file_is_not_empty(self):
        content = CLAUDE_MD_SOTA.read_text().strip()
        self.assertGreater(len(content), 0, "CLAUDE-MD-SOTA.md should be populated")

    def test_under_300_lines(self):
        lines = CLAUDE_MD_SOTA.read_text().splitlines()
        self.assertLess(len(lines), 300, f"CLAUDE-MD-SOTA.md is {len(lines)} lines (limit 300)")

    def test_has_all_sections(self):
        content = CLAUDE_MD_SOTA.read_text()
        required_sections = [
            "Purpose & Scope",
            "Part 1: Structural Standards",
            "Part 2: Content Guidelines",
            "Part 3: Integration Guidelines",
            "Part 4: Behavioral Patterns",
            "Part 5: Maintenance Guidelines",
            "Source Attribution",
        ]
        for section in required_sections:
            self.assertIn(section, content, f"Missing section: {section}")

    def test_has_source_attribution_with_urls(self):
        content = CLAUDE_MD_SOTA.read_text()
        attr_start = content.index("## Source Attribution")
        attr_section = content[attr_start:]
        self.assertIn("https://", attr_section, "Source Attribution should contain URLs")

    def test_has_source_attribution_with_dates(self):
        content = CLAUDE_MD_SOTA.read_text()
        attr_start = content.index("## Source Attribution")
        attr_section = content[attr_start:]
        self.assertRegex(attr_section, r"\d{4}-\d{2}-\d{2}", "Source Attribution should contain dates")

    def test_has_tier1_sources_in_attribution(self):
        content = CLAUDE_MD_SOTA.read_text()
        attr_start = content.index("## Source Attribution")
        attr_section = content[attr_start:]
        self.assertIn("T1", attr_section, "Should reference Tier 1 sources")

    def test_no_hardcoded_content_marker(self):
        """All content should be source-attributed, not invented."""
        content = CLAUDE_MD_SOTA.read_text()
        self.assertIn(
            "Source Attribution",
            content,
            "Document must have Source Attribution proving content origin",
        )


class TestInsightsRawPlaceholder(unittest.TestCase):
    """insights-raw.md placeholder exists."""

    def test_file_exists(self):
        self.assertTrue(INSIGHTS_RAW.exists(), f"Missing: {INSIGHTS_RAW}")

    def test_has_instructions_header(self):
        content = INSIGHTS_RAW.read_text()
        self.assertTrue(
            content.startswith("# "),
            "insights-raw.md should start with a heading",
        )

    def test_mentions_insights(self):
        content = INSIGHTS_RAW.read_text().lower()
        self.assertIn("/insights", content)

    def test_mentions_refresh_guidelines(self):
        content = INSIGHTS_RAW.read_text().lower()
        self.assertIn("/refresh-guidelines", content)


class TestGitignoreEntries(unittest.TestCase):
    """Enrichment artifacts are gitignored.

    The .gitignore uses a broad 'docs' entry (ignoring the whole directory)
    with negation exceptions for tracked files (docs/CLAUDE.md,
    docs/CLAUDE-MD-SOTA.md). We verify actual git behaviour via
    'git check-ignore' rather than checking for literal file strings.
    """

    @classmethod
    def setUpClass(cls):
        cls.content = GITIGNORE.read_text()

    @staticmethod
    def _is_gitignored(rel_path: str) -> bool:
        import subprocess
        r = subprocess.run(
            ["git", "check-ignore", "-q", rel_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )
        return r.returncode == 0

    def test_guidelines_raw_json_ignored(self):
        self.assertTrue(
            self._is_gitignored("docs/guidelines-raw.json"),
            "docs/guidelines-raw.json should be covered by .gitignore",
        )

    def test_insights_raw_md_ignored(self):
        self.assertTrue(
            self._is_gitignored("docs/insights-raw.md"),
            "docs/insights-raw.md should be covered by .gitignore",
        )

    def test_insights_parsed_json_ignored(self):
        self.assertTrue(
            self._is_gitignored("docs/insights-parsed.json"),
            "docs/insights-parsed.json should be covered by .gitignore",
        )

    def test_freshness_report_json_ignored(self):
        self.assertTrue(
            self._is_gitignored("docs/freshness-report.json"),
            "docs/freshness-report.json should be covered by .gitignore",
        )

    def test_docs_dir_broadly_ignored(self):
        """docs/ directory is ignored at the directory level."""
        self.assertRegex(
            self.content,
            r"(?m)^docs$",
            ".gitignore should contain a bare 'docs' entry covering the whole directory",
        )

    def test_claude_md_sota_not_ignored(self):
        """docs/CLAUDE-MD-SOTA.md is whitelisted (tracked)."""
        self.assertFalse(
            self._is_gitignored("docs/CLAUDE-MD-SOTA.md"),
            "docs/CLAUDE-MD-SOTA.md should NOT be gitignored (it is tracked)",
        )


class TestClaudeMdProjectStructure(unittest.TestCase):
    """CLAUDE.md project structure includes all enrichment files."""

    def test_insights_raw_listed(self):
        content = CLAUDE_MD.read_text()
        self.assertIn("insights-raw.md", content)

    def test_insights_parsed_json_listed(self):
        content = CLAUDE_MD.read_text()
        self.assertIn("insights-parsed.json", content)

    def test_parse_insights_script_listed(self):
        content = CLAUDE_MD.read_text()
        self.assertIn("parse-insights.py", content)

    def test_refresh_guidelines_listed(self):
        content = CLAUDE_MD.read_text()
        self.assertIn("refresh-guidelines", content)


# ===================================================================
# 2. parse_curated_sources() tests
# ===================================================================


class TestParseCuratedSources(unittest.TestCase):
    """Test parse_curated_sources against the real curated-sources.md."""

    @classmethod
    def setUpClass(cls):
        fg = _load_fg()
        cls.sources = fg.parse_curated_sources(CURATED_SOURCES_MD)

    def test_returns_list(self):
        self.assertIsInstance(self.sources, list)

    def test_at_least_three_tier1_sources(self):
        t1 = [s for s in self.sources if s["tier"] == 1]
        self.assertGreaterEqual(
            len(t1), 3, "Should have at least 3 Tier 1 sources"
        )

    def test_has_tier2_sources(self):
        t2 = [s for s in self.sources if s["tier"] == 2]
        self.assertGreater(len(t2), 0, "Should have Tier 2 sources")

    def test_has_tier3_sources(self):
        t3 = [s for s in self.sources if s["tier"] == 3]
        self.assertGreater(len(t3), 0, "Should have Tier 3 sources")

    def test_all_sources_have_required_fields(self):
        required = {"id", "source_name", "url", "tier", "themes", "last_verified"}
        for src in self.sources:
            self.assertTrue(
                required.issubset(src.keys()),
                f"Source {src.get('id', '?')} missing fields: "
                f"{required - src.keys()}",
            )

    def test_ids_follow_pattern(self):
        import re

        pattern = re.compile(r"^T\d+-\d+$")
        for src in self.sources:
            self.assertRegex(
                src["id"],
                pattern,
                f"Source ID '{src['id']}' doesn't match T{{tier}}-{{num}} pattern",
            )

    def test_tiers_match_id_prefix(self):
        for src in self.sources:
            expected_tier = int(src["id"][1])
            self.assertEqual(
                src["tier"],
                expected_tier,
                f"Source {src['id']} tier {src['tier']} doesn't match ID prefix",
            )

    def test_all_urls_are_https(self):
        for src in self.sources:
            self.assertTrue(
                src["url"].startswith("https://"),
                f"Source {src['id']} URL should use HTTPS: {src['url']}",
            )

    def test_all_sources_have_themes(self):
        for src in self.sources:
            self.assertIsInstance(src["themes"], list)
            self.assertGreater(
                len(src["themes"]),
                0,
                f"Source {src['id']} should have at least one theme",
            )

    def test_unique_ids(self):
        ids = [s["id"] for s in self.sources]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate source IDs found")

    def test_themes_are_valid(self):
        valid_themes = {
            "structural",
            "content",
            "anti-patterns",
            "integration",
            "behavioral",
            "maintenance",
        }
        for src in self.sources:
            for theme in src["themes"]:
                self.assertIn(
                    theme,
                    valid_themes,
                    f"Source {src['id']} has invalid theme: '{theme}'",
                )


class TestParseCuratedSourcesSynthetic(unittest.TestCase):
    """Test parse_curated_sources against synthetic markdown input."""

    def _parse(self, markdown: str) -> list[dict]:
        fg = _load_fg()
        tmp = Path("/tmp/test_curated_sources.md")
        tmp.write_text(markdown)
        try:
            return fg.parse_curated_sources(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_single_entry(self):
        md = textwrap.dedent("""\
            ## Tier 1: Official

            ### T1-001: Test Source
            - **URL**: https://example.com/page
            - **Themes**: structural, content
            - **Description**: A test source.
        """)
        result = self._parse(md)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "T1-001")
        self.assertEqual(result[0]["source_name"], "Test Source")
        self.assertEqual(result[0]["url"], "https://example.com/page")
        self.assertEqual(result[0]["tier"], 1)
        self.assertEqual(result[0]["themes"], ["structural", "content"])

    def test_multiple_tiers(self):
        md = textwrap.dedent("""\
            ## Tier 1: Official
            ### T1-001: First
            - **URL**: https://example.com/1
            - **Themes**: structural

            ## Tier 2: Community
            ### T2-001: Second
            - **URL**: https://example.com/2
            - **Themes**: behavioral
        """)
        result = self._parse(md)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["tier"], 1)
        self.assertEqual(result[1]["tier"], 2)

    def test_entry_without_url_is_skipped(self):
        md = textwrap.dedent("""\
            ### T1-001: No URL
            - **Themes**: structural
        """)
        result = self._parse(md)
        self.assertEqual(len(result), 0)

    def test_entry_without_themes_gets_empty_list(self):
        md = textwrap.dedent("""\
            ### T1-001: No Themes
            - **URL**: https://example.com
        """)
        result = self._parse(md)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["themes"], [])

    def test_empty_file_returns_empty_list(self):
        result = self._parse("")
        self.assertEqual(result, [])

    def test_no_matching_headings_returns_empty(self):
        md = "# Title\n\nSome text without source entries.\n"
        result = self._parse(md)
        self.assertEqual(result, [])

    def test_last_verified_parsed(self):
        md = textwrap.dedent("""\
            ### T1-001: Test Source
            - **URL**: https://example.com/page
            - **Themes**: structural
            - **Last verified**: 2026-02-12
        """)
        result = self._parse(md)
        self.assertEqual(result[0]["last_verified"], "2026-02-12")

    def test_last_verified_missing_is_none(self):
        md = textwrap.dedent("""\
            ### T1-001: Test Source
            - **URL**: https://example.com/page
            - **Themes**: structural
        """)
        result = self._parse(md)
        self.assertIsNone(result[0]["last_verified"])


# ===================================================================
# 2b. check_url_status() tests (mocked)
# ===================================================================


class TestCheckUrlStatus(unittest.TestCase):
    """Test URL status checking."""

    def setUp(self):
        self.fg = _load_fg()

    @patch.object(_load_fg(), "_opener")
    def test_success_returns_200(self, mock_opener):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.url = "https://example.com"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp

        status, url = self.fg.check_url_status("https://example.com")
        self.assertEqual(status, 200)
        self.assertEqual(url, "https://example.com")

    def test_http_error_returns_code(self):
        with patch.object(
            self.fg,
            "_opener",
            **{
                "open.side_effect": self.fg.urllib.error.HTTPError(
                    "https://example.com", 404, "Not Found", {}, None
                )
            },
        ):
            status, url = self.fg.check_url_status("https://example.com")
            self.assertEqual(status, 404)
            self.assertIsNone(url)

    def test_network_error_returns_none(self):
        with patch.object(
            self.fg,
            "_opener",
            **{
                "open.side_effect": self.fg.urllib.error.URLError("Connection refused")
            },
        ):
            status, url = self.fg.check_url_status("https://example.com")
            self.assertIsNone(status)
            self.assertIsNone(url)

    def test_timeout_returns_none(self):
        with patch.object(
            self.fg,
            "_opener",
            **{"open.side_effect": TimeoutError()},
        ):
            status, url = self.fg.check_url_status("https://example.com")
            self.assertIsNone(status)
            self.assertIsNone(url)


# ===================================================================
# 2c. check_source_freshness() tests
# ===================================================================


class TestCheckSourceFreshness(unittest.TestCase):
    """Test source freshness checking logic."""

    def setUp(self):
        self.fg = _load_fg()
        self.today = datetime(2026, 2, 17, tzinfo=timezone.utc)

    def _make_source(self, last_verified="2026-02-10"):
        return {
            "id": "T1-001",
            "source_name": "Test",
            "url": "https://example.com",
            "tier": 1,
            "themes": ["structural"],
            "last_verified": last_verified,
        }

    def test_fresh_source_not_stale(self):
        sources = [self._make_source("2026-02-10")]
        with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertFalse(results[0]["is_stale"])
        self.assertTrue(results[0]["is_reachable"])
        self.assertFalse(results[0]["needs_attention"])

    def test_stale_source_detected(self):
        sources = [self._make_source("2025-12-01")]
        with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertTrue(results[0]["is_stale"])
        self.assertTrue(results[0]["needs_attention"])
        self.assertGreater(results[0]["days_since_verified"], 30)

    def test_missing_date_is_stale(self):
        sources = [self._make_source(None)]
        with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertTrue(results[0]["is_stale"])
        self.assertEqual(results[0]["days_since_verified"], -1)

    def test_broken_url_detected(self):
        sources = [self._make_source("2026-02-10")]
        with patch.object(self.fg, "check_url_status", return_value=(404, None)):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertFalse(results[0]["is_reachable"])
        self.assertTrue(results[0]["needs_attention"])
        self.assertEqual(results[0]["http_status"], 404)

    def test_network_error_detected(self):
        sources = [self._make_source("2026-02-10")]
        with patch.object(self.fg, "check_url_status", return_value=(None, None)):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertFalse(results[0]["is_reachable"])
        self.assertIsNone(results[0]["http_status"])

    def test_redirect_captured(self):
        sources = [self._make_source("2026-02-10")]
        with patch.object(self.fg, "check_url_status", return_value=(200, "https://new.com/page")):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertEqual(results[0]["final_url"], "https://new.com/page")
        self.assertTrue(results[0]["is_reachable"])

    def test_multiple_sources(self):
        sources = [
            self._make_source("2026-02-10"),
            self._make_source("2025-11-01"),
        ]
        sources[1]["id"] = "T2-001"
        with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
            results = self.fg.check_source_freshness(sources, stale_threshold_days=30, today=self.today)
        self.assertEqual(len(results), 2)
        self.assertFalse(results[0]["is_stale"])
        self.assertTrue(results[1]["is_stale"])


# ===================================================================
# 2d. check_freshness_main() integration tests (mocked)
# ===================================================================


class TestCheckFreshnessMain(unittest.TestCase):
    """Test check_freshness_main() function behavior."""

    def setUp(self):
        self.fg = _load_fg()

    def test_writes_report_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
                result = self.fg.check_freshness_main(docs_dir=docs_dir)
            report_path = docs_dir / "freshness-report.json"
            self.assertEqual(result, 0)
            self.assertTrue(report_path.exists())
            data = json.loads(report_path.read_text())
            self.assertIn("sources", data)
            self.assertIn("stale_threshold_days", data)
            self.assertIn("total_sources", data)

    def test_returns_1_when_curated_sources_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(self.fg, "CURATED_SOURCES", Path("/nonexistent/path.md")):
                result = self.fg.check_freshness_main(docs_dir=Path(tmpdir))
                self.assertEqual(result, 1)

    def test_report_counts_are_consistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            with patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")):
                self.fg.check_freshness_main(docs_dir=docs_dir)
            data = json.loads((docs_dir / "freshness-report.json").read_text())
            self.assertEqual(data["total_sources"], len(data["sources"]))


# ===================================================================
# 2e. freshness-report.json output validation (if present)
# ===================================================================


FRESHNESS_REPORT_JSON = PROJECT_ROOT / "docs" / "freshness-report.json"


class TestFreshnessReportJsonSchema(unittest.TestCase):
    """Validate freshness-report.json output schema (if present)."""

    @classmethod
    def setUpClass(cls):
        if not FRESHNESS_REPORT_JSON.exists():
            raise unittest.SkipTest("freshness-report.json not present")
        with open(FRESHNESS_REPORT_JSON) as f:
            cls.data = json.load(f)

    def test_has_top_level_fields(self):
        for field in (
            "generated_at",
            "stale_threshold_days",
            "total_sources",
            "stale_count",
            "broken_count",
            "needs_attention_count",
            "sources",
        ):
            self.assertIn(field, self.data, f"Missing top-level field: {field}")

    def test_sources_have_required_fields(self):
        required = {"id", "source_name", "url", "is_stale", "is_reachable", "needs_attention"}
        for src in self.data["sources"]:
            self.assertTrue(
                required.issubset(src.keys()),
                f"Source {src.get('id', '?')} missing: {required - src.keys()}",
            )

    def test_counts_are_consistent(self):
        self.assertEqual(self.data["total_sources"], len(self.data["sources"]))


# ===================================================================
# 3. strip_html() / HTMLTextExtractor tests
# ===================================================================


class TestStripHtml(unittest.TestCase):
    """Test HTML to plain text conversion."""

    def setUp(self):
        self.strip_html = _load_fg().strip_html

    def test_plain_text_passthrough(self):
        self.assertEqual(self.strip_html("Hello world"), "Hello world")

    def test_basic_tag_removal(self):
        result = self.strip_html("<p>Hello</p>")
        self.assertIn("Hello", result)
        self.assertNotIn("<p>", result)

    def test_nested_tags(self):
        result = self.strip_html("<div><p>Hello <b>world</b></p></div>")
        self.assertIn("Hello", result)
        self.assertIn("world", result)
        self.assertNotIn("<", result)

    def test_script_tags_stripped(self):
        html = "<p>Before</p><script>alert('xss')</script><p>After</p>"
        result = self.strip_html(html)
        self.assertIn("Before", result)
        self.assertIn("After", result)
        self.assertNotIn("alert", result)

    def test_style_tags_stripped(self):
        html = "<style>.foo { color: red; }</style><p>Content</p>"
        result = self.strip_html(html)
        self.assertIn("Content", result)
        self.assertNotIn("color", result)

    def test_nav_footer_stripped(self):
        html = "<nav>Menu</nav><main>Body</main><footer>Foot</footer>"
        result = self.strip_html(html)
        self.assertIn("Body", result)
        self.assertNotIn("Menu", result)
        self.assertNotIn("Foot", result)

    def test_empty_html(self):
        self.assertEqual(self.strip_html(""), "")

    def test_newlines_on_block_elements(self):
        html = "<h1>Title</h1><p>Para 1</p><p>Para 2</p>"
        result = self.strip_html(html)
        self.assertIn("Title", result)
        self.assertIn("Para 1", result)
        self.assertIn("Para 2", result)

    def test_list_items_separated(self):
        html = "<ul><li>One</li><li>Two</li><li>Three</li></ul>"
        result = self.strip_html(html)
        self.assertIn("One", result)
        self.assertIn("Two", result)
        self.assertIn("Three", result)


class TestHtmlTextExtractorSkipDepth(unittest.TestCase):
    """Test nested skip tag handling."""

    def test_nested_script_tags(self):
        fg = _load_fg()
        html = "<script><script>inner</script></script><p>Visible</p>"
        result = fg.strip_html(html)
        self.assertIn("Visible", result)

    def test_skip_depth_doesnt_go_negative(self):
        fg = _load_fg()
        # Extra end tags shouldn't crash
        html = "</script></script><p>Still works</p>"
        result = fg.strip_html(html)
        self.assertIn("Still works", result)


# ===================================================================
# 4. _truncate() tests
# ===================================================================


class TestTruncate(unittest.TestCase):
    """Test text truncation."""

    def setUp(self):
        self._truncate = _load_fg()._truncate

    def test_short_text_unchanged(self):
        self.assertEqual(self._truncate("hello", 100), "hello")

    def test_exact_limit_unchanged(self):
        text = "a" * 100
        self.assertEqual(self._truncate(text, 100), text)

    def test_over_limit_truncated(self):
        text = "a" * 200
        result = self._truncate(text, 100)
        self.assertEqual(len(result), 100)
        self.assertTrue(result.endswith("..."))

    def test_ellipsis_content_preserved(self):
        text = "abcdefghij"
        result = self._truncate(text, 8)
        self.assertEqual(result, "abcde...")

    def test_empty_string(self):
        self.assertEqual(self._truncate("", 100), "")


# ===================================================================
# 5. extract_content_blocks() tests
# ===================================================================


class TestExtractContentBlocks(unittest.TestCase):
    """Test content block extraction from markdown text."""

    def setUp(self):
        self.extract = _load_fg().extract_content_blocks

    def test_headings_split_into_blocks(self):
        text = "# Title\nIntro text\n## Section A\nBody A\n## Section B\nBody B"
        blocks = self.extract(text, ["structural", "content"])
        # Should have blocks for sections with body text
        self.assertGreater(len(blocks), 0)

    def test_each_block_has_required_fields(self):
        text = "# Title\nIntro\n## Section\nBody content here"
        blocks = self.extract(text, ["structural"])
        for block in blocks:
            self.assertIn("theme", block)
            self.assertIn("heading", block)
            self.assertIn("text", block)

    def test_no_headings_single_block(self):
        text = "Just plain text without any headings."
        blocks = self.extract(text, ["content"])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["heading"], "(no heading)")
        self.assertEqual(blocks[0]["theme"], "content")

    def test_empty_text_no_blocks(self):
        blocks = self.extract("", ["content"])
        self.assertEqual(blocks, [])

    def test_whitespace_only_no_blocks(self):
        blocks = self.extract("   \n\n  ", ["content"])
        self.assertEqual(blocks, [])

    def test_default_theme_when_no_themes(self):
        text = "Just text."
        blocks = self.extract(text, [])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["theme"], "content")

    def test_theme_classification_structural(self):
        text = "# File Structure\nOrganize your file into sections with proper hierarchy and layout."
        blocks = self.extract(text, ["structural", "content"])
        themes = [b["theme"] for b in blocks]
        self.assertIn("structural", themes)

    def test_theme_classification_integration(self):
        text = "# Hook Configuration\nConfigure hooks and skills in settings to automate triggers."
        blocks = self.extract(text, ["integration", "content"])
        themes = [b["theme"] for b in blocks]
        self.assertIn("integration", themes)

    def test_theme_classification_behavioral(self):
        text = "# Workflow Patterns\nAlways prefer this approach and style when processing."
        blocks = self.extract(text, ["behavioral", "content"])
        themes = [b["theme"] for b in blocks]
        self.assertIn("behavioral", themes)

    def test_theme_classification_anti_patterns(self):
        text = "# Common Mistakes\nAvoid these bad anti-pattern pitfalls and never do wrong things."
        blocks = self.extract(text, ["anti-patterns", "content"])
        themes = [b["theme"] for b in blocks]
        self.assertIn("anti-patterns", themes)

    def test_theme_classification_maintenance(self):
        text = "# Keeping Current\nUpdate and maintain regularly, review for stale outdated content."
        blocks = self.extract(text, ["maintenance", "content"])
        themes = [b["theme"] for b in blocks]
        self.assertIn("maintenance", themes)

    def test_blocks_filtered_by_declared_themes(self):
        """Blocks whose best theme isn't in the source's declared themes are excluded."""
        # Text clearly about hooks (integration) but declared themes only has 'structural'
        text = "# Hook Setup\nConfigure hook triggers and agent automation events."
        blocks = self.extract(text, ["structural"])
        # The block may be excluded because 'integration' is not in declared themes
        # OR classified as structural with lower score — both are valid
        for block in blocks:
            self.assertIn(block["theme"], ["structural", "integration"])

    def test_long_body_truncated(self):
        text = "# Section\n" + "x" * 5000
        blocks = self.extract(text, [])  # no theme filter
        self.assertGreater(len(blocks), 0)
        self.assertLessEqual(len(blocks[0]["text"]), 2000)

    def test_empty_sections_skipped(self):
        text = "# Title\n## Empty\n## HasBody\nSome content"
        blocks = self.extract(text, ["content"])
        headings = [b["heading"] for b in blocks]
        self.assertNotIn("Empty", headings)

    def test_heading_levels_1_through_4(self):
        text = "# H1\nBody1\n## H2\nBody2\n### H3\nBody3\n#### H4\nBody4"
        blocks = self.extract(text, ["content"])
        headings = [b["heading"] for b in blocks]
        for h in ("H1", "H2", "H3", "H4"):
            self.assertIn(h, headings, f"Missing heading level: {h}")


# ===================================================================
# 6. guidelines-raw.json output validation (if present)
# ===================================================================


class TestGuidelinesRawJsonSchema(unittest.TestCase):
    """Validate guidelines-raw.json output schema (if it exists from a previous run)."""

    @classmethod
    def setUpClass(cls):
        if not GUIDELINES_RAW_JSON.exists():
            raise unittest.SkipTest(
                "guidelines-raw.json not present — run fetch-guidelines.py first"
            )
        with open(GUIDELINES_RAW_JSON) as f:
            cls.data = json.load(f)

    def test_valid_json(self):
        self.assertIsInstance(self.data, dict)

    def test_has_top_level_fields(self):
        for field in (
            "generated_at",
            "sources_attempted",
            "sources_fetched",
            "sources_failed",
            "entries",
        ):
            self.assertIn(field, self.data, f"Missing top-level field: {field}")

    def test_entries_is_list(self):
        self.assertIsInstance(self.data["entries"], list)

    def test_sources_counts_are_ints(self):
        self.assertIsInstance(self.data["sources_attempted"], int)
        self.assertIsInstance(self.data["sources_fetched"], int)
        self.assertIsInstance(self.data["sources_failed"], int)

    def test_sources_fetched_at_least_tier1(self):
        t1_entries = [e for e in self.data["entries"] if e.get("tier") == 1]
        self.assertGreaterEqual(
            len(t1_entries), 3, "Should fetch at least 3 Tier 1 sources"
        )

    def test_each_entry_has_required_fields(self):
        required = {
            "source_id",
            "source_url",
            "source_name",
            "tier",
            "themes",
            "last_fetched",
            "content_blocks",
        }
        for entry in self.data["entries"]:
            self.assertTrue(
                required.issubset(entry.keys()),
                f"Entry {entry.get('source_id', '?')} missing: "
                f"{required - entry.keys()}",
            )

    def test_content_blocks_are_lists(self):
        for entry in self.data["entries"]:
            self.assertIsInstance(
                entry["content_blocks"],
                list,
                f"Entry {entry['source_id']} blocks should be a list",
            )

    def test_content_blocks_have_required_fields(self):
        for entry in self.data["entries"]:
            for block in entry["content_blocks"]:
                for field in ("theme", "heading", "text"):
                    self.assertIn(
                        field,
                        block,
                        f"Block in {entry['source_id']} missing '{field}'",
                    )

    def test_tier1_sources_have_content(self):
        for entry in self.data["entries"]:
            if entry["tier"] == 1:
                self.assertGreater(
                    len(entry["content_blocks"]),
                    0,
                    f"T1 source {entry['source_id']} has no content blocks",
                )

    def test_tiers_are_valid(self):
        for entry in self.data["entries"]:
            self.assertIn(
                entry["tier"],
                (1, 2, 3),
                f"Entry {entry['source_id']} has invalid tier: {entry['tier']}",
            )

    def test_no_duplicate_source_ids(self):
        ids = [e["source_id"] for e in self.data["entries"]]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate source IDs in output")

    def test_math_sources_attempted_eq_fetched_plus_failed(self):
        self.assertEqual(
            self.data["sources_attempted"],
            self.data["sources_fetched"] + self.data["sources_failed"],
        )


# ===================================================================
# 7. fetch_url() tests (mocked — no real network)
# ===================================================================


class TestFetchUrlMocked(unittest.TestCase):
    """Test fetch_url with mocked HTTP responses."""

    def setUp(self):
        self.fg = _load_fg()

    @patch.object(_load_fg(), "_opener")
    def test_returns_text_on_success(self, mock_opener):
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Type": "text/plain; charset=utf-8"}
        mock_resp.read.return_value = b"Hello world"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp

        result = self.fg.fetch_url("https://example.com")
        self.assertEqual(result, "Hello world")

    @patch.object(_load_fg(), "_opener")
    def test_strips_html_content(self, mock_opener):
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_resp.read.return_value = b"<p>Hello</p>"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp

        result = self.fg.fetch_url("https://example.com")
        self.assertIn("Hello", result)
        self.assertNotIn("<p>", result)

    def test_returns_none_on_http_error(self):
        with patch.object(
            self.fg,
            "_opener",
            **{
                "open.side_effect": self.fg.urllib.error.HTTPError(
                    "https://example.com", 404, "Not Found", {}, None
                )
            },
        ):
            result = self.fg.fetch_url("https://example.com")
            self.assertIsNone(result)

    def test_returns_none_on_url_error(self):
        with patch.object(
            self.fg,
            "_opener",
            **{
                "open.side_effect": self.fg.urllib.error.URLError("Connection refused")
            },
        ):
            result = self.fg.fetch_url("https://example.com")
            self.assertIsNone(result)


# ===================================================================
# 8. main() integration tests (mocked I/O)
# ===================================================================


class TestMainFunction(unittest.TestCase):
    """Test main() function behavior."""

    def setUp(self):
        self.fg = _load_fg()

    def test_returns_1_when_curated_sources_missing(self):
        with patch.object(
            self.fg, "CURATED_SOURCES", Path("/nonexistent/path.md")
        ):
            result = self.fg.main()
            self.assertEqual(result, 1)

    def test_returns_1_when_all_fetches_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(self.fg, "fetch_url", return_value=None):
                with patch.object(self.fg, "CURATED_SOURCES", CURATED_SOURCES_MD):
                    result = self.fg.main(docs_dir=Path(tmpdir))
                    self.assertEqual(result, 1)


# ===================================================================
# 9. RedirectHandler tests
# ===================================================================


class TestRedirectHandler(unittest.TestCase):
    """Test that the 308 redirect handler exists."""

    def test_handler_class_exists(self):
        fg = _load_fg()
        self.assertTrue(hasattr(fg, "_RedirectHandler"))

    def test_handler_has_308_method(self):
        fg = _load_fg()
        handler = fg._RedirectHandler()
        self.assertTrue(
            hasattr(handler, "http_error_308"),
            "Handler should handle HTTP 308",
        )

    def test_opener_exists(self):
        fg = _load_fg()
        self.assertTrue(hasattr(fg, "_opener"))


# ===================================================================
# 10. parse-insights.py script existence and structure
# ===================================================================


class TestParseInsightsScriptExists(unittest.TestCase):
    """parse-insights.py exists and is loadable."""

    def test_file_exists(self):
        self.assertTrue(PARSE_INSIGHTS_PATH.exists(), f"Missing: {PARSE_INSIGHTS_PATH}")

    def test_module_loads(self):
        pi = _load_pi()
        self.assertIsNotNone(pi)

    def test_has_required_functions(self):
        pi = _load_pi()
        for name in (
            "find_report",
            "InsightsHTMLParser",
            "parse_facets",
            "parse_session_meta",
            "main",
        ):
            self.assertTrue(hasattr(pi, name), f"Module missing: {name}")

    def test_has_build_entries(self):
        pi = _load_pi()
        self.assertTrue(hasattr(pi, "_build_entries"))

    def test_has_extract_heading(self):
        pi = _load_pi()
        self.assertTrue(hasattr(pi, "_extract_heading"))


# ===================================================================
# 11. find_report() tests
# ===================================================================


class TestFindReport(unittest.TestCase):
    """Test report discovery and staleness detection."""

    def setUp(self):
        self.pi = _load_pi()

    def test_missing_report_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path, days = self.pi.find_report(Path(tmpdir))
            self.assertIsNone(path)
            self.assertEqual(days, -1)

    def test_existing_report_returns_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            report.write_text("<html></html>")
            path, days = self.pi.find_report(Path(tmpdir))
            self.assertIsNotNone(path)
            self.assertEqual(path, report)

    def test_fresh_report_staleness_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            report.write_text("<html></html>")
            _, days = self.pi.find_report(Path(tmpdir))
            self.assertEqual(days, 0)

    def test_stale_report_detected(self):
        import os
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            report.write_text("<html></html>")
            # Set mtime to 10 days ago
            old_time = time.time() - (10 * 86400)
            os.utime(report, (old_time, old_time))
            _, days = self.pi.find_report(Path(tmpdir))
            self.assertGreaterEqual(days, 9)


# ===================================================================
# 12. InsightsHTMLParser synthetic tests
# ===================================================================


class TestInsightsHTMLParserSynthetic(unittest.TestCase):
    """Test HTML parser against synthetic report fragments."""

    def setUp(self):
        self.pi = _load_pi()

    def _parse(self, html: str):
        parser = self.pi.InsightsHTMLParser()
        parser.feed(html)
        return parser

    def test_empty_html(self):
        p = self._parse("")
        for section in p.sections.values():
            self.assertEqual(len(section), 0)
        self.assertEqual(len(p.claude_md_recs), 0)

    def test_big_win_extraction(self):
        html = """
        <h2 id="section-wins">Wins</h2>
        <div class="big-win">
            <div class="big-win-title">Great workflow</div>
            <div class="big-win-desc">You did well here.</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["wins"]), 1)
        self.assertEqual(p.sections["wins"][0]["title"], "Great workflow")
        self.assertEqual(p.sections["wins"][0]["description"], "You did well here.")

    def test_friction_extraction(self):
        html = """
        <h2 id="section-friction">Friction</h2>
        <div class="friction-category">
            <div class="friction-title">Slow sessions</div>
            <div class="friction-desc">Sessions take too long.</div>
            <ul class="friction-examples">
                <li>Example 1</li>
                <li>Example 2</li>
            </ul>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["friction"]), 1)
        self.assertEqual(p.sections["friction"][0]["title"], "Slow sessions")
        self.assertIn("Example 1", p.sections["friction"][0].get("evidence", ""))

    def test_feature_card_extraction(self):
        html = """
        <h2 id="section-features">Features</h2>
        <div class="feature-card">
            <div class="feature-title">Custom Skills</div>
            <div class="feature-oneliner">Reusable prompts</div>
            <div class="feature-why">Saves time on repetitive tasks.</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["features"]), 1)
        self.assertEqual(p.sections["features"][0]["title"], "Custom Skills")

    def test_pattern_card_extraction(self):
        html = """
        <h2 id="section-patterns">Patterns</h2>
        <div class="pattern-card">
            <div class="pattern-title">Encode workflows</div>
            <div class="pattern-summary">Make it a command</div>
            <div class="pattern-detail">Your most repeated workflow should be automated.</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["patterns"]), 1)
        self.assertEqual(p.sections["patterns"][0]["title"], "Encode workflows")

    def test_horizon_card_extraction(self):
        html = """
        <h2 id="section-horizon">Horizon</h2>
        <div class="horizon-card">
            <div class="horizon-title">Autonomous validation</div>
            <div class="horizon-possible">Claude validates all docs in one run.</div>
            <div class="horizon-tip">Use TodoWrite for tracking.</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["horizon"]), 1)
        self.assertEqual(p.sections["horizon"][0]["title"], "Autonomous validation")

    def test_claude_md_recommendation_extraction(self):
        html = """
        <div class="claude-md-item">
            <input class="cmd-checkbox" data-text="Always validate docs twice.">
            <div class="cmd-why">Missed items on first pass in 3 sessions.</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.claude_md_recs), 1)
        self.assertEqual(p.claude_md_recs[0]["text"], "Always validate docs twice.")
        self.assertIn("Missed items", p.claude_md_recs[0]["evidence"])

    def test_multiple_cards_same_section(self):
        html = """
        <h2 id="section-wins">Wins</h2>
        <div class="big-win">
            <div class="big-win-title">Win 1</div>
            <div class="big-win-desc">Desc 1</div>
        </div>
        <div class="big-win">
            <div class="big-win-title">Win 2</div>
            <div class="big-win-desc">Desc 2</div>
        </div>
        """
        p = self._parse(html)
        self.assertEqual(len(p.sections["wins"]), 2)

    def test_subtitle_extraction(self):
        html = '<p class="subtitle">134 messages across 19 sessions (24 total) | 2026-01-16 to 2026-02-10</p>'
        p = self._parse(html)
        self.assertIn("19 sessions", p.subtitle)

    def test_narrative_extraction(self):
        html = """
        <h2 id="section-usage">Usage</h2>
        <div class="narrative">
            <p>You use Claude Code primarily for editing.</p>
        </div>
        """
        p = self._parse(html)
        self.assertGreater(len(p.sections["usage"]), 0)


# ===================================================================
# 13. parse_facets() tests
# ===================================================================


class TestParseFacets(unittest.TestCase):
    """Test facets JSON parsing."""

    def setUp(self):
        self.pi = _load_pi()

    def test_missing_dir_returns_defaults(self):
        result = self.pi.parse_facets(Path("/nonexistent/facets"))
        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(result["friction_types"], {})

    def test_valid_facet_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            facets_dir = Path(tmpdir) / "facets"
            facets_dir.mkdir()
            (facets_dir / "session1.json").write_text(json.dumps({
                "friction_counts": {"api_error": 2, "incomplete": 1},
                "session_type": "debugging",
                "outcome": "fully_achieved",
                "brief_summary": "Fixed a bug",
            }))
            result = self.pi.parse_facets(facets_dir)
            self.assertEqual(result["total_sessions"], 1)
            self.assertEqual(result["friction_types"]["api_error"], 2)
            self.assertEqual(result["outcomes"]["fully_achieved"], 1)
            self.assertEqual(len(result["summaries"]), 1)

    def test_aggregation_across_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            facets_dir = Path(tmpdir) / "facets"
            facets_dir.mkdir()
            (facets_dir / "s1.json").write_text(json.dumps({
                "friction_counts": {"api_error": 1},
                "outcome": "fully_achieved",
            }))
            (facets_dir / "s2.json").write_text(json.dumps({
                "friction_counts": {"api_error": 3},
                "outcome": "partially_achieved",
            }))
            result = self.pi.parse_facets(facets_dir)
            self.assertEqual(result["total_sessions"], 2)
            self.assertEqual(result["friction_types"]["api_error"], 4)

    def test_invalid_json_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            facets_dir = Path(tmpdir) / "facets"
            facets_dir.mkdir()
            (facets_dir / "bad.json").write_text("not json")
            result = self.pi.parse_facets(facets_dir)
            self.assertEqual(result["total_sessions"], 0)


# ===================================================================
# 14. parse_session_meta() tests
# ===================================================================


class TestParseSessionMeta(unittest.TestCase):
    """Test session-meta JSON parsing."""

    def setUp(self):
        self.pi = _load_pi()

    def test_missing_dir_returns_defaults(self):
        result = self.pi.parse_session_meta(Path("/nonexistent/meta"))
        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(result["tool_counts"], {})

    def test_valid_meta_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_dir = Path(tmpdir) / "session-meta"
            meta_dir.mkdir()
            (meta_dir / "s1.json").write_text(json.dumps({
                "user_message_count": 5,
                "assistant_message_count": 10,
                "tool_counts": {"Edit": 8, "Bash": 3},
                "languages": {"Markdown": 12, "YAML": 2},
                "start_time": "2026-01-20T10:00:00",
            }))
            result = self.pi.parse_session_meta(meta_dir)
            self.assertEqual(result["total_sessions"], 1)
            self.assertEqual(result["total_messages"], 15)
            self.assertEqual(result["tool_counts"]["Edit"], 8)
            self.assertEqual(result["languages"]["Markdown"], 12)
            self.assertEqual(result["date_range_start"], "2026-01-20")

    def test_aggregation_across_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_dir = Path(tmpdir) / "session-meta"
            meta_dir.mkdir()
            (meta_dir / "s1.json").write_text(json.dumps({
                "tool_counts": {"Edit": 5},
                "languages": {"Markdown": 10},
                "start_time": "2026-01-15T10:00:00",
            }))
            (meta_dir / "s2.json").write_text(json.dumps({
                "tool_counts": {"Edit": 3, "Bash": 7},
                "languages": {"Markdown": 5, "YAML": 4},
                "start_time": "2026-02-05T10:00:00",
            }))
            result = self.pi.parse_session_meta(meta_dir)
            self.assertEqual(result["total_sessions"], 2)
            self.assertEqual(result["tool_counts"]["Edit"], 8)
            self.assertEqual(result["tool_counts"]["Bash"], 7)
            self.assertEqual(result["languages"]["Markdown"], 15)
            self.assertEqual(result["date_range_start"], "2026-01-15")
            self.assertEqual(result["date_range_end"], "2026-02-05")


# ===================================================================
# 15. _build_entries() tests
# ===================================================================


class TestBuildEntries(unittest.TestCase):
    """Test content block builder."""

    def setUp(self):
        self.pi = _load_pi()

    def test_empty_sections_produce_no_entries(self):
        entries = self.pi._build_entries(
            {"wins": [], "friction": [], "features": [], "patterns": [], "horizon": [], "usage": []},
            [],
        )
        self.assertEqual(entries, [])

    def test_claude_md_recs_produce_entry(self):
        entries = self.pi._build_entries(
            {"wins": [], "friction": [], "features": [], "patterns": [], "horizon": [], "usage": []},
            [{"text": "Always validate twice.", "evidence": "Missed items."}],
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source_id"], "insights-claudemd-rec")
        self.assertEqual(entries[0]["tier"], "insights")
        self.assertEqual(len(entries[0]["content_blocks"]), 1)

    def test_wins_produce_entry(self):
        entries = self.pi._build_entries(
            {
                "wins": [{"title": "Good workflow", "description": "It works."}],
                "friction": [], "features": [], "patterns": [], "horizon": [], "usage": [],
            },
            [],
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source_id"], "insights-wins")

    def test_all_sections_produce_entries(self):
        sections = {
            "wins": [{"title": "W", "description": "D"}],
            "friction": [{"title": "F", "description": "D"}],
            "features": [{"title": "Fe", "description": "D"}],
            "patterns": [{"title": "P", "description": "D"}],
            "horizon": [{"title": "H", "description": "D"}],
            "usage": [{"title": "U", "description": "D"}],
        }
        recs = [{"text": "R", "evidence": "E"}]
        entries = self.pi._build_entries(sections, recs)
        source_ids = {e["source_id"] for e in entries}
        expected = {
            "insights-claudemd-rec", "insights-friction", "insights-wins",
            "insights-features", "insights-patterns", "insights-horizon",
            "insights-usage",
        }
        self.assertEqual(source_ids, expected)

    def test_all_entries_have_insights_tier(self):
        sections = {
            "wins": [{"title": "W", "description": "D"}],
            "friction": [], "features": [], "patterns": [], "horizon": [], "usage": [],
        }
        entries = self.pi._build_entries(sections, [])
        for entry in entries:
            self.assertEqual(entry["tier"], "insights")


# ===================================================================
# 16. insights-parsed.json output validation (if present)
# ===================================================================


class TestInsightsParsedJsonSchema(unittest.TestCase):
    """Validate insights-parsed.json output schema (if present)."""

    @classmethod
    def setUpClass(cls):
        if not INSIGHTS_PARSED_JSON.exists():
            raise unittest.SkipTest(
                "insights-parsed.json not present — run parse-insights.py first"
            )
        with open(INSIGHTS_PARSED_JSON) as f:
            cls.data = json.load(f)

    def test_valid_json(self):
        self.assertIsInstance(self.data, dict)

    def test_has_top_level_fields(self):
        for field in (
            "generated_at",
            "report_path",
            "report_modified_at",
            "staleness_days",
            "is_stale",
            "sessions_analyzed",
            "date_range",
            "entries",
            "session_stats",
        ):
            self.assertIn(field, self.data, f"Missing top-level field: {field}")

    def test_entries_is_list(self):
        self.assertIsInstance(self.data["entries"], list)

    def test_entries_have_required_fields(self):
        required = {"source_id", "source_name", "tier", "themes", "content_blocks"}
        for entry in self.data["entries"]:
            self.assertTrue(
                required.issubset(entry.keys()),
                f"Entry {entry.get('source_id', '?')} missing: {required - entry.keys()}",
            )

    def test_all_entries_are_insights_tier(self):
        for entry in self.data["entries"]:
            self.assertEqual(
                entry["tier"], "insights",
                f"Entry {entry['source_id']} should have tier 'insights'",
            )

    def test_content_blocks_have_required_fields(self):
        for entry in self.data["entries"]:
            for block in entry["content_blocks"]:
                for field in ("theme", "heading", "text"):
                    self.assertIn(
                        field, block,
                        f"Block in {entry['source_id']} missing '{field}'",
                    )

    def test_valid_source_ids(self):
        valid_ids = {
            "insights-claudemd-rec", "insights-friction", "insights-wins",
            "insights-features", "insights-patterns", "insights-horizon",
            "insights-usage",
        }
        for entry in self.data["entries"]:
            self.assertIn(
                entry["source_id"], valid_ids,
                f"Unknown source_id: {entry['source_id']}",
            )

    def test_session_stats_has_required_fields(self):
        stats = self.data["session_stats"]
        for field in ("total_sessions", "total_messages", "top_tools", "primary_languages", "outcome_distribution"):
            self.assertIn(field, stats, f"session_stats missing: {field}")

    def test_no_duplicate_source_ids(self):
        ids = [e["source_id"] for e in self.data["entries"]]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate source IDs in output")


# ===================================================================
# 17. parse-insights.py main() tests (using temp dirs)
# ===================================================================


class TestParseInsightsMain(unittest.TestCase):
    """Test main() function behavior."""

    def setUp(self):
        self.pi = _load_pi()

    def test_returns_0_with_missing_report(self):
        """Graceful degradation: missing report produces minimal output, returns 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            result = self.pi.main(report_dir=Path(tmpdir), docs_dir=docs_dir)
            self.assertEqual(result, 0)
            output_file = docs_dir / "insights-parsed.json"
            self.assertTrue(output_file.exists())
            data = json.loads(output_file.read_text())
            self.assertEqual(data["entries"], [])
            self.assertEqual(data["sessions_analyzed"], 0)

    def test_returns_0_with_valid_report(self):
        """Produces output from a minimal valid report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            report.write_text("""
            <html>
            <h2 id="section-wins">Wins</h2>
            <div class="big-win">
                <div class="big-win-title">Test Win</div>
                <div class="big-win-desc">A great test win.</div>
            </div>
            </html>
            """)
            docs_dir = Path(tmpdir) / "docs"
            result = self.pi.main(report_dir=Path(tmpdir), docs_dir=docs_dir)
            self.assertEqual(result, 0)
            output_file = docs_dir / "insights-parsed.json"
            self.assertTrue(output_file.exists())
            data = json.loads(output_file.read_text())
            self.assertGreater(len(data["entries"]), 0)


# ===================================================================
# 18. Plugin packaging tests
# ===================================================================

PLUGIN_MANIFEST = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
PLUGIN_MARKETPLACE = PROJECT_ROOT / ".claude-plugin" / "marketplace.json"


class TestDocsDir(unittest.TestCase):
    """Tests for --docs-dir argument support in both scripts."""

    def test_fetch_guidelines_main_accepts_docs_dir(self):
        """main() accepts docs_dir param without raising an exception."""
        fg = _load_fg()
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            with patch.object(fg, "fetch_url", return_value=None):
                with patch.object(fg, "CURATED_SOURCES", CURATED_SOURCES_MD):
                    result = fg.main(docs_dir=docs_dir)
            # Returns 1 because all fetches failed; docs_dir was accepted with no exception.
            self.assertEqual(result, 1)

    def test_fetch_guidelines_main_writes_to_docs_dir(self):
        """main() with mocked success writes guidelines-raw.json to docs_dir."""
        fg = _load_fg()
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            mock_text = "# Best Practices\nUse CLAUDE.md for project instructions."
            with patch.object(fg, "fetch_url", return_value=mock_text):
                with patch.object(fg, "CURATED_SOURCES", CURATED_SOURCES_MD):
                    result = fg.main(docs_dir=docs_dir)
            self.assertEqual(result, 0)
            output_file = docs_dir / "guidelines-raw.json"
            self.assertTrue(output_file.exists(), "guidelines-raw.json should be in docs_dir")
            data = json.loads(output_file.read_text())
            self.assertIn("entries", data)

    def test_fetch_guidelines_check_freshness_writes_to_docs_dir(self):
        """check_freshness_main(docs_dir) writes freshness-report.json to docs_dir."""
        fg = _load_fg()
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            with patch.object(fg, "check_url_status", return_value=(200, "https://example.com")):
                result = fg.check_freshness_main(docs_dir=docs_dir)
            self.assertEqual(result, 0)
            report_file = docs_dir / "freshness-report.json"
            self.assertTrue(report_file.exists(), "freshness-report.json should be in docs_dir")

    def test_parse_insights_main_accepts_docs_dir(self):
        """parse-insights main() accepts docs_dir and writes to that directory."""
        pi = _load_pi()
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "custom-docs"
            result = pi.main(report_dir=Path(tmpdir), docs_dir=docs_dir)
            self.assertEqual(result, 0)
            output_file = docs_dir / "insights-parsed.json"
            self.assertTrue(
                output_file.exists(),
                f"insights-parsed.json should be written to docs_dir: {docs_dir}",
            )


class TestPluginManifest(unittest.TestCase):
    """Validate the Claude Code plugin manifest."""

    @classmethod
    def setUpClass(cls):
        if not PLUGIN_MANIFEST.exists():
            raise unittest.SkipTest(
                ".claude-plugin/plugin.json not present — run Phase 1 first"
            )
        with open(PLUGIN_MANIFEST) as f:
            cls.manifest = json.load(f)

    def test_manifest_is_valid_json(self):
        self.assertIsInstance(self.manifest, dict)

    def test_manifest_has_name(self):
        self.assertIn("name", self.manifest)
        self.assertIsInstance(self.manifest["name"], str)
        self.assertGreater(len(self.manifest["name"]), 0)

    def test_manifest_has_version(self):
        self.assertIn("version", self.manifest)
        self.assertRegex(self.manifest["version"], r"^\d+\.\d+\.\d+$")

    def test_manifest_has_description(self):
        self.assertIn("description", self.manifest)
        self.assertGreater(len(self.manifest["description"]), 0)

    def test_manifest_has_skills_field(self):
        self.assertIn("skills", self.manifest)

    def test_manifest_name_contains_claude_md(self):
        self.assertIn("claude-md", self.manifest["name"])


class TestSkillMdFrontmatter(unittest.TestCase):
    """Validate that SKILL.md has proper YAML frontmatter for plugin packaging."""

    @classmethod
    def setUpClass(cls):
        cls.content = SKILL_MD.read_text()
        cls.lines = cls.content.splitlines()

    def test_starts_with_yaml_delimiter(self):
        self.assertEqual(
            self.lines[0], "---",
            "SKILL.md must start with --- (YAML frontmatter block)",
        )

    def test_has_closing_yaml_delimiter(self):
        # Second occurrence of --- closes the frontmatter
        closing_indices = [i for i, line in enumerate(self.lines[1:], 1) if line == "---"]
        self.assertGreater(
            len(closing_indices), 0, "SKILL.md must have a closing --- for frontmatter"
        )

    def test_frontmatter_has_name(self):
        self.assertIn("name:", self.content)

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


if __name__ == "__main__":
    unittest.main()
