import os
import sys
import time
import subprocess
import signal

import redis


def test_worker_consumes_job(tmp_path):
    """Start the worker as a subprocess, push a job into Redis sorted set, and assert the job is consumed."""
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT

    # start worker
    worker_proc = subprocess.Popen([sys.executable, "src/app/worker.py"], cwd=ROOT, env=env)

    try:
        # give worker a moment to initialize
        time.sleep(0.5)

        r = redis.Redis(host="127.0.0.1", port=6379, db=0)

        # push a test job (member format: "priority::payload") with score = now*1000
        member = "0::acceptance-job"
        score = int(time.time()) * 1000
        r.zadd("dispatcher:priority_queue", {member: score})

        # wait up to 6 seconds for worker to consume the job
        deadline = time.time() + 6
        consumed = False
        while time.time() < deadline:
            items = r.zrange("dispatcher:priority_queue", 0, -1)
            if not items:
                consumed = True
                break
            time.sleep(0.2)

        assert consumed, "Worker did not consume the job in time"
    finally:
        # terminate worker
        try:
            worker_proc.send_signal(signal.SIGINT)
            worker_proc.wait(timeout=3)
        except Exception:
            worker_proc.kill()
            worker_proc.wait(timeout=3)
