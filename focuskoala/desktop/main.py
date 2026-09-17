"""
FocusKoala Main Desktop Launcher
Initializes SQLite database, starts FastAPI background server, and launches PySide6 UI.
"""

import sys
import os
import threading
import uvicorn

# Ensure package path is resolved
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from focuskoala.desktop.agent import FocusKoalaAgent
from focuskoala.desktop.database import init_db
from focuskoala.api.server import app as fastapi_app


def start_fastapi(host: str = "127.0.0.1", port: int = 8000):
    """Runs the FastAPI server for browser extension and local client communication."""
    print(f"[FocusKoala] Starting local agent API at http://{host}:{port} ...")
    uvicorn.run(fastapi_app, host=host, port=port, log_level="warning")


def main():
    print("=" * 60)
    print("🐨 FocusKoala — Windows 10/11 Desktop Productivity Agent")
    print("=" * 60)

    # 1. Initialize SQLite Database
    init_db()

    # 2. Instantiate Agent
    agent = FocusKoalaAgent()

    # 3. Start FastAPI server in background daemon thread
    api_thread = threading.Thread(target=start_fastapi, kwargs={"host": "0.0.0.0", "port": 8000}, daemon=True)
    api_thread.start()

    # 4. Launch PySide6 Desktop GUI (if display is available)
    try:
        from PySide6.QtWidgets import QApplication
        from focuskoala.ui.dashboard import FocusKoalaDashboard

        qt_app = QApplication(sys.argv)
        qt_app.setApplicationName("FocusKoala")

        dashboard = FocusKoalaDashboard(agent)
        dashboard.show()

        print("[FocusKoala] Desktop Dashboard launched successfully.")
        sys.exit(qt_app.exec())
    except Exception as e:
        print(f"[FocusKoala] Note: GUI environment not active or PySide6 display unavailable: {e}")
        print("[FocusKoala] Running in API & Headless Agent Mode. Listening on port 8000...")
        # Keep API running
        try:
            api_thread.join()
        except KeyboardInterrupt:
            print("\n[FocusKoala] Stopping agent.")


if __name__ == "__main__":
    main()
