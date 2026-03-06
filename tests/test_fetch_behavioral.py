"""
Sprint 2: Behavioral Test Coverage — fetch-guidelines.py

Tests exercise actual script behavior (not just structure):
  - HTMLTextExtractor strips unwanted tags, preserves headings text
  - extract_content_blocks themes sections from markdown-headed text
  - main() end-to-end with mocked fetch_url: JSON schema, content blocks,
    source metadata preserved, partial failure still produces valid output
  - check_freshness_main() with mocked check_url_status: stale and broken flagging
  - Edge cases: empty sources, all failures, no headings (single-block fallback),
    content exceeding MAX_CONTENT_LENGTH

All tests run fully offline — no network calls are made.
"""

import importlib.util
import json
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = (
    PROJECT_ROOT / "skills" / "refresh-guidelines" / "scripts" / "fetch-guidelines.py"
)
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

_fg_module = None


def _load_fg():
    global _fg_module
    if _fg_module is not None:
        return _fg_module
    spec = importlib.util.spec_from_file_location("fetch_guidelines", SCRIPT_PATH)
    _fg_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_fg_module)
    return _fg_module


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

# A single source entry as parse_curated_sources would return
SAMPLE_SOURCE = {
    "id": "T1-001",
    "source_name": "Test Best Practices Source",
    "url": "https://example.com/best-practices",
    "tier": 1,
    "themes": ["structural", "content"],
    "last_verified": "2026-01-01",
}

# Markdown-headed text as fetch_url would return after HTML stripping
# (uses # headings so extract_content_blocks finds multiple themed sections)
MOCK_FETCH_TEXT = textwrap.dedent("""\
    # CLAUDE.md Best Practices

    Introduction about effective CLAUDE.md authoring.

    ## Structure and Format

    Keep your CLAUDE.md file well organized with clear sections.
    Use proper size, length, and layout guidelines. Good skeleton helps.

    ## Content and Documentation

    Document important conventions and rules.
    Always include and describe what matters. Write clear instructions.

    ## Anti-Patterns to Avoid

    Avoid common mistakes and anti-patterns. Never bloat your file.
    Don't use wrong approaches or embed unnecessary code.

    ## Maintenance and Updates

    Update and review your CLAUDE.md regularly. Refresh when stale or outdated.
    Improve incrementally to keep it current and useful.
""")


# ===========================================================================
# 1. HTMLTextExtractor unit tests
# ===========================================================================


