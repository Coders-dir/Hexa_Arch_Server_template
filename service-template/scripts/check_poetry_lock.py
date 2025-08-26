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

    # Try the modern check first. Some Poetry versions don't support --check
    # (they print a 'does not exist' message); capture output and inspect it so
    # we can fall back to regenerate-and-compare instead of failing the job.
    try:
        proc = subprocess.run(["poetry", "lock", "--check"], cwd=cwd, capture_output=True, text=True)
        if proc.returncode == 0:
            print("poetry lock is up-to-date (checked with --check)")
            return 0

        # Combine stdout/stderr and look for messages that indicate the option
        # is not supported rather than a real lock mismatch.
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        lowered = combined.lower()
        unsupported_signals = [
            "does not exist",
            "no such option",
            "unknown option",
            "is not a command",
            "is not a valid option",
        ]
        if any(s in lowered for s in unsupported_signals):
            print("--check not supported by this poetry version; falling back to regenerate-and-compare")
        else:
            print("poetry reported lock mismatch via --check or non-zero exit")
            print(combined)
            return 1
    except Exception:
        # Fallback path for Poetry versions or environments where running
        # the above fails; fall through to regenerate-and-compare.
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
