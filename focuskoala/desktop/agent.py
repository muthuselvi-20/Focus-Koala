"""
FocusKoala Core Desktop Agent
Orchestrates monitoring, blocking events, focus mode timers, and mascot animations.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
from .database import FocusKoalaDB
from .rules import normalize_domain
from .blocker import Blocker
from .usage_tracker import UsageTracker
from .todo import TodoManager
from .pattern_engine import PatternEngine


class FocusKoalaAgent:
    def __init__(self, db: Optional[FocusKoalaDB] = None):
        self.db = db or FocusKoalaDB()
        self.blocker = Blocker(self.db)
        self.usage_tracker = UsageTracker(self.db, self.blocker)
        self.todo_manager = TodoManager(self.db)
        self.pattern_engine = PatternEngine(self.db)
        self.on_intervention_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    def register_intervention_handler(self, callback: Callable[[Dict[str, Any]], None]):
        """Attach UI callback when Koala animation should trigger."""
        self.on_intervention_callback = callback

    def process_heartbeat(self, domain: str, duration_seconds: float = 3.0) -> Dict[str, Any]:
        result = self.usage_tracker.report_heartbeat(domain, duration_seconds)
        if result.get("should_block") and self.on_intervention_callback:
            # Notify UI to slide in animated koala
            try:
                self.on_intervention_callback(result)
            except Exception as e:
                print(f"[FocusKoala] Error triggering UI intervention: {e}")
        return result

    # --- Focus Mode (Feature 12) ---
    def start_focus_mode(self, duration_minutes: int, custom_task: Optional[str] = None) -> Dict[str, Any]:
        """
        Activates Focus Mode for 30m, 60m, 90m, or custom duration.
        All distracting websites are blocked during this window.
        """
        now = datetime.now(timezone.utc)
        end_time = now + timedelta(minutes=duration_minutes)
        top_task = custom_task or (self.todo_manager.get_top_recommended_task() or {}).get("title", "Deep Focus")

        self.db.set_setting("focus_mode_active", "true")
        self.db.set_setting("focus_mode_end", end_time.isoformat())
        self.db.set_setting("focus_mode_task", top_task)

        # Block all enabled sites for the duration of focus mode
        sites = self.db.get_websites()
        for s in sites:
            if s["enabled"]:
                self.blocker.block_domain(s["domain"], duration_minutes * 60, reason="focus_mode")

        return {
            "active": True,
            "duration_minutes": duration_minutes,
            "end_time": end_time.isoformat(),
            "task": top_task
        }

    def stop_focus_mode(self) -> Dict[str, Any]:
        self.db.set_setting("focus_mode_active", "false")
        self.db.set_setting("focus_mode_end", "")
        self.db.set_setting("focus_mode_task", "")
        return {"active": False}

    def get_focus_mode_status(self) -> Dict[str, Any]:
        active = self.db.get_setting("focus_mode_active", "false") == "true"
        if not active:
            return {"active": False, "remaining_seconds": 0, "remaining_formatted": "00:00", "task": ""}

        end_str = self.db.get_setting("focus_mode_end", "")
        task = self.db.get_setting("focus_mode_task", "Focus Session")
        try:
            end_dt = datetime.fromisoformat(end_str)
            now = datetime.now(timezone.utc)
            rem = (end_dt - now).total_seconds()
            if rem <= 0:
                self.stop_focus_mode()
                return {"active": False, "remaining_seconds": 0, "remaining_formatted": "00:00", "task": ""}
            mins = int(rem // 60)
            secs = int(rem % 60)
            return {
                "active": True,
                "remaining_seconds": int(rem),
                "remaining_formatted": f"{mins:02d}:{secs:02d}",
                "task": task
            }
        except Exception:
            return {"active": False, "remaining_seconds": 0, "remaining_formatted": "00:00", "task": ""}

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Returns consolidated data for dashboard UI."""
        recovery = self.pattern_engine.get_time_recovery()
        today_usage = self.db.get_all_today_usage()
        websites = self.db.get_websites()
        todos = self.todo_manager.get_all()
        focus_status = self.get_focus_mode_status()
        insights = self.pattern_engine.get_insights()

        # Format website usage items
        site_usage_list = []
        for w in websites:
            dur = today_usage.get(w["domain"], 0.0)
            mins = int(round(dur / 60))
            site_usage_list.append({
                "domain": w["domain"],
                "name": w["name"],
                "limit_seconds": w["limit_seconds"],
                "cooldown_seconds": w["cooldown_seconds"],
                "enabled": bool(w["enabled"]),
                "used_minutes": mins,
                "used_seconds": dur,
                "used_formatted": f"{mins}m" if mins > 0 else f"{int(dur)}s",
                "is_blocked": self.blocker.is_blocked(w["domain"])["is_blocked"]
            })

        total_distraction_secs = sum(today_usage.values())
        distraction_mins = int(round(total_distraction_secs / 60))

        return {
            "today_focus": recovery["today_focus_formatted"],
            "today_distraction": f"{distraction_mins}m" if distraction_mins > 0 else f"{int(total_distraction_secs)}s",
            "time_recovered": recovery["distraction_prevented_formatted"],
            "tasks_completed": recovery["tasks_completed"],
            "websites": site_usage_list,
            "todos": todos,
            "focus_mode": focus_status,
            "insights": insights,
            "top_task": self.todo_manager.get_top_recommended_task()
        }
