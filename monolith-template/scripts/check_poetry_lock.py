"""Fail if `pyproject.toml` and `poetry.lock` are out of sync.

This script tries to use `poetry lock --check` (supported in newer Poetry).
If not available, it will regenerate `poetry.lock`, detect changes, and restore
the original file. Exit 0 when lock matches pyproject, non-zero otherwise.
"""
import subprocess
import sys
import os
import hashlib


def sha1(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main():
    cwd = os.getcwd()
    lock_path = os.path.join(cwd, "poetry.lock")
    if not os.path.exists(lock_path):
        print("poetry.lock not found; run `poetry lock` to generate one first.")
        return 1

    # Try the modern check first
    try:
        subprocess.check_call(["poetry", "lock", "--check"], cwd=cwd)
        print("poetry lock is up-to-date (checked with --check)")
        return 0
    except subprocess.CalledProcessError:
        print("poetry reported lock mismatch via --check or non-zero exit")
        return 1
    except Exception:
        # Fallback path for Poetry versions without --check
        print("--check not supported; falling back to regenerate-and-compare")

    before = sha1(lock_path)
    try:
        subprocess.check_call(["poetry", "lock"], cwd=cwd)
    except subprocess.CalledProcessError as e:
        print("poetry lock failed:", e)
        return 2

    after = sha1(lock_path)
    if before != after:
        print("poetry.lock would change if regenerated; please run 'poetry lock' and commit the result.")
        # restore original from git to avoid dirty working tree
        try:
            subprocess.check_call(["git", "checkout", "--", "poetry.lock"], cwd=cwd)
        except Exception:
            print("failed to restore poetry.lock from git; working tree may be modified")
        return 3

    print("poetry lock is up-to-date (regenerated and matches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
