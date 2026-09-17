"""
FocusKoala Usage Tracker Module
Tracks active website sessions received from browser extension, computes cumulative usage,
and checks limit thresholds to trigger Koala interventions.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .database import FocusKoalaDB
from .rules import normalize_domain, evaluate_usage
from .blocker import Blocker


class UsageTracker:
    def __init__(self, db: Optional[FocusKoalaDB] = None, blocker: Optional[Blocker] = None):
        self.db = db or FocusKoalaDB()
        self.blocker = blocker or Blocker(self.db)
        # In-memory tracking for active sessions: {domain: {"last_seen": timestamp, "accumulated": float}}
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    def report_heartbeat(self, domain: str, duration_seconds: float = 3.0) -> Dict[str, Any]:
        """
        Called periodically (every 3-5 seconds) by browser extension when a monitored tab is active.
        """
        clean_domain = normalize_domain(domain)
        site_config = self.db.get_website_by_domain(clean_domain)

        # If domain is not configured or disabled, do not track
        if not site_config or not site_config["enabled"]:
            return {
                "tracked": False,
                "warning": False,
                "should_block": False,
                "message": "Domain not tracked.",
                "domain": clean_domain
            }

        # Check if already blocked
        block_status = self.blocker.is_blocked(clean_domain)
        if block_status["is_blocked"]:
            return {
                "tracked": True,
                "warning": True,
                "should_block": True,
                "remaining_seconds": 0,
                "cooldown_remaining": block_status["remaining_seconds"],
                "message": f"{clean_domain} is blocked.",
                "domain": clean_domain
            }

        # Persist session increment in database
        self.db.record_usage(clean_domain, duration_seconds)

        # Get total usage today for this domain
        today_usage = self.db.get_today_usage_by_domain(clean_domain)
        is_test_mode = self.db.get_setting("test_mode", "true") == "true"
        limit_seconds = site_config["limit_seconds"]

        eval_result = evaluate_usage(clean_domain, today_usage, limit_seconds, is_test_mode=is_test_mode)

        if eval_result["should_block"]:
            # Trigger block and record intervention!
            cooldown = site_config["cooldown_seconds"]
            self.blocker.block_domain(clean_domain, cooldown, reason="limit_exceeded")
            top_task = self.db.get_top_incomplete_todo()
            task_id = top_task["id"] if top_task else None
            self.db.record_intervention(clean_domain, event_type="limit_reached", task_id=task_id)

            return {
                "tracked": True,
                "warning": True,
                "should_block": True,
                "current_usage": today_usage,
                "limit_seconds": limit_seconds,
                "remaining_seconds": 0.0,
                "cooldown_seconds": cooldown,
                "message": eval_result["message"],
                "domain": clean_domain,
                "recommended_task": top_task
            }

        return {
            "tracked": True,
            "warning": eval_result["warning"],
            "should_block": False,
            "current_usage": today_usage,
            "limit_seconds": limit_seconds,
            "remaining_seconds": eval_result["remaining_seconds"],
            "message": eval_result["message"],
            "domain": clean_domain
        }
