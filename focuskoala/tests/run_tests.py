"""
Self-contained FocusKoala Test Runner (Uses standard library unittest)
Can be executed with: python3 focuskoala/tests/run_tests.py
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta

# Ensure focuskoala package is accessible
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from focuskoala.desktop.database import FocusKoalaDB
from focuskoala.desktop.rules import normalize_domain, evaluate_usage, get_reopen_message
from focuskoala.desktop.blocker import Blocker
from focuskoala.desktop.usage_tracker import UsageTracker
from focuskoala.desktop.todo import TodoManager
from focuskoala.desktop.pattern_engine import PatternEngine
from focuskoala.desktop.agent import FocusKoalaAgent


class TestFocusKoalaCore(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_fd)
        self.db = FocusKoalaDB(self.temp_path)

    def tearDown(self):
        try:
            os.remove(self.temp_path)
        except Exception:
            pass

    def test_database_initialization(self):
        websites = self.db.get_websites()
        self.assertGreaterEqual(len(websites), 3)
        domains = [w["domain"] for w in websites]
        self.assertIn("instagram.com", domains)
        self.assertIn("youtube.com", domains)
        self.assertIn("reddit.com", domains)

        # Verify test mode values for Instagram: 60s limit, 120s cooldown
        ig = self.db.get_website_by_domain("instagram.com")
        self.assertIsNotNone(ig)
        self.assertEqual(ig["limit_seconds"], 60)
        self.assertEqual(ig["cooldown_seconds"], 120)

    def test_domain_normalization(self):
        self.assertEqual(normalize_domain("https://www.instagram.com/p/123"), "instagram.com")
        self.assertEqual(normalize_domain("http://www.youtube.com/watch?v=abc"), "youtube.com")
        self.assertEqual(normalize_domain("reddit.com/r/programming"), "reddit.com")

    def test_test_mode_thresholds(self):
        # 30s warning
        warn_res = evaluate_usage("instagram.com", 30.0, 60, is_test_mode=True)
        self.assertTrue(warn_res["warning"])
        self.assertFalse(warn_res["should_block"])

        # 60s intervention
        block_res = evaluate_usage("instagram.com", 60.0, 60, is_test_mode=True)
        self.assertTrue(block_res["warning"])
        self.assertTrue(block_res["should_block"])
        self.assertEqual(block_res["remaining_seconds"], 0.0)

    def test_blocking_and_cooldown(self):
        blocker = Blocker(self.db)
        blocker.block_domain("instagram.com", 120)
        status = blocker.is_blocked("instagram.com")
        self.assertTrue(status["is_blocked"])
        self.assertGreater(status["remaining_seconds"], 100)

    def test_cooldown_expiry(self):
        blocker = Blocker(self.db)
        past_iso = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        self.db.set_block("instagram.com", past_iso)
        status = blocker.is_blocked("instagram.com")
        self.assertFalse(status["is_blocked"])
        self.assertEqual(status["remaining_seconds"], 0)

    def test_reopen_attempt_escalation(self):
        blocker = Blocker(self.db)
        blocker.block_domain("instagram.com", 120)

        att1 = blocker.record_reopen_attempt("instagram.com")
        self.assertEqual(att1["attempts"], 1)
        self.assertIn("break", att1["koala_quote"].lower())

        att2 = blocker.record_reopen_attempt("instagram.com")
        self.assertEqual(att2["attempts"], 2)
        self.assertIn("nice try", att2["koala_quote"].lower())

        att3 = blocker.record_reopen_attempt("instagram.com")
        self.assertEqual(att3["attempts"], 3)
        self.assertIn("3 times", att3["koala_quote"])

    def test_task_aware_redirection(self):
        todo_mgr = TodoManager(self.db)
        top = todo_mgr.get_top_recommended_task()
        self.assertIsNotNone(top)
        self.assertEqual(top["completed"], 0)
        self.assertEqual(top["priority"], "high")

    def test_usage_tracker_acceptance_flow(self):
        tracker = UsageTracker(self.db)
        h1 = tracker.report_heartbeat("instagram.com", 15.0)
        self.assertFalse(h1["warning"])

        h2 = tracker.report_heartbeat("instagram.com", 15.0)
        self.assertTrue(h2["warning"])
        self.assertFalse(h2["should_block"])

        h3 = tracker.report_heartbeat("instagram.com", 30.0)
        self.assertTrue(h3["should_block"])
        self.assertTrue(tracker.blocker.is_blocked("instagram.com")["is_blocked"])

    def test_pattern_engine_and_recovery(self):
        engine = PatternEngine(self.db)
        rec = engine.get_time_recovery()
        self.assertIn("today_focus_formatted", rec)
        self.assertIn("distraction_prevented_formatted", rec)

        ins = engine.get_insights()
        self.assertIn("peak_distraction_hour", ins)


if __name__ == "__main__":
    unittest.main(verbosity=2)
