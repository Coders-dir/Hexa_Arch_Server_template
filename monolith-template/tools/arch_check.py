#!/usr/bin/env python3
import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / 'service-template' / 'tools' / 'arch_check.py'
if not TARGET.exists():
    print(f"Target not found: {TARGET}")
    sys.exit(2)
sys.exit(runpy.run_path(str(TARGET), run_name='__main__') or 0)
