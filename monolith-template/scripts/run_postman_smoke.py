#!/usr/bin/env python3
"""Shim to run service-template Postman smoke script from monolith-template path."""
import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / 'service-template' / 'scripts' / 'run_postman_smoke.py'
if not TARGET.exists():
    print(f"Target not found: {TARGET}")
    sys.exit(2)

sys.exit(runpy.run_path(str(TARGET), run_name='__main__') or 0)
