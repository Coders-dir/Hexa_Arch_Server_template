#!/usr/bin/env python3
"""Shim to run the canonical contract_check in service-template and forward exit code."""
import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / 'service-template' / 'tools' / 'contract_check.py'
if not TARGET.exists():
    print(f"Target not found: {TARGET}")
    sys.exit(2)

sys.exit(runpy.run_path(str(TARGET), run_name='__main__') or 0)
