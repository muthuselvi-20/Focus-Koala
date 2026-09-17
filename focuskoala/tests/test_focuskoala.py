"""
FocusKoala Test Suite
Validates SQLite persistence, rule thresholds (30s warning, 60s limit),
blocking, cooldowns, reopen attempts, task-aware redirection, and pattern engine.
"""

import os
import sys
import tempfile
import pytest
from datetime import datetime, timezone, timedelta

# Path configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from focuskoala.desktop.database import FocusKoalaDB, init_db
from focuskoala.desktop.rules import normalize_domain, evaluate_usage, get_reopen_message
from focuskoala.desktop.blocker import Blocker
from focuskoala.desktop.usage_tracker import UsageTracker
from focuskoala.desktop.todo import TodoManager
from focuskoala.desktop.pattern_engine import PatternEngine
from focuskoala.desktop.agent import FocusKoalaAgent


@pytest.fixture
def test_db():
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)
    db = FocusKoalaDB(temp_path)
    yield db
    try:
        os.remove(temp_path)
    except Exception:
        pass


def test_database_initialization_and_seeding(test_db):
    """Verifies SQLite tables and initial default websites and todos exist."""
    websites = test_db.get_websites()
    assert len(websites) >= 3
    domains = [w["domain"] for w in websites]
    assert "instagram.com" in domains
    assert "youtube.com" in domains
    assert "reddit.com" in domains

    # Verify test mode values for Instagram: 60s limit, 120s cooldown
    ig = test_db.get_website_by_domain("instagram.com")
    assert ig is not None
    assert ig["limit_seconds"] == 60
    assert ig["cooldown_seconds"] == 120

    # Verify initial todos
    todos = test_db.get_todos()
    assert len(todos) >= 4
    top_task = test_db.get_top_incomplete_todo()
    assert top_task is not None
    assert "DSA" in top_task["title"]


def test_domain_normalization():
    """Verifies URLs and subdomains normalize to clean domains."""
    assert normalize_domain("https://www.instagram.com/explore/") == "instagram.com"
    assert normalize_domain("http://instagram.com:8080/user") == "instagram.com"
    assert normalize_domain("www.youtube.com/watch?v=123") == "youtube.com"
    assert normalize_domain("reddit.com") == "reddit.com"


def test_limit_detection_test_mode():
    """
    Verifies Test Mode:
      - 30 seconds -> warning
      - 60 seconds -> intervention
    """
    # 1. Below 30s
    res_under = evaluate_usage("instagram.com", 20.0, 60, is_test_mode=True)
    assert not res_under["warning"]
    assert not res_under["should_block"]

    # 2. At 30s (warning threshold)
    res_warn = evaluate_usage("instagram.com", 30.0, 60, is_test_mode=True)
    assert res_warn["warning"]
    assert not res_warn["should_block"]
    assert "seconds left" in res_warn["message"]

    # 3. At 60s (limit reached -> intervention)
    res_limit = evaluate_usage("instagram.com", 60.0, 60, is_test_mode=True)
    assert res_limit["warning"]
    assert res_limit["should_block"]
    assert res_limit["remaining_seconds"] == 0.0


def test_blocking_and_cooldown_persistence(test_db):
    """Verifies that blocked state survives application/DB re-instantiation."""
    blocker = Blocker(test_db)
    blocker.block_domain("instagram.com", 120, reason="limit_exceeded")

    status = blocker.is_blocked("instagram.com")
    assert status["is_blocked"]
    assert status["remaining_seconds"] > 100

    # Test persistence across new DB connection
    new_db = FocusKoalaDB(test_db.db_path)
    new_blocker = Blocker(new_db)
    new_status = new_blocker.is_blocked("instagram.com")
    assert new_status["is_blocked"]


def test_cooldown_expiration(test_db):
    """Verifies that after cooldown time elapses, access is automatically restored."""
    blocker = Blocker(test_db)
    # Set a block in the past
    past_iso = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
    test_db.set_block("instagram.com", past_iso)

    status = blocker.is_blocked("instagram.com")
    assert not status["is_blocked"]
    assert status["remaining_seconds"] == 0


def test_reopen_attempt_escalation(test_db):
    """Verifies escalating Koala messages on repeated attempts."""
    blocker = Blocker(test_db)
    blocker.block_domain("instagram.com", 120)

    # Attempt 1
    att1 = blocker.record_reopen_attempt("instagram.com")
    assert att1["attempts"] == 1
    assert "break" in att1["koala_quote"].lower()

    # Attempt 2
    att2 = blocker.record_reopen_attempt("instagram.com")
    assert att2["attempts"] == 2
    assert "nice try" in att2["koala_quote"].lower()

    # Attempt 3
    att3 = blocker.record_reopen_attempt("instagram.com")
    assert att3["attempts"] == 3
    assert "3 times" in att3["koala_quote"]


def test_task_aware_redirection(test_db):
    """Verifies that the highest-priority incomplete task is recommended."""
    todo_mgr = TodoManager(test_db)
    top_task = todo_mgr.get_top_recommended_task()
    assert top_task is not None
    assert top_task["completed"] == 0
    assert top_task["priority"] == "high"

    # Complete it and check next recommended
    todo_mgr.toggle(top_task["id"])
    next_task = todo_mgr.get_top_recommended_task()
    assert next_task["id"] != top_task["id"]


def test_usage_tracker_end_to_end(test_db):
    """Verifies full acceptance flow from heartbeat to intervention block."""
    tracker = UsageTracker(test_db)

    # Heartbeat 1: 15s (no warning)
    h1 = tracker.report_heartbeat("instagram.com", 15.0)
    assert not h1["warning"]
    assert not h1["should_block"]

    # Heartbeat 2: 15s (total 30s -> warning)
    h2 = tracker.report_heartbeat("instagram.com", 15.0)
    assert h2["warning"]
    assert not h2["should_block"]

    # Heartbeat 3: 30s (total 60s -> intervention!)
    h3 = tracker.report_heartbeat("instagram.com", 30.0)
    assert h3["should_block"]
    assert h3["remaining_seconds"] == 0.0

    # Ensure Instagram is now recorded as blocked
    block_status = tracker.blocker.is_blocked("instagram.com")
    assert block_status["is_blocked"]


def test_pattern_engine_and_time_recovery(test_db):
    """Verifies statistical analysis without LLM and time recovery calculation."""
    engine = PatternEngine(test_db)
    recovery = engine.get_time_recovery()
    assert "today_focus_formatted" in recovery
    assert "distraction_prevented_formatted" in recovery
    assert "tasks_completed" in recovery

    insights = engine.get_insights()
    assert "most_distracting_website" in insights
    assert "peak_distraction_hour" in insights


def test_focus_mode_blocks_all_distractions(test_db):
    """Verifies Focus Mode blocks enabled distracting websites."""
    agent = FocusKoalaAgent(test_db)
    agent.start_focus_mode(duration_minutes=30)

    # In focus mode, instagram.com should be blocked
    status = agent.blocker.is_blocked("instagram.com")
    assert status["is_blocked"]

    agent.stop_focus_mode()
    agent.blocker.unblock("instagram.com")
    status_unblocked = agent.blocker.is_blocked("instagram.com")
    assert not status_unblocked["is_blocked"]
