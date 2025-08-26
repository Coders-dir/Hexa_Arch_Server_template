#!/usr/bin/env python3
"""Simple lockfile check: fail if pyproject.toml changed in the PR but poetry.lock not updated.

This is a conservative heuristic for PRs: it inspects git to see if `pyproject.toml` changed
and if so whether `poetry.lock` changed as well. For local runs it exits 0.
"""
import sys
from subprocess import check_output, CalledProcessError


def changed_files():
    try:
        out = check_output(["git", "diff", "--name-only", "origin/main..."])
        return out.decode().splitlines()
    except CalledProcessError:
        return []


def main():
    files = changed_files()
    if not files:
        print("No PR range detected; skipping lockfile check (local run).")
        return 0
    py_changed = any(f == "pyproject.toml" or f.endswith("pyproject.toml") for f in files)
    lock_changed = any(f == "poetry.lock" or f.endswith("poetry.lock") for f in files)
    if py_changed and not lock_changed:
        print("pyproject.toml changed but poetry.lock not updated. Please run 'poetry lock' and include the updated lockfile in the PR.")
        return 3
    print("Lockfile consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
