"""
FocusKoala Main Desktop Dashboard (PySide6)
Central hub showing Focus metrics, Website usage, Today's tasks, Focus Mode, and navigation.
"""

from typing import Optional

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFrame, QGridLayout, QStackedWidget, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

from .koala_widget import KoalaWidget
from .todo_view import TodoView
from .insights import InsightsView
from .settings import SettingsView
from .intervention import InterventionWindow


class FocusKoalaDashboard(QMainWindow if PYSIDE_AVAILABLE else object):
    def __init__(self, agent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__()
        self.agent = agent
        self.setWindowTitle("FocusKoala 🐨 — Desktop Productivity Agent")
        self.resize(860, 620)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #12141A;
            }
            QLabel {
                color: #FFFFFF;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)

        self.intervention_window = InterventionWindow(self.agent)
        if self.agent:
            self.agent.register_intervention_handler(self._handle_agent_intervention)

        self._init_ui()

        # Timer to update stats every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(2000)

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Left Sidebar Navigation ---
        sidebar = QFrame(self)
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #181A22;
                border-right: 1px solid #282C37;
            }
        """)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 20, 16, 20)
        side_layout.setSpacing(10)

        # Mascot & Logo
        logo_row = QHBoxLayout()
        self.koala_icon = KoalaWidget(sidebar, size=36)
        logo_row.addWidget(self.koala_icon)
        app_title = QLabel("FocusKoala", sidebar)
        app_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #FFFFFF; border: none;")
        logo_row.addWidget(app_title)
        logo_row.addStretch()
        side_layout.addLayout(logo_row)

        side_layout.addSpacing(16)

        # Nav Buttons
        self.btn_dash = self._create_nav_btn("📊 Dashboard", 0)
        self.btn_focus = self._create_nav_btn("🎯 Focus Mode", 1)
        self.btn_tasks = self._create_nav_btn("📝 Tasks", 2)
        self.btn_insights = self._create_nav_btn("💡 Insights", 3)
        self.btn_websites = self._create_nav_btn("🌐 Manage Websites", 4)

        side_layout.addWidget(self.btn_dash)
        side_layout.addWidget(self.btn_focus)
        side_layout.addWidget(self.btn_tasks)
        side_layout.addWidget(self.btn_insights)
        side_layout.addWidget(self.btn_websites)

        side_layout.addStretch()

        # Quick Test Trigger
        test_trigger_btn = QPushButton("🧪 Test Intervention", sidebar)
        test_trigger_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(229, 142, 38, 0.15);
                color: #F8B739;
                border: 1px dashed #E58E26;
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(229, 142, 38, 0.25);
            }
        """)
        test_trigger_btn.clicked.connect(self._trigger_test_intervention)
        side_layout.addWidget(test_trigger_btn)

        root_layout.addWidget(sidebar)

        # --- Right Stacked Content Pages ---
        self.pages = QStackedWidget(self)

        # Page 0: Main Dashboard
        self.page_dash = self._create_dashboard_page()
        self.pages.addWidget(self.page_dash)

        # Page 1: Focus Mode page
        self.page_focus = self._create_focus_mode_page()
        self.pages.addWidget(self.page_focus)

        # Page 2: Tasks
        self.todo_view = TodoView(self.agent)
        self.pages.addWidget(self.todo_view)

        # Page 3: Insights
        self.insights_view = InsightsView(self.agent)
        self.pages.addWidget(self.insights_view)

        # Page 4: Settings / Manage Websites
        self.settings_view = SettingsView(self.agent)
        self.pages.addWidget(self.settings_view)

        root_layout.addWidget(self.pages)

        self.refresh_dashboard()

    def _create_nav_btn(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9CA3AF;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
                padding: 10px 12px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: #FFFFFF;
            }
        """)
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(page_index))
        return btn

    def _create_dashboard_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Dashboard Overview", w)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFF;")
        layout.addWidget(header)

        # 4 Metric Cards
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(12)

        self.card_focus = self._make_metric_card("TODAY'S FOCUS", "2h 18m", "#10B981")
        self.card_distract = self._make_metric_card("TODAY'S DISTRACTION", "31m", "#EF4444")
        self.card_recov = self._make_metric_card("TIME RECOVERED", "47m", "#E58E26")
        self.card_tasks = self._make_metric_card("TASKS COMPLETED", "4", "#3B82F6")

        metrics_grid.addWidget(self.card_focus["frame"], 0, 0)
        metrics_grid.addWidget(self.card_distract["frame"], 0, 1)
        metrics_grid.addWidget(self.card_recov["frame"], 0, 2)
        metrics_grid.addWidget(self.card_tasks["frame"], 0, 3)

        layout.addLayout(metrics_grid)

        # Two Column section: Website Usage & Today's Tasks
        cols = QHBoxLayout()
        cols.setSpacing(14)

        # Left Column: Website Usage
        site_box = QFrame(w)
        site_box.setStyleSheet("background: #181A22; border: 1px solid #282C37; border-radius: 12px; padding: 14px;")
        site_layout = QVBoxLayout(site_box)
        site_title = QLabel("Website Usage", site_box)
        site_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFF; border: none;")
        site_layout.addWidget(site_title)

        self.site_list_widget = QListWidget(site_box)
        self.site_list_widget.setStyleSheet("background: transparent; border: none;")
        site_layout.addWidget(self.site_list_widget)
        cols.addWidget(site_box, stretch=1)

        # Right Column: Today's Tasks
        todo_box = QFrame(w)
        todo_box.setStyleSheet("background: #181A22; border: 1px solid #282C37; border-radius: 12px; padding: 14px;")
        todo_layout = QVBoxLayout(todo_box)
        todo_title = QLabel("Today's Tasks", todo_box)
        todo_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFF; border: none;")
        todo_layout.addWidget(todo_title)

        self.dash_todo_list = QListWidget(todo_box)
        self.dash_todo_list.setStyleSheet("background: transparent; border: none;")
        todo_layout.addWidget(self.dash_todo_list)
        cols.addWidget(todo_box, stretch=1)

        layout.addLayout(cols)

        # Action Buttons Row
        btn_bar = QHBoxLayout()
        btn_focus_mode = QPushButton("🎯 Start Focus Mode", w)
        btn_focus_mode.setStyleSheet("background: #E58E26; color: #FFF; font-weight: bold; padding: 10px 18px; border: none; border-radius: 8px;")
        btn_focus_mode.clicked.connect(lambda: self.pages.setCurrentIndex(1))

        btn_manage = QPushButton("🌐 Manage Websites", w)
        btn_manage.setStyleSheet("background: #242833; color: #FFF; padding: 10px 18px; border: 1px solid #374151; border-radius: 8px;")
        btn_manage.clicked.connect(lambda: self.pages.setCurrentIndex(4))

        btn_all_tasks = QPushButton("📝 Tasks", w)
        btn_all_tasks.setStyleSheet("background: #242833; color: #FFF; padding: 10px 18px; border: 1px solid #374151; border-radius: 8px;")
        btn_all_tasks.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        btn_ins = QPushButton("💡 Insights", w)
        btn_ins.setStyleSheet("background: #242833; color: #FFF; padding: 10px 18px; border: 1px solid #374151; border-radius: 8px;")
        btn_ins.clicked.connect(lambda: self.pages.setCurrentIndex(3))

        btn_bar.addWidget(btn_focus_mode)
        btn_bar.addWidget(btn_manage)
        btn_bar.addWidget(btn_all_tasks)
        btn_bar.addWidget(btn_ins)
        btn_bar.addStretch()

        layout.addLayout(btn_bar)
        return w

    def _make_metric_card(self, title: str, default_val: str, accent_color: str):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #181A22;
                border: 1px solid #282C37;
                border-top: 3px solid {accent_color};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        ly = QVBoxLayout(frame)
        ly.setContentsMargins(6, 4, 6, 4)

        t = QLabel(title, frame)
        t.setStyleSheet("font-size: 10px; font-weight: bold; color: #9CA3AF; letter-spacing: 0.5px; border: none;")
        ly.addWidget(t)

        v = QLabel(default_val, frame)
        v.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; margin-top: 2px; border: none;")
        ly.addWidget(v)

        return {"frame": frame, "val": v}

    def _create_focus_mode_page(self) -> QWidget:
        """Feature 12: Focus Mode (30m, 60m, 90m, custom)."""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QLabel("🐨 Focus Mode", w)
        h.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFF;")
        layout.addWidget(h)

        sub = QLabel("Block distracting websites and dedicate undistracted time toward your goal.", w)
        sub.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        layout.addWidget(sub)

        # Current Status Card
        self.focus_status_card = QFrame(w)
        self.focus_status_card.setStyleSheet("background: #181A22; border: 2px solid #E58E26; border-radius: 14px; padding: 20px;")
        f_layout = QVBoxLayout(self.focus_status_card)

        self.focus_timer_lbl = QLabel("No active focus session", self.focus_status_card)
        self.focus_timer_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #F8B739; border: none;")
        f_layout.addWidget(self.focus_timer_lbl)

        self.focus_task_lbl = QLabel("", self.focus_status_card)
        self.focus_task_lbl.setStyleSheet("font-size: 14px; color: #D1D5DB; border: none;")
        f_layout.addWidget(self.focus_task_lbl)

        layout.addWidget(self.focus_status_card)

        # Quick Duration Buttons
        dur_row = QHBoxLayout()
        for mins in [30, 60, 90]:
            btn = QPushButton(f"{mins} Minutes", w)
            btn.setStyleSheet("background: #242833; color: #FFF; padding: 12px; border: 1px solid #374151; border-radius: 8px; font-weight: bold;")
            btn.clicked.connect(lambda checked, m=mins: self._start_focus(m))
            dur_row.addWidget(btn)

        btn_custom = QPushButton("Custom...", w)
        btn_custom.setStyleSheet("background: #242833; color: #FFF; padding: 12px; border: 1px solid #374151; border-radius: 8px; font-weight: bold;")
        btn_custom.clicked.connect(self._start_custom_focus)
        dur_row.addWidget(btn_custom)

        layout.addLayout(dur_row)

        self.btn_stop_focus = QPushButton("Stop Focus Mode", w)
        self.btn_stop_focus.setStyleSheet("background: #EF4444; color: #FFF; padding: 10px; font-weight: bold; border-radius: 8px; border: none;")
        self.btn_stop_focus.clicked.connect(self._stop_focus)
        layout.addWidget(self.btn_stop_focus)

        layout.addStretch()
        return w

    def _start_focus(self, minutes: int):
        if self.agent:
            self.agent.start_focus_mode(minutes)
            self.refresh_dashboard()

    def _start_custom_focus(self):
        mins, ok = QInputDialog.getInt(self, "Custom Focus Mode", "Minutes:", 45, 5, 240)
        if ok:
            self._start_focus(mins)

    def _stop_focus(self):
        if self.agent:
            self.agent.stop_focus_mode()
            self.refresh_dashboard()

    def _trigger_test_intervention(self):
        """Simulates 60s limit breach for test acceptance."""
        self.intervention_window.trigger_intervention(
            domain="instagram.com",
            task_title="Complete 3 DSA problems"
        )

    def _handle_agent_intervention(self, result):
        domain = result.get("domain", "distracting website")
        task = (result.get("recommended_task") or {}).get("title", "Focus Task")
        self.intervention_window.trigger_intervention(domain, task)

    def refresh_dashboard(self):
        if not PYSIDE_AVAILABLE or not self.agent:
            return
        summary = self.agent.get_dashboard_summary()

        self.card_focus["val"].setText(summary.get("today_focus", "0m"))
        self.card_distract["val"].setText(summary.get("today_distraction", "0m"))
        self.card_recov["val"].setText(summary.get("time_recovered", "0m"))
        self.card_tasks["val"].setText(str(summary.get("tasks_completed", 0)))

        # Update Website Usage List
        self.site_list_widget.clear()
        for site in summary.get("websites", []):
            item = QListWidgetItem(f"🌐  {site['name']} — {site['used_formatted']}")
            if site.get("is_blocked"):
                item.setText(f"🛑  {site['name']} — BLOCKED")
            self.site_list_widget.addItem(item)

        # Update Today's Tasks preview
        self.dash_todo_list.clear()
        for t in summary.get("todos", [])[:5]:
            mark = "☑" if t["completed"] else "☐"
            self.dash_todo_list.addItem(f"{mark}  {t['title']}")

        # Focus mode status
        f_status = summary.get("focus_mode", {})
        if f_status.get("active"):
            self.focus_timer_lbl.setText(f"Remaining: {f_status['remaining_formatted']}")
            self.focus_task_lbl.setText(f"Current task: {f_status.get('task', '')}")
            self.btn_stop_focus.show()
        else:
            self.focus_timer_lbl.setText("No active focus session")
            self.focus_task_lbl.setText("Select a duration to begin.")
            self.btn_stop_focus.hide()
