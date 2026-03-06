"""
Sprint 2: Behavioral Test Coverage — parse-insights.py

Tests exercise actual script behavior (not just structure):
  - InsightsHTMLParser extracts all 7 section types from fixture HTML
  - main() end-to-end with fixture report_dir: JSON schema, sections populated,
    CLAUDE.md recs extracted, subtitle parsed, session stats collected
  - Missing report graceful degradation: returns 0, writes minimal output
  - Stale report warning: is_stale=True when report mtime is 14+ days old

All tests run fully offline — no network calls are made.
"""

import importlib.util
import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARSE_INSIGHTS_PATH = (
    PROJECT_ROOT / "skills" / "refresh-guidelines" / "scripts" / "parse-insights.py"
)
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

_pi_module = None


def _load_pi():
    global _pi_module
    if _pi_module is not None:
        return _pi_module
    spec = importlib.util.spec_from_file_location("parse_insights", PARSE_INSIGHTS_PATH)
    _pi_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_pi_module)
    return _pi_module


# ===========================================================================
# 1. InsightsHTMLParser unit tests
# ===========================================================================


class TestInsightsHTMLParser(unittest.TestCase):
    """InsightsHTMLParser extracts structured data from fixture report HTML."""

    def setUp(self):
        self.pi = _load_pi()
        self.html = (FIXTURES_DIR / "sample-report.html").read_text()

    def _parse(self):
        parser = self.pi.InsightsHTMLParser()
        parser.feed(self.html)
        return parser

    def test_wins_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["wins"]), 0)

    def test_wins_entry_has_title_and_description(self):
        parser = self._parse()
        win = parser.sections["wins"][0]
        self.assertIn("title", win)
        self.assertIn("description", win)
        self.assertEqual(win["title"], "Test-Driven Development")

    def test_friction_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["friction"]), 0)

    def test_friction_entry_has_evidence(self):
        parser = self._parse()
        friction = parser.sections["friction"][0]
        self.assertIn("evidence", friction)
        self.assertIn("Forgetting previous architectural decisions", friction["evidence"])

    def test_features_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["features"]), 0)

    def test_feature_entry_has_one_liner(self):
        parser = self._parse()
        feature = parser.sections["features"][0]
        self.assertIn("one_liner", feature)
        self.assertIn("Session-persistent memory", feature["one_liner"])

    def test_patterns_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["patterns"]), 0)

    def test_pattern_entry_has_summary(self):
        parser = self._parse()
        pattern = parser.sections["patterns"][0]
        self.assertIn("summary", pattern)
        self.assertIn("Progressive improvement", pattern["summary"])

    def test_horizon_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["horizon"]), 0)

    def test_horizon_entry_has_tip(self):
        parser = self._parse()
        horizon = parser.sections["horizon"][0]
        self.assertIn("tip", horizon)
        self.assertIn("pre-commit hook", horizon["tip"])

    def test_usage_section_populated(self):
        parser = self._parse()
        self.assertGreater(len(parser.sections["usage"]), 0)

    def test_claude_md_recs_extracted(self):
        parser = self._parse()
        self.assertGreater(len(parser.claude_md_recs), 0)

    def test_claude_md_rec_has_text(self):
        parser = self._parse()
        rec = parser.claude_md_recs[0]
        self.assertIn("text", rec)
        self.assertIn("Add always-use-tdd rule", rec["text"])

    def test_subtitle_extracted(self):
        parser = self._parse()
        self.assertIn("19 sessions", parser.subtitle)
        self.assertIn("2026-01-16", parser.subtitle)

    def test_stats_extracted(self):
        parser = self._parse()
        self.assertIn("Messages", parser.stats)
        self.assertIn("Sessions", parser.stats)


# ===========================================================================
# 2. parse_subtitle unit tests
# ===========================================================================


class TestParseSubtitle(unittest.TestCase):
    """_parse_subtitle extracts session count and date range."""

    def setUp(self):
        self.pi = _load_pi()

    def test_extracts_session_count(self):
        sessions, _ = self.pi._parse_subtitle(
            "134 messages across 19 sessions (24 total) | 2026-01-16 to 2026-02-10"
        )
        self.assertEqual(sessions, 19)

    def test_extracts_date_range(self):
        _, date_range = self.pi._parse_subtitle(
            "134 messages across 19 sessions (24 total) | 2026-01-16 to 2026-02-10"
        )
        self.assertEqual(date_range, "2026-01-16 to 2026-02-10")

    def test_empty_subtitle_returns_zeros(self):
        sessions, date_range = self.pi._parse_subtitle("")
        self.assertEqual(sessions, 0)
        self.assertEqual(date_range, "")


