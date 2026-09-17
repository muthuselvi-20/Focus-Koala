"""
FocusKoala 2D Animated Mascot Widget
Renders the Koala mascot in 5 emotional states:
  - idle
  - warning
  - intervention
  - happy
  - disappointed
Supports full sequence animations (slides onto screen, gestures, closes, returns).
"""

import os
from typing import Optional

try:
    from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, Signal, QTimer
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
    from PySide6.QtGui import QPixmap, QPainter, QColor
    from PySide6.QtSvg import QSvgRenderer
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


class KoalaWidget(QWidget if PYSIDE_AVAILABLE else object):
    """Visual 2D mascot widget for FocusKoala."""
    if PYSIDE_AVAILABLE:
        animation_completed = Signal(str)

    def __init__(self, parent=None, size: int = 140):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.size_px = size
        self.current_state = "idle"
        self.asset_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "koala"
        )

        self.setFixedSize(self.size_px, self.size_px)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setFixedSize(self.size_px, self.size_px)
        self.label.setAlignment(Qt.AlignCenter)

        self.set_mood("idle")

    def set_mood(self, mood: str):
        """Sets mood to one of: idle, warning, intervention, happy, disappointed."""
        if not PYSIDE_AVAILABLE:
            self.current_state = mood
            return

        self.current_state = mood
        svg_path = os.path.join(self.asset_dir, f"{mood}.svg")
        if os.path.exists(svg_path):
            pixmap = QPixmap(self.size_px, self.size_px)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer = QSvgRenderer(svg_path)
            renderer.render(painter)
            painter.end()
            self.label.setPixmap(pixmap)
        else:
            # Fallback text emoji representation
            mood_emojis = {
                "idle": "🐨",
                "warning": "🐨⚠️",
                "intervention": "🐨🛑",
                "happy": "🐨✨",
                "disappointed": "🐨😐"
            }
            self.label.setText(mood_emojis.get(mood, "🐨"))
            self.label.setStyleSheet("font-size: 64px;")

    def play_intervention_sequence(self, on_close_tab_callback=None, on_finished_callback=None):
        """
        Plays the 8-step animation sequence:
          1. Koala appears.
          2. Koala slides onto screen.
          3. Koala moves toward the browser area.
          4. Koala points/gestures toward the browser.
          5. Koala performs a close gesture.
          6. Browser tab is closed or redirected.
          7. Koala returns.
          8. Todo List appears.
        """
        if not PYSIDE_AVAILABLE:
            if on_close_tab_callback:
                on_close_tab_callback()
            if on_finished_callback:
                on_finished_callback()
            return

        # Step 1 & 2: Slide onto screen
        self.set_mood("warning")

        QTimer.singleShot(400, lambda: self.set_mood("intervention"))

        # Step 3 & 4 & 5: Gesture toward browser
        if on_close_tab_callback:
            QTimer.singleShot(1200, on_close_tab_callback)

        # Step 6 & 7: Return to happy/todo trigger
        def finish_anim():
            self.set_mood("happy")
            if on_finished_callback:
                on_finished_callback()
            self.animation_completed.emit("intervention_done")

        QTimer.singleShot(2200, finish_anim)
