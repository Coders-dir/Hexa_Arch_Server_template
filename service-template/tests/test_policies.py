import subprocess
import json
import os


def test_arch_check_runs():
    res = subprocess.run(["python3", "service-template/tools/arch_check.py"], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_openapi_and_contract():
    # generate openapi
    res = subprocess.run(["python3", "service-template/tools/generate_openapi.py"], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # validate openapi JSON
    path = "service-template/src/app/openapi.json"
    assert os.path.exists(path)
    with open(path) as fh:
        data = json.load(fh)
    assert "openapi" in data
    # run contract check
    res = subprocess.run(["python3", "service-template/tools/contract_check.py"], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_lockfile_check_allows_local_skip():
    res = subprocess.run(["python3", "service-template/tools/lockfile_check.py"], capture_output=True, text=True)
    # local run may return 0 (skipped) or 3 (intentional fail in PR context)
    assert res.returncode in (0, 3)
