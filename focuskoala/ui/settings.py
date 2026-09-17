"""
FocusKoala Settings View (PySide6)
Allows configuring website limits, cooldown timers, test mode, and site toggles.
"""

from typing import Optional

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
        QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QMessageBox, QSpinBox
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


class SettingsView(QWidget if PYSIDE_AVAILABLE else object):
    if PYSIDE_AVAILABLE:
        settings_changed = Signal()

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

        header = QLabel("Website Limits & Rules", self)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header)

        # Quick Test Mode Banner
        test_banner = QHBoxLayout()
        self.test_mode_cb = QCheckBox("Enable Quick Test Mode (Instagram: 60s limit, 120s cooldown)", self)
        self.test_mode_cb.setStyleSheet("color: #F8B739; font-weight: bold; font-size: 13px;")
        if self.agent:
            self.test_mode_cb.setChecked(self.agent.db.get_setting("test_mode", "true") == "true")
        self.test_mode_cb.stateChanged.connect(self.on_toggle_test_mode)
        test_banner.addWidget(self.test_mode_cb)
        layout.addLayout(test_banner)

        # Add Website Form
        add_form = QHBoxLayout()
        self.domain_input = QLineEdit(self)
        self.domain_input.setPlaceholderText("Domain (e.g. twitter.com)")
        self.domain_input.setStyleSheet("background: #242833; border: 1px solid #374151; padding: 6px 10px; color: #FFF; border-radius: 6px;")
        add_form.addWidget(self.domain_input, stretch=2)

        self.limit_spin = QSpinBox(self)
        self.limit_spin.setRange(1, 300)
        self.limit_spin.setValue(30)
        self.limit_spin.setSuffix(" min limit")
        self.limit_spin.setStyleSheet("background: #242833; border: 1px solid #374151; padding: 6px; color: #FFF; border-radius: 6px;")
        add_form.addWidget(self.limit_spin, stretch=1)

        self.cool_spin = QSpinBox(self)
        self.cool_spin.setRange(1, 300)
        self.cool_spin.setValue(45)
        self.cool_spin.setSuffix(" min cool")
        self.cool_spin.setStyleSheet("background: #242833; border: 1px solid #374151; padding: 6px; color: #FFF; border-radius: 6px;")
        add_form.addWidget(self.cool_spin, stretch=1)

        add_site_btn = QPushButton("Add Site", self)
        add_site_btn.setStyleSheet("background: #E58E26; color: #FFF; font-weight: bold; padding: 6px 14px; border: none; border-radius: 6px;")
        add_site_btn.clicked.connect(self.on_add_site)
        add_form.addWidget(add_site_btn)

        layout.addLayout(add_form)

        # Table of Websites
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Domain", "Limit", "Cooldown", "Active", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1A1C23;
                border: 1px solid #2E333D;
                color: #FFFFFF;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #242833;
                color: #9CA3AF;
                padding: 6px;
                border: none;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        if not PYSIDE_AVAILABLE or not self.agent:
            return
        sites = self.agent.db.get_websites()
        self.table.setRowCount(len(sites))

        for row, s in enumerate(sites):
            self.table.setItem(row, 0, QTableWidgetItem(s["domain"]))
            lim_text = f"{s['limit_seconds']}s" if s["limit_seconds"] < 120 else f"{s['limit_seconds'] // 60}m"
            cool_text = f"{s['cooldown_seconds']}s" if s["cooldown_seconds"] < 120 else f"{s['cooldown_seconds'] // 60}m"
            self.table.setItem(row, 1, QTableWidgetItem(lim_text))
            self.table.setItem(row, 2, QTableWidgetItem(cool_text))

            cb = QCheckBox()
            cb.setChecked(bool(s["enabled"]))
            cb.stateChanged.connect(lambda state, dom=s["domain"]: self.on_toggle_site(dom, state))
            self.table.setCellWidget(row, 3, cb)

            del_btn = QPushButton("Remove")
            del_btn.setStyleSheet("background: #EF4444; color: #FFF; border: none; border-radius: 4px; padding: 4px;")
            del_btn.clicked.connect(lambda checked, dom=s["domain"]: self.on_remove_site(dom))
            self.table.setCellWidget(row, 4, del_btn)

    def on_add_site(self):
        dom = self.domain_input.text().strip()
        if not dom or not self.agent:
            return
        lim_sec = self.limit_spin.value() * 60
        cool_sec = self.cool_spin.value() * 60
        name = dom.split(".")[0].capitalize()
        self.agent.db.add_website(dom, name, lim_sec, cool_sec, enabled=True)
        self.domain_input.clear()
        self.refresh_table()
        self.settings_changed.emit()

    def on_toggle_site(self, domain: str, state):
        if self.agent:
            self.agent.db.update_website(domain, enabled=(state == Qt.Checked))
            self.settings_changed.emit()

    def on_remove_site(self, domain: str):
        if self.agent:
            self.agent.db.remove_website(domain)
            self.refresh_table()
            self.settings_changed.emit()

    def on_toggle_test_mode(self, state):
        if self.agent:
            val = "true" if state == Qt.Checked else "false"
            self.agent.db.set_setting("test_mode", val)
            self.settings_changed.emit()
