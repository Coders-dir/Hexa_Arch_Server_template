import os
import time
import subprocess
import sys

import requests


def test_metrics_endpoint():
    # ensure app is running; start uvicorn if not
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT

    # start app
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.app.main:app", "--host", "127.0.0.1", "--port", "8001"], cwd=ROOT, env=env)
    try:
        # wait for startup
        for _ in range(10):
            try:
                r = requests.get("http://127.0.0.1:8001/metrics", timeout=1)
                if r.status_code == 200:
                    break
            except Exception:
                time.sleep(0.5)
        else:
            proc.kill()
            assert False, "metrics endpoint not reachable"

        text = requests.get("http://127.0.0.1:8001/metrics", timeout=1).text
        # The app exposes Prometheus metrics; assert a generic metric is present
        assert "python_gc_objects_collected_total" in text or "api_key_repo_pool_init_failures_created" in text
    finally:
        proc.kill()
        proc.wait()
