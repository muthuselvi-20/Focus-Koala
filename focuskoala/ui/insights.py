"""
FocusKoala Insights View (PySide6)
Displays productivity analytics, peak distraction patterns, and recovered time.
"""

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


class InsightsView(QWidget if PYSIDE_AVAILABLE else object):
    def __init__(self, agent=None, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.agent = agent
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header = QLabel("🐨 Your Insights", self)
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header)

        # Mascot quote card
        self.quote_card = QFrame(self)
        self.quote_card.setStyleSheet("""
            QFrame {
                background-color: #242833;
                border: 1px solid #E58E26;
                border-radius: 12px;
                padding: 14px;
            }
        """)
        q_layout = QVBoxLayout(self.quote_card)
        self.pattern_label = QLabel(self)
        self.pattern_label.setStyleSheet("font-size: 14px; color: #F8B739; font-weight: 500;")
        self.pattern_label.setWordWrap(True)
        q_layout.addWidget(self.pattern_label)
        layout.addWidget(self.quote_card)

        # Stats Grid
        grid = QGridLayout()
        grid.setSpacing(12)

        self.card_most_dist = self._make_stat_card("MOST DISTRACTING", "Instagram — 42m")
        self.card_peak_hour = self._make_stat_card("PEAK DISTRACTION", "2 PM")
        self.card_attempts = self._make_stat_card("REOPEN ATTEMPTS", "5")
        self.card_recovered = self._make_stat_card("TIME RECOVERED", "47m")

        grid.addWidget(self.card_most_dist["frame"], 0, 0)
        grid.addWidget(self.card_peak_hour["frame"], 0, 1)
        grid.addWidget(self.card_attempts["frame"], 1, 0)
        grid.addWidget(self.card_recovered["frame"], 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        self.refresh_insights()

    def _make_stat_card(self, title: str, val: str):
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E212B;
                border: 1px solid #2E333D;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        ly = QVBoxLayout(frame)
        lbl_title = QLabel(title, frame)
        lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #9CA3AF; letter-spacing: 0.5px;")
        ly.addWidget(lbl_title)

        lbl_val = QLabel(val, frame)
        lbl_val.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; margin-top: 4px;")
        ly.addWidget(lbl_val)

        return {"frame": frame, "title": lbl_title, "value": lbl_val}

    def refresh_insights(self):
        if not PYSIDE_AVAILABLE or not self.agent:
            return
        data = self.agent.pattern_engine.get_insights()
        self.pattern_label.setText(data.get("pattern_message") or '🐨 "Track more sessions to reveal your distraction patterns."')

        site = data.get("most_distracting_website", "Instagram")
        dur = data.get("most_distracting_duration", "0m")
        self.card_most_dist["value"].setText(f"{site.capitalize()} — {dur}")
        self.card_peak_hour["value"].setText(data.get("peak_distraction_hour", "2 PM"))
        self.card_attempts["value"].setText(str(data.get("reopen_attempts", 0)))
        self.card_recovered["value"].setText(str(data.get("time_recovered", "0m")))