# ===========================================================================
# 3. parse_facets and parse_session_meta unit tests
# ===========================================================================


class TestParseFacets(unittest.TestCase):
    """parse_facets aggregates data from facets/*.json files."""

    def setUp(self):
        self.pi = _load_pi()

    def test_parses_fixture_facets(self):
        result = self.pi.parse_facets(FIXTURES_DIR / "facets")
        self.assertEqual(result["total_sessions"], 1)
        self.assertIn("success", result["outcomes"])
        self.assertIn("coding", result["session_types"])

    def test_friction_counts_aggregated(self):
        result = self.pi.parse_facets(FIXTURES_DIR / "facets")
        self.assertIn("context_loss", result["friction_types"])
        self.assertEqual(result["friction_types"]["context_loss"], 3)

    def test_brief_summaries_collected(self):
        result = self.pi.parse_facets(FIXTURES_DIR / "facets")
        self.assertEqual(len(result["summaries"]), 1)

    def test_missing_directory_returns_empty(self):
        result = self.pi.parse_facets(Path("/nonexistent/facets"))
        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(result["outcomes"], {})


class TestParseSessionMeta(unittest.TestCase):
    """parse_session_meta aggregates data from session-meta/*.json files."""

    def setUp(self):
        self.pi = _load_pi()

    def test_parses_fixture_session_meta(self):
        result = self.pi.parse_session_meta(FIXTURES_DIR / "session-meta")
        self.assertEqual(result["total_sessions"], 1)
        self.assertEqual(result["total_messages"], 35)  # 15 + 20

    def test_tool_counts_aggregated(self):
        result = self.pi.parse_session_meta(FIXTURES_DIR / "session-meta")
        self.assertIn("Read", result["tool_counts"])
        self.assertEqual(result["tool_counts"]["Read"], 12)

    def test_languages_aggregated(self):
        result = self.pi.parse_session_meta(FIXTURES_DIR / "session-meta")
        self.assertIn("python", result["languages"])

    def test_date_range_extracted(self):
        result = self.pi.parse_session_meta(FIXTURES_DIR / "session-meta")
        self.assertEqual(result["date_range_start"], "2026-01-16")

    def test_missing_directory_returns_empty(self):
        result = self.pi.parse_session_meta(Path("/nonexistent/session-meta"))
        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(result["tool_counts"], {})


# ===========================================================================
# 4. main() end-to-end with fixture report directory
# ===========================================================================


