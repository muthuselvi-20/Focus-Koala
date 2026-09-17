# FocusKoala 🐨

> Local-first Windows 10/11 desktop productivity agent that detects excessive social-media usage, intervenes with an animated Koala, blocks the distracting website, and redirects you directly toward your next Todo task.

---

## 🚀 Quick Setup & Run Instructions

### 1. Requirements
- Python 3.11+ (or 3.10+)
- Google Chrome or Microsoft Edge (for Manifest V3 extension)

### 2. Install Dependencies
```bash
pip install -r focuskoala/requirements.txt
```

### 3. Start FocusKoala Desktop & Agent API
```bash
python run.py
```
*This launches:*
- The **FastAPI Local Agent** on `http://127.0.0.1:8000`
- The **PySide6 Desktop Dashboard & Animated Mascot**

### 4. Install Browser Extension (Chrome / Edge)
1. Open your browser and navigate to `chrome://extensions` or `edge://extensions`.
2. Toggle on **Developer Mode** (top right corner).
3. Click **Load unpacked**.
4. Select the directory: `focuskoala/extension`.
5. FocusKoala is now active!

---

## 🧪 Acceptance Test (Test Mode)

The default test mode is configured for **Instagram**:
- **Time limit**: 60 seconds
- **Warning**: 30 seconds
- **Cooldown**: 120 seconds

### Walkthrough:
1. Start `python run.py`.
2. Open `instagram.com` in your browser.
3. At **30 seconds**, the floating Koala warning appears:
   > 🐨 *"You have 30 seconds left on instagram.com."*
4. At **60 seconds**, the animated Koala intervention triggers:
   - Koala slides in and gestures to close the distraction.
   - The Instagram tab safely redirects to the FocusKoala blocked page (`blocked.html`).
   - Instagram enters a **120-second cooldown** (stored persistently in SQLite).
   - Today's Todo List appears with your highest priority task: *"Complete 3 DSA problems"*.
5. If you attempt to open Instagram again:
   - **Attempt 1**: 🐨 *"Instagram is on a break."* + Remaining countdown (e.g. `01:42`).
   - **Attempt 2**: 🐨 *"Nice try 😐"*
   - **Attempt 3+**: 🐨 *"You have tried opening Instagram 3 times."*
6. Clicking **[Start Task]** redirects you immediately to your focus task.
7. After the 120-second cooldown expires, access is automatically restored.

---

## 🔬 Run Automated Tests
```bash
pytest focuskoala/tests/test_focuskoala.py -v
```

---

## 📁 Architecture Overview
```
focuskoala/
├── desktop/         # Core Python desktop agent, rules, blocker, SQLite, todo, pattern engine
├── ui/              # PySide6 desktop GUI, animated Koala mascot widget, intervention window
├── api/             # FastAPI local REST service for extension communication
├── extension/       # Chrome/Edge Manifest V3 extension (background worker, blocked page, popup)
├── assets/koala/    # 2D Koala mascot SVG assets (idle, warning, intervention, happy, disappointed)
├── tests/           # Full pytest acceptance test suite
├── requirements.txt
├── README.md
└── run.py
```
