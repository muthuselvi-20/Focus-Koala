"""
FocusKoala Todo Module
Task management with task-aware redirection (recommends highest-priority incomplete task).
"""

from typing import List, Dict, Any, Optional
from .database import FocusKoalaDB


class TodoManager:
    def __init__(self, db: Optional[FocusKoalaDB] = None):
        self.db = db or FocusKoalaDB()

    def get_all(self) -> List[Dict[str, Any]]:
        return self.db.get_todos()

    def get_top_recommended_task(self) -> Optional[Dict[str, Any]]:
        """Finds the highest-priority incomplete task for task-aware redirection."""
        return self.db.get_top_incomplete_todo()

    def add(self, title: str, priority: str = "medium") -> Dict[str, Any]:
        return self.db.add_todo(title, priority)

    def update(self, todo_id: str, title: Optional[str] = None, priority: Optional[str] = None, completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        return self.db.update_todo(todo_id, title, priority, completed)

    def toggle(self, todo_id: str) -> Optional[Dict[str, Any]]:
        todos = self.db.get_todos()
        for t in todos:
            if t["id"] == todo_id:
                new_status = not bool(t["completed"])
                return self.db.update_todo(todo_id, completed=new_status)
        return None

    def delete(self, todo_id: str) -> bool:
        return self.db.delete_todo(todo_id)