class TestInsightsMainEndToEnd(unittest.TestCase):
    """main() end-to-end with fixture report_dir — no network calls."""

    def setUp(self):
        self.pi = _load_pi()
        self.tmpdir = Path(tempfile.mkdtemp())
        self.docs_dir = self.tmpdir / "docs"
        self.docs_dir.mkdir()

        # Set up a fake usage-data directory with fixture files
        self.report_dir = self.tmpdir / "usage-data"
        self.report_dir.mkdir()
        shutil.copy(FIXTURES_DIR / "sample-report.html", self.report_dir / "report.html")
        shutil.copytree(FIXTURES_DIR / "facets", self.report_dir / "facets")
        shutil.copytree(FIXTURES_DIR / "session-meta", self.report_dir / "session-meta")

    def _load_output(self):
        return json.loads((self.docs_dir / "insights-parsed.json").read_text())

    def test_returns_0(self):
        result = self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        self.assertEqual(result, 0)

    def test_writes_output_file(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        self.assertTrue((self.docs_dir / "insights-parsed.json").exists())

    def test_output_top_level_schema(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        for key in ("generated_at", "report_path", "report_modified_at",
                    "staleness_days", "is_stale", "sessions_analyzed",
                    "date_range", "entries", "session_stats"):
            self.assertIn(key, data)

    def test_entries_nonempty(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertGreater(len(data["entries"]), 0)

    def test_wins_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-wins", source_ids)

    def test_friction_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-friction", source_ids)

    def test_features_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-features", source_ids)

    def test_patterns_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-patterns", source_ids)

    def test_horizon_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-horizon", source_ids)

    def test_claude_md_recs_entry_present(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        source_ids = [e["source_id"] for e in self._load_output()["entries"]]
        self.assertIn("insights-claudemd-rec", source_ids)

    def test_subtitle_sessions_parsed(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertEqual(data["sessions_analyzed"], 19)

    def test_subtitle_date_range_parsed(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertIn("2026-01-16", data["date_range"])
        self.assertIn("2026-02-10", data["date_range"])

    def test_session_stats_schema(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        stats = self._load_output()["session_stats"]
        for key in ("total_sessions", "total_messages", "top_tools",
                    "primary_languages", "outcome_distribution"):
            self.assertIn(key, stats)

    def test_session_stats_from_fixture_meta(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        stats = self._load_output()["session_stats"]
        self.assertEqual(stats["total_sessions"], 1)
        self.assertEqual(stats["total_messages"], 35)

    def test_outcome_distribution_from_fixture_facets(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        stats = self._load_output()["session_stats"]
        self.assertIn("success", stats["outcome_distribution"])

    def test_entry_content_blocks_nonempty(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        for entry in self._load_output()["entries"]:
            self.assertGreater(len(entry["content_blocks"]), 0,
                               f"Entry {entry['source_id']} has no content blocks")

    def test_generated_at_is_iso_timestamp(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        from datetime import datetime
        ts = self._load_output()["generated_at"]
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ===========================================================================
# 5. Missing report — graceful degradation
# ===========================================================================


class TestInsightsMissingReport(unittest.TestCase):
    """main() with nonexistent report_dir returns 0 and writes minimal output."""

    def setUp(self):
        self.pi = _load_pi()
        self.tmpdir = Path(tempfile.mkdtemp())
        self.docs_dir = self.tmpdir / "docs"
        self.docs_dir.mkdir()
        self.report_dir = self.tmpdir / "nonexistent-usage-data"  # Does not exist

    def test_returns_0_on_missing_report(self):
        result = self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        self.assertEqual(result, 0)

    def test_writes_output_file_on_missing_report(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        self.assertTrue((self.docs_dir / "insights-parsed.json").exists())

    def test_minimal_output_has_empty_entries(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = json.loads((self.docs_dir / "insights-parsed.json").read_text())
        self.assertEqual(data["entries"], [])

    def test_minimal_output_sessions_analyzed_is_zero(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = json.loads((self.docs_dir / "insights-parsed.json").read_text())
        self.assertEqual(data["sessions_analyzed"], 0)

    def test_minimal_output_schema_valid(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = json.loads((self.docs_dir / "insights-parsed.json").read_text())
        for key in ("generated_at", "report_path", "staleness_days",
                    "is_stale", "entries", "session_stats"):
            self.assertIn(key, data)

    def test_no_exception_on_missing_report(self):
        try:
            self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        except Exception as exc:
            self.fail(f"main() raised unexpected exception: {exc}")


# ===========================================================================
# 6. Stale report detection
# ===========================================================================


class TestInsightsStaleReport(unittest.TestCase):
    """main() detects and reports a stale report.html (mtime 14+ days old)."""

    def setUp(self):
        self.pi = _load_pi()
        self.tmpdir = Path(tempfile.mkdtemp())
        self.docs_dir = self.tmpdir / "docs"
        self.docs_dir.mkdir()
        self.report_dir = self.tmpdir / "usage-data"
        self.report_dir.mkdir()

        report_file = self.report_dir / "report.html"
        shutil.copy(FIXTURES_DIR / "sample-report.html", report_file)

        # Set mtime to 14 days ago so report is stale (threshold = 7 days)
        stale_time = time.time() - (14 * 24 * 3600)
        os.utime(report_file, (stale_time, stale_time))

    def _load_output(self):
        return json.loads((self.docs_dir / "insights-parsed.json").read_text())

    def test_is_stale_true_when_14_days_old(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertTrue(data["is_stale"])

    def test_staleness_days_at_least_14(self):
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertGreaterEqual(data["staleness_days"], 14)

    def test_stale_report_still_produces_entries(self):
        """Stale does not mean empty — content is still parsed."""
        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertGreater(len(data["entries"]), 0)

    def test_fresh_report_is_not_stale(self):
        """A report with current mtime should not be flagged as stale."""
        report_file = self.report_dir / "report.html"
        fresh_time = time.time()
        os.utime(report_file, (fresh_time, fresh_time))

        self.pi.main(report_dir=self.report_dir, docs_dir=self.docs_dir)
        data = self._load_output()
        self.assertFalse(data["is_stale"])
        self.assertLessEqual(data["staleness_days"], 1)


if __name__ == "__main__":
    unittest.main()
