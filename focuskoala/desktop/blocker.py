"""
FocusKoala Blocker Module
Manages website blocking, cooldown verification, and reopen attempt recording.
All block state is persisted in SQLite to survive app restarts.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from .database import FocusKoalaDB
from .rules import normalize_domain, get_reopen_message


class Blocker:
    def __init__(self, db: Optional[FocusKoalaDB] = None):
        self.db = db or FocusKoalaDB()

    def block_domain(self, domain: str, cooldown_seconds: int, reason: str = "limit_exceeded") -> Dict[str, Any]:
        clean_domain = normalize_domain(domain)
        now = datetime.now(timezone.utc)
        blocked_until = now + timedelta(seconds=cooldown_seconds)
        return self.db.set_block(clean_domain, blocked_until.isoformat(), reason)

    def is_blocked(self, domain: str) -> Dict[str, Any]:
        """
        Checks if the domain is actively blocked.
        If the cooldown period has expired, automatically removes the block.
        """
        clean_domain = normalize_domain(domain)
        block = self.db.get_block(clean_domain)
        if not block:
            # Also check if global Focus Mode is active
            focus_mode = self.db.get_setting("focus_mode_active", "false") == "true"
            if focus_mode:
                # In focus mode, all enabled distracting websites are blocked
                site = self.db.get_website_by_domain(clean_domain)
                if site and site["enabled"]:
                    return {
                        "is_blocked": True,
                        "remaining_seconds": 600,
                        "remaining_formatted": "Focus Mode Active",
                        "attempts": 1,
                        "reason": "focus_mode"
                    }
            return {
                "is_blocked": False,
                "remaining_seconds": 0,
                "remaining_formatted": "00:00",
                "attempts": 0,
                "reason": None
            }

        try:
            blocked_until = datetime.fromisoformat(block["blocked_until"])
            now = datetime.now(timezone.utc)
            remaining = (blocked_until - now).total_seconds()
            if remaining <= 0:
                # Cooldown has expired! Restore access
                self.db.remove_block(clean_domain)
                return {
                    "is_blocked": False,
                    "remaining_seconds": 0,
                    "remaining_formatted": "00:00",
                    "attempts": block.get("attempts", 0),
                    "reason": None
                }
            
            # Still blocked
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            formatted = f"{mins:02d}:{secs:02d}"
            return {
                "is_blocked": True,
                "remaining_seconds": int(remaining),
                "remaining_formatted": formatted,
                "attempts": block.get("attempts", 0),
                "reason": block.get("reason", "limit_exceeded")
            }
        except Exception:
            return {
                "is_blocked": False,
                "remaining_seconds": 0,
                "remaining_formatted": "00:00",
                "attempts": 0,
                "reason": None
            }

    def record_reopen_attempt(self, domain: str) -> Dict[str, Any]:
        """Increments reopen attempt and returns the updated count and koala message."""
        clean_domain = normalize_domain(domain)
        attempts = self.db.increment_block_attempt(clean_domain)
        top_task = self.db.get_top_incomplete_todo()
        task_title = top_task["title"] if top_task else None
        headline, koala_quote = get_reopen_message(clean_domain.split(".")[0], attempts, task_title)

        status = self.is_blocked(clean_domain)
        return {
            "domain": clean_domain,
            "attempts": attempts,
            "headline": headline,
            "koala_quote": koala_quote,
            "remaining_seconds": status["remaining_seconds"],
            "remaining_formatted": status["remaining_formatted"],
            "recommended_task": top_task
        }

    def unblock(self, domain: str) -> bool:
        clean_domain = normalize_domain(domain)
        return self.db.remove_block(clean_domain)
