#!/usr/bin/env python3
"""
FocusKoala Root Entry Point
Usage:
    python run.py
"""

import sys
import os

# Add focuskoala directory to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from focuskoala.desktop.main import main

if __name__ == "__main__":
    main()
