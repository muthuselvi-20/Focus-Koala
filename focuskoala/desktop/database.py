"""
FocusKoala SQLite Database Module
Stores website rules, usage logs, active blocks, todos, settings, and interventions.
Survives application restart.
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "focuskoala.db")


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initialize SQLite database with required tables, indexes, and initial defaults."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    # 1. websites table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS websites (
        id TEXT PRIMARY KEY,
        domain TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        limit_seconds INTEGER NOT NULL,
        cooldown_seconds INTEGER NOT NULL,
        enabled INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # 2. usage_sessions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage_sessions (
        id TEXT PRIMARY KEY,
        domain TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        duration_seconds REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_domain ON usage_sessions(domain);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_start ON usage_sessions(start_time);")

    # 3. blocked_sites table (persists blocks across app restart)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blocked_sites (
        domain TEXT PRIMARY KEY,
        blocked_at TEXT NOT NULL,
        blocked_until TEXT NOT NULL,
        reason TEXT DEFAULT 'limit_exceeded',
        attempts INTEGER DEFAULT 0
    );
    """)

    # 4. todos table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        priority TEXT DEFAULT 'medium',
        created_at TEXT NOT NULL,
        completed_at TEXT
    );
    """)

    # 5. settings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # 6. intervention_events table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS intervention_events (
        id TEXT PRIMARY KEY,
        domain TEXT NOT NULL,
        triggered_at TEXT NOT NULL,
        event_type TEXT NOT NULL,
        task_id TEXT
    );
    """)

    conn.commit()

    # Seed initial test data if empty
    cur.execute("SELECT COUNT(*) FROM websites")
    if cur.fetchone()[0] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        default_sites = [
            ("site_instagram", "instagram.com", "Instagram", 60, 120, 1, now_iso),  # Test mode: 60s limit, 120s cooldown
            ("site_youtube", "youtube.com", "YouTube", 2700, 1800, 1, now_iso),     # 45m limit, 30m cooldown
            ("site_reddit", "reddit.com", "Reddit", 1200, 1800, 1, now_iso),        # 20m limit, 30m cooldown
        ]
        cur.executemany(
            "INSERT INTO websites (id, domain, name, limit_seconds, cooldown_seconds, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            default_sites
        )

    cur.execute("SELECT COUNT(*) FROM todos")
    if cur.fetchone()[0] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        default_todos = [
            ("todo_1", "Complete 3 DSA problems", 0, "high", now_iso, None),
            ("todo_2", "Study Random Forest", 0, "medium", now_iso, None),
            ("todo_3", "Finish ML project", 0, "high", now_iso, None),
            ("todo_4", "Revise Python OOP", 1, "low", now_iso, now_iso),
        ]
        cur.executemany(
            "INSERT INTO todos (id, title, completed, priority, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
            default_todos
        )

    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        default_settings = [
            ("test_mode", "true"),
            ("focus_mode_active", "false"),
            ("focus_mode_end", ""),
            ("focus_mode_task", ""),
            ("warning_threshold_ratio", "0.5"),  # 50% for test mode (30s on 60s limit)
        ]
        cur.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", default_settings)

    conn.commit()
    conn.close()


class FocusKoalaDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    # --- Websites ---
    def get_websites(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM websites ORDER BY name ASC")
            return [dict(row) for row in cur.fetchall()]

    def get_website_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        clean_domain = domain.lower().replace("www.", "").strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM websites WHERE domain = ? OR domain = ?", (clean_domain, f"www.{clean_domain}"))
            row = cur.fetchone()
            return dict(row) if row else None

    def add_website(self, domain: str, name: str, limit_seconds: int, cooldown_seconds: int, enabled: bool = True) -> Dict[str, Any]:
        clean_domain = domain.lower().replace("www.", "").strip()
        site_id = f"site_{clean_domain.replace('.', '_')}"
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO websites (id, domain, name, limit_seconds, cooldown_seconds, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
                name = excluded.name,
                limit_seconds = excluded.limit_seconds,
                cooldown_seconds = excluded.cooldown_seconds,
                enabled = excluded.enabled
            """, (site_id, clean_domain, name, limit_seconds, cooldown_seconds, 1 if enabled else 0, now_iso))
            conn.commit()
        return self.get_website_by_domain(clean_domain)

    def remove_website(self, domain: str) -> bool:
        clean_domain = domain.lower().replace("www.", "").strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM websites WHERE domain = ?", (clean_domain,))
            conn.commit()
            return cur.rowcount > 0

    def update_website(self, domain: str, limit_seconds: Optional[int] = None, cooldown_seconds: Optional[int] = None, enabled: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        clean_domain = domain.lower().replace("www.", "").strip()
        existing = self.get_website_by_domain(clean_domain)
        if not existing:
            return None
        new_limit = limit_seconds if limit_seconds is not None else existing["limit_seconds"]
        new_cooldown = cooldown_seconds if cooldown_seconds is not None else existing["cooldown_seconds"]
        new_enabled = (1 if enabled else 0) if enabled is not None else existing["enabled"]
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE websites SET limit_seconds = ?, cooldown_seconds = ?, enabled = ? WHERE domain = ?",
                        (new_limit, new_cooldown, new_enabled, clean_domain))
            conn.commit()
        return self.get_website_by_domain(clean_domain)

    # --- Blocked Sites ---
    def set_block(self, domain: str, blocked_until_iso: str, reason: str = "limit_exceeded") -> Dict[str, Any]:
        clean_domain = domain.lower().replace("www.", "").strip()
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO blocked_sites (domain, blocked_at, blocked_until, reason, attempts)
            VALUES (?, ?, ?, ?, 0)
            ON CONFLICT(domain) DO UPDATE SET
                blocked_at = excluded.blocked_at,
                blocked_until = excluded.blocked_until,
                reason = excluded.reason
            """, (clean_domain, now_iso, blocked_until_iso, reason))
            conn.commit()
        return self.get_block(clean_domain)

    def get_block(self, domain: str) -> Optional[Dict[str, Any]]:
        clean_domain = domain.lower().replace("www.", "").strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM blocked_sites WHERE domain = ?", (clean_domain,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM blocked_sites")
            return [dict(row) for row in cur.fetchall()]

    def remove_block(self, domain: str) -> bool:
        clean_domain = domain.lower().replace("www.", "").strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM blocked_sites WHERE domain = ?", (clean_domain,))
            conn.commit()
            return cur.rowcount > 0

    def increment_block_attempt(self, domain: str) -> int:
        clean_domain = domain.lower().replace("www.", "").strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE blocked_sites SET attempts = attempts + 1 WHERE domain = ?", (clean_domain,))
            conn.commit()
            cur.execute("SELECT attempts FROM blocked_sites WHERE domain = ?", (clean_domain,))
            row = cur.fetchone()
            return row[0] if row else 1

    # --- Usage Sessions ---
    def record_usage(self, domain: str, duration_seconds: float, start_time_iso: Optional[str] = None, end_time_iso: Optional[str] = None) -> str:
        clean_domain = domain.lower().replace("www.", "").strip()
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        start_iso = start_time_iso or now_iso
        end_iso = end_time_iso or now_iso
        session_id = f"session_{int(now.timestamp() * 1000)}"
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO usage_sessions (id, domain, start_time, end_time, duration_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, clean_domain, start_iso, end_iso, duration_seconds, now_iso))
            conn.commit()
        return session_id

    def get_today_usage_by_domain(self, domain: str) -> float:
        clean_domain = domain.lower().replace("www.", "").strip()
        today_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM usage_sessions
            WHERE domain = ? AND start_time LIKE ?
            """, (clean_domain, f"{today_date_str}%"))
            row = cur.fetchone()
            return float(row[0]) if row else 0.0

    def get_all_today_usage(self) -> Dict[str, float]:
        today_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT domain, COALESCE(SUM(duration_seconds), 0) as total_dur
            FROM usage_sessions
            WHERE start_time LIKE ?
            GROUP BY domain
            """, (f"{today_date_str}%",))
            return {row["domain"]: float(row["total_dur"]) for row in cur.fetchall()}

    def get_all_usage_sessions(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usage_sessions ORDER BY start_time DESC")
            return [dict(row) for row in cur.fetchall()]

    # --- Todos ---
    def get_todos(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM todos ORDER BY completed ASC, CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC")
            return [dict(row) for row in cur.fetchall()]

    def get_top_incomplete_todo(self) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT * FROM todos
            WHERE completed = 0
            ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at ASC
            LIMIT 1
            """)
            row = cur.fetchone()
            return dict(row) if row else None

    def add_todo(self, title: str, priority: str = "medium") -> Dict[str, Any]:
        todo_id = f"todo_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO todos (id, title, completed, priority, created_at, completed_at)
            VALUES (?, ?, 0, ?, ?, NULL)
            """, (todo_id, title.strip(), priority.lower(), now_iso))
            conn.commit()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            return dict(cur.fetchone())

    def update_todo(self, todo_id: str, title: Optional[str] = None, priority: Optional[str] = None, completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            row = cur.fetchone()
            if not row:
                return None
            existing = dict(row)
            new_title = title.strip() if title is not None else existing["title"]
            new_prio = priority.lower() if priority is not None else existing["priority"]
            new_completed = (1 if completed else 0) if completed is not None else existing["completed"]
            completed_at = datetime.now(timezone.utc).isoformat() if new_completed and not existing["completed"] else (None if not new_completed else existing["completed_at"])

            cur.execute("""
            UPDATE todos SET title = ?, priority = ?, completed = ?, completed_at = ? WHERE id = ?
            """, (new_title, new_prio, new_completed, completed_at, todo_id))
            conn.commit()
            cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            return dict(cur.fetchone())

    def delete_todo(self, todo_id: str) -> bool:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            conn.commit()
            return cur.rowcount > 0

    # --- Settings ---
    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))
            conn.commit()

    # --- Intervention Events ---
    def record_intervention(self, domain: str, event_type: str = "limit_reached", task_id: Optional[str] = None) -> str:
        event_id = f"event_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO intervention_events (id, domain, triggered_at, event_type, task_id)
            VALUES (?, ?, ?, ?, ?)
            """, (event_id, domain, now_iso, event_type, task_id))
            conn.commit()
        return event_id

    def get_interventions(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM intervention_events ORDER BY triggered_at DESC")
            return [dict(row) for row in cur.fetchall()]
