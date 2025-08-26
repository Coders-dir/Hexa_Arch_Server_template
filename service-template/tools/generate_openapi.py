#!/usr/bin/env python3
"""Generate OpenAPI JSON by importing the FastAPI app and writing its openapi output.

This script imports `src.app.main.app` and writes `src/app/openapi.json`.
"""
import json
from pathlib import Path
import sys


def main():
    try:
        # Ensure project root is on sys.path so 'src' package can be imported
        root = Path(__file__).resolve().parents[1]
        proj_root = str(root)
        if proj_root not in sys.path:
            sys.path.insert(0, proj_root)
        # Import the app module under package name 'src'
        import importlib

        app_mod = importlib.import_module("src.app.main")
        app = getattr(app_mod, "app", None)
        if app is None:
            print("No FastAPI app found in src.app.main")
            return 2
        openapi = app.openapi()
        out = Path(__file__).resolve().parents[1] / "src" / "app" / "openapi.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(openapi, indent=2))
        print(f"Wrote OpenAPI to {out}")
        return 0
    except ModuleNotFoundError as e:
        print("Failed to generate OpenAPI: missing dependency:", e)
        print("Ensure dependencies are installed (poetry install) in Codespaces before running this script.")
        return 3
    except Exception as e:
        print("Failed to generate OpenAPI:", e)
        return 3


if __name__ == "__main__":
    sys.exit(main())