class TestHTMLTextExtractor(unittest.TestCase):
    """HTMLTextExtractor strips skip-tags and preserves readable content."""

    def setUp(self):
        self.fg = _load_fg()
        self.fixture_html = (FIXTURES_DIR / "sample-source.html").read_text()

    def test_strip_html_returns_nonempty_string(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result.strip()), 0)

    def test_script_content_excluded(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertNotIn("this should not appear", result)
        self.assertNotIn("trackingData", result)

    def test_nav_content_excluded(self):
        result = self.fg.strip_html(self.fixture_html)
        # Nav links should be excluded (nav is a SKIP_TAG)
        self.assertNotIn("Home", result)

    def test_footer_content_excluded(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertNotIn("Footer content", result)

    def test_heading_text_preserved(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertIn("Structure and Format", result)
        self.assertIn("Content and Documentation", result)
        self.assertIn("Anti-Patterns to Avoid", result)

    def test_paragraph_content_preserved(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertIn("CLAUDE.md", result)

    def test_no_raw_tags_in_output(self):
        result = self.fg.strip_html(self.fixture_html)
        self.assertNotIn("<html>", result)
        self.assertNotIn("<body>", result)
        self.assertNotIn("<h2>", result)
        self.assertNotIn("<p>", result)


# ===========================================================================
# 2. extract_content_blocks unit tests
# ===========================================================================


class TestExtractContentBlocks(unittest.TestCase):
    """extract_content_blocks splits text into themed sections."""

    def setUp(self):
        self.fg = _load_fg()

    def test_returns_list(self):
        blocks = self.fg.extract_content_blocks(MOCK_FETCH_TEXT, ["structural"])
        self.assertIsInstance(blocks, list)

    def test_multiple_blocks_from_headed_text(self):
        blocks = self.fg.extract_content_blocks(MOCK_FETCH_TEXT, ["structural", "content"])
        self.assertGreater(len(blocks), 1)

    def test_block_has_required_fields(self):
        blocks = self.fg.extract_content_blocks(MOCK_FETCH_TEXT, ["structural"])
        for block in blocks:
            self.assertIn("theme", block)
            self.assertIn("heading", block)
            self.assertIn("text", block)

    def test_structure_section_gets_structural_theme(self):
        blocks = self.fg.extract_content_blocks(MOCK_FETCH_TEXT, ["structural", "content"])
        headings_by_theme = {b["heading"]: b["theme"] for b in blocks}
        self.assertIn("Structure and Format", headings_by_theme)
        self.assertEqual(headings_by_theme["Structure and Format"], "structural")

    def test_antipatterns_section_gets_antipatterns_theme(self):
        blocks = self.fg.extract_content_blocks(MOCK_FETCH_TEXT, ["anti-patterns", "structural"])
        headings_by_theme = {b["heading"]: b["theme"] for b in blocks}
        self.assertIn("Anti-Patterns to Avoid", headings_by_theme)
        self.assertEqual(headings_by_theme["Anti-Patterns to Avoid"], "anti-patterns")

    def test_no_headings_returns_single_block(self):
        text = "Just plain text with no markdown headings at all."
        blocks = self.fg.extract_content_blocks(text, ["content"])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["heading"], "(no heading)")

    def test_no_headings_single_block_uses_first_theme(self):
        text = "Plain text without headings."
        blocks = self.fg.extract_content_blocks(text, ["structural", "content"])
        self.assertEqual(blocks[0]["theme"], "structural")

    def test_empty_text_returns_no_blocks(self):
        blocks = self.fg.extract_content_blocks("", ["content"])
        self.assertEqual(blocks, [])

    def test_text_truncated_at_2000_chars(self):
        long_body = "word " * 1000  # ~5000 chars
        text = f"## Big Section\n{long_body}"
        # Use empty themes list to bypass theme filtering
        blocks = self.fg.extract_content_blocks(text, [])
        self.assertGreater(len(blocks), 0)
        for block in blocks:
            self.assertLessEqual(len(block["text"]), 2003)  # 2000 + "..."

    def test_truncated_text_ends_with_ellipsis(self):
        long_body = "x" * 3000
        text = f"## Section\n{long_body}"
        # Use empty themes list to bypass theme filtering
        blocks = self.fg.extract_content_blocks(text, [])
        self.assertTrue(blocks[0]["text"].endswith("..."))


# ===========================================================================
# 3. main() end-to-end tests
# ===========================================================================


class TestFetchMainEndToEnd(unittest.TestCase):
    """main() end-to-end with mocked HTTP — no network calls."""

    def setUp(self):
        self.fg = _load_fg()
        self.tmpdir = Path(tempfile.mkdtemp())

    def _run_main(self, sources=None, fetch_return=MOCK_FETCH_TEXT):
        src = sources if sources is not None else [SAMPLE_SOURCE]
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=src),
            patch.object(self.fg, "fetch_url", return_value=fetch_return),
        ):
            return self.fg.main(docs_dir=self.tmpdir)

    def _load_output(self):
        return json.loads((self.tmpdir / "guidelines-raw.json").read_text())

    def test_returns_0_on_success(self):
        self.assertEqual(self._run_main(), 0)

    def test_writes_output_file(self):
        self._run_main()
        self.assertTrue((self.tmpdir / "guidelines-raw.json").exists())

    def test_output_top_level_schema(self):
        self._run_main()
        data = self._load_output()
        for key in ("generated_at", "sources_attempted", "sources_fetched",
                    "sources_failed", "entries"):
            self.assertIn(key, data)

    def test_sources_counts_correct(self):
        self._run_main()
        data = self._load_output()
        self.assertEqual(data["sources_attempted"], 1)
        self.assertEqual(data["sources_fetched"], 1)
        self.assertEqual(data["sources_failed"], 0)

    def test_one_entry_per_successful_source(self):
        self._run_main()
        data = self._load_output()
        self.assertEqual(len(data["entries"]), 1)

    def test_entry_schema(self):
        self._run_main()
        entry = self._load_output()["entries"][0]
        for key in ("source_id", "source_url", "source_name", "tier",
                    "themes", "last_fetched", "content_blocks"):
            self.assertIn(key, entry)

    def test_source_metadata_preserved_in_entry(self):
        self._run_main()
        entry = self._load_output()["entries"][0]
        self.assertEqual(entry["source_id"], "T1-001")
        self.assertEqual(entry["source_name"], "Test Best Practices Source")
        self.assertEqual(entry["tier"], 1)
        self.assertEqual(entry["themes"], ["structural", "content"])

    def test_content_blocks_nonempty(self):
        self._run_main()
        entry = self._load_output()["entries"][0]
        self.assertGreater(len(entry["content_blocks"]), 0)

    def test_content_blocks_schema(self):
        self._run_main()
        blocks = self._load_output()["entries"][0]["content_blocks"]
        for block in blocks:
            self.assertIn("theme", block)
            self.assertIn("heading", block)
            self.assertIn("text", block)

    def test_partial_failure_produces_valid_output(self):
        sources = [
            {**SAMPLE_SOURCE, "id": "T1-001", "url": "https://ok.example.com"},
            {**SAMPLE_SOURCE, "id": "T1-002", "url": "https://fail.example.com"},
        ]

        def selective_fetch(url):
            return MOCK_FETCH_TEXT if "ok" in url else None

        with (
            patch.object(self.fg, "parse_curated_sources", return_value=sources),
            patch.object(self.fg, "fetch_url", side_effect=selective_fetch),
        ):
            result = self.fg.main(docs_dir=self.tmpdir)

        self.assertEqual(result, 0)
        data = self._load_output()
        self.assertEqual(data["sources_attempted"], 2)
        self.assertEqual(data["sources_fetched"], 1)
        self.assertEqual(data["sources_failed"], 1)
        self.assertEqual(len(data["entries"]), 1)

    def test_generated_at_is_iso_timestamp(self):
        self._run_main()
        ts = self._load_output()["generated_at"]
        # Should parse as ISO 8601 without raising
        from datetime import datetime
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ===========================================================================
# 4. main() edge cases
# ===========================================================================


class TestFetchMainEdgeCases(unittest.TestCase):
    """Edge cases: empty sources, all failures, no headings, oversized content."""

    def setUp(self):
        self.fg = _load_fg()
        self.tmpdir = Path(tempfile.mkdtemp())

    def test_all_urls_fail_returns_1(self):
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[SAMPLE_SOURCE]),
            patch.object(self.fg, "fetch_url", return_value=None),
        ):
            result = self.fg.main(docs_dir=self.tmpdir)
        self.assertEqual(result, 1)

    def test_no_sources_returns_1(self):
        with patch.object(self.fg, "parse_curated_sources", return_value=[]):
            result = self.fg.main(docs_dir=self.tmpdir)
        self.assertEqual(result, 1)

    def test_html_with_no_headings_single_block_fallback(self):
        html = "<html><body><p>Just plain text, no markdown headings here.</p></body></html>"
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[SAMPLE_SOURCE]),
            patch.object(self.fg, "fetch_url", return_value=html),
        ):
            result = self.fg.main(docs_dir=self.tmpdir)

        self.assertEqual(result, 0)
        data = json.loads((self.tmpdir / "guidelines-raw.json").read_text())
        blocks = data["entries"][0]["content_blocks"]
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["heading"], "(no heading)")

    def test_content_exceeding_max_is_truncated(self):
        long_section = "word " * 1000  # ~5000 chars, well above 2000 limit
        text = f"## Oversized Section\n{long_section}"
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[SAMPLE_SOURCE]),
            patch.object(self.fg, "fetch_url", return_value=text),
        ):
            self.fg.main(docs_dir=self.tmpdir)

        data = json.loads((self.tmpdir / "guidelines-raw.json").read_text())
        for block in data["entries"][0]["content_blocks"]:
            self.assertLessEqual(len(block["text"]), 2003)

    def test_multiple_sources_all_fail_returns_1(self):
        sources = [
            {**SAMPLE_SOURCE, "id": "T1-001"},
            {**SAMPLE_SOURCE, "id": "T1-002"},
        ]
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=sources),
            patch.object(self.fg, "fetch_url", return_value=None),
        ):
            result = self.fg.main(docs_dir=self.tmpdir)
        self.assertEqual(result, 1)


