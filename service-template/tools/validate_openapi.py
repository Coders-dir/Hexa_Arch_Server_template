#!/usr/bin/env python3
"""Validate basic structure of generated OpenAPI JSON."""
import json
from pathlib import Path
import sys


def main():
    p = Path(__file__).resolve().parents[1] / "src" / "app" / "openapi.json"
    if not p.exists():
        print(f"OpenAPI file not found: {p}")
        return 2
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        print("Invalid JSON:", e)
        return 3
    if not isinstance(data, dict) or "openapi" not in data or "paths" not in data:
        print("OpenAPI JSON missing required top-level keys ('openapi','paths')")
        return 4
    print("OpenAPI JSON looks valid (basic checks).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
