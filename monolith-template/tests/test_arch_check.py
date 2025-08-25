def test_arch_check_runs():
    import subprocess
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    script = root / "tools" / "arch_check.py"
    res = subprocess.run(["python3", str(script)], capture_output=True, text=True)
    assert res.returncode == 0, f"arch_check failed: {res.stdout}\n{res.stderr}"