# ===========================================================================
# 5. check_freshness_main() behavioral tests
# ===========================================================================


class TestFreshnessCheckBehavioral(unittest.TestCase):
    """check_freshness_main() with mocked check_url_status — no network calls."""

    def setUp(self):
        self.fg = _load_fg()
        self.tmpdir = Path(tempfile.mkdtemp())

    def _run_freshness(self, sources=None, url_status=(200, "https://example.com")):
        src = sources if sources is not None else [SAMPLE_SOURCE]
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=src),
            patch.object(self.fg, "check_url_status", return_value=url_status),
        ):
            return self.fg.check_freshness_main(self.tmpdir)

    def _load_report(self):
        return json.loads((self.tmpdir / "freshness-report.json").read_text())

    def test_returns_0_on_success(self):
        self.assertEqual(self._run_freshness(), 0)

    def test_writes_freshness_report(self):
        self._run_freshness()
        self.assertTrue((self.tmpdir / "freshness-report.json").exists())

    def test_report_top_level_schema(self):
        self._run_freshness()
        report = self._load_report()
        for key in ("generated_at", "stale_threshold_days", "total_sources",
                    "stale_count", "broken_count", "needs_attention_count", "sources"):
            self.assertIn(key, report)

    def test_report_source_entry_schema(self):
        self._run_freshness()
        src_entry = self._load_report()["sources"][0]
        for key in ("id", "source_name", "url", "tier", "last_verified",
                    "is_stale", "days_since_verified", "http_status",
                    "is_reachable", "final_url", "needs_attention"):
            self.assertIn(key, src_entry)

    def test_ok_source_not_flagged(self):
        from datetime import date
        today_str = date.today().strftime("%Y-%m-%d")
        recent_source = {**SAMPLE_SOURCE, "last_verified": today_str}
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[recent_source]),
            patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")),
        ):
            self.fg.check_freshness_main(self.tmpdir)
        report = self._load_report()
        self.assertEqual(report["stale_count"], 0)
        self.assertEqual(report["broken_count"], 0)

    def test_stale_source_flagged(self):
        stale_source = {**SAMPLE_SOURCE, "last_verified": "2020-01-01"}  # Years old
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[stale_source]),
            patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")),
        ):
            self.fg.check_freshness_main(self.tmpdir)

        report = self._load_report()
        self.assertEqual(report["stale_count"], 1)
        self.assertTrue(report["sources"][0]["is_stale"])
        self.assertTrue(report["sources"][0]["needs_attention"])

    def test_http_404_flagged_as_broken(self):
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[SAMPLE_SOURCE]),
            patch.object(self.fg, "check_url_status", return_value=(404, None)),
        ):
            self.fg.check_freshness_main(self.tmpdir)

        report = self._load_report()
        self.assertEqual(report["broken_count"], 1)
        self.assertFalse(report["sources"][0]["is_reachable"])
        self.assertEqual(report["sources"][0]["http_status"], 404)

    def test_unreachable_source_flagged_as_broken(self):
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[SAMPLE_SOURCE]),
            patch.object(self.fg, "check_url_status", return_value=(None, None)),
        ):
            self.fg.check_freshness_main(self.tmpdir)

        report = self._load_report()
        self.assertEqual(report["broken_count"], 1)
        self.assertFalse(report["sources"][0]["is_reachable"])
        self.assertIsNone(report["sources"][0]["http_status"])

    def test_missing_last_verified_treated_as_stale(self):
        no_date_source = {**SAMPLE_SOURCE, "last_verified": None}
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=[no_date_source]),
            patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")),
        ):
            self.fg.check_freshness_main(self.tmpdir)

        report = self._load_report()
        self.assertEqual(report["stale_count"], 1)
        self.assertTrue(report["sources"][0]["is_stale"])

    def test_total_sources_count_correct(self):
        sources = [
            {**SAMPLE_SOURCE, "id": "T1-001"},
            {**SAMPLE_SOURCE, "id": "T1-002"},
            {**SAMPLE_SOURCE, "id": "T1-003"},
        ]
        with (
            patch.object(self.fg, "parse_curated_sources", return_value=sources),
            patch.object(self.fg, "check_url_status", return_value=(200, "https://example.com")),
        ):
            self.fg.check_freshness_main(self.tmpdir)

        report = self._load_report()
        self.assertEqual(report["total_sources"], 3)


if __name__ == "__main__":
    unittest.main()
