"""Lightweight smoke runner for Postman collection endpoints.

Behavior:
- Hits /health and expects {"status":"ok"}
- If ADMIN_TOKEN env var present, hits GET /api/admin/api-keys and POST /api/admin/api-keys

Exit codes:
- 0 on success
- non-zero on failure
"""
import os
import sys
import time
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def check_health():
    url = f"{BASE}/health"
    print("Checking health ->", url)
    r = requests.get(url, timeout=5)
    print("status", r.status_code, r.text)
    if r.status_code != 200:
        print("Health check failed")
        return False
    try:
        j = r.json()
        return j.get("status") == "ok"
    except Exception:
        return False


def admin_list():
    url = f"{BASE}/api/admin/api-keys"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"} if ADMIN_TOKEN else {}
    print("Listing api-keys ->", url)
    r = requests.get(url, headers=headers, timeout=5)
    print("status", r.status_code, r.text)
    return r.status_code == 200


def admin_create():
    url = f"{BASE}/api/admin/api-keys"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"} if ADMIN_TOKEN else {}
    payload = {"name": "smoke-key", "owner": "smoke"}
    print("Creating api-key ->", url)
    r = requests.post(url, json=payload, headers=headers, timeout=5)
    print("status", r.status_code, r.text)
    return r.status_code == 200


if __name__ == "__main__":
    # Wait for service to be up a few seconds
    for i in range(10):
        if check_health():
            break
        print("waiting for service...", i)
        time.sleep(1)
    else:
        print("service did not become healthy")
        sys.exit(2)

    ok = True
    if ADMIN_TOKEN:
        ok = ok and admin_list()
        ok = ok and admin_create()
    if not ok:
        print("smoke failed")
        sys.exit(3)
    print("smoke ok")
    sys.exit(0)
