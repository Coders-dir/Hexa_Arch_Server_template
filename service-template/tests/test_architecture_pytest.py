import subprocess


def test_architecture_enforcement():
    """Run the architecture enforcement check and assert zero violations."""
    res = subprocess.run(['python3', 'monolith-template/tools/arch_check.py'], capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
    assert res.returncode == 0
