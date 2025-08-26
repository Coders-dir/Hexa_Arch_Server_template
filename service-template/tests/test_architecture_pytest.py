import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_path(p: str) -> str:
    return str((REPO_ROOT / p).resolve())


def test_architecture_enforcement():
    """Run the architecture enforcement check and assert zero violations."""
    res = subprocess.run(['python3', repo_path('service-template/tools/arch_check.py')], capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
    assert res.returncode == 0
