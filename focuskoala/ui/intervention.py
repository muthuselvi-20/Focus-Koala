"""
FocusKoala Intervention Window
Floating window that slides into view upon limit breach, plays the Koala animation,
blocks the distracting website, and transitions smoothly into Today's Todo List.
"""

from typing import Optional, Dict, Any

try:
    from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QApplication
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

from .koala_widget import KoalaWidget


class InterventionWindow(QWidget if PYSIDE_AVAILABLE else object):
    def __init__(self, agent=None, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.agent = agent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(440, 360)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Card container
        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #1A1C23;
                border: 2px solid #E58E26;
                border-radius: 20px;
                color: #FFFFFF;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setAlignment(Qt.AlignCenter)

        # Mascot
        self.koala = KoalaWidget(self, size=110)
        card_layout.addWidget(self.koala, alignment=Qt.AlignCenter)

        # Title
        self.title_label = QLabel("FocusKoala Intervention 🐨", self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8B739; border: none;")
        self.title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title_label)

        # Subtitle / Message
        self.msg_label = QLabel("Time's up for Instagram! Let's refocus.", self)
        self.msg_label.setStyleSheet("font-size: 14px; color: #D1D5DB; margin-top: 4px; border: none;")
        self.msg_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.msg_label)

        # Task Box
        self.task_box = QFrame(self)
        self.task_box.setStyleSheet("""
            QFrame {
                background-color: #242833;
                border: 1px solid #374151;
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        task_layout = QVBoxLayout(self.task_box)
        task_layout.setContentsMargins(12, 10, 12, 10)

        self.task_badge = QLabel("NEXT TASK TO COMPLETE", self.task_box)
        self.task_badge.setStyleSheet("font-size: 10px; font-weight: bold; color: #E58E26; border: none;")
        task_layout.addWidget(self.task_badge)

        self.task_title = QLabel("Complete 3 DSA problems", self.task_box)
        self.task_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #FFF; border: none;")
        task_layout.addWidget(self.task_title)

        card_layout.addWidget(self.task_box)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 12, 0, 0)

        self.start_task_btn = QPushButton("Start Task 🚀", self)
        self.start_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #E58E26;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #F8B739;
            }
        """)
        self.start_task_btn.clicked.connect(self.on_start_task)
        btn_layout.addWidget(self.start_task_btn)

        self.dismiss_btn = QPushButton("Open Todo List", self)
        self.dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #FFFFFF;
                font-size: 13px;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        self.dismiss_btn.clicked.connect(self.on_open_todos)
        btn_layout.addWidget(self.dismiss_btn)

        card_layout.addLayout(btn_layout)
        layout.addWidget(self.card)

    def trigger_intervention(self, domain: str = "instagram.com", task_title: Optional[str] = None):
        """Displays the intervention window with animation."""
        if not PYSIDE_AVAILABLE:
            return

        self.msg_label.setText(f"{domain.capitalize()} is now on a break.")
        if task_title:
            self.task_title.setText(task_title)
        elif self.agent:
            top = self.agent.todo_manager.get_top_recommended_task()
            if top:
                self.task_title.setText(top["title"])

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        self.show()
        self.raise_()

        # Play mascot intervention animation sequence
        self.koala.play_intervention_sequence(
            on_close_tab_callback=lambda: print(f"[FocusKoala] Closing/Redirecting {domain} tab."),
            on_finished_callback=lambda: self.msg_label.setText("Todo List ready. Let's conquer your goal!")
        )

    def on_start_task(self):
        self.close()

    def on_open_todos(self):
        self.close()
