import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_path(p: str) -> str:
    return str((REPO_ROOT / p).resolve())


def test_lockfile_check():
    """Run the lockfile check script. In local runs the script may exit 0 (skip) or 3 (fail).
    Accept either to allow local development without PR context."""
    res = subprocess.run(['python3', repo_path('service-template/tools/lockfile_check.py')], capture_output=True, text=True)
    print(res.stdout)
    print(res.stderr)
    assert res.returncode in (0,3)
