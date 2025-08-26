#!/usr/bin/env python3
"""Contract check: compare generated OpenAPI JSON with an expected contract if present.

If `contracts/expected_openapi.json` exists, the script compares top-level keys and reports
missing paths or operations. If no expected contract is present, the script exits 0 with a warning.
"""
import json
from pathlib import Path
import sys


def load(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"Failed to load JSON from {path}: {e}")
        return None


def compare(expected, actual):
    diffs = []
    exp_paths = set(expected.get("paths", {}).keys())
    act_paths = set(actual.get("paths", {}).keys())
    for p in exp_paths - act_paths:
        diffs.append(f"Missing path in generated OpenAPI: {p}")
    # compare operations per path
    for p in exp_paths & act_paths:
        exp_ops = set(expected["paths"][p].keys())
        act_ops = set(actual["paths"][p].keys())
        for op in exp_ops - act_ops:
            diffs.append(f"Missing operation for {p}: {op}")
    return diffs


def main():
    root = Path(__file__).resolve().parents[1]
    gen = root / "src" / "app" / "openapi.json"
    expected = root / "contracts" / "expected_openapi.json"
    if not gen.exists():
        print(f"Generated OpenAPI not found: {gen}")
        return 2
    actual = load(gen)
    if actual is None:
        return 3
    if not expected.exists():
        print("No expected contract found (contracts/expected_openapi.json). Skipping strict contract comparison.")
        return 0
    exp = load(expected)
    if exp is None:
        return 4
    diffs = compare(exp, actual)
    if diffs:
        print("Contract differences detected:")
        for d in diffs:
            print(" -", d)
        return 5
    print("Contract check passed: generated OpenAPI conforms to expected contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
