"""
FocusKoala Todo List View (PySide6)
Interactive task organizer with priority levels and instant completion toggles.
"""

from typing import Optional

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
        QListWidget, QListWidgetItem, QComboBox, QCheckBox, QFrame, QMessageBox
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


class TodoView(QWidget if PYSIDE_AVAILABLE else object):
    if PYSIDE_AVAILABLE:
        todos_changed = Signal()

    def __init__(self, agent=None, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.agent = agent
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("Today's Tasks", self)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header)

        # Input Row
        input_row = QHBoxLayout()
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter new task (e.g., Complete 3 DSA problems)...")
        self.task_input.setStyleSheet("""
            QLineEdit {
                background-color: #242833;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 8px 12px;
                color: #FFF;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #E58E26;
            }
        """)
        input_row.addWidget(self.task_input, stretch=3)

        self.prio_combo = QComboBox(self)
        self.prio_combo.addItems(["High", "Medium", "Low"])
        self.prio_combo.setStyleSheet("""
            QComboBox {
                background-color: #242833;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 6px 10px;
                color: #FFF;
            }
        """)
        input_row.addWidget(self.prio_combo, stretch=1)

        self.add_btn = QPushButton("Add Task", self)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #E58E26;
                color: #FFFFFF;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #F8B739;
            }
        """)
        self.add_btn.clicked.connect(self.on_add_task)
        input_row.addWidget(self.add_btn)

        layout.addLayout(input_row)

        # Task List
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1A1C23;
                border: 1px solid #2E333D;
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: #242833;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 6px;
            }
        """)
        layout.addWidget(self.list_widget)

        self.refresh_todos()

    def refresh_todos(self):
        if not PYSIDE_AVAILABLE or not self.agent:
            return
        self.list_widget.clear()
        todos = self.agent.todo_manager.get_all()
        for t in todos:
            item = QListWidgetItem(self.list_widget)
            widget = self._create_item_widget(t)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

    def _create_item_widget(self, todo):
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(4, 2, 4, 2)

        cb = QCheckBox()
        cb.setChecked(bool(todo["completed"]))
        cb.stateChanged.connect(lambda state, tid=todo["id"]: self.on_toggle(tid))
        row.addWidget(cb)

        title = QLabel(todo["title"])
        style = "font-size: 13px; color: #FFF;"
        if todo["completed"]:
            style = "font-size: 13px; color: #6B7280; text-decoration: line-through;"
        title.setStyleSheet(style)
        row.addWidget(title, stretch=1)

        # Priority tag
        prio = todo.get("priority", "medium")
        prio_colors = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}
        prio_label = QLabel(prio.upper())
        prio_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: bold;
            color: {prio_colors.get(prio, '#F59E0B')};
            background-color: rgba(255,255,255,0.05);
            padding: 2px 6px;
            border-radius: 4px;
        """)
        row.addWidget(prio_label)

        # Delete btn
        del_btn = QPushButton("✕")
        del_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #9CA3AF;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        del_btn.clicked.connect(lambda checked, tid=todo["id"]: self.on_delete(tid))
        row.addWidget(del_btn)

        return w

    def on_add_task(self):
        text = self.task_input.text().strip()
        if not text:
            return
        prio = self.prio_combo.currentText().lower()
        if self.agent:
            self.agent.todo_manager.add(text, prio)
            self.task_input.clear()
            self.refresh_todos()
            self.todos_changed.emit()

    def on_toggle(self, todo_id: str):
        if self.agent:
            self.agent.todo_manager.toggle(todo_id)
            self.refresh_todos()
            self.todos_changed.emit()

    def on_delete(self, todo_id: str):
        if self.agent:
            self.agent.todo_manager.delete(todo_id)
            self.refresh_todos()
            self.todos_changed.emit()
