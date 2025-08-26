#!/usr/bin/env python3
"""Shim: run the service-template openapi generator and copy the output to the monolith path.

This preserves compatibility for tests and tools that expect the OpenAPI JSON at
monolith-template/src/app/openapi.json while the canonical script lives in
service-template/tools/generate_openapi.py and writes service-template/src/app/openapi.json.
"""
import runpy
import sys
import shutil
from pathlib import Path


TARGET = Path(__file__).resolve().parents[2] / 'service-template' / 'tools' / 'generate_openapi.py'
if not TARGET.exists():
    print(f"Target not found: {TARGET}")
    sys.exit(2)

# Run the target script and capture exit code
rc = 0
try:
    runpy.run_path(str(TARGET), run_name='__main__')
except SystemExit as e:
    rc = e.code or 0
except Exception as e:
    print("Error running target generate_openapi:", e)
    rc = 2

# If the service-template script produced an openapi.json, copy it to the monolith path
src_openapi = TARGET.resolve().parents[1] / 'src' / 'app' / 'openapi.json'
dest_openapi = Path(__file__).resolve().parents[1] / 'src' / 'app' / 'openapi.json'
if src_openapi.exists():
    dest_openapi.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(str(src_openapi), str(dest_openapi))
        print(f"Copied OpenAPI from {src_openapi} -> {dest_openapi}")
    except Exception as e:
        print("Failed to copy OpenAPI file:", e)
        rc = rc or 2
else:
    print(f"OpenAPI not found at expected source path: {src_openapi}")

sys.exit(rc)
