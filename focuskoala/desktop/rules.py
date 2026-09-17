"""
FocusKoala Rules Engine
Handles domain matching, limit thresholds, cooldown evaluation, and koala responses.
"""

from urllib.parse import urlparse
from typing import Dict, Any, Tuple, Optional


def normalize_domain(url_or_domain: str) -> str:
    """Extract clean domain name without protocol, www, port, or path."""
    if not url_or_domain:
        return ""
    text = url_or_domain.strip().lower()
    if not (text.startswith("http://") or text.startswith("https://")):
        text = "https://" + text
    try:
        parsed = urlparse(text)
        netloc = parsed.netloc or parsed.path
        # Remove port if present
        domain = netloc.split(":")[0]
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url_or_domain.lower().replace("www.", "").strip()


def evaluate_usage(domain: str, current_usage_seconds: float, limit_seconds: int, is_test_mode: bool = True) -> Dict[str, Any]:
    """
    Evaluates usage against warning and limit thresholds.
    In Test Mode:
      - 30 seconds -> warning
      - 60 seconds -> intervention
    In Standard Mode:
      - ~80% of limit -> warning (e.g. 5 minutes left)
      - 100% of limit -> intervention
    """
    if limit_seconds <= 0:
        return {
            "warning": False,
            "should_block": False,
            "remaining_seconds": 999999,
            "message": "No limit configured."
        }

    remaining_seconds = max(0.0, limit_seconds - current_usage_seconds)

    # Calculate warning threshold
    if is_test_mode and limit_seconds == 60:
        # Test mode explicit requirement: 30 seconds -> warning, 60 seconds -> intervention
        warning_seconds = 30.0
    else:
        # ~80% of limit
        warning_seconds = limit_seconds * 0.80

    if current_usage_seconds >= limit_seconds:
        return {
            "warning": True,
            "should_block": True,
            "remaining_seconds": 0.0,
            "message": f"Limit reached for {domain}! It's time for FocusKoala to intervene. 🐨"
        }
    elif current_usage_seconds >= warning_seconds:
        mins_left = max(1, int(round(remaining_seconds / 60)))
        if remaining_seconds <= 60:
            warning_msg = f"🐨 You have {int(remaining_seconds)} seconds left on {domain}."
        else:
            warning_msg = f"🐨 You have {mins_left} minute{'s' if mins_left > 1 else ''} left on {domain}."
        return {
            "warning": True,
            "should_block": False,
            "remaining_seconds": remaining_seconds,
            "message": warning_msg
        }
    else:
        return {
            "warning": False,
            "should_block": False,
            "remaining_seconds": remaining_seconds,
            "message": f"{int(remaining_seconds)} seconds remaining."
        }


def get_reopen_message(site_name: str, attempt_count: int, task_title: Optional[str] = None) -> Tuple[str, str]:
    """
    Generates escalating Koala reaction for repeated attempts to reopen blocked website.
    Example:
    Attempt 1: 🐨 "Instagram is on a break."
    Attempt 2: 🐨 "Nice try 😐"
    Attempt 3: 🐨 "You have tried opening Instagram 3 times."
    """
    name = site_name.capitalize()
    if attempt_count <= 1:
        headline = f"{name} is currently on a break."
        mood = "warning"
        koala_quote = f'🐨 "{name} is on a break."'
    elif attempt_count == 2:
        headline = f"Nice try! 😄"
        mood = "disappointed"
        koala_quote = '🐨 "Nice try 😐"'
    else:
        headline = f"Step away from {name}."
        mood = "disappointed"
        koala_quote = f'🐨 "You have tried opening {name} {attempt_count} times."'

    if task_title:
        koala_quote += f'\n"You planned: {task_title}"'

    return headline, koala_quote
