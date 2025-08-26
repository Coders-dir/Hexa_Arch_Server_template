import os
import time

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="integration tests")


@pytest.mark.usefixtures("integration_dbs")
def test_admin_api_db_create_list_revoke():
    os.environ["USE_DB_KEYS"] = "1"
    from src.app.main import app

    client = TestClient(app)

    # create key
    resp = client.post("/api/admin/api-keys", json={"name": "dbkey", "owner": "ci"})
    assert resp.status_code == 200
    body = resp.json()
    assert "kid" in body and "token" in body
    kid = body["kid"]

    # short retry loop for eventual consistency
    found = False
    for _ in range(10):
        resp = client.get("/api/admin/api-keys")
        if resp.status_code == 200 and any(k["kid"] == kid for k in resp.json()):
            found = True
            break
        time.sleep(0.5)
    assert found

    # revoke
    resp = client.post(f"/api/admin/api-keys/{kid}/revoke")
    assert resp.status_code == 200

