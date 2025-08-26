#!/usr/bin/env python3
"""Shim: forward to service-template/scripts/check_poetry_lock.py
This keeps CI workflows that reference monolith-template/scripts working during migration.
"""
import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / 'service-template' / 'scripts' / 'check_poetry_lock.py'
if not TARGET.exists():
    print(f"Target not found: {TARGET}")
    sys.exit(2)

sys.exit(runpy.run_path(str(TARGET), run_name='__main__') or 0)
