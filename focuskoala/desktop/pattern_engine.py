"""
FocusKoala Pattern Engine & Insights Module
Rule-based analytics for distraction patterns, time recovery calculations, and productivity insights.
No external LLM or cloud services used.
"""

from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, List, Optional
from .database import FocusKoalaDB


class PatternEngine:
    def __init__(self, db: Optional[FocusKoalaDB] = None):
        self.db = db or FocusKoalaDB()

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyzes historical usage sessions, peak distraction hours, and recurrent trends.
        """
        sessions = self.db.get_all_usage_sessions()
        top_task = self.db.get_top_incomplete_todo()
        task_name = top_task["title"] if top_task else "next priority task"

        if not sessions:
            return {
                "detected": False,
                "peak_hour": None,
                "peak_hour_formatted": "N/A",
                "most_distracting_domain": "None yet",
                "message": '🐨 "Start tracking to uncover your daily focus patterns!"'
            }

        # Group usage by hour of day (0-23)
        hour_usage = defaultdict(float)
        domain_usage = defaultdict(float)
        session_count_by_hour = defaultdict(int)

        for s in sessions:
            try:
                start_dt = datetime.fromisoformat(s["start_time"])
                hour = start_dt.hour
                dur = s["duration_seconds"]
                hour_usage[hour] += dur
                session_count_by_hour[hour] += 1
                domain_usage[s["domain"]] += dur
            except Exception:
                continue

        if not hour_usage:
            return {
                "detected": False,
                "peak_hour": None,
                "peak_hour_formatted": "N/A",
                "most_distracting_domain": "None",
                "message": '🐨 "Keep up the great work!"'
            }

        # Find peak distraction hour
        peak_hour = max(hour_usage.keys(), key=lambda h: hour_usage[h])
        most_distracting = max(domain_usage.keys(), key=lambda d: domain_usage[d])

        # Format hour (e.g. 14 -> "2 PM")
        period = "AM" if peak_hour < 12 else "PM"
        display_hour = peak_hour if (1 <= peak_hour <= 12) else (peak_hour - 12 if peak_hour > 12 else 12)
        peak_hour_formatted = f"{display_hour} {period}"

        # If enough historical data or repeated pattern detected
        has_pattern = session_count_by_hour[peak_hour] >= 2 or hour_usage[peak_hour] >= 60

        if has_pattern:
            advice = (
                f'🐨 "You often lose focus around {peak_hour_formatted}."\n'
                f'"Your {task_name} is waiting."'
            )
        else:
            advice = f'🐨 "Good momentum! Your peak browsing is around {peak_hour_formatted}."'

        return {
            "detected": has_pattern,
            "peak_hour": peak_hour,
            "peak_hour_formatted": peak_hour_formatted,
            "most_distracting_domain": most_distracting,
            "domain_usage": dict(domain_usage),
            "hour_usage": dict(hour_usage),
            "message": advice
        }

    def get_time_recovery(self) -> Dict[str, Any]:
        """
        Calculates recovered time from prevented distractions and completed tasks (Feature 11).
        """
        # Blocked events and cooldown durations represent prevented distraction
        interventions = self.db.get_interventions()
        todos = self.db.get_todos()

        completed_tasks = [t for t in todos if t["completed"]]
        completed_count = len(completed_tasks)

        # Calculate prevented distraction:
        # Each intervention saves the user from the cooldown duration (or at least 15-30 minutes of browsing spiral)
        total_prevented_seconds = 0
        websites = {w["domain"]: w for w in self.db.get_websites()}

        for iv in interventions:
            domain = iv["domain"]
            site = websites.get(domain)
            cooldown = site["cooldown_seconds"] if site else 1800
            total_prevented_seconds += cooldown

        # In case of fresh install or test session, default reasonable recovered minutes
        prevented_minutes = max(int(round(total_prevented_seconds / 60)), 0)
        if prevented_minutes == 0 and len(interventions) > 0:
            prevented_minutes = len(interventions) * 2

        # Today's focus time (e.g. estimated from completed tasks + focus mode sessions)
        # Each completed task is roughly 30-45 minutes of productive focus
        focus_minutes = (completed_count * 35) + (prevented_minutes // 2)
        if focus_minutes == 0:
            focus_minutes = 25  # baseline default

        focus_h = focus_minutes // 60
        focus_m = focus_minutes % 60
        focus_formatted = f"{focus_h}h {focus_m}m" if focus_h > 0 else f"{focus_m}m"

        return {
            "today_focus_minutes": focus_minutes,
            "today_focus_formatted": focus_formatted,
            "distraction_prevented_minutes": prevented_minutes,
            "distraction_prevented_formatted": f"{prevented_minutes}m",
            "tasks_completed": completed_count,
            "message": f'🐨 "You recovered {prevented_minutes} minutes today!"' if prevented_minutes > 0 else '🐨 "FocusKoala is ready to save your time!"'
        }

    def get_insights(self) -> Dict[str, Any]:
        """Feature 14 — Comprehensive Insights Summary."""
        patterns = self.analyze_patterns()
        recovery = self.get_time_recovery()

        # Reopen attempts count across all blocked sites
        blocks = self.db.get_all_blocks()
        total_attempts = sum(b.get("attempts", 0) for b in blocks)

        # Longest distraction session
        sessions = self.db.get_all_usage_sessions()
        longest_seconds = max([s["duration_seconds"] for s in sessions], default=0.0)
        longest_minutes = int(round(longest_seconds / 60))

        # Most distracting website
        all_today = self.db.get_all_today_usage()
        if all_today:
            most_distracting_domain = max(all_today.keys(), key=lambda d: all_today[d])
            most_distracting_minutes = int(round(all_today[most_distracting_domain] / 60))
        else:
            most_distracting_domain = patterns.get("most_distracting_domain", "None")
            most_distracting_minutes = 0

        return {
            "most_distracting_website": most_distracting_domain,
            "most_distracting_duration": f"{most_distracting_minutes}m",
            "longest_distraction": f"{longest_minutes}m" if longest_minutes > 0 else f"{int(longest_seconds)}s",
            "peak_distraction_hour": patterns.get("peak_hour_formatted", "2 PM"),
            "reopen_attempts": total_attempts,
            "time_recovered": recovery["distraction_prevented_formatted"],
            "tasks_completed": recovery["tasks_completed"],
            "pattern_message": patterns.get("message", ""),
            "recovery_message": recovery.get("message", "")
        }
