#!/usr/bin/env python3
"""Increment the PROMPT_COUNTER.md Current value and optionally commit the change.

Usage:
  python3 tools/increment_prompt_counter.py [--commit]
"""
import re
import sys
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / 'PROMPT_COUNTER.md'


def read_count():
    txt = PC.read_text()
    m = re.search(r"Current: (\d+)", txt)
    if not m:
        return 0
    return int(m.group(1))


def write_count(n: int):
    txt = PC.read_text()
    txt = re.sub(r"Current: (\d+)", f"Current: {n}", txt)
    PC.write_text(txt)


def git_commit():
    try:
        subprocess.run(["git", "add", str(PC)], check=True)
        subprocess.run(["git", "commit", "-m", "chore: bump prompt counter"], check=True)
        print("Committed prompt counter bump")
    except Exception as e:
        print("Commit failed:", e)


def main():
    n = read_count()
    n += 1
    write_count(n)
    print(f"Prompt counter incremented to {n}")
    if '--commit' in sys.argv:
        git_commit()


if __name__ == '__main__':
    main()
